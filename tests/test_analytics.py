# coding: utf-8
import unittest

from analytics.client import Analytics


class AnalyticsClientTest(unittest.TestCase):

    def setUp(self):
        self.analytics = Analytics()

    def test_compute_impact_factor(self):

        data = {
            "options": {
                "title": {
                    "text": "Impact Factor for 1, 2, 3, 4, 5 years and immediacy index"
                }, 
                "series": [
                    {
                        "data": [
                            0.1111111111111111, 
                            0.01098901098901099, 
                            0.02666666666666667
                        ], 
                        "name": "immediacy"
                    }, 
                    {
                        "data": [
                            0.31840796019900497, 
                            0.35555555555555557, 
                            0.12087912087912088
                        ], 
                        "name": "1 year"
                    }, 
                    {
                        "data": [
                            0.4231974921630094, 
                            0.4742268041237113, 
                            0.2596685082872928
                        ], 
                        "name": "2 years"
                    }, 
                    {
                        "data": [
                            0.5431818181818182, 
                            0.4938875305623472, 
                            0.450261780104712
                        ], 
                        "name": "3 years"
                    }, 
                    {
                        "data": [
                            0.6366782006920415, 
                            0.560377358490566, 
                            0.492
                        ], 
                        "name": "4 years"
                    }, 
                    {
                        "data": [
                            0.6354166666666666, 
                            0.592814371257485, 
                            0.5040257648953301
                        ], 
                        "name": "5 years"
                    }
                ], 
                "yAxis": {
                    "title": {
                        "text": "Impact Factor"
                    }, 
                    "labels": {
                        "format": "{value}"
                    }, 
                    "min": 0
                }, 
                "chart": {
                    "type": "line", 
                    "backgroundColor": "transparent"
                }, 
                "tooltip": {
                    "headerFormat": "Impact factor", 
                    "followPointer": True, 
                    "pointFormat": "<br/><strong>Base year</strong>: {point.category}<br/><strong>{series.name}</strong>: {point.y:.4f}"
                }, 
                "credits": {
                    "text": "Source: SciELO.org", 
                    "href": "http://www.scielo.org"
                }, 
                "xAxis": {
                    "categories": [ 
                        "2013", 
                        "2014", 
                        "2015"
                    ]
                }, 
                "legend": {
                    "highlightSeries": {
                        "enabled": True
                    }, 
                    "align": "center"
                }
            }
        }

        result = self.analytics._compute_impact_factor(data)

        expected = [
            ["2013",0.1111111111111111,0.31840796019900497,0.4231974921630094,0.5431818181818182,0.6366782006920415,0.6354166666666666],
            ["2014",0.01098901098901099,0.35555555555555557,0.4742268041237113,0.4938875305623472,0.560377358490566,0.592814371257485],
            ["2015",0.02666666666666667,0.12087912087912088,0.2596685082872928,0.450261780104712,0.492,0.5040257648953301]
        ]

        self.assertEqual(expected, result)


