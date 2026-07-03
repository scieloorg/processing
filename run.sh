#!/bin/bash
#
# Script para tabulação de acessos e publicação de artigos SciELO.
# Envia notificações ao Slack quando SLACK_WEBHOOK_URL estiver configurado
# e copia os arquivos gerados para um diretório persistente.

set -euo pipefail

readonly DOCKER_ENV="${DOCKER_ENV:-0}"
if [[ "$DOCKER_ENV" == "1" ]]; then
    readonly PROCESSING_SETTINGS_FILE="${PROCESSING_SETTINGS_FILE-}"
else
    readonly PROCESSING_SETTINGS_FILE="${PROCESSING_SETTINGS_FILE:-/etc/scieloapps/processing.ini}"
fi
readonly VENV_DIR="${VENV_DIR:-/var/www/.venvs/processing}"
readonly WORK_DIR="${WORK_DIR:-/var/www/processing}"
readonly LOG_DIR="${LOG_DIR:-/var/log/processing}"
readonly NETWORK_DIR="network"
readonly TABS_DIR="${TABS_DIR:-/var/www/static_scielo_org/tabs}"
readonly MAX_RETRIES="${MAX_RETRIES:-3}"
readonly RETRY_DELAY="${RETRY_DELAY:-5}"
readonly EXIT_ON_FAILURE="${EXIT_ON_FAILURE:-true}"
readonly TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
readonly REPORT_DATE="$(date +%F)"
readonly MASTER_LOG="$LOG_DIR/master_$TIMESTAMP.log"
readonly SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
readonly FAILED_COLLECTIONS_FILE="${FAILED_COLLECTIONS_FILE:-$LOG_DIR/failed_collections.queue}"

readonly DEFAULT_ACRONYMS=(
    "scl-BR" "arg-AR" "bol-BO" "chl-CL" "cub-CU" "col-CO"
    "cri-CR" "ecu-EC" "esp-ES" "mex-MX" "per-PE" "prt-PR"
    "pry-PY" "psi-BR" "rve-BR" "rvt-BR" "spa-BR" "sss-BR"
    "sza-SZ" "ury-UY" "ven-VE" "wid-WI" "dom-DO"
)

readonly CSV_FILES=(
    "documents_affiliations"
    "documents_affiliation_nationality"
    "documents_authors"
    "documents_counts"
    "documents_dates"
    "documents_languages"
    "documents_licenses"
    "journals"
    "journals_status_changes"
)

kbart_csv_file() {
    local acronym=$1
    echo "SciELO_${acronym}_AllTitles_${REPORT_DATE}.csv"
}

notify_slack() {
    local message=$1
    [[ -z "$SLACK_WEBHOOK_URL" ]] && return 0

    local payload
    payload=$(python -c 'import json, sys; print(json.dumps({"text": sys.argv[1]}))' "$message")

    curl -sS -o /dev/null -X POST \
        -H "Content-type: application/json" \
        --data "$payload" \
        "$SLACK_WEBHOOK_URL" || log_error "Falha ao enviar notificação para o Slack"
}

log_message() {
    local level="${2:-INFO}"
    mkdir -p "$LOG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $1" | tee -a "$MASTER_LOG"
}

log_error() {
    log_message "$1" "ERROR" >&2
}

log_success() {
    log_message "$1" "SUCCESS"
}

normalize_collection_list() {
    awk 'NF && !seen[$0]++ { print $0 }'
}

load_failed_collections() {
    [[ -f "$FAILED_COLLECTIONS_FILE" ]] || return 0
    normalize_collection_list < "$FAILED_COLLECTIONS_FILE"
}

record_failed_collection() {
    local item=$1
    mkdir -p "$(dirname "$FAILED_COLLECTIONS_FILE")"
    {
        [[ -f "$FAILED_COLLECTIONS_FILE" ]] && cat "$FAILED_COLLECTIONS_FILE"
        echo "$item"
    } | normalize_collection_list > "${FAILED_COLLECTIONS_FILE}.tmp"
    mv "${FAILED_COLLECTIONS_FILE}.tmp" "$FAILED_COLLECTIONS_FILE"
}

clear_failed_collection() {
    local item=$1
    [[ -f "$FAILED_COLLECTIONS_FILE" ]] || return 0

    grep -Fxv "$item" "$FAILED_COLLECTIONS_FILE" > "${FAILED_COLLECTIONS_FILE}.tmp" || true
    if [[ -s "${FAILED_COLLECTIONS_FILE}.tmp" ]]; then
        mv "${FAILED_COLLECTIONS_FILE}.tmp" "$FAILED_COLLECTIONS_FILE"
    else
        rm -f "${FAILED_COLLECTIONS_FILE}.tmp" "$FAILED_COLLECTIONS_FILE"
    fi
}

