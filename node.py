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
        self.role = 'follower'

        #Persistent state on all servers:
        self.currentTerm = 0
        self.votedFor = None

        #Volatile state on all servers:
        self.commitIndex = 0
        self.lastApplied = 0

        #Volatile state on leaders:
        self.nextIndex = 0
        self.matchIndex = 0

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

    def request_vote(self):
        RequestVote = {
            'term' : self.currentTerm + 1,
            'candidateId' : self.id,
            'lastLogIndex' : self.commitIndex,
            'lastLogTerm' : self.currentTerm
        }
        for peer in self.peers:
            self.send(RequestVote, peer)

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


