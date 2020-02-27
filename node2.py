from node import Node

if __name__ == '__main__':
    conf = {
            'id' : 'node2',
            'port' : 10002,
            'peers' :[
                    ('localhost', 10001),
                    ('localhost', 10003)
                    ]
            }
    node = Node(conf)
    node.run()