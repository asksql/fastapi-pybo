from pydantic import BaseModel


class ChatSender(BaseModel):
    sender: str
    message: str


class ChatReply(ChatSender):
    reply: str
