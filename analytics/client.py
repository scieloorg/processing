# coding: utf-8
import logging

import requests

logger = logging.getLogger(__name__)

class Analytics(object):

    def __init__(self):

        self.source = 'http://analytics.scielo.org'

    def _compute_impact_factor(self, data):

        categories = data.get('options', {}).get('xAxis', {}).get('categories', []) 
        series = data.get('options', {}).get('series', [])
        result = []
        for index in range(len(categories)):
            line = [
                categories[index],
                series[0]['data'][index], # imediatez
                series[1]['data'][index], # 1 ano
                series[2]['data'][index], # 2 anos
                series[3]['data'][index], # 3 anos
                series[4]['data'][index], # 4 anos
                series[5]['data'][index]  # 5 anos
            ]
            result.append(line)
        
        return result

    def impact_factor(self, issn, collection):
        endpoint = '/ajx/bibliometrics/journal/impact_factor_chart'

        url = self.source + endpoint

        payload = {
            "journal":  issn,
            "collection":  collection
        }

        try:
            logger.debug('Requesting data to Analytics %s %s' % (url, str(payload)))
            response = requests.get(url, params=payload, timeout=360)
        except Exception as e:
            logger.error('Could not retrieve data from Analytics %s %s' % (url, str(payload)))
            return None

        try:
            data = response.json()
        except:
            logger.error('Could not load json for Analytics %s %s' % (url, str(payload)))
            return None

        return self._compute_impact_factor(data)