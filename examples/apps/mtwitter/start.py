import sys
import twitter
import random
import textwrap
from pymt import *

#Spawn Multi-Touch Window
w = MTWindow(fullscreen=True)
sz = w.size

#Exit Button
exitButton = MTButton(label="X", pos=(sz[0]-30, sz[1]-30), size=(30, 30))
w.add_widget(exitButton)

@exitButton.event
def on_press(*largs):
	sys.exit()

#Create Twitter API interface and login
api = twitter.Api(username=sys.argv[1], password=sys.argv[2])

#Place Everything On a Kinetic Scatter Plane
k = MTKinetic()
w.add_widget(k)

p = MTScatterPlane()
k.add_widget(p)

#Generate and Load Friend List
FriendListScatter = MTScatterWidget(size=(500, 500))
p.add_widget(FriendListScatter)

friendList = MTKineticList(searchable=False, deletable=False, size=(400, 500), pos=(50,0), title="Friends")
FriendListScatter.add_widget(friendList)

twitFriends = api.GetFriends()
for f in twitFriends:
	un = f.name.encode('ASCII', 'replace')
	friendList.add_widget(MTKineticItem(label=un, size=(350, 50)))

#Load Firends Timeline Based on Selection From Friend List
@friendList.event
def on_press(item, callback):
	FriendTimelineScatter = MTScatterWidget(size=(500, 500))
	p.add_widget(FriendTimelineScatter)

	FriendTimelineList = MTKineticList(searchable=False, deletable=False, size=(400, 500), pos=(50, 0), title=callback.name)
	FriendTimelineScatter.add_widget(FriendTimelineList)

	TimelineExitButton = MTButton(label='X', pos=(450, 450), size=(50, 50), font_size=20)
	FriendTimelineScatter.add_widget(TimelineExitButton)

	FriendTimelineItems = api.GetUserTimeline(callback.id)
	for s in FriendTimelineItems:
		us = s.text.encode('ASCII', 'replace')
		FriendTimelineList.add_widget(MTKineticItem(label=us, size=(390, 50), multiline=True, width=300))


	@TimelineExitButton.event
	def on_press(*largs):
		p.remove_widget(FriendTimelineScatter)

#Status Update Window
statusInput = MTTextInput()
w.add_widget(statusInput)

@statusInput.event
def on_text_validate():
	if len(statusInput.label) > 140:
		statusPostError = MTModalPopup(title="ERROR!", content="Warning, your status update is larger than 140 characters, please shorten your post.", size=(300, 150))
		w.add_widget(statusPostError)
	else:
		api.PostUpdate(statusInput.label)
		statusPostSucess = MTModalPopup(title="SUCESS!", content="Your post has been successfully sent to twitter.")
		w.add_widget(statusPostSucess)
		statusInput.label = ""

runTouchApp()
