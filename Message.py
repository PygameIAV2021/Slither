import cbor

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
        return cbor.dumps({'type': self.type, 'mes': self.mes})

    @staticmethod
    def deserialize(data):
        d = cbor.loads(data)
        return Message(d['type'], d['mes'])