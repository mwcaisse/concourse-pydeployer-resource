#!/usr/bin/env python3

import argparse
import json
import sys

from jsonschema import validate

source_schema = {
    "type": "object",
    "properties": {
        "host": {"type": "string"},
        "ssh_port": {"type": "string"},
        "ssh_user": {"type": "string"},
        "ssh_private_key": {"type": "string"},
    },
    "required": ["host", "ssh_port", "ssh_user", "ssh_private_key"]
}

params_schema = {
    "type": "object",
    "properties": {
        "package": {"type": "string"}
    },
    "required": ["package"]

}

input_schema = {
    "type": "object",
    "properties": {
        "source": source_schema,
        "params": params_schema,
    },
    "required": ["source", "params"]

}


def validate_input_params(input_params):
    validate(instance=input_params, schema=input_schema)


def main(args):
    input_params = json.load(sys.stdin)
    validate_input_params(input_params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploys an application to a server using pydeployer via concourse")
    parser.add_argument("build_directory", help="The job's build directory") # build directory

    args = parser.parse_args()

    if not args.build_directory:
        print("Build directory is required")
    else:
        main(args)

