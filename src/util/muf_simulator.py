import zmq
import re
from time import sleep
from src.util import run_and_convert_dialogs

C_CLIENT = b'MDPC01'
context = zmq.Context()


#SURF client
import src.util.surf.SURFClient as SURFClient
import threading
SURFClient.subscribe("MSG_NLG")
t = threading.Thread(target=SURFClient.clientThread)
t.start()


def request_bytes(utterance):
    return bytes('{\"messageId\":\"MSG_ASR\",\"payload\":\"{\\"utterance\\":\\"' + utterance + '\\",\\"confidence\\":1.0}\",\"requestType\":\"\",\"sessionId\":\"\"}', encoding='utf-8')


def exchange(socket, phone_id, utterance, start, send_to_surf=True):
    if start is 1:
        request = bytes(utterance, encoding='utf-8')
    else:
        request = request_bytes(utterance)

    '''
    send to SURF
    '''
    if send_to_surf:
        import json
        requestjson = json.loads(request.decode("utf-8"))
        if 'payload' in requestjson.keys():
            if len(requestjson['payload']) > 0:
                payloadjson = json.loads(requestjson['payload'])
                if 'utterance' in payloadjson.keys():
                    SURFClient.sendMessage("MSG_ASR", payloadjson['utterance'])
                    num_of_char = len(payloadjson['utterance'])
                    sleep(num_of_char * 0.1) # 50 msec per char

    socket.send_multipart([C_CLIENT, bytes(phone_id, encoding='utf-8'), request])

    message = socket.recv_multipart()
    splitting = re.split("\\\\\"", message[2].decode('utf-8'), maxsplit=3, flags=0)
    output = splitting[1]

    utt = run_and_convert_dialogs.parse_agent_action(output)[4]

    utt = utt.replace("\\u0027", "'")
    utt = utt.replace("\\", "")
    SURFClient.sendMessage("MSG_NLG", utt)
    numOfChar = len(utt)
    sleep(numOfChar * 0.1)  # 50 msec per char

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