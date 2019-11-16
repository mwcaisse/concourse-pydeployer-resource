#!/usr/bin/env python3

import argparse
import json
import sys
import io
import os
from paramiko import SSHClient
from scp import SCPClient


from jsonschema import validate

source_schema = {
    "type": "object",
    "properties": {
        "ssh_host": {"type": "string"},
        "ssh_port": {"type": "string"},
        "ssh_user": {"type": "string"},
        "ssh_private_key": {"type": "string"},
        "ssh_private_key_passphrase": {"type": "string"},
    },
    "required": ["host", "ssh_port", "ssh_user", "ssh_private_key"]
}

params_schema = {
    "type": "object",
    "properties": {
        "package_directory": {"type": "string"}
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


def execute(build_directory, source, params):

    # Add some validation to see if we can find the pydist file first?

    # connect to the Server
    ssh = SSHClient()
    ssh.connect(
        hostname=source["ssh_host"],
        port=source["ssh_port"],
        username=source["ssh_username"],
        passphrase=source.get("ssh_private_key_passphrase"),
        pkey=io.StringIO(source["ssh_private_key"]),
        look_for_keys=False,
        allow_agent=False
    )

    # Construct package directory
    package_directory = os.path.join(build_directory, params["package_directory"])

    # Copy over the pydist package
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(package_directory, recursive=True, remote_path="~/pydeployer-tmp")

    # Install the package
    # TODO: Add some validation around running these commands
    ssh.exec_command("cd ~/pydeployer-tmp")
    ssh.exec_command("pydeployer deploy *.pydist")
    # ssh.exec_command("rm -r *")

    # Close out the ssh connection
    ssh.close()

    return {
        "version": {"ref": "test-version-1"},
        "metadata": [
        ]
    }


def main(args):
    input_params = json.load(sys.stdin)
    validate_input_params(input_params)

    output = execute(args.build_directory, input_params["source"], input_params["params"])
    print(json.dumps(output))

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploys an application to a server using pydeployer via concourse")
    parser.add_argument("build_directory", help="The job's build directory") # build directory

    args = parser.parse_args()

    if not args.build_directory:
        print("Build directory is required")
        exit(2)
    else:
        res = main(args)
        exit(res)

