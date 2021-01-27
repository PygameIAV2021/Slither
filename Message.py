import cbor  # concise binary object representation, used to send minimum of bytes
from enum import Enum


class MesType(str, Enum):
    """The message types of the protocol"""

    HelloServer = 0
    HelloClient = 1
    Input = 2
    Position = 3
    YouAreDeath = 4
    NewEnemy = 5


class Message:
    """messages transferred between the client and server"""

    def __init__(self, type: MesType, mes):
        self.type = type
        self.mes = mes

    def serialize(self) -> bytes:
        """serialize this message-object to bytes"""

        return cbor.dumps({'t': self.type, 'm': self.mes})

    @staticmethod
    def deserialize(data: dir):
        """returns a message object, generated by the data"""

        d = cbor.loads(data)
        return Message(d['t'], d['m'])


class ConnectionCodes:
    serverFull = 3001
    clientClosedByUser = 3002
    youWereKilled = 3003
    protocolError = 3004
