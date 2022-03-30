from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

class Graph(object):
    def __init__(self, ip, port):
        self.g = None
        self.ip = ip
        self.port = port

    def connect_janusgraph(self):
        address = 'ws://{}:{}/gremlin'.format(self.ip, self.port)
        try:
            connection = DriverRemoteConnection(address, 'g')
            g = traversal().withRemote(connection)
            self.g = g
            print("janusgraph connected at {}".format(address))
        except:
            print("Cannot connect.")
            return False
        return True

    def disconnect_janusgraph(self):
        try:
            self.g.closed()
            print("disconnected.")
        except:
            print("disconnecting error")

    def add_vertex(self, label , prop):
        """ args = (g, label, prop)"""
        n = self.g.addV(label)
        for k, v in prop.items():
            n.property(k ,v)

        print(f"add vertex {label}, {prop}")
        print(n.next())
        return True
