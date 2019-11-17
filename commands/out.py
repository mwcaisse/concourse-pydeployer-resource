#!/usr/bin/env python3

import argparse
import json
import sys
import io
import os
import time
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from paramiko.rsakey import RSAKey
from scp import SCPClient


from jsonschema import validate

source_schema = {
    "type": "object",
    "properties": {
        "ssh_host": {"type": "string"},
        "ssh_port": {"type": "number"},
        "ssh_user": {"type": "string"},
        "ssh_private_key": {"type": "string"},
        "ssh_private_key_passphrase": {"type": "string"},
    },
    "required": ["ssh_host", "ssh_port", "ssh_user", "ssh_private_key"]
}

params_schema = {
    "type": "object",
    "properties": {
        "package_directory": {"type": "string"}
    },
    "required": ["package_directory"]

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

    # Load up the private key for the connection
    private_key = RSAKey.from_private_key(io.StringIO(source["ssh_private_key"]))

    # Construct package directory
    package_directory = os.path.join(build_directory, params["package_directory"])

    log_output("Connecting to {}".format(source["ssh_host"]))
    # connect to the Server
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy)
    ssh.connect(
        hostname=source["ssh_host"],
        port=source["ssh_port"],
        username=source["ssh_user"],
        pkey=private_key,
        look_for_keys=False,
        allow_agent=False
    )

    log_output("Connected to {}. Copying over artifiacts from: {}".format(source["ssh_host"], package_directory))

    # Before we copy over the file, delete the pydeployer-tmp folder, as SCP's behaviour changes if it already exists
    # TODO: pydeployer-tmp should be pulled out into a variable and input config
    execute_command(ssh, "rm -r ~/pydeployer-tmp")

    def scp_progress(filename, size, sent):
        sys.stderr.write("%s's progress: %.2f%%  \r" % (filename, float(sent)/float(size)*100))

    # Copy over the pydist package
    with SCPClient(ssh.get_transport(), progress=scp_progress) as scp:
        scp.put(package_directory, recursive=True, remote_path="~/pydeployer-tmp")

    log_output("Copied artifacts. Executing deployment")
    # Install the package
    # TODO: Add some validation around running these commands
    execute_command(ssh, "pydeployer deploy *.pydist", working_directory="~/pydeployer-tmp")

    log_output("Deployment done. Terminating SSH connection.")
    # Close out the ssh connection
    ssh.close()

    return {
        "version": {"version": "test-version-2"}
    }


def execute_command(ssh, command, working_directory=None):
    if working_directory:
        command = "cd {working_directory}; {command}".format(working_directory=working_directory, command=command
                                                             )
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    stdout_str = stdout.read().decode("UTF-8")
    stderr_str = stderr.read().decode("UTF-8")

    if stdout_str:
        log_output(stdout_str)
    if stderr_str:
        log_output(stderr_str)


def log_output(message, **kwargs):
    print(message, file=sys.stderr, **kwargs)


def main():
    build_directory = sys.argv[1]
    input_params = json.load(sys.stdin)
    validate_input_params(input_params)

    output = execute(build_directory, input_params["source"], input_params["params"])
    print(json.dumps(output))


if __name__ == "__main__":
    main()


