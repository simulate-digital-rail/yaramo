
from uuid import uuid4


class BaseElement(object):
    def __init__(self, uuid: str= None, name: str=None) -> None:
        self.uuid = uuid or str(uuid4())
        self.name = str(name) if name else None

    def __str__(self):
        return self.name or self.uuid

class TrackElement(BaseElement):
    def __init__(self, maximum_speed: int = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.maximum_speed = maximum_speed
