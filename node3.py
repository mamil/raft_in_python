from node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node3',
            'port' : 10003,
            'peers' :{
                    'node1' : ('localhost', 10001),
                    'node2' : ('localhost', 10002),
                    'node4' : ('localhost', 10004),
                    'node5' : ('localhost', 10005)
                }
            }
    node = Node(conf)
    node.run()