from twisted.internet import reactor
from twisted.words.protocols import irc
from twisted.internet import protocol
import json, mumble, threading

config = json.load(open('config.json'))

class IRCBot(irc.IRCClient):
    nickname = str(config['ircnick'])
    channel = str(config['ircchannel'])
    def signedOn(self):
        self.join(self.channel)
        print "Signed on as %s." % self.nickname

    def joined(self, channel):
        print "Joined %s." % channel

        self.sendMumbleInfo(mumble.getUserSummaries())
        self.runMumbleChecks()

    def sendMumbleInfo(self, text):
        self.lastSent = text
        self.msg(self.channel, self.lastSent)

    def runMumbleChecks(self):
        threading.Timer(5, self.runMumbleChecks).start()
        newText = mumble.getUserSummaries()
        if newText != self.lastSent:
            self.sendMumbleInfo(newText)

class IRCFactory(protocol.ClientFactory):
    protocol = IRCBot

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % reason

reactor.connectTCP(str(config['irchost']), int(config['ircport']), IRCFactory())
reactor.run()
