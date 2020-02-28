from node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node2',
            'port' : 10002,
            'peers' :{
                    'node1' : ('localhost', 10001),
                    'node3' : ('localhost', 10003)
                }
            }
    node = Node(conf)
    node.run()