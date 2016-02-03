===================
Relatórios Públicos
===================

Alguns relatórios são produzidos mensalmente e publicados on-line para que usuários,
instituições e outros interessados possam fazer download.

Para o download desses relatórios acessar: http://analytics.scielo.org/w/downloads

------------------------
Relatórios de Periódicos
------------------------

Relatório de periódicos
=======================

**nome do arquivo:** journals.csv 

**finalidade:** Relatório de periódicos com metadados básicos para extração de
indicadores.

Formatos de saída
-----------------

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
    * data de inclusão
    * licença de uso padrão

Relatório de histórico de mudanças de status dos periódicos
===========================================================

**nome do arquivo:** journals_history.csv

**finalidade:** Relatório de mudança de status de publicação dos periódicos no
SciELO.

Formatos de saída
-----------------

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

Relatório de acessos por periódico e ano de publicação dos documento
====================================================================

**nome do arquivo:** accesses_by_journals.csv

**finalidade:** Relatório de acessos aos documentos nos formatos html, abstract,
pdf e epdf por periódico e ano de publicação do documento.

Formatos de saída
-----------------

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * issn scielo
    * issn impresso
    * issn eletrônico
    * título
    * área temática
    * ano de publicação
    * ano de acesso
    * acesso ao html
    * acesso ao abstract
    * acesso ao PDF
    * acesso ao EPDF
    * total de acessos

Relatório de fator de impacto por periódico
===========================================

**nome do arquivo:** impact_factor.csv

**finalidade:** Relatório de fator de impacto dos periódicos, com indice de 
imediatez, fator de impacto para 1, 2, 3, 4 e 5 anos.

Formatos de saída
-----------------

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * issn scielo
    * issn impresso
    * issn eletrônico
    * título
    * área temática
    * ano de publicação
    * ano base
    * imediatez
    * fator de impacto 1 ano
    * fator de impacto 2 anos
    * fator de impacto 3 anos
    * fator de impacto 4 anos
    * fator de impacto 5 anos


Relatório de periódicos em formato Kbart
========================================

**nome do arquivo:** journals_kbart.csv

**finalidade:** Relatório de periódicos no formato Kbart.

Formatos de saída
-----------------

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * Título do Periódico (publication_title)
    * ISSN impresso (print_identifier)
    * ISSN online (online_identifier)
    * Data do primeiro fascículo (date_first_issue_online)
    * volume do primeiro fascículo (num_first_vol_online)
    * número do primeiro fascículo (num_first_issue_online)
    * Data do último fascículo publicado (date_last_issue_online)
    * volume do último fascículo publicado (num_last_vol_online)
    * número do último fascículo publicado (num_last_issue_online)
    * url de fascículos (title_url)
    * primeiro autor (first_author)
    * ID do periódico no SciELO (title_id)
    * informação de embargo (embargo_info)
    * cobertura (coverage_depth)
    * informação sobre cobertura (coverage_notes)
    * nome do publicador (publisher_name)
    * tipo de publicação (publication_type)
    * data de publicação monográfica impressa (date_monograph_published_print)
    * data de publicação monográfica online (date_monograph_published_online)
    * volume de monografia (monograph_volume)
    * edição de monografia (monograph_edition)
    * primeiro editor (first_editor)
    * ID de publicação pai (parent_publication_title_id)
    * ID de publicação prévia (preceding_publication_title_id)
    * tipo de acesso (access_type)

------------------------
Relatórios de Documentos
------------------------

Relatório de pontuação de documentos no altmetrics
==================================================

**nome do arquivo:** altmetrics.csv

**finalidade:** Relatório geral pontuação dos documentos SciELO no Altmetrics,


.. note::

    os metadados deste relatório estão condicionados a qualidade dos metadados 
    disponíveis no altmetrics.

Formatos de saída
-----------------

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * título do artigo
    * doi
    * url
    * altmetrics url
    * score

Relatório com Dados de afiliação dos documentos
===============================================

**nome do arquivo:** aff_normalization.csv

**finalidade:** Relatório geral de afiliações dos documentos incluindo afiliações
normalizadas e não normalizadas. Este relatório serve de insumo para o processo
de normalização conduzido pelos departamentos de produção da Rede SciELO.

Formatos de saída
-----------------

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

Relatório de afiliações dos documentos
======================================

**nome do arquivo:** affiliations.csv

**finalidade:** Relatório com autores dos documentos, para extração
de indicadores de publicação.

Formatos de saída
-----------------

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
=============================================================

**nome do arquivo:** counts.csv

**finalidade:** Relatório com contagens de dos documentos, para extração
de indicadores de publicação.

Formatos de saída
-----------------

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
===============================

**nome do arquivo:** dates.csv

**finalidade:** Relatório com datas do documento.

Formatos de saída
-----------------

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

Relatório de idiomas de publicação dos documentos
=================================================

**nome do arquivo:** languages.csv

**finalidade:** Relatório de idiomas de publicação dos documentos.

Formatos de saída
-----------------

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
===========================================

**nome do arquivo:** licenses.csv

**finalidade:** Relatório de licnças de uso dos documentos.

Formatos de saída
-----------------

Os formatos de saída disponíveis para este relatório são: CSV.

Formato CSV::

    * PID
    * ISSN
    * título
    * área temática
    * ano de publicação
    * tipo de documento
    * license