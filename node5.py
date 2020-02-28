from node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node5',
            'port' : 10005,
            'peers' :{
                    'node1' : ('localhost', 10001),
                    'node2' : ('localhost', 10002),
                    'node3' : ('localhost', 10003),
                    'node4' : ('localhost', 10004)
                }
            }
    node = Node(conf)
    node.run()