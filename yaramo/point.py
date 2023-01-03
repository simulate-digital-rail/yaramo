from yaramo.node import Node


class Point(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_through_node(self, node: Node):
        if node not in self.connected_nodes:
            raise Exception('The through node is not in connected nodes!')

        if node.uuid == self.connected_on_head.uuid:
            raise Exception('The through node cannot be connected on the node head!')
        
        self.through_node = node
        self.diverting_node = self.connected_on_left if node.uuid != self.connected_on_left.uuid else self.connected_on_right
