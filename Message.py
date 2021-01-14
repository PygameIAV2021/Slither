import json

from enum import Enum


class MesType(str, Enum):
    HelloServer = "HelloServer",
    HelloClient = "HelloClient",
    Input = "Input"
    Position = "Pos"


class Message:

    def __init__(self, type: MesType, mes):
        self.type = type
        self.mes = mes

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2).encode('utf8')

    @staticmethod
    def deserialize(string: str):
        return json.loads(string, object_hook=lambda d: Message(**d))