validate_prerequisites() {
    mkdir -p "$LOG_DIR" "$TABS_DIR"

    if [[ -n "$PROCESSING_SETTINGS_FILE" && ! -f "$PROCESSING_SETTINGS_FILE" ]]; then
        log_error "Arquivo de configuração não encontrado: $PROCESSING_SETTINGS_FILE"
        exit 1
    fi

    if [[ "$DOCKER_ENV" != "1" && ! -f "$VENV_DIR/bin/activate" ]]; then
        log_error "Virtualenv Python 3 não encontrado: $VENV_DIR"
        exit 1
    fi
}

validate_acronym() {
    local item=$1
    if [[ ! $item =~ ^[a-z]{3}(-[A-Z]{2})?(-)?$ ]]; then
        log_error "Formato inválido de acrônimo: $item (esperado: abc, abc-XY ou abc-)"
        return 1
    fi
}

setup_environment() {
    export PROCESSING_SETTINGS_FILE

    if [[ "$DOCKER_ENV" != "1" ]]; then
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate"
    fi

    cd "$WORK_DIR"
    log_success "Ambiente configurado (Python $(python --version))"
}

prepare_network_directory() {
    rm -rf "$WORK_DIR/$NETWORK_DIR"
    mkdir -p "$WORK_DIR/$NETWORK_DIR"
}

run_processing_command() {
    local cmd=$1
    local acron=$2
    local acrond=$3
    local extra_args="${4:-}"
    local output_file="${5:-}"
    local log_file="$LOG_DIR/${cmd}_${acrond}.log"
    local full_cmd="processing_${cmd} -c $acron $extra_args -o $log_file -l ERROR"

    if [[ -n "$output_file" ]]; then
        full_cmd="$full_cmd -r $output_file"
    fi

    log_message "Executando: $cmd para $acron"

    local attempt=1
    while [[ $attempt -le $MAX_RETRIES ]]; do
        if [[ $attempt -gt 1 ]]; then
            log_message "Tentativa $attempt/$MAX_RETRIES para $cmd ($acron)"
            sleep "$RETRY_DELAY"
        fi

        if eval "$full_cmd" 2>&1 | tee -a "$log_file"; then
            log_success "Comando $cmd concluído para $acron"
            return 0
        fi

        log_error "Falha no comando $cmd para $acron (tentativa $attempt/$MAX_RETRIES)"
        attempt=$((attempt + 1))
    done

    log_error "Comando $cmd falhou após $MAX_RETRIES tentativas para $acron"
    return 1
}

