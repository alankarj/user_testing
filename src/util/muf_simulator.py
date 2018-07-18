import zmq
import re

C_CLIENT = b'MDPC01'
context = zmq.Context()


def request_bytes(utterance):
    return bytes('{\"messageId\":\"MSG_ASR\",\"payload\":\"{\\"utterance\\":\\"' + utterance + '\\",\\"confidence\\":1.0}\",\"requestType\":\"\",\"sessionId\":\"\"}', encoding='utf-8')


def exchange(socket, phone_id, utterance, start):
    if start is 1:
        request = bytes(utterance, encoding='utf-8')
    else:
        request = request_bytes(utterance)
    socket.send_multipart([C_CLIENT, bytes(phone_id, encoding='utf-8'), request])

    message = socket.recv_multipart()
    splitting = re.split("\\\\\"", message[2].decode('utf-8'), maxsplit=3, flags=0)
    output = splitting[1]
    return output


def send_receive_message(socket, phone_id, request):
    socket.send_multipart([C_CLIENT, bytes(phone_id, encoding='utf-8'), request])
    message = socket.recv_multipart()
    return message


def setup(socket, phone_id, muf_address):
    # connect to server
    socket.connect(muf_address)
    # send initial request and receive reply
    request = bytes("{\"requestType\":\"REQUEST_CONNECT\",\"sessionId\":\"" + phone_id + "\",\"url\":\"" + muf_address + "\",\"payload\":\"\"}", encoding='utf-8')
    socket.send_multipart([C_CLIENT, b'session-manager', request])
    message = socket.recv_multipart()
    return message


def simulation(phone_id, ip_address):
    muf_address = "tcp://" + ip_address + ":5555"
    socket = context.socket(zmq.REQ)
    setup(socket, phone_id, muf_address)
    return socket
