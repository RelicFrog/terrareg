
import unittest.mock
import re

import pytest

import terrareg.config


class TestConfig:
    """Test Config class."""

    @classmethod
    def setup_class(cls):
        """Setup class"""
        # Create list to hold all tested variables
        cls.tested_variables = []

    @classmethod
    def teardown_class(cls):
        """Ensure that all configs from Config class have been tested."""
        valid_config_re = re.compile(r'^[A-Z]')

        untested_properties = []

        for prop in dir(terrareg.config.Config):

            # Check if attribute looks like a config variable
            if not valid_config_re.match(prop):
                continue

            # If property has not been tested, add to list of untested configs
            if prop not in cls.tested_variables:
                untested_properties.append(prop)

        # Assert that there were no untested configs
        if untested_properties:
            print('Untested configs: ', untested_properties)
        assert untested_properties == []

    @classmethod
    def register_checked_config(cls, config):
        """Register a config item as having been tested."""
        if config not in cls.tested_variables:
            cls.tested_variables.append(config)

    @pytest.mark.parametrize('config_name,override_expected_value', [
        ('ADMIN_AUTHENTICATION_TOKEN', None),
        ('ANALYTICS_TOKEN_DESCRIPTION', None),
        ('ANALYTICS_TOKEN_PHRASE', None),
        ('APPLICATION_NAME', None),
        ('CONTRIBUTED_NAMESPACE_LABEL', None),
        ('DATABASE_URL', None),
        ('DATA_DIRECTORY', 'unittest-value/data'),
        ('EXAMPLES_DIRECTORY', None),
        ('EXAMPLE_ANALYTICS_TOKEN', None),
        ('GIT_PROVIDER_CONFIG', None),
        ('LOGO_URL', None),
        ('MODULES_DIRECTORY', None),
        ('SECRET_KEY', None),
        ('SSL_CERT_PRIVATE_KEY', None),
        ('SSL_CERT_PUBLIC_KEY', None),
        ('TERRAFORM_EXAMPLE_VERSION_TEMPLATE', None),
        ('TRUSTED_NAMESPACE_LABEL', None),
        ('VERIFIED_MODULE_LABEL', None),
        ('INFRACOST_API_KEY', None),
        ('INFRACOST_PRICING_API_ENDPOINT', None),
    ])
    def test_string_configs(self, config_name, override_expected_value):
        """Test string configs to ensure they are overriden with environment variables."""
        self.register_checked_config(config_name)
        with unittest.mock.patch('os.environ', {config_name: 'unittest-value'}):
            assert getattr(terrareg.config.Config(), config_name) == (override_expected_value if override_expected_value is not None else 'unittest-value')

    @pytest.mark.parametrize('config_name', [
        'ADMIN_SESSION_EXPIRY_MINS',
        'LISTEN_PORT'
    ])
    def test_integer_configs(self, config_name):
        """Test integer configs to ensure they are overriden with environment variables."""
        self.register_checked_config(config_name)
        with unittest.mock.patch('os.environ', {config_name: '582612'}):
            assert getattr(terrareg.config.Config(), config_name) == 582612

    @pytest.mark.parametrize('test_value,expected_value', [
        # Check empty value produces an empty array
        ('', []),
        # Ensure a single value produces an array with a single value
        ('unittest-value', ['unittest-value']),
        # Ensure a single value with a space produces an array with a single value
        ('unittest value', ['unittest value']),
        # Ensure a single value with a leading/trailing comma produces an array with a single value
        (',unittest-value,', ['unittest-value']),
        # Ensure multiple values produce an array with a both values
        ('unittest-value1,test-value2', ['unittest-value1', 'test-value2'])
    ])
    @pytest.mark.parametrize('config_name', [
        ('ALLOWED_PROVIDERS'),
        ('ANALYTICS_AUTH_KEYS'),
        ('PUBLISH_API_KEYS'),
        ('REQUIRED_MODULE_METADATA_ATTRIBUTES'),
        ('TRUSTED_NAMESPACES'),
        ('UPLOAD_API_KEYS'),
        ('VERIFIED_MODULE_NAMESPACES')
    ])
    def test_list_configs(self, config_name, test_value, expected_value):
        """Test list configs to ensure they are overriden with environment variables."""
        self.register_checked_config(config_name)
        # Check that input value produces expected list value
        with unittest.mock.patch('os.environ', {config_name: test_value}):
            assert getattr(terrareg.config.Config(), config_name) == expected_value

    @pytest.mark.parametrize('test_value,expected_value', [
        ('true', True),
        ('True', True),
        ('TRUE', True),
        ('false', False),
        ('False', False),
        ('FALSE', False),
        ('0', False),
        ('1', True),
        ('yes', True),
        ('no', False)
    ])
    @pytest.mark.parametrize('config_name', [
        'ALLOW_CUSTOM_GIT_URL_MODULE_PROVIDER',
        'ALLOW_CUSTOM_GIT_URL_MODULE_VERSION',
        'ALLOW_MODULE_HOSTING',
        'ALLOW_UNIDENTIFIED_DOWNLOADS',
        'AUTO_CREATE_MODULE_PROVIDER',
        'AUTO_PUBLISH_MODULE_VERSIONS',
        'DEBUG',
        'DELETE_EXTERNALLY_HOSTED_ARTIFACTS',
        'DISABLE_TERRAREG_EXCLUSIVE_LABELS',
        'AUTOGENERATE_MODULE_PROVIDER_DESCRIPTION',
        'ENABLE_SECURITY_SCANNING',
        'AUTOGENERATE_USAGE_BUILDER_VARIABLES',
        'THREADED',
        'INFRACOST_TLS_INSECURE_SKIP_VERIFY'
    ])
    def test_boolean_configs(self, config_name, test_value, expected_value):
        """Test boolean configs to ensure they are overriden with environment variables."""
        self.register_checked_config(config_name)
        # Check that input value generates the expected boolean value
        with unittest.mock.patch('os.environ', {config_name: test_value}):
            assert getattr(terrareg.config.Config(), config_name) is expected_value

