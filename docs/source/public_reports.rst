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