from enum import Enum

import simplejson as json


class EnumEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return str(o)
        return super().default(o)
