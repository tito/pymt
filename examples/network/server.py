from pymt.logger import pymt_logger
from serializer import SerializerNetworkServer
import time

if __name__ == '__main__':

    # Start a standalone server
    s = SerializerNetworkServer()
    s.start()

    # Get message, and print them
    while True:
        try:
            clientid, message = s.queue.pop()
        except:
            time.sleep(1)
            continue
        print 'Got a message from', clientid, message
