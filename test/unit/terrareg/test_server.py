
from unittest.mock import MagicMock
import sys

import pytest

from terrareg.models import Namespace, Module
from terrareg.module_search import ModuleSearch
from terrareg.filters import NamespaceTrustFilter
from test.unit.terrareg import MockModuleProvider, client


@pytest.fixture()
def mocked_search_module_providers(request):
    """Create mocked instance of search_module_providers method."""
    unmocked_search_module_providers = ModuleSearch.search_module_providers
    def cleanup_mocked_search_provider():
        ModuleSearch.search_module_providers = unmocked_search_module_providers
    request.addfinalizer(cleanup_mocked_search_provider)

    ModuleSearch.search_module_providers = MagicMock(return_value=[])

def test_api_module_list_with_no_params(client, mocked_search_module_providers):
    """Call with no parameters"""
    res = client.get('/v1/modules')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }

    ModuleSearch.search_module_providers.assert_called_with(provider=None, verified=False, offset=0, limit=10)

def test_api_module_list_with_limit_offset(client, mocked_search_module_providers):
    """Call with limit and offset"""
    res = client.get('/v1/modules?offset=23&limit=12')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 23, 'limit': 12, 'next_offset': 35, 'prev_offset': 11}, 'modules': []
    }

    ModuleSearch.search_module_providers.assert_called_with(provider=None, verified=False, offset=23, limit=12)

def test_api_module_list_with_max_limit(client, mocked_search_module_providers):
    """Call with limit higher than max"""
    res = client.get('/v1/modules?offset=65&limit=55')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 65, 'limit': 50, 'next_offset': 115, 'prev_offset': 15}, 'modules': []
    }

    ModuleSearch.search_module_providers.assert_called_with(provider=None, verified=False, offset=65, limit=50)

def test_api_module_list_with_provider_filter(client, mocked_search_module_providers):
    """Call with provider limit"""
    res = client.get('/v1/modules?provider=testprovider')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }

    ModuleSearch.search_module_providers.assert_called_with(provider='testprovider', verified=False, offset=0, limit=10)

def test_api_module_list_with_verified_false(client, mocked_search_module_providers):
    """Call with verified flag as false"""
    res = client.get('/v1/modules?verified=false')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(provider=None, verified=False, offset=0, limit=10)


def test_api_module_list_with_verified_true(client, mocked_search_module_providers):
    """Call with verified flag as true"""
    res = client.get('/v1/modules?verified=true')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(provider=None, verified=True, offset=0, limit=10)

def test_api_module_list_with_module_response(client, mocked_search_module_providers):
    """Test return of single module module"""
    namespace = Namespace(name='testnamespace')
    module = Module(namespace=namespace, name='mock-module')
    mock_module_provider = MockModuleProvider(module=module, name='testprovider')
    mock_module_provider.MOCK_LATEST_VERSION_NUMBER = '1.2.3'
    ModuleSearch.search_module_providers.return_value = [mock_module_provider]

    res = client.get('/v1/modules?offset=0&limit=1')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 1, 'next_offset': 1, 'prev_offset': 0}, 'modules': [
            {'id': 'testnamespace/mock-module/testprovider/1.2.3', 'owner': 'Mock Owner',
             'namespace': 'testnamespace', 'name': 'mock-module',
             'version': '1.2.3', 'provider': 'testprovider',
             'description': 'Mock description', 'source': 'http://mock.example.com/mockmodule',
             'published_at': '2020-01-01T23:18:12', 'downloads': 0, 'verified': True}
        ]
    }

def test_api_module_list_with_multiple_modules_response(client, mocked_search_module_providers):
    """Test multiple modules in results"""
    namespace = Namespace(name='testnamespace')
    module = Module(namespace=namespace, name='mock-module')
    mock_module_provider = MockModuleProvider(module=module, name='testprovider')
    mock_module_provider.MOCK_LATEST_VERSION_NUMBER = '1.2.3'
    mock_namespace_2 = Namespace(name='secondtestnamespace')
    mock_module_2 = Module(namespace=mock_namespace_2, name='mockmodule2')
    mock_module_provider_2 = MockModuleProvider(module=mock_module_2, name='secondprovider')
    mock_module_provider_2.MOCK_LATEST_VERSION_NUMBER = '3.0.0'
    ModuleSearch.search_module_providers.return_value = [mock_module_provider_2, mock_module_provider]

    res = client.get('/v1/modules?offset=0&limit=2')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 2, 'next_offset': 2, 'prev_offset': 0}, 'modules': [
            mock_module_provider_2.get_latest_version().get_api_outline(),
            mock_module_provider.get_latest_version().get_api_outline(),
        ]
    }

def test_api_module_search_with_no_params(client, mocked_search_module_providers):
    """Test ApiModuleSearch with no params"""
    res = client.get('/v1/modules/search')
    assert res.status_code == 400
    ModuleSearch.search_module_providers.assert_not_called()

def test_api_module_search_with_query_string(client, mocked_search_module_providers):
    """Call with query param"""
    res = client.get('/v1/modules/search?q=unittestteststring')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='unittestteststring', namespace=None, provider=None, verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=0, limit=10)

