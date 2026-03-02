#!/bin/bash
#
# Script para tabulação de acessos e publicação de artigos SciELO
# Versão Python 3
#
# Uso direto no servidor:
#   1. $ ./run.sh
#   2. $ ./run.sh "scl-BR arg-AR"
#
# Uso via Docker:
#   docker run --rm \
#     -v /etc/scieloapps/processing.ini:/etc/scieloapps/processing.ini:ro \
#     -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:ro \
#     -v /var/log/processing:/var/log/processing \
#     scielo-processing "scl-BR arg-AR"

set -euo pipefail

#==============================================================================
# CONFIGURAÇÕES
#==============================================================================

# Em Docker: DOCKER_ENV=1, WORK_DIR=/app são definidos no Dockerfile
readonly DOCKER_ENV="${DOCKER_ENV:-0}"
readonly PROCESSING_SETTINGS_FILE="${PROCESSING_SETTINGS_FILE:-/etc/scieloapps/processing.ini}"
readonly VENV_DIR="${VENV_DIR:-/var/www/.venvs/processing}"
readonly WORK_DIR="${WORK_DIR:-/var/www/processing}"
readonly LOG_DIR="${LOG_DIR:-/var/log/processing}"
readonly NETWORK_DIR="network"
readonly REMOTE_SERVER="orfeu.scielo.org"
readonly REMOTE_PATH="/var/www/static_scielo_org/tabs"
readonly MAX_PARALLEL_JOBS=4
readonly MAX_RETRIES=3
readonly RETRY_DELAY=5
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly MASTER_LOG="$LOG_DIR/master_$TIMESTAMP.log"
readonly SLACK_WEBHOOK_URL="omitido"

# Coleções padrão
readonly DEFAULT_ACRONYMS=(
    "scl-BR" "arg-AR" "bol-BO" "chl-CL" "cub-CU" "col-CO"
    "cri-CR" "ecu-EC" "esp-ES" "mex-MX" "per-PE" "prt-PR"
    "pry-PY" "psi-BR" "rve-BR" "rvt-BR" "spa-BR" "sss-BR"
    "sza-SZ" "ury-UY" "ven-VE" "wid-WI" "dom-DO"
)

# Arquivos CSV gerados
readonly CSV_FILES=(
    "documents_affiliations"
    "documents_authors"
    "documents_counts"
    "documents_dates"
    "documents_languages"
    "documents_licenses"
    "journals"
    "journals_status_changes"
    "journals_kbart"
)

#==============================================================================
# FUNÇÕES AUXILIARES
#==============================================================================

notify_slack() {
    local message=$1
    [[ -z "$SLACK_WEBHOOK_URL" ]] && return 0

    curl -s -o /dev/null -X POST \
        -H 'Content-type: application/json' \
        --data "{\"text\": \"$message\"}" \
        "$SLACK_WEBHOOK_URL" || log_error "Falha ao enviar notificação para o Slack"
}

log_message() {
    local level="${2:-INFO}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $1" | tee -a "$MASTER_LOG"
}

log_error() {
    log_message "$1" "ERROR" >&2
}

log_success() {
    log_message "$1" "SUCCESS"
}

cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script finalizado com erros (código: $exit_code)"
    else
        log_success "Script finalizado com sucesso"
    fi
}

trap cleanup EXIT
trap 'log_error "Erro na linha $LINENO"' ERR

validate_prerequisites() {
    log_message "Validando pré-requisitos..."

    if [[ ! -f "$PROCESSING_SETTINGS_FILE" ]]; then
        log_error "Arquivo de configuração não encontrado: $PROCESSING_SETTINGS_FILE"
        exit 1
    fi

    if [[ "$DOCKER_ENV" != "1" ]]; then
        if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
            log_error "Virtualenv Python 3 não encontrado: $VENV_DIR"
            log_error "Para criar o ambiente:"
            log_error "  python3 -m venv $VENV_DIR"
            log_error "  source $VENV_DIR/bin/activate"
            log_error "  pip install -e $WORK_DIR"
            exit 1
        fi
    fi

    if [[ ! -d "$LOG_DIR" ]]; then
        log_message "Criando diretório de logs: $LOG_DIR"
        mkdir -p "$LOG_DIR"
    fi

    log_success "Pré-requisitos validados"
}

validate_acronym() {
    local item=$1
    if [[ ! $item =~ ^[a-z]{3}(-[A-Z]{2})?(-)?$ ]]; then
        log_error "Formato inválido de acrônimo: $item (esperado: abc, abc-XY ou abc-)"
        return 1
    fi
    return 0
}

