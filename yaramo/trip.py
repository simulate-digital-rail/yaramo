
import random
from yaramo.base_element import BaseElement
from yaramo.edge import Edge


class Trip(BaseElement):

    def __init__(self, edges: list[Edge], **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or random.randrange(1000, 10000)
        self.edges = edges

    def get_length(self):
        total_length = 0.0
        for edge in self.edges:
            total_length = total_length + edge.length
        return total_length
