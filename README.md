# SciELO Processing

Conjunto de utilitários para a produção de tabulações com metadados e métricas
e também para o envio de dados à parceiros.


## Requisitos:
* Python 3.14

## Docker

Para instalar as dependências e executar a suíte de testes:

```bash
docker compose run --rm tests
```

Para executar o processamento via Docker, configure as variáveis em um arquivo
`.env` local, baseado em `.env.example`. O `.env` não deve ser versionado.

```bash
cp .env.example .env
```

Preencha no `.env` os valores equivalentes ao antigo `config.ini`:

```ini
ARTICLEMETA_THRIFTSERVER=
ARTICLEMETA_ADMINTOKEN=
RATCHET_THRIFTSERVER=
ACCESSSTATS_THRIFTSERVER=
CITEDBY_THRIFTSERVER=
PUBLICATIONSTATS_THRIFTSERVER=
SOLR_SEARCH_SCIELO_ORG=
SOLR_SEARCH_SCIELO_ORG_INDEX=
PUBLICATIONSTATS_TIMEOUT_MS=60000
SLACK_WEBHOOK_URL=
```

Depois execute:

```bash
docker compose run --rm processing "scl-BR"
```

Os logs ficam persistidos em `var/log/processing` e os arquivos ZIP gerados em
`var/tabs`.

## Kubernetes / Argo

O agendamento para Argo Workflows está em `k8s/argo-cronworkflow.yaml` com o cron:

```text
0 3 1,8,15,22 1-12 *
```

O workflow executa as coleções sequencialmente. Quando uma coleção falha, o
script envia a notificação de erro e continua para a próxima. Ao final, o job
termina com falha, mantém os checkpoints para retomada e preserva o ZIP de rede
completo publicado anteriormente.

Os valores sensíveis devem ser criados em um Secret do Kubernetes chamado
`processing-env`, baseado em `k8s/processing-env.secret.example.yaml`. Não
versione o Secret real.

Volumes esperados:

```text
processing-data -> /var/www/static_scielo_org/tabs
processing-logs -> /var/log/processing
```

O processamento é orquestrado pelo comando `processing_tabs`. Os logs informam
coleção, etapa, tentativa, duração, comando executado e arquivos produzidos.

A exportação KBART inclui todos os periódicos da coleção, correntes e não
correntes. Para os correntes, os campos de última publicação ficam vazios;
para os demais, são preenchidos com os dados disponíveis.

Quando uma coleção falha, o runner registra o acrônimo em
`/var/log/processing/failed_collections.queue` por padrão. Na próxima execução,
essa fila é carregada antes da lista normal de coleções. Cada etapa concluída
também é salva em um checkpoint; assim, somente etapas incompletas são
executadas novamente. Por padrão, os checkpoints ficam em
`$TABS_DIR/.processing-checkpoints`, no mesmo volume persistente dos arquivos
gerados. Os caminhos podem ser alterados com `FAILED_COLLECTIONS_FILE` e
`CHECKPOINT_DIR`. Checkpoints de uma data anterior são descartados para evitar
que arquivos de períodos diferentes sejam combinados.

As etapas de documentos, periódicos e KBART somente são concluídas quando os
arquivos essenciais possuem pelo menos um registro além do cabeçalho. O arquivo
de mudanças de status pode conter somente o cabeçalho. Quando essa validação
falha, o pacote da coleção não é publicado e o último pacote completo da rede é
preservado.

Aplicação:

```bash
kubectl apply -f k8s/processing-env.secret.yaml
kubectl apply -f k8s/argo-cronworkflow.yaml
```


## Exportação de dados ao DOAJ

Esta integração é realizada por meio de um robô que obtém os metadados dos
documentos a partir do ArticleMeta, já codificados em XML conforme o _schema_
do DOAJ, e os envia, um a um, através do formulário de submissão de artigos em
XML, do site do DOAJ. Este processo não é ótimo mas é o único que nos permite
enviar metadados em múltiplos idiomas.

Ao depositar um documento, o DOAJ verifica automaticamente se os _ISSNs_
informados correspondem exatamente com os cadastrados em sua base de dados e,
no caso de qualquer divergência, o depósito é rejeitado. A fim de contornar
este problema, é possível construir uma _base de correções_ que poderá ser
utilizada pelo utilitário de depósito. A _base de correções_ é produzida a
partir de consultas às bases do DOAJ e, quando aplicada, modifica os metadados
dos documentos de forma que os _ISSNs_ fiquem conforme esperado pelo DOAJ.

Para produzir a _base de correções_ e armazená-la em `/tmp/corr.jsonl`:

```bash
python export/gen_doaj_correctionsdb.py gen-correctionsdb > /tmp/corr.jsonl
```

Para executar o depósito dos documentos no DOAJ:

```bash
PROCESSING_SETTINGS_FILE=myconfig.ini processing_export_doaj --corrections_db /tmp/corr.jsonl --user US3R --password P4SSW0RD
```

Note que: (a) será necessário criar um arquivo de configurações e atribuí-lo
à variável `PROCESSING_SETTINGS_FILE`. Este arquivo poderá ser baseado no
[exemplo](https://raw.githubusercontent.com/scieloorg/processing/master/config.ini-TEMPLATE)
fornecido no projeto e (b) que o utilitário `processing_export_doaj` aceita
opções que podem ser usadas de forma a delimitar o conjunto de dados que serão
depositados no DOAJ. Para mais detalhes execute
`PROCESSING_SETTINGS_FILE=myconfig.ini processing_export_doaj --help`.
