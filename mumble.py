import Ice, Murmur, json
config = json.load(open('config.json'))
ic = Ice.initialize()

# http://wiki.mumble.info/wiki/Channel_Viewer_Protocol
def loadChannel(iceChannel):
	channel = {}
	channel['id'] = iceChannel.c.id
	channel['name'] = iceChannel.c.name
	channel['parent'] = iceChannel.c.parent
	channel['childChannels'] = []
	channel['users'] = []
	channel['links'] = []
	channel['description'] = iceChannel.c.description
	channel['temporary'] = iceChannel.c.temporary
	channel['position'] = iceChannel.c.position
	for childChannel in iceChannel.children:
		channel['childChannels'].append(loadChannel(childChannel))
	for user in iceChannel.users:
		channel['users'].append(loadUser(user))
	return channel

def loadUser(iceUser):
	user = {}
	user['session'] = iceUser.session
	user['userid'] = iceUser.userid
	user['mute'] = iceUser.mute
	user['deaf'] = iceUser.deaf
	user['suppress'] = iceUser.suppress
	user['selfMute'] = iceUser.selfMute
	user['selfDeaf'] = iceUser.selfDeaf
	user['channel'] = iceUser.channel
	user['name'] = iceUser.name
	user['onlinesecs'] = iceUser.onlinesecs
	user['idlesecs'] = iceUser.idlesecs
	user['os'] = iceUser.os
	user['release'] = iceUser.release
	user['bytespersec'] = iceUser.bytespersec
	user['prioritySpeaker'] = iceUser.prioritySpeaker
	#user['address'] = iceUser.address # todo
	user['recording'] = iceUser.recording
	user['version'] = iceUser.version
	user['osversion'] = iceUser.osversion
	user['identity'] = iceUser.identity
	user['context'] = iceUser.context
	user['comment'] = iceUser.comment
	user['tcponly'] = iceUser.tcponly
	user['udpPing'] = iceUser.udpPing
	user['tcpPing'] = iceUser.tcpPing
	return user

def getUserSummaries():
	base = ic.stringToProxy('Meta:tcp -h ' + str(config['mumblehost']) + ' -p ' + str(config['mumbleport']))
	meta = Murmur.MetaPrx.checkedCast(base)
	server = meta.getBootedServers()[0]
	rootChannel = loadChannel(server.getTree())

	allUsers = {}
	allChannels = {}
	channelsToCheck = [rootChannel]
	while len(channelsToCheck) > 0:
		checking = channelsToCheck.pop()
		channelsToCheck += checking['childChannels']
		for user in checking['users']:
			allUsers[user['name']] = user
		allChannels[checking['id']] = checking

	channelPaths = {}
	for channelId, channelInfo in allChannels.items():
		parts = []
		check = channelInfo
		while True:
			parts.append(check['name'])
			if check['parent'] in allChannels:
				check = allChannels[check['parent']]
			else:
				break
		parts.reverse()
		if len(parts) > 1:
			# Only the Root channel is called Root, everything below it does
			# not show the 'Root' prefix.
			parts = parts[1:]
		channelPaths[channelId] = ' -> '.join(parts)

	userSummaries = []
	for userName, user in allUsers.items():
		userSummary = userName + ' (Channel: ' + channelPaths[user['channel']]

		if user['deaf'] or user['selfDeaf']:
			userSummary += ', Deaf'

		if user['mute'] or user['selfMute']:
			userSummary += ', Mute'

		userSummary += ')'
		userSummaries.append(userSummary)

	return 'Users on ' + str(config['mumbleDisplayName']) + ': ' + ', '.join(userSummaries)
