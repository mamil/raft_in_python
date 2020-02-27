import socket
import json
import logging
import time

logging.basicConfig(level=logging.INFO)

class Node:
    def __init__(self, conf):
        self.id = conf['id']
        self.peers = conf['peers'] 
        self.port = conf['port']

        self.bufferSize = 10240

        #msg send and receive
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('localhost', self.port))
        self.serverSocket.settimeout(2)

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):
        data, addr = self.serverSocket.recvfrom(self.bufferSize)
        return json.loads(data), addr

    def send(self, data, addr):
        data = json.dumps(data).encode('utf-8')
        self.clientSocket.sendto(data, addr)

    def run(self):
        while True:
            try:
                data, addr = self.receive()
            except Exception as e:
                data, addr = None, None
                logging.info(e)
                
            logging.info("receive: {}, {}".format(data, addr))

            self.send("from {}".format(self.id), self.peers[0]) #这里也需要考虑超时吗？？双端都是send会卡住？
            self.send("from {}".format(self.id), self.peers[1])

            time.sleep(1)


