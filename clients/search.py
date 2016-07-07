# coding: utf-8
"""
Client for the search.scielo.org Solr API.

This client connects to Solr API.
"""
import logging
import json

import requests

import utils

logger = logging.getLogger(__name__)


API_DOMAIN = utils.settings.get('app:main', {}).get(
    'solr_search_scielo_org', 'localhost:8080')

API_INDEX = utils.settings.get('app:main', {}).get(
    'solr_search_scielo_org_index', 'search-scielo')


class Search(object):

    UPDATE_ENDPOINT = 'http://%s/solr/%s/update' % (API_DOMAIN, API_INDEX)

    def _do_request(self, url, params=None, data=None, headers=None):
        """
        Realiza as requisições diversas utilizando a biblioteca requests,
        tratando de forma genérica as exceções.
        """

        if not headers:
            headers = {'content-type': 'application/json'}

        try:
            response = requests.get(
                url, params=params, data=data, headers=headers)
        except:
            return None

        if response.status_code == 200:
            return response

    def update_document_indicators(self, doc_id, citations, accesses):
        """
            Atualiza os indicadores de acessos e citações de um determinado
            doc_id.
            exemplo de doc_id: S0021-25712009000400007-spa
        """

        headers = {'content-type': 'application/json'}

        data = {
            "add": {
                "doc": {
                    "id": doc_id
                }
            }
        }

        if citations:
            data['add']['doc']['total_received'] = {'set': str(citations)}

        if accesses:
            data['add']['doc']['total_access'] = {'set': str(accesses)}

        params = {'wt': 'json'}

        response = self._do_request(
            self.UPDATE_ENDPOINT,
            params=params,
            data=json.dumps(data),
            headers=headers
        )

        if not response:
            logger.debug('Document (%s) could not be updated' % doc_id)

        logger.debug('Document (%s) updated' % doc_id)

    def _commit(self):
        """
            Envia requisição de commit do indice através da API.
        """

        params = {'commit': 'true'}

        response = self._do_request(
            self.UPDATE_ENDPOINT,
            params=params
        )

        if response and response.status_code == 200:
            logger.debug('Index commited')
            return None

        logger.warning('Fail to commite index')

    def _optimize(self):
        """
            Envia requisição de optimização do indice através da API.
        """

        params = {'optimize': 'true'}

        response = self._do_request(
            self.UPDATE_ENDPOINT,
            params=params
        )

        if response and response.status_code == 200:
            logger.debug('Index optimized')
            return None

        logger.warning('Fail to optimize index')

    def deploy(self):
        """
            Executa o commit e optimize do indice.
        """
        self._commit()
        self._optimize()
