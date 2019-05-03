#!/usr/bin/env python3
"""
CLI wrapper for basic container (Docker/libpod) management tasks

Authored by Justin W. Flory.

This is a Python wrapper script to simplify specific tasks in a container
environment. It is designed to work with your container management tool of
choice (currently `podman` and `docker`). A CLI menu makes these selections
possible.

This project was created for a lab assignment in NSSA-244 Virtualization at the
Rochester Institute of Technology. in Spring 2019. Prof. Garret Arcoraci taught
the course.

NOTICE:
This Source Code Form is subject to the terms of the Mozilla Public License, v.
2.0. If a copy of the MPL was not distributed with this file, You can obtain
one at https://mozilla.org/MPL/2.0/.
"""

import argparse
import os
import subprocess
import sys


def determine_container_runtime():
    """Determine what container runtime user has installed. Prefer Podman."""
    os_path = os.environ['PATH'].split(':')
    for path in os_path:
        if os.path.isfile(path + '/podman') is True:
            return 'podman'
        elif os.path.isfile(path + '/docker') is True:
            return 'docker'
        # Expected that some paths will not contain binary
        else:
            pass


def opt_create(args):
    """Create a new container."""
    cmd_str_pull = container_runtime + ' pull ' + args.container_image + ':' \
        + args.container_image_tag
    cmd_str_create = container_runtime \
        + ' create -i --name ' + args.container_name + ' ' \
        + args.container_image + ':' + args.container_image_tag

    subprocess.run(cmd_str_pull.split(), check=True)
    subprocess.run(cmd_str_create.split(), check=True)


def opt_delete(args):
    """Delete an existing container."""
    subprocess.run([
        container_runtime,
        'rm',
        args.container_name],
        check=True)


def opt_get(args):
    """Get information about containers or container host."""

    # List available network connections (Docker only)
    # https://github.com/containers/libpod/issues/2909#issuecomment-483105074
    if args.container_get_network is True:
        subprocess.run(['docker', 'network', 'ls'], check=True)

    # List running containers
    elif args.container_get_running is True:
        subprocess.run([container_runtime, 'ps'], check=True)

    # Inspect parameters of container
    elif args.container_name is True:
        subprocess.run([
            container_runtime,
            'inspect',
            args.container_name],
            check=True)


def opt_ping(args):
    """Ping between two running containers to test connectivity.

    NOTE: This method only works for CentOS 7.x hosts. It uses the YUM package
    manager and the iputils package to get the `ping` command.
    """

    # Install iputils for ping package
    subprocess.run([
        container_runtime,
        'exec',
        '-t',
        args.container_ping_from,
        'yum', '-y', 'install', 'iputils'],
        check=True)

    # Pass ping command and parameters into container
    subprocess.run([
        container_runtime,
        'exec',
        '-t',
        args.container_ping_from,
        'ping',
        args.container_ping_to],
        check=True)


def opt_shell(args):
    """Open an interactive shell inside of a container."""
    subprocess.run([
        container_runtime,
        'exec',
        '-t',
        args.container_name,
        '/bin/bash'],
        check=True)


def opt_start(args):
    """Start a container."""
    subprocess.run([
        container_runtime,
        'start',
        args.container_name],
        check=True)


def opt_stop(args):
    """Stop a running container."""
    subprocess.run([
        container_runtime,
        'stop',
        args.container_name],
        check=True)


def main():
    """Main method to set up argument parsing."""

    # Set up argument parser and subparsers
    parser = argparse.ArgumentParser(
        description='Wrapper to perform basic container management tasks')
    subparsers = parser.add_subparsers(
        help='sub-command help')

    # Parser for "create" sub-command
    parser_create = subparsers.add_parser(
        'create',
        help='create a new container')
    parser_create.add_argument(
        '-i', '--base-image',
        dest='container_image',
        help='(required) name/URL of base image',
        metavar='<image_name>',
        required=True)
    parser_create.add_argument(
        '-n', '--name',
        dest='container_name',
        help='(required) name of new container',
        metavar='<my_container_name>',
        required=True)
    parser_create.add_argument(
        '-t', '--base-image-tag',
        default='latest',
        dest='container_image_tag',
        help='container tag to use (default: latest)',
        metavar='<tag_id>')

    # Parser for "delete" sub-command
    parser_delete = subparsers.add_parser(
        'delete',
        help='delete an existing container')
    parser_delete.add_argument(
        '-n', '--name',
        dest='container_name',
        help='(required) name of container',
        metavar='<my_container_name>',
        required=True)

    # Parser for "get" sub-command
    parser_get = subparsers.add_parser(
        'get',
        help='get info about containers or container host')
    parser_get.add_argument(
        '-n', '--name',
        dest='container_name',
        help='name of container to inspect',
        metavar='<my_container_name>')
    parser_get.add_argument(
        '--network',
        action='store_true',
        dest='container_get_network',
        help='(Docker only!) list available network connections')
    parser_get.add_argument(
        '-r', '--running',
        action='store_true',
        dest='container_get_running',
        help='list all running containers')

    # Parser for "ping" sub-command
    parser_ping = subparsers.add_parser(
        'ping',
        help='ping between two running containers to test connectivity')
    parser_ping.add_argument(
        '-f', '--from',
        dest='container_ping_from',
        help='(required) name of container to send ping from',
        metavar='<my_container_name>',
        required=True)
    parser_ping.add_argument(
        '-t', '--to',
        dest='container_ping_to',
        help='(required) name of container to ping',
        metavar='<my_container_name>',
        required=True)

    # Parser for "shell" sub-command
    parser_shell = subparsers.add_parser(
        'shell',
        help='open interactive shell of a running container')
    parser_shell.add_argument(
        '-n', '--name',
        dest='container_name',
        help='(required) name of container',
        metavar='<my_container_name>',
        required=True)

    # Parser for "start" sub-command
    parser_start = subparsers.add_parser(
        'start',
        help='start a container')
    parser_start.add_argument(
        '-n', '--name',
        dest='container_name',
        help='(required) name of container',
        metavar='<my_container_name>',
        required=True)

    # Parser for "stop" sub-command
    parser_stop = subparsers.add_parser(
        'stop',
        help='stop a container')
    parser_stop.add_argument(
        '-n', '--name',
        dest='container_name',
        help='(required) name of new container',
        metavar='<my_container_name>',
        required=True)

    # Determine what container runtime is available
    global container_runtime
    container_runtime = determine_container_runtime()

    # Actual processing of arguments and send to function
    args = parser.parse_args()
    if sys.argv[1] == 'create':
        opt_create(args)
    elif sys.argv[1] == 'delete':
        opt_delete(args)
    elif sys.argv[1] == 'get':
        opt_get(args)
    elif sys.argv[1] == 'ping':
        opt_ping(args)
    elif sys.argv[1] == 'shell':
        opt_shell(args)
    elif sys.argv[1] == 'start':
        opt_start(args)
    elif sys.argv[1] == 'stop':
        opt_stop(args)
    else:
        print('//TODO: proper error handling')


main()

# Resources used:
#   - https://docs.python.org/3.7/library/argparse.html
#   - https://docs.python.org/3.7/howto/argparse.html
#   - https://docs.python.org/3/library/subprocess.html
#   - https://docs.python.org/3.7/tutorial/datastructures.html
#   - https://www.python.org/dev/peps/pep-0257/
#   - https://docs.docker.com/engine/reference/commandline/network_inspect/
#   - https://docs.docker.com/engine/reference/commandline/create/
#   - https://stackoverflow.com/a/4693385
