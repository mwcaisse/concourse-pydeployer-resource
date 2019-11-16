import pytest

from jsonschema.validators import Draft7Validator
from jsonschema.exceptions import ValidationError
from commands.out import validate_input_params, input_schema


def test_input_schema_is_valid():
    Draft7Validator.check_schema(input_schema)


def test_valid_input_passes_validation():
    params = {
        "source": {
            "ssh_host": "192.168.1.1",
            "ssh_port": "7865",
            "ssh_user": "mitchell",
            "ssh_private_key": "BLAH BLAH BLAH",
        },
        "params": {
            "package": "s3/pydeployer-web.pydist"
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