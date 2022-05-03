
from unittest import mock
import pytest

from terrareg.models import Module, ModuleProvider, Namespace
from terrareg.module_search import ModuleSearch
from test.integration.terrareg import TerraregIntegrationTest

class TestGetSearchFilters(TerraregIntegrationTest):

    def test_non_search_no_results(self):
        """Test search with no results"""

        results = ModuleSearch.get_search_filters(query='this-search-does-not-exist-at-all')
        assert results == {'providers': {}, 'contributed': 0, 'trusted_namespaces': 0, 'verified': 0}

    def test_contributed_module_one_version(self):
        """Test search with one contributed module with one version"""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', []):
            results = ModuleSearch.get_search_filters(query='contributedmodule-oneversion')

        assert results == {'providers': {'aws': 1}, 'contributed': 1, 'trusted_namespaces': 0, 'verified': 0}

    def test_contributed_module_multi_version(self):
        """Test search with one module provider with multiple versions."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', []):
            results = ModuleSearch.get_search_filters(query='contributedmodule-multiversion')

        assert results == {'providers': {'aws': 1}, 'contributed': 1, 'trusted_namespaces': 0, 'verified': 0}

    def test_contributed_multiple_modules(self):
        """Test search with partial module name match with multiple matches."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', []):
            results = ModuleSearch.get_search_filters(query='contributedmodule')

        assert results == {'providers': {'aws': 2, 'gcp': 1}, 'contributed': 3, 'trusted_namespaces': 0, 'verified': 0}

    def test_contributed_multiple_modules(self):
        """Test search with unpubished module provider version."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', []):
            results = ModuleSearch.get_search_filters(query='contributedmodule-unverified')

        assert results == {'providers': {}, 'contributed': 0, 'trusted_namespaces': 0, 'verified': 0}

    def test_verified_module_one_version(self):
        """Test search with one contributed module with one version"""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', ['modulesearch']):
            results = ModuleSearch.get_search_filters(query='contributedmodule-oneversion')

        assert results == {'providers': {'aws': 1}, 'contributed': 0, 'trusted_namespaces': 1, 'verified': 0}

    def test_verified_module_multi_version(self):
        """Test search with one module provider with multiple versions."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', ['modulesearch']):
            results = ModuleSearch.get_search_filters(query='contributedmodule-multiversion')

        assert results == {'providers': {'aws': 1}, 'contributed': 0, 'trusted_namespaces': 1, 'verified': 0}

    def test_verified_multiple_modules(self):
        """Test search with partial module name match with multiple matches."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', ['doestexist','modulesearch','nordoesthis']):
            results = ModuleSearch.get_search_filters(query='contributedmodule')

        assert results == {'providers': {'aws': 2, 'gcp': 1}, 'contributed': 0, 'trusted_namespaces': 3, 'verified': 0}

    def test_verified_multiple_modules(self):
        """Test search with unpubished module provider version."""

        with mock.patch('terrareg.config.Config.TRUSTED_NAMESPACES', ['doestexist','modulesearch']):
            results = ModuleSearch.get_search_filters(query='contributedmodule-unpublished')

        assert results == {'providers': {}, 'contributed': 0, 'trusted_namespaces': 0, 'verified': 0}


