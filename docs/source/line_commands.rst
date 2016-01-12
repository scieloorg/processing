Utilitário de linha de comando
==============================

Relatório de Acessos aos documentos
-----------------------------------

**comando:** processing_accesses_dumpdata

**escopo:** documentos

**finalidade:** Extração de indicadores

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV, JSON.

Formato CSV::
    
    * acrônimo da coleção
    * PID do documento
    * ISSN no SciELO
    * título do periódico
    * PID do fascículo
    * rótulo do fascículo
    * título do documento
    * data de publicação
    * ano e mês de publicação
    * ano de publicação
    * tipo de documento
    * áreas do periódico multivalorado (separado por "," virgula)
    * idioma de publicação multivalorado (separado por "," virgula)
    * país de afiliação multivalorado (ISO-3166 separado por "," virgula)
    * data do acesso
    * ano do acesso
    * mês do acesso
    * dia do acesso (Quando selecinada granulariade mensal o dia será sempre 1)
    * acesso ao resumo
    * acesso ao html
    * acesso ao pdf
    * acesso ao epdf (ReadCube)
    * acesso total (resumo + html + pdf + epdf)

Formato JSON::

    {
        "pid": "S0100-879X1998000800006",
        "access_epdf": 0,
        "access_date": "2014-09-01T00:00:00",
        "access_month": "09",
        "id": "scl_S0100-879X1998000800006",
        "languages": ["en"],
        "access_total": 19,
        "issue": "S0100-879X19980008",
        "issue_title": "Braz J Med Biol Res, n.31 v.8, 1998",
        "journal_title": "Brazilian Journal of Medical and Biological Research",
        "collection": "scl",
        "access_abstract": 0,
        "publication_date": "1998-08",
        "document_type": "research-article",
        "access_year": "2014",
        "processing_date": "1998-09-21",
        "document_title": "Annual changes in serum calcium and inorganic phosphate levels and correlation with gonadal status of a freshwater murrel, Channa punctatus (Bloch)",
        "access_html": 18,
        "subject_areas": ["Biological Sciences", "Health Sciences"],
        "issn": "0100-879X",
        "publication_year": "1998",
        "aff_countries": ["IN"],
        "access_day": "",
        "access_pdf": 1
    }

Relatório de citação recebida por artigos no SciELO
---------------------------------------------------

**comando:** processing_bibliometric_citedby

**escopo:** documentos

**finalidade:** Extração de indicadores

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * título do documento
    * citado por PID
    * citado por ISSN
    * citado por título
    * citado por título do documento

Relatórido de citações em Altmetrics
------------------------------------

**comando:** processing_evaluation_altmetrics

**escopo:** documentos

**finalidade:** Extração de indicadores

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * ISSN
    * título do periódico
    * data de publicação
    * título do artigo
    * doi
    * url
    * altmetrics url
    * score

Exportação de metadados para DOAJ
---------------------------------

**comando:** processing_export_doaj

**escopo:** documentos

**finalidade:** Envío de metadados ao DOAJ

Relatório com status de periódicos do DOAJ
------------------------------------------

**comando:** processing_export_doaj_journals

**escopo:** periódicos

**finalidade:** Extração de relatório de situação dos periódicos SciELO no DOAJ.

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * acrônimo da coleção
    * issn scielo,
    * issn impresso
    * issn eletrônico
    * título do periódico
    * ID no DOAJ
    * Provider no DOAJ
    * Status no DOAJ

Relatório com dados de periódicos em formato KBART
--------------------------------------------------

**comando:** processing_export_kbart

**escopo:** periódicos

**finalidade:** Extração de relatório de periódicos de acordo com formato KBART

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * título do Periódico
    * ISSN impresso
    * ISSN online
    * data do primeiro número
    * volume do primeiro número
    * número do primeiro número
    * data do último número publicado
    * volume do último número publicado
    * número do último número publicado
    * url issues
    * id no SciELO

Gerador de chaves naturais de artigos SciELO
--------------------------------------------

**comando:** processing_export_natural_keys

**escopo:** periódicos

**finalidade:** Gerar chaves naturais de artigos SciELO no formato esperado pelo
Scielo Manager, com o objetivo de testar inconsistências no metadado de registros
do legado para minimizar impactos no momento de migração do legado para o SciELO
Manager.

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * acrônimo da coleção
    * pid
    * título
    * volume
    * número
    * ano de publicação
    * primeira página
    * primeria página seq
    * última página
    * e-location
    * ahead of print id
    * chave

