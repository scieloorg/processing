# SciELO Processing

Conjunto de utilitários para a produção de tabulações com metadados e métricas
e também para o envio de dados à parceiros.


## Requisitos:
* Python 2.7


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
