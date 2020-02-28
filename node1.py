from node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node1',
            'port' : 10001,
            'peers' :{
                    'node2' : ('localhost', 10002),
                    'node3' : ('localhost', 10003)
                }
            }
    node = Node(conf)
    node.run()