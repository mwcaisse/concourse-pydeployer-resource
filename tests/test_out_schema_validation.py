import pytest
import os

from jsonschema.validators import Draft7Validator
from jsonschema.exceptions import ValidationError
from commands.out import validate_input_params, input_schema, read_version_from_file


def test_input_schema_is_valid():
    Draft7Validator.check_schema(input_schema)


def test_valid_input_passes_validation():
    params = {
        "source": {
            "ssh_host": "192.168.1.1",
            "ssh_port": 7865,
            "ssh_user": "mitchell",
            "ssh_private_key": "BLAH BLAH BLAH",
        },
        "params": {
            "package_directory": "s3/",
            "version_file": "s3/version"
        }
    }

    validate_input_params(params)
    assert True


def test_missing_source_fails_validation():
    params = {
        "params": {
            "package": "s3/pydeployer-web.pydist"
        }
    }
    with pytest.raises(ValidationError):
        validate_input_params(params)


def test_missing_params_fails_validation():
    params = {
        "source": {
            "ssh_host": "192.168.1.1",
            "ssh_port": 7865,
            "ssh_user": "mitchell",
            "ssh_private_key": "BLAH BLAH BLAH",
        }
    }
    with pytest.raises(ValidationError):
        validate_input_params(params)


def test_missing_version_fails_validation():
    params = {
        "source": {
            "ssh_host": "192.168.1.1",
            "ssh_port": 7865,
            "ssh_user": "mitchell",
            "ssh_private_key": "BLAH BLAH BLAH",
        },
        "params": {
            "package": "s3/pydeployer-web.pydist"
        }
    }
    with pytest.raises(ValidationError):
        validate_input_params(params)


def test_read_file_version():
    version_file_path = "./version_test"
    expected_version = "0.1.0-SNAPSHOT"

    with open(version_file_path, "w") as version_test_file:
        version_test_file.write(expected_version)

    actual_version = read_version_from_file(version_file_path)

    os.remove(version_file_path)
    assert actual_version == expected_version
