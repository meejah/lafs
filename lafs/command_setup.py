from __future__ import print_function
import sys
import json

from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.internet.error import ProcessExitedAlready, ProcessDone
from twisted.internet.protocol import ProcessProtocol

import wormhole
import wormhole.xfer_util


appid = u"testing some stuff"
relay = u"ws://wormhole-relay.lothar.com:4000/v1"

@inlineCallbacks
def config_from_wormhole(reactor, code):
    print("Converting '{}' to JSON via wormhole".format(code))
    json = yield wormhole.xfer_util.receive(reactor, appid, relay, code)
    print("JSON", json)
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
    print("Setting up")
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
            '--webport', 'tcp:7777:interface=127.0.0.1',  # FIXME meejah testing
            node_dir,
        )
    )
    yield proto.done

    print("Running")
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