process_collection() {
    local item=$1
    local is_network_mode=$2
    local counter=$3
    local acron nationality acrond kbart_file tail_head=1

    validate_acronym "$item" || return 1

    acron=$(echo "$item" | cut -f1 -d-)
    nationality=$(echo "$item" | cut -f2 -d- -s)
    acrond="$acron"
    [[ "$acron" == "scl" ]] && acrond="bra"
    kbart_file=$(kbart_csv_file "$acrond")
    [[ $counter -gt 1 ]] && tail_head=2

    log_message "Processando coleção: $item"

    local temp_dir
    temp_dir=$(mktemp -d -p "$WORK_DIR" "tmp_${acrond}_XXXXXX")
    cd "$temp_dir"

    local has_errors=0
    local critical_errors=0

    if [[ -n "$nationality" ]]; then
        run_processing_command "publication_all" "$acron" "$acrond" "-n $nationality" || has_errors=1
    else
        run_processing_command "publication_all" "$acron" "$acrond" "" || has_errors=1
    fi

    run_processing_command "publication_journals" "$acron" "$acrond" "" "journals.csv" || {
        has_errors=1
        critical_errors=1
    }
    run_processing_command "publication_journals_status_changes" "$acron" "$acrond" "" "journals_status_changes.csv" || {
        has_errors=1
        critical_errors=1
    }
    run_processing_command "export_kbart" "$acron" "$acrond" "" "$kbart_file" || {
        has_errors=1
        critical_errors=1
    }

    if [[ $critical_errors -gt 0 ]]; then
        notify_slack ":x: Processing: erro crítico na coleção \`$acron\`. ZIP não gerado. Log: \`$MASTER_LOG\`"
        cd "$WORK_DIR"
        rm -rf "$temp_dir"
        return 1
    fi

    [[ $has_errors -gt 0 ]] && notify_slack ":warning: Processing: erro não-crítico na coleção \`$acron\`. Log: \`$MASTER_LOG\`"

    local zip_files=()
    for csv in "${CSV_FILES[@]}"; do
        [[ -f "${csv}.csv" ]] && zip_files+=("${csv}.csv")
    done
    [[ -f "$kbart_file" ]] && zip_files+=("$kbart_file")

    if [[ ${#zip_files[@]} -eq 0 ]]; then
        log_error "Nenhum arquivo CSV encontrado para $acron"
        cd "$WORK_DIR"
        rm -rf "$temp_dir"
        return 1
    fi

    zip -q "tabs_${acrond}.zip" "${zip_files[@]}"
    cp "tabs_${acrond}.zip" "$TABS_DIR/"
    log_success "Arquivo tabs_${acrond}.zip copiado para $TABS_DIR"

    if [[ "$is_network_mode" == "true" ]]; then
        for csv in "${CSV_FILES[@]}"; do
            [[ -f "${csv}.csv" ]] && tail -n +"$tail_head" "${csv}.csv" >> "$WORK_DIR/$NETWORK_DIR/${csv}.csv"
        done
        [[ -f "$kbart_file" ]] && tail -n +"$tail_head" "$kbart_file" >> "$WORK_DIR/$NETWORK_DIR/$(kbart_csv_file network)"
    fi

    cd "$WORK_DIR"
    rm -rf "$temp_dir"
    return 0
}

process_network_zip() {
    cd "$WORK_DIR/$NETWORK_DIR"

    local network_files=()
    for csv in "${CSV_FILES[@]}"; do
        [[ -f "${csv}.csv" ]] && network_files+=("${csv}.csv")
    done
    local network_kbart_file
    network_kbart_file=$(kbart_csv_file network)
    [[ -f "$network_kbart_file" ]] && network_files+=("$network_kbart_file")

    if [[ ${#network_files[@]} -eq 0 ]]; then
        log_error "Nenhum arquivo encontrado para criar tabs_network.zip"
        return 1
    fi

    zip -q tabs_network.zip "${network_files[@]}"
    cp tabs_network.zip "$TABS_DIR/"
    cd "$WORK_DIR"
    log_success "Arquivo tabs_network.zip copiado para $TABS_DIR"
}

main() {
    local start_time end_time duration
    start_time=$(date +%s)

    validate_prerequisites
    setup_environment

    notify_slack ":hourglass_flowing_sand: Processing iniciado em \`$(hostname)\`."

    local acronyms_to_process=()
    local is_network_mode="false"

    if [[ $# -eq 0 ]]; then
        acronyms_to_process=("${DEFAULT_ACRONYMS[@]}")
        is_network_mode="true"
        prepare_network_directory
    else
        IFS=' ' read -ra acronyms_to_process <<< "$1"
    fi

    local pending_failed_collections=()
    while IFS= read -r item; do
        pending_failed_collections+=("$item")
    done < <(load_failed_collections)

    if [[ ${#pending_failed_collections[@]} -gt 0 ]]; then
        log_message "Reprocessando coleções pendentes de falha anterior: ${pending_failed_collections[*]}"
        acronyms_to_process=("${pending_failed_collections[@]}" "${acronyms_to_process[@]}")
        mapfile -t acronyms_to_process < <(printf '%s\n' "${acronyms_to_process[@]}" | normalize_collection_list)
    fi

    local counter=0
    local failed_collections=()

    for item in "${acronyms_to_process[@]}"; do
        counter=$((counter + 1))
        if process_collection "$item" "$is_network_mode" "$counter"; then
            clear_failed_collection "$item"
        else
            record_failed_collection "$item"
            failed_collections+=("$item")
        fi
    done

    if [[ "$is_network_mode" == "true" ]]; then
        if ! process_network_zip; then
            failed_collections+=("network")
        fi
    fi

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    if [[ ${#failed_collections[@]} -gt 0 ]]; then
        log_error "Coleções falhadas: ${failed_collections[*]}"
        notify_slack ":x: Processing finalizado com falhas (${#failed_collections[@]}/$counter) em ${duration}s. Coleções: ${failed_collections[*]}. Logs: \`$LOG_DIR\`"
        if [[ "$EXIT_ON_FAILURE" == "true" ]]; then
            exit 1
        fi
        log_success "Processing finalizado com falhas reportadas, sem interromper o job"
        exit 0
    fi

    log_success "Processing finalizado em ${duration}s. Arquivos persistidos em $TABS_DIR"
    notify_slack ":white_check_mark: Processing finalizado com sucesso. Coleções: $counter. Tempo: ${duration}s. Arquivos: \`$TABS_DIR\`"
}

main "$@"
