'''
Test of audio core, with event play/stop.
'''

import os
from pymt import *

# load the sound
filename = os.path.join(os.path.dirname(__file__), 'test_audio.wav')
sound = SoundLoader.load(filename)

# install callack for on_play/on_stop event
@sound.event
def on_play():
    print '-> sound started, status is', sound.status

@sound.event
def on_stop():
    print '-> sound finished, status is', sound.status
    stopTouchApp()

# start to play the sound
sound.play()

# run the application
runTouchApp()