setup_environment() {
    log_message "Configurando ambiente..."

    export PROCESSING_SETTINGS_FILE

    if [[ "$DOCKER_ENV" != "1" ]]; then
        # Servidor: ativar virtualenv Python 3
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate" || {
            log_error "Falha ao ativar virtualenv: $VENV_DIR"
            exit 1
        }
    fi

    cd "$WORK_DIR" || {
        log_error "Falha ao acessar diretório de trabalho: $WORK_DIR"
        exit 1
    }

    log_success "Ambiente configurado (Python $(python3 --version))"
}

prepare_network_directory() {
    if [[ -d "$NETWORK_DIR" ]]; then
        log_message "Limpando diretório $NETWORK_DIR existente"
        rm -rf "$NETWORK_DIR"
    fi

    mkdir -p "$NETWORK_DIR"
    log_success "Diretório $NETWORK_DIR preparado"
}

#==============================================================================
# FUNÇÕES DE PROCESSAMENTO
#==============================================================================

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
    local success=false

    while [[ $attempt -le $MAX_RETRIES ]]; do
        if [[ $attempt -gt 1 ]]; then
            log_message "Tentativa $attempt/$MAX_RETRIES para $cmd ($acron)"
            sleep $RETRY_DELAY
        fi

        if eval "$full_cmd" 2>&1 | tee -a "$log_file"; then
            log_success "Comando $cmd concluído para $acron"
            success=true
            break
        else
            local exit_code=$?
            log_error "Falha no comando $cmd para $acron (tentativa $attempt/$MAX_RETRIES, código: $exit_code)"

            if grep -q "TTransportException\|Connection reset by peer\|TSocket read 0 bytes" "$log_file" 2>/dev/null; then
                log_message "Erro de conexão detectado, aguardando antes de retentar..."
            fi
        fi

        attempt=$((attempt + 1))
    done

    if [[ "$success" == "false" ]]; then
        log_error "Comando $cmd falhou após $MAX_RETRIES tentativas para $acron (ver: $log_file)"
        return 1
    fi

    return 0
}

