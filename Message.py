import json

from enum import Enum

class Command(str, Enum):
    HelloServer = "Hs",
    HelloClient = "Hc",



class Message:
    def __init__(self, name, command: Command, mes):
        self.name = name
        self.command = command
        self.mes = mes

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2).encode('utf8')

    @staticmethod
    def deserialize(string: str):
        return json.loads(string, object_hook=lambda d: Message(**d))