Relatório com Dados de afiliação dos documentos
-----------------------------------------------

**comando:** processing_export_normalize_affiliations

**escopo:** documentos

**finalidade:** Relatório geral de afiliações dos documentos incluindo afiliações
normalizadas e não normalizadas. Este relatório serve de insumo para o processo
de normalização conduzido pelos departamentos de produção da Rede SciELO.

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * acrônimo da coleção
    * PID
    * ano de publicação
    * tipo de documento
    * título
    * número
    * normalizado?
    * id de afiliação
    * instituição original
    * paises original
    * instituição normalizada
    * país normalizado ISO-3661
    * código de país normalizado ISO-3166
    * estado normalizado ISO-3166
    * código de estado normalizado ISO-3166

Exportação de documentos no formato XML RSPS
--------------------------------------------

**comando:** processing_export_xmlrsps

**escopo:** documentos

**finalidade:** Exportar todos os documentos SciELO para o formato XML RSPS. 
Muitos documentos do legado não conseguem produzir o XML RSPS de forma integral
e em conformidade com a Especificação SciELO PS devido a falta de metadados,
erros de marcação, erros em metadados, etc. Estes XML's servem atualmente para
enviar metadados para outras instituições e também para indicar ao SciELO quais
documentos devem ser corrigidos antes da migração para as novas ferramentas de
controle de catalogos e metadados (SciELO Manager).

Relatório de afiliações dos documentos
--------------------------------------

**comando:** processing_publication_authors
**escopo:** documentos
**finalidade:** Relatório com autores dos documentos, para extração
de indicadores de publicação.

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * paises de afiliação (separado por "," virgula)
    * exclusivo nacional
    * exclusivo estrangeiro
    * nacional + estrangeiro

Relatório de contagens gerais relacionadas aos dos documentos
-------------------------------------------------------------

**comando:** processing_publication_counts

**escopo:** documentos

**finalidade:** Relatório com contagens de dos documentos, para extração
de indicadores de publicação.

Formatos de saída
˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * issn
    * título da revista
    * área temática
    * ano de publicação
    * tipo de documento
    * total autores
    * 0 autores
    * 1 autor
    * 2 autores
    * 3 autores
    * 4 autores
    * 5 autores
    * +6 autores
    * total páginas
    * total referências

Relatório de datas do documento
-------------------------------

**comando:** processing_publication_dates

**escopo:** documentos

**finalidade:** Relatório com datas do documento.

Formatos de saída
````````````````

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * recebido
    * revisado
    * aceito
    * publicado
    * entrada no SciELO
    * atualização no SciELO

Relatório de periódicos
-----------------------

**comando:** processing_publication_journals

**escopo:** periódicos

**finalidade:** Relatório de periódicos com metadados básicos para extração de
indicadores.

Formatos de saída
`````````````````

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * issn scielo
    * issn impresso
    * issn eletrônico
    * nome do publicador
    * título
    * título abreviado
    * título nlm
    * periodicidade
    * área temática
    * bases WOS
    * áreas temáticas WOS
    * situação atual
    * ano de inclusão
    * licença de uso padrão

Relatório de histórico de mudanças de status dos periódicos
-----------------------------------------------------------

**comando:** processing_publication_journals_history

**escopo:** periódicos

**finalidade:** Relatório de mudança de status de publicação dos periódicos no
SciELO.

Formatos de saída
`````````````````

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * issn scielo
    * issn impresso
    * issn eletrônico
    * nome do publicador
    * título
    * título abreviado
    * título nlm
    * área temática
    * bases WOS
    * áreas temáticas WOS
    * situação atual
    * ano de inclusão
    * licença de uso padrão
    * histórico data
    * histórico ano
    * histórico status

Relatório de idiomas de publicação dos documentos
-------------------------------------------------

**comando:** processing_publication_languages

**escopo:** documentos

**finalidade:** Relatório de idiomas de publicação dos documentos.

Formatos de saída
`````````````````

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * idiomas (separado por "," virgula)
    * pt
    * es
    * en
    * other
    * pt-es
    * pt-en
    * en-es
    * exclusivo nacional
    * exclusivo estrangeiro
    * nacional + estrangeiro

Relatório de licenças de uso dos documentos
-------------------------------------------

**comando:** processing_publication_licenses

**escopo:** documentos

**finalidade:** Relatório de licnças de uso dos documentos.

Formatos de saída
`````````````````

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * license