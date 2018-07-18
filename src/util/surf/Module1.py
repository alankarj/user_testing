import random
import time
import zmq
import Config
import threading
from message import Message
import SURFClient

if __name__ == '__main__':
    SURFClient.subscribe("MSG_NLG")
    t = threading.Thread(target=SURFClient.clientThread)
    t.start()

    while True:
        n = input()
        SURFClient.sendMessage("MSG_NLG", n)