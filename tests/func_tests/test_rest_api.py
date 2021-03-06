from urllib2 import urlopen

from tornado.httpclient import HTTPClient

import rmock
from rmock.runners.http.param_parsers import rest_params_parser


class TestRESTApi(object):

    @classmethod
    def setup_class(cls):
        cls.http_client = HTTPClient()

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_get_simple(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234/subresource/20/30' % port)
        mock['/resource/1234/subresource/20/30'].assert_called_with('get')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_edge_cases(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s' % port)
        mock['/'].assert_called_with('get')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_post_simple(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234' % port, 'q=a')
        mock['/resource/1234'].assert_called_with('post', 'q=a')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_put_simple(self, mock):
        port = mock.runner_params.port
        self.http_client.fetch('http://localhost:%s/resource/1234' % port, method='PUT', body='q=a')
        mock['/resource/1234'].assert_called_with('put', 'q=a')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_delete_simple(self, mock):
        port = mock.runner_params.port
        self.http_client.fetch('http://localhost:%s/resource/1234' % port, method='DELETE')
        mock['/resource/1234'].assert_called_with('delete')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_get_query_string(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234?k=v' % port)
        mock['/resource/1234'].assert_called_with('get', k='v')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_get_query_string_multi(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234?k=v&k=s' % port)
        mock['/resource/1234'].assert_called_with('get', k=['v', 's'])

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_post_query_string(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234?k=v' % port, 'q=a')
        mock['/resource/1234'].assert_called_with('post', 'q=a', k='v')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_post_query_string_multi(self, mock):
        port = mock.runner_params.port
        urlopen('http://localhost:%s/resource/1234?k=v&k=s' % port, 'q=a')
        mock['/resource/1234'].assert_called_with('post', 'q=a', k=['v', 's'])

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_put_query_string(self, mock):
        port = mock.runner_params.port
        self.http_client.fetch('http://localhost:%s/resource/1234?k=v' % port, method='PUT', body='q=a')
        mock['/resource/1234'].assert_called_with('put', 'q=a', k='v')

    @rmock.patch("http", protocol_args=dict(params_parser=rest_params_parser))
    def test_rest_api_delete_query_string(self, mock):
        port = mock.runner_params.port
        self.http_client.fetch('http://localhost:%s/resource/1234?k=v' % port, method='DELETE')
        mock['/resource/1234'].assert_called_with('delete', k='v')
