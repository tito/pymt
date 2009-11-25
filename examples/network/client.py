import os
os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt.logger import pymt_logger
from serializer import SerializerNetworkClient, Serializer
from pymt import *
import time

if __name__ == '__main__':

    # Connect a client to the default port
    client = SerializerNetworkClient('127.0.0.1', 12000)

    # Create a tree
    box = MTBoxLayout()
    box.add_widget(MTSlider(max=2000, value=500))
    box.add_widget(MTSlider(value=75, orientation='horizontal'))

    # Send widget over client
    client.send_widget(box)

    # Wait a little
    time.sleep(3)
