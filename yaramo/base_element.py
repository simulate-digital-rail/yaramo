from typing import Tuple
from uuid import uuid4
import json


class BaseElement(object):
    def __init__(self, uuid: str= None, name: str=None) -> None:
        self.uuid = uuid or str(uuid4())
        self.name = str(name) if name else None

    def __str__(self):
        return self.name or self.uuid

    def to_serializable(self) -> Tuple[dict, dict]:
        """Return a dictionary of members with references and a dictionary of referenced objects.
        """
        return self.__dict__, {}

    def to_json(self) -> str:
        return json.dumps(self.to_serializable())