process_collection() {
    local item=$1
    local is_network_mode=$2
    local counter=$3

    local acron nationality acrond tail_head=0

    acron=$(echo "$item" | cut -f1 -d-)
    nationality=$(echo "$item" | cut -f2 -d- -s)

    if [[ "$item" == *"-" ]] && [[ -z "$nationality" ]]; then
        nationality=""
    fi

    acrond="$acron"

    if ! validate_acronym "$item"; then
        return 1
    fi

    log_message "========================================="
    log_message "Processando coleção: $item (acron=$acron, nationality=${nationality:-none})"
    log_message "========================================="

    if [[ "$acron" == "scl" ]]; then
        acrond="bra"
    fi

    if [[ $counter -gt 1 ]]; then
        tail_head=2
    fi

    local temp_dir
    temp_dir=$(mktemp -d -p "$WORK_DIR" "tmp_${acrond}_XXXXXX")
    cd "$temp_dir" || return 1

    local has_errors=0
    local critical_errors=0

    if [[ -n "$nationality" ]]; then
        run_processing_command "publication_all" "$acron" "$acrond" "-n $nationality" || has_errors=1
    else
        run_processing_command "publication_all" "$acron" "$acrond" "" || has_errors=1
    fi

    if ! run_processing_command "publication_journals" "$acron" "$acrond" "" "journals.csv"; then
        has_errors=1
        critical_errors=1
    fi

    if ! run_processing_command "publication_journals_status_changes" "$acron" "$acrond" "" "journals_status_changes.csv"; then
        has_errors=1
        critical_errors=1
    fi

    if ! run_processing_command "export_kbart" "$acron" "$acrond" "" "journals_kbart.csv"; then
        has_errors=1
        critical_errors=1
    fi

    if [[ $critical_errors -gt 0 ]]; then
        log_error "Erros críticos detectados no processamento de $acron - ZIP não será criado"
        notify_slack ":x: *Erro crítico* na coleção \`$acron\` — ZIP não gerado para o Processing. Log: \`$LOG_DIR/processing_${acrond}.log\`"
        cd "$WORK_DIR"
        rm -rf "$temp_dir"
        return 1
    fi

    if [[ $has_errors -eq 1 ]]; then
        log_error "Erros não-críticos detectados no processamento de $acron"
        notify_slack ":warning: Erro não-crítico na coleção \`$acron\` — Processing. Log: \`$LOG_DIR/processing_${acrond}.log\`"
    fi

    log_message "Criando arquivo tabs_${acrond}.zip"

    local zip_files=()
    for csv in "${CSV_FILES[@]}"; do
        if [[ -f "${csv}.csv" ]]; then
            zip_files+=("${csv}.csv")
        fi
    done

    if [[ ${#zip_files[@]} -eq 0 ]]; then
        log_error "Nenhum arquivo CSV encontrado para $acron"
        cd "$WORK_DIR"
        rm -rf "$temp_dir"
        return 1
    fi

    zip -q "tabs_${acrond}.zip" "${zip_files[@]}" || {
        log_error "Falha ao criar ZIP para $acron"
        cd "$WORK_DIR"
        rm -rf "$temp_dir"
        return 1
    }

    log_message "Copiando tabs_${acrond}.zip para servidor remoto"
    if scp -q -o ConnectTimeout=30 "tabs_${acrond}.zip" "${REMOTE_SERVER}:${REMOTE_PATH}/"; then
        log_success "Arquivo tabs_${acrond}.zip copiado com sucesso"
    else
        log_error "Falha ao copiar tabs_${acrond}.zip para servidor remoto"
    fi

    if [[ "$is_network_mode" == "true" ]]; then
        log_message "Concatenando arquivos para rede (tail_head=$tail_head)"

        for csv in "${CSV_FILES[@]}"; do
            if [[ -f "${csv}.csv" ]]; then
                tail -n +"$tail_head" "${csv}.csv" >> "$WORK_DIR/$NETWORK_DIR/${csv}.csv" 2>/dev/null || {
                    log_error "Falha ao concatenar ${csv}.csv"
                }
            fi
        done
    fi

    cd "$WORK_DIR"
    rm -rf "$temp_dir"

    log_success "Processamento de $acron concluído"
    return 0
}

process_network_zip() {
    log_message "========================================="
    log_message "Criando arquivo de rede consolidado"
    log_message "========================================="

    cd "$NETWORK_DIR" || {
        log_error "Falha ao acessar diretório $NETWORK_DIR"
        return 1
    }

    local network_files=()
    for csv in "${CSV_FILES[@]}"; do
        if [[ -f "${csv}.csv" ]]; then
            network_files+=("${csv}.csv")
        fi
    done

    if [[ ${#network_files[@]} -eq 0 ]]; then
        log_error "Nenhum arquivo encontrado para criar tabs_network.zip"
        cd "$WORK_DIR"
        return 1
    fi

    log_message "Criando tabs_network.zip com ${#network_files[@]} arquivos"
    zip -q tabs_network.zip "${network_files[@]}" || {
        log_error "Falha ao criar tabs_network.zip"
        cd "$WORK_DIR"
        return 1
    }

    log_message "Copiando tabs_network.zip para servidor remoto"
    if scp -q -o ConnectTimeout=30 tabs_network.zip "${REMOTE_SERVER}:${REMOTE_PATH}/"; then
        log_success "Arquivo tabs_network.zip copiado com sucesso"
    else
        log_error "Falha ao copiar tabs_network.zip para servidor remoto"
    fi

    cd "$WORK_DIR"
    log_success "Arquivo de rede consolidado criado"
}

#==============================================================================
# FUNÇÃO PRINCIPAL
#==============================================================================

main() {
    local start_time
    start_time=$(date +%s)

    log_message "========================================="
    log_message "Iniciando processamento SciELO"
    log_message "========================================="

    validate_prerequisites
    setup_environment

    local acronyms_to_process=()
    local is_network_mode="false"

    if [[ $# -eq 0 ]]; then
        acronyms_to_process=("${DEFAULT_ACRONYMS[@]}")
        is_network_mode="true"
        prepare_network_directory
        log_message "Modo: REDE (todas as coleções)"
    else
        IFS=' ' read -ra acronyms_to_process <<< "$1"
        log_message "Modo: SELETIVO (${#acronyms_to_process[@]} coleções)"
    fi

    log_message "Coleções a processar: ${acronyms_to_process[*]}"

    local counter=0
    local failed_collections=()

    for item in "${acronyms_to_process[@]}"; do
        counter=$((counter + 1))

        if ! process_collection "$item" "$is_network_mode" "$counter"; then
            failed_collections+=("$item")
        fi
    done

    if [[ "$is_network_mode" == "true" ]]; then
        process_network_zip
    fi

    if [[ "$DOCKER_ENV" != "1" ]]; then
        deactivate
    fi

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_message "========================================="
    log_message "RELATÓRIO FINAL"
    log_message "========================================="
    log_message "Coleções processadas: $counter"
    log_message "Coleções com falhas: ${#failed_collections[@]}"

    if [[ ${#failed_collections[@]} -gt 0 ]]; then
        log_error "Coleções falhadas: ${failed_collections[*]}"
    fi

    log_message "Tempo total de execução: ${duration}s"
    log_message "Log completo: $MASTER_LOG"
    log_success "Processamento finalizado"

    if [[ ${#failed_collections[@]} -gt 0 ]]; then
        exit 1
    fi
}

#==============================================================================
# EXECUÇÃO
#==============================================================================

main "$@"
