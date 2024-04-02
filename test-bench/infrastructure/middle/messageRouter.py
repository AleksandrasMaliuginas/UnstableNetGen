from typing import Callable, Dict
from messaging import Message, MessageType


class MessageRouter:

    def __init__(self, messageTypeToHandler: Dict[MessageType, Callable[[Message], (bytes | None)]]) -> None:
        self.routes = messageTypeToHandler

    def onPacketReceived(self, buffer: bytes):

        message = Message.decode(buffer)

        messageHandler = self.routes.get(message.msgType)
        if messageHandler:
            return messageHandler(message)

        print("Unrecognized message:", message)
