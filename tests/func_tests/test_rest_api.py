from urllib2 import urlopen

import rmock

from rmock.runners.http.param_parsers import rest_params_parser

class TestRESTApi(object):

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_simple(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234/subresource/20/30' % port)
        mock.empty().assert_called_with('/resource/1234/subresource/20/30')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_edge_cases(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s' % port)
        mock.empty().assert_called_with('/')
