import sys
sys.path.append("..")
from src.node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node4',
            'port' : 10004,
            'peers' :{
                    'node1' : ('localhost', 10001),
                    'node2' : ('localhost', 10002),
                    'node3' : ('localhost', 10003),
                    'node5' : ('localhost', 10005)
                }
            }
    node = Node(conf)
    node.run()
