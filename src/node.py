import socket
import json
import logging
import time
import random

logging.basicConfig(level=logging.INFO)

class Node:
    def __init__(self, conf):
        self.id = conf['id']
        self.peers = conf['peers'] 
        self.port = conf['port']

        self.bufferSize = 10240
        self.role = 'follower'

        #timer
        self.heartBeat = 3
        self.wait_ms = (150,300)
        self.next_leader_election_time = time.time() + self.heartBeat + random.randint(*self.wait_ms) / 1000

        #Persistent state on all servers:
        self.currentTerm = 0
        self.votedFor = None
        self.votedForTerm = 0

        #Volatile state on all servers:
        self.commitIndex = 0
        self.lastApplied = 0

        #Volatile state on leaders:
        self.nextIndex = 0
        self.matchIndex = 0

        #Persistent state on candidate:
        self.getted_vote = 0

        #msg send and receive
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('localhost', self.port))
        self.serverSocket.settimeout(self.heartBeat - 1)

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):
        data, addr = self.serverSocket.recvfrom(self.bufferSize)
        return json.loads(data), addr

    def send(self, data, addr):
        data = json.dumps(data).encode('utf-8')
        self.clientSocket.sendto(data, addr)

    def request_vote(self):
        # logging.info("!!!in request_vote!!!")

        self.votedFor = self.id #投票给自己
        RequestVote = {
            'type' : 'RequestVote',
            'id' : self.id,
            'term' : self.currentTerm,
            'candidateId' : self.id,
            'lastLogIndex' : self.commitIndex,
            'lastLogTerm' : self.currentTerm
        }
        for key in self.peers.keys():
            self.send(RequestVote, self.peers[key])

    def request_vote_response(self, data): #还要加约束，不能谁都true
        response = {
                        'type' : 'RequestVote_Response',
                        'id' : self.id,
                        'term' : self.currentTerm,
                        'voteGranted' : False
                    }

        if data['term'] < self.currentTerm:
            response = {
                        'type' : 'RequestVote_Response',
                        'id' : self.id,
                        'term' : self.currentTerm,
                        'voteGranted' : False
                    }
        elif (self.votedFor == None or self.votedFor == data['id']) and data['lastLogIndex'] >= self.commitIndex:
            self.votedFor = data['id'] #什么时候清空呢？第一轮平票，第二轮的时候，如果不改，还是投给之前那个，那还是平票。
            self.votedForTerm = data['term'] #增加记录
            response = {
                        'type' : 'RequestVote_Response',
                        'id' : self.id,
                        'term' : self.currentTerm,
                        'voteGranted' : True
                    }
        elif self.votedFor != None and data['term'] > self.votedForTerm: # 上次平票，如果这次有term更新的来了，那么投票
            self.votedFor = data['id'] #什么时候清空呢？第一轮平票，第二轮的时候，如果不改，还是投给之前那个，那还是平票。
            self.votedForTerm = data['term'] #增加记录
            response = {
                        'type' : 'RequestVote_Response',
                        'id' : self.id,
                        'term' : self.currentTerm,
                        'voteGranted' : True
                    }

        self.send(response, self.peers[data['id']])

    def follower_handle(self, data):
        if data == None:
            currentTime = time.time()
            logging.info('current:{}, next:{}'.format(currentTime, self.next_leader_election_time))
            #超时开始选举
            if currentTime >= self.next_leader_election_time:
                # self.getted_vote = 0
                self.role = 'candidate'
                self.currentTerm += 1
                self.request_vote()
                logging.info('{} change to candidate, request_vote'.format(self.id))
        else:
            if data['type'] == 'RequestVote':
                self.request_vote_response(data)
                self.role = 'follower'
                # self.next_leader_election_time = time.time() + self.heartBeat + random.randint(*self.wait_ms) / 1000
                # logging.info('###sending {}'.format(response))
            elif data['type'] == 'AppendEntries':
                self.role = 'follower'
                self.next_leader_election_time = time.time() + self.heartBeat + random.randint(*self.wait_ms) / 1000

    def leader_handle(self, data):
        logging.info('{} is leader now!!'.format(self.id))

        msg = {
            'type' : 'AppendEntries',
            'id' : self.id,
            'info' : ''
        }
        for key in self.peers.keys():
            self.send(msg, self.peers[key])

    def candidate_handle(self, data):
        logging.info('{} is candidate now!!'.format(self.id))

        if data != None:
            if data['type'] == 'RequestVote_Response' and data['voteGranted'] == True:
                self.getted_vote += 1
                logging.info('current vote:{}, need:{}'.format(self.getted_vote, int((len(self.peers) / 2))))

                if (self.getted_vote + 1) > int((len(self.peers) / 2)): # +1 是加自己对自己的一票
                    self.getted_vote = 0
                    self.role = 'leader'
            elif data['type'] == 'RequestVote':
                self.request_vote_response(data)
            elif data['type'] == 'AppendEntries':
                self.getted_vote = 0
                self.role = 'follower'
        else:
            self.currentTerm += 1 #一次选举超时，开始下一次
            self.getted_vote = 0
            self.request_vote()

    def run(self):
        while True:
            try:
                data, addr = self.receive()
            except Exception as e:
                data, addr = None, None #可以不用Timer,因为这里socket超时就相当于一个计时器,但是这样有个问题，超时之后的随机时间就无效了。
                logging.info(e)
                
            logging.info("role:{}, receive: {}, {}".format(self.role, data, addr))

            if self.role == 'follower':
                self.follower_handle(data)
            elif self.role == 'leader':
                self.leader_handle(data)
            elif self.role == 'candidate':
                self.candidate_handle(data)
