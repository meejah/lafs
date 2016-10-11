from __future__ import print_function
import sys
import json

from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.internet.error import ProcessExitedAlready, ProcessDone
from twisted.internet.protocol import ProcessProtocol

import wormhole
import wormhole.xfer_util

import click


appid = u"meejah.ca/lafs"
relay = u"ws://wormhole-relay.lothar.com:4000/v1"

@inlineCallbacks
def config_from_wormhole(reactor, code):
    click.echo("Converting '{}' to JSON via wormhole".format(code))
    json = yield wormhole.xfer_util.receive(reactor, appid, relay, code)
    click.echo("Received {} bytes.".format(len(json)))
    returnValue(json)


class _DumpOutputProtocol(ProcessProtocol):
    """
    Internal helper.
    """
    def __init__(self, f):
        self.done = Deferred()
        self._out = f if f is not None else sys.stdout

    def processEnded(self, reason):
        if not self.done.called:
            self.done.callback(None)

    def processExited(self, reason):
        if not isinstance(reason.value, ProcessDone):
            self.done.errback(reason)

    def outReceived(self, data):
        self._out.write(data)

    def errReceived(self, data):
        self._out.write(data)


@inlineCallbacks
def setup(reactor, node_dir, cfg):
    click.echo("Setting up new node:")
    click.echo("  nicknake: {config[nickname]}".format(config=cfg))
    click.echo("  shares configuration:")
    click.echo("    needed: {config[needed]}".format(config=cfg))
    click.echo("     total: {config[total]}".format(config=cfg))
    click.echo("     happy: {config[happy]}".format(config=cfg))

    # XXX should check if 3456 is already taken, and if so allocate a
    # random port for the webport.

    # XXX need to set the needed/happy/total shares options
    # (preferably via command-line)
    proto = _DumpOutputProtocol(None)
    reactor.spawnProcess(
        proto,
        sys.executable,
        (
            sys.executable, '-m', 'allmydata.scripts.runner',
            'create-node',
            '--nickname', cfg['nickname'],
            '--introducer', cfg['introducer'],
            '--listen', 'none',
            '--no-storage',
            '--webport', 'tcp:7778:interface=127.0.0.1',  # FIXME meejah testing
            '--needed', config['needed'],
            '--total', config['total'],
            '--happy', config['happy'],
            node_dir,
        )
    )
    yield proto.done

    print("Running the new node")
    # XXX FIXME on Windows, "tahoe start" runs in the foreground! :(
    proto = _DumpOutputProtocol(None)
    reactor.spawnProcess(
        proto,
        sys.executable,
        (
            sys.executable, '-m', 'allmydata.scripts.runner',
            'start',
            node_dir,
        )
    )
    yield proto.done


@inlineCallbacks
def serve_config(reactor, cfg_json):

    code_d = Deferred()

    def on_code(code):
        code_d.callback(code)
    print("starting transfer")
    done = wormhole.xfer_util.send(
        reactor,
        appid,
        relay,
        data=json.dumps(cfg_json),
        code=None,
        use_tor=False,
        on_code=on_code,
    )
    done.addErrback(code_d.errback)
    code = yield code_d
    returnValue((done, code))
