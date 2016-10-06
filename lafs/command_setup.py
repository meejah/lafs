from __future__ import print_function
import json

from twisted.internet.defer import inlineCallbacks, Deferred, returnValue

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


@inlineCallbacks
def setup(reactor, cfg):
    print("Setting up")
    print(cfg)
    yield


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
