import random
import time
import zmq
import src.util.surf.Config as Config
import threading
from src.util.surf.message import Message

# subscription message key list
keyList = []
# Prepare our context and subscriber
ctx = zmq.Context()
sequence = 0
snapshot = ctx.socket(zmq.DEALER)
snapshot.linger = 0
snapshot.connect("tcp://" + Config.serverAddress + ":5556")
subscriber = ctx.socket(zmq.SUB)
subscriber.linger = 0
subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
subscriber.connect("tcp://" + Config.serverAddress + ":5557")
publisher = ctx.socket(zmq.PUSH)
publisher.linger = 0
publisher.connect("tcp://" + Config.serverAddress + ":5558")

'''
    main client thread
'''
def clientThread():
    random.seed(time.time())
    kvmap = {}

    # Get state snapshot
    msg0 = Message(1)
    msg0.key = b"ICANHAZ?"
    msg0.body = b"from python"
    msg0.send(snapshot)

    while True:
        try:
            msg1 = Message.recv(snapshot)
        except:
            return          # Interrupted

        if msg1.key == b"KTHXBAI":
            sequence = msg1.sequence
            print ("I: Received snapshot=%d" % sequence)
            break          # Done
        msg1.store(kvmap)

    poller = zmq.Poller()
    poller.register(subscriber, zmq.POLLIN)

    while True:
        msg = Message.recv(subscriber)
        if msg is None:
            break
        if msg.sequence > sequence:
            if keyList.__contains__("*"):
                sequence = msg.sequence
                msg.store(kvmap)
                receiveMessage(msg)
            else:
                for key in keyList:
                    if msg.key.decode('utf-8').find(key) != -1:
                        sequence = msg.sequence
                        msg.store(kvmap)
                        receiveMessage(msg)



'''
    add keys to subcribe
'''
def subscribe(key):
    keyList.append(key)

'''
    send a message to server
'''
def sendMessage(key, msgStr):
    msg = Message(sequence)
    msg.key = key.encode('utf-8')
    msg.body = msgStr.encode('utf-8')
    msg.send(publisher)

'''
    receive a message from server
'''
def receiveMessage(msg):
    print(msg.key.decode('utf-8'), msg.body.decode('utf-8'))