import json
from typing import Tuple
from uuid import uuid4


class BaseElement(object):
    def __init__(self, uuid: str = None, name: str = None, **kwargs) -> None:
        self.uuid = uuid or str(uuid4())
        self.name = str(name) if name else None

    def __str__(self):
        return self.name or self.uuid

    def to_serializable(self) -> Tuple[dict, dict]:
        """Returns a dictionary of members with references and a dictionary of referenced objects.

        In subclasses this creates a dictionary with immediately serializable attributes and
        references (uuids) to attributes that are objects and also a second dictionary where said objects are serialized (by deligation).
        
        Serialization
        -------------
        The idea is to collect all attributes of an object that can be serialized immediately and
        to delegate serialization of more complex objects (second dictionary).
        """

        return self.__dict__, {}

    def to_json(self) -> str:
        return json.dumps(self.to_serializable()[0])
