
from uuid import uuid4


class BaseElement(object):
    def __init__(self, uuid: str= None, name: str=None) -> None:
        self.uuid = uuid or str(uuid4())
        self.name = name
