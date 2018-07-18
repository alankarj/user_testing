#!/usr/bin/env python3
#
# MUF simulation 
# Non-incremental versions only
#

import unittest
import zmq
import time
import unicodedata
import sys
import re

from threading import Thread

C_CLIENT = b'MDPC01'
context = zmq.Context()
# set ip address in main method
mufAddress = "tcp://localhost:5555"
ipAddress = "localhost"

def request_bytes(utterance):
    return bytes('{\"messageId\":\"MSG_ASR\",\"payload\":\"{\\"utterance\\":\\"' + utterance + '\\",\\"confidence\\":1.0}\",\"requestType\":\"\",\"sessionId\":\"\"}', encoding='utf-8')
 
def turn_exchange_automatic(socket, phoneID, num, genre, director, actor):
    message = setup(socket, phoneID)
    # genre
    request = request_bytes(genre)
    # print("request ", request)
    startTime = time.time()
    socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
    # print("sent ", request)
    message = socket.recv_multipart()
    endTime = time.time()
    print("genre (duration): ", round((endTime - startTime) * 1000)/1000)

    # director
    request = request_bytes(director)
    startTime = time.time()
    socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
    message = socket.recv_multipart()
    endTime = time.time()
    print("director (duration): ", round((endTime - startTime) * 1000)/1000)

    for i in range(0, num):
        # message
        request = request_bytes(actor)
        print("sending: ", time.time())
        startTime = time.time()
        socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
        message = socket.recv_multipart()
        endTime = time.time()
        print("result (duration): ", round((endTime - startTime) * 1000)/1000)

    socket.close()
    return message

def turn_exchange_manual(socket, phoneID, utterance):
    print(setup(socket, phoneID))
    # utterance = input("Enter input (q to quit): ")

    while (utterance is not 'q'):
        request = request_bytes(utterance)
        # print("request ", request)
        startTime = time.time()
        socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
        # print("sent ", request)
        message = socket.recv_multipart()
        endTime = time.time()
        print("duration: ", round((endTime - startTime) * 1000)/1000)
        splitting = re.split("\\\\\"", message[2].decode("utf-8"), maxsplit=3, flags=0)
        output = splitting[1]
        print(output)
        print("")
        utterance = input("Enter input (q to quit): ")
        print("")

    socket.close()
    return message

def exchange(socket, phoneID, utterance):
    request = request_bytes(utterance)
    socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])

    message = socket.recv_multipart()
    splitting = re.split("\\\\\"", message[2].decode("utf-8"), maxsplit=3, flags=0)
    output = splitting[1]

    return output

def send_receive_message(socket, phoneID, request):
    start_time = time.time()
    socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
    message = socket.recv_multipart()
    end_time = time.time()
    # print(end_time - start_time)
    return message


def setup(socket, phoneID):

    # connect to server
    socket.connect(mufAddress)

    # send initial request and receive reply
    request = bytes("{\"requestType\":\"REQUEST_CONNECT\",\"sessionId\":\"" + phoneID + "\",\"url\":\"" + mufAddress + "\",\"payload\":\"\"}", encoding='utf-8')
    socket.send_multipart([C_CLIENT, b'session-manager', request])
    message = socket.recv_multipart()
    # print("connected ", time.time())
    # print(message)

    # start conversation
    # request = b'{\"messageId\":\"MSG_START_INTERACTION\",\"payload\":\"\",\"requestType\":\"\",\"sessionId\":\"\"}'
    # socket.send_multipart([C_CLIENT, bytes(phoneID, encoding='utf-8'), request])
    # message = socket.recv_multipart()
    # splitting = re.split("\\\\\"", message[2].decode("utf-8"), maxsplit=3, flags=0)
    # output = splitting[1]
    # print("interaction started ", time.time())
    return output

def simulation(ip):
    ipAddress = ip
    mufAddress = "tcp://" + ipAddress + ":5555"
    socket1 = context.socket(zmq.REQ)
    phonepi = "3141592653589793"
    setup(socket, phoneID)

if __name__ == '__main__':

    # comment out one of the two lines below
    # ipAddress = input("Enter ip address: ")
    ipAddress = "128.237.207.193"

    mufAddress = "tcp://" + ipAddress + ":5555"

    # run simulation
    simulation()