def test_api_module_search_with_limit_offset(client, mocked_search_module_providers):
    """Call with limit and offset"""
    res = client.get('/v1/modules/search?q=test&offset=23&limit=12')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 23, 'limit': 12, 'next_offset': 35, 'prev_offset': 11}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace=None, provider=None, verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=23, limit=12)

def test_api_module_search_with_max_limit(client, mocked_search_module_providers):
    """Call with limit higher than max"""
    res = client.get('/v1/modules/search?q=test&offset=65&limit=55')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 65, 'limit': 50, 'next_offset': 115, 'prev_offset': 15}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace=None, provider=None, verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=65, limit=50)

def test_api_module_search_with_provider(client, mocked_search_module_providers):
    """Call with provider filter"""
    res = client.get('/v1/modules/search?q=test&provider=testprovider')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace=None, provider='testprovider', verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=0, limit=10)

def test_api_module_search_with_namespace(client, mocked_search_module_providers):
    """Call with namespace filter"""
    res = client.get('/v1/modules/search?q=test&namespace=testnamespace')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace='testnamespace', provider=None, verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=0, limit=10)

def test_api_module_search_with_namespace_trust_filters(client, mocked_search_module_providers):
    """Call with trusted namespace/contributed filters"""
    for namespace_filter in [['&trusted_namespaces=false', []],
                             ['&trusted_namespaces=true', [NamespaceTrustFilter.TRUSTED_NAMESPACES]],
                             ['&contributed=false', []],
                             ['&contributed=true', [NamespaceTrustFilter.CONTRIBUTED]],
                             ['&trusted_namespaces=false&contributed=false', []],
                             ['&trusted_namespaces=true&contributed=false', [NamespaceTrustFilter.TRUSTED_NAMESPACES]],
                             ['&trusted_namespaces=false&contributed=true', [NamespaceTrustFilter.CONTRIBUTED]],
                             ['&trusted_namespaces=true&contributed=true', [NamespaceTrustFilter.TRUSTED_NAMESPACES, NamespaceTrustFilter.CONTRIBUTED]]]:

        res = client.get('/v1/modules/search?q=test{0}'.format(namespace_filter[0]))

        assert res.status_code == 200
        assert res.json == {
            'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
        }
        ModuleSearch.search_module_providers.assert_called_with(
            query='test', namespace=None, provider=None, verified=False,
            namespace_trust_filters=namespace_filter[1],
            offset=0, limit=10)

def test_api_module_search_with_verified_false(client, mocked_search_module_providers):
    """Call with verified flag as false"""
    res = client.get('/v1/modules/search?q=test&verified=false')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace=None, provider=None, verified=False,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=0, limit=10)

def test_api_module_search_with_verified_true(client, mocked_search_module_providers):
    """Test call with verified as true"""
    res = client.get('/v1/modules/search?q=test&verified=true')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 10, 'next_offset': 10, 'prev_offset': 0}, 'modules': []
    }
    ModuleSearch.search_module_providers.assert_called_with(
        query='test', namespace=None, provider=None, verified=True,
        namespace_trust_filters=NamespaceTrustFilter.UNSPECIFIED,
        offset=0, limit=10)

def test_api_module_search_with_single_module_response(client, mocked_search_module_providers):
    """Test return of single module module"""
    namespace = Namespace(name='testnamespace')
    module = Module(namespace=namespace, name='mock-module')
    mock_module_provider = MockModuleProvider(module=module, name='testprovider')
    mock_module_provider.MOCK_LATEST_VERSION_NUMBER = '1.2.3'
    ModuleSearch.search_module_providers.return_value = [mock_module_provider]

    res = client.get('/v1/modules/search?q=test&offset=0&limit=1')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 1, 'next_offset': 1, 'prev_offset': 0}, 'modules': [
            {'id': 'testnamespace/mock-module/testprovider/1.2.3', 'owner': 'Mock Owner',
             'namespace': 'testnamespace', 'name': 'mock-module',
             'version': '1.2.3', 'provider': 'testprovider',
             'description': 'Mock description', 'source': 'http://mock.example.com/mockmodule',
             'published_at': '2020-01-01T23:18:12', 'downloads': 0, 'verified': True}
        ]
    }

def test_api_module_search_with_multiple_module_response(client, mocked_search_module_providers):
    """Test multiple modules in results"""
    namespace = Namespace(name='testnamespace')
    module = Module(namespace=namespace, name='mock-module')
    mock_module_provider = MockModuleProvider(module=module, name='testprovider')
    mock_module_provider.MOCK_LATEST_VERSION_NUMBER = '1.2.3'
    mock_namespace_2 = Namespace(name='secondtestnamespace')
    mock_module_2 = Module(namespace=mock_namespace_2, name='mockmodule2')
    mock_module_provider_2 = MockModuleProvider(module=mock_module_2, name='secondprovider')
    mock_module_provider_2.MOCK_LATEST_VERSION_NUMBER = '3.0.0'
    ModuleSearch.search_module_providers.return_value = [mock_module_provider_2, mock_module_provider]

    res = client.get('/v1/modules/search?q=test&offset=0&limit=2')

    assert res.status_code == 200
    assert res.json == {
        'meta': {'current_offset': 0, 'limit': 2, 'next_offset': 2, 'prev_offset': 0}, 'modules': [
            mock_module_provider_2.get_latest_version().get_api_outline(),
            mock_module_provider.get_latest_version().get_api_outline(),
        ]
    }
