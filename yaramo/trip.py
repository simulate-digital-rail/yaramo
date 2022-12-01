import uuid
import random
from yaramo.edge import Edge


class Trip(object):

    def __init__(self, edges: list[Edge], name: str = None, uuid: str = None):
        self.trip_uuid = uuid or str(uuid.uuid4())
        self.trip_name = name if name is not None else random.randrange(1000, 10000)
        self.edges = edges

    def get_length(self):
        total_length = 0.0
        for edge in self.edges:
            total_length = total_length + edge.length()
        return total_length
