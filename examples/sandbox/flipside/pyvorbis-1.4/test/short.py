#!/usr/bin/env python

'''short.py - a really brief demonstration of using the ao and ogg modules'''

import ogg.vorbis
import ao

filename = 'test.ogg'
device = 'esd'
SIZE = 4096

vf = ogg.vorbis.VorbisFile(filename)
id = ao.driver_id(device)
ao = ao.AudioDevice(id)

while 1:
    (buff, bytes, bit) = vf.read(SIZE)
    if bytes == 0: break
    ao.play(buff, bytes)
