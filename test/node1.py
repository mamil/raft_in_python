import sys
sys.path.append("..")
from src.node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node1',
            'port' : 10001,
            'peers' :{
                    'node2' : ('localhost', 10002),
                    'node3' : ('localhost', 10003),
                    'node4' : ('localhost', 10004),
                    'node5' : ('localhost', 10005)
                }
            }
    node = Node(conf)
    node.run()