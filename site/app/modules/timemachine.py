import paho.mqtt.client as mqtt
from threading import Thread
import os
import time

USER_NAME='timemachine'
PASSWORD='hellotimemachine'
CA_PATH = '/code/site/app/modules/ca.crt'
HOST = '222.201.144.236'
PORT = 8883
MEDIA_ROOT = '/code/site/app/media/recorder'

class Replayer:
    def __init__(self, topic_prefix):
        super().__init__()
        self._topic_prefix = topic_prefix
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.username_pw_set(USER_NAME, PASSWORD)
        self._client.tls_set(ca_certs=CA_PATH)
        self._client.connect(HOST, PORT, 60) 

    def on_connect(self, client, userdata, flags, rc):
        try:
            f = open(MEDIA_ROOT+self._topic_prefix+'/realtime', 'r') 
            for line in f.readlines():
                client.publish(self._topic_prefix+'/replay', line[:-1])
        except IOError:
            print('can not access:'+MEDIA_ROOT+self._topic_prefix+'/realtime')

    def open(self):
        self._client.loop_start()

    def close(self):
        self._client.loop_stop()
        self._client.disconnect()


class Recorder:
    def __init__(self, topic_prefix):
        self._topic_prefix = topic_prefix
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.username_pw_set(USER_NAME, PASSWORD)
        self._client.tls_set(ca_certs=CA_PATH)
        self._client.connect(HOST, PORT, 60)
        os.makedirs(MEDIA_ROOT+self._topic_prefix, exist_ok=True)
        self._f = open(MEDIA_ROOT+self._topic_prefix+'/realtime', 'w')
    
    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self._topic_prefix+'/realtime')

    def _on_message(self, client, userdata, msg):
        self._f.write(str(msg.payload, encoding='utf-8'))
        self._f.write('\n')

    def open(self):
        self._client.loop_start()
        
    def close(self):
        self._client.loop_stop()
        self._client.unsubscribe(self._topic_prefix+'/realtime')
        self._client.disconnect()
        self._f.close()

def on_connect(client, userdata, flags, rc):
    client.subscribe('/+/+/+/timemachine')

timemachines = {}
def on_message(client, userdata, msg):
    topic_prefix = msg.topic[:-12]
    # what's the cmd?
    cmd = msg.payload
    if cmd == b'replay_open':
        if topic_prefix not in timemachines:
            replayer = Replayer(topic_prefix)
            timemachines[topic_prefix]=replayer
            replayer.open()
    elif cmd == b'replay_close':
        if topic_prefix in timemachines:
            timemachines[topic_prefix].close()
            del timemachines[topic_prefix]
    elif cmd == b'record_open':
        if topic_prefix not in timemachines:
            recorder = Recorder(topic_prefix)
            timemachines[topic_prefix]=recorder
            recorder.open()
    elif cmd == b'record_close':
        if topic_prefix in timemachines:
            timemachines[topic_prefix].close()
            del timemachines[topic_prefix]

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USER_NAME, PASSWORD)
    client.tls_set(ca_certs=CA_PATH)
    client.connect(HOST, PORT, 60)
    client.loop_forever()
