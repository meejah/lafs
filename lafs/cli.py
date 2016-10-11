from __future__ import print_function

import sys
import json
import click

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react

from . import command_setup

@click.group()
def lafs():
    """
    High-level utilities to work with the Tahoe-LAFS secure storage system
    """


@lafs.command()
@click.option(
    '-j', '--json', 'json_file',
    help="JSON file to load setup information from",
    type=click.File(),
    required=False,
    default=None,
)
@click.option(
    '-p', '--path',
    help="Where to create the new Tahoe node",
    type=click.Path(exists=False),
    prompt="Non-existant directory for new Tahoe node",
)
@click.argument(
    'activation_code',
    "Provide an activate-code",
    required=False,
)
def setup(json_file, activation_code, path):
    """
    Set up a new node
    """
    cfg_json = None
    if json_file is not None:
        cfg_json = json.load(json_file)
    if cfg_json is None and activation_code is None:
        activation_code = click.prompt(
            "Please enter an activation code:"
        )
        if not activation_code.strip():
            click.echo("No code found")
            raise click.Abort()

    @inlineCallbacks
    def main(reactor, cfg, code):
        if cfg is None:
            if code is None:
                raise Exception(
                    "Need an activation code or JSON configuration to proceed"
                )
            
            cfg = yield command_setup.config_from_wormhole(reactor, code)
            cfg = json.loads(cfg)
        yield command_setup.setup(reactor, path, cfg)
    react(main, (cfg_json, activation_code))


@lafs.command()
@click.option(
    '-j', '--json', 'json_file',
    help="JSON file to load setup information from",
    type=click.File(),
    required=True,
)
# XXX timeout?
def serve_config(json_file):
    """
    Serves given JSON via magic-wormhole and prints the code to stdout
    """
    cfg_json = json.load(json_file)

    @inlineCallbacks
    def main(reactor):
        sys.stderr = open('/dev/null', 'w')
        done, code = yield command_setup.serve_config(reactor, cfg_json)
        print(code)
        sys.stdout.flush()
        yield done
    react(main)
