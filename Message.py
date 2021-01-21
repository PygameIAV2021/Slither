import cbor

from enum import Enum


class MesType(str, Enum):
    HelloServer = 0
    HelloClient = 1
    Input = 2
    Position = 3


class Message:

    def __init__(self, type: MesType, mes):
        self.type = type
        self.mes = mes

    def serialize(self):
        return cbor.dumps({'t': self.type, 'm': self.mes})

    @staticmethod
    def deserialize(data):
        d = cbor.loads(data)
        return Message(d['t'], d['m'])
