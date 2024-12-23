from fastapi import APIRouter, Depends

from domain.chat import chat_schema
from domain.user.user_router import get_current_user
from domain.chat import chat_graph
from models import User


router = APIRouter(
    prefix="/api/chat",
)


@router.post("/req", response_model=chat_schema.ChatReply)
def chat_request(_chat_sender: chat_schema.ChatSender,
                 current_user: User = Depends(get_current_user)):
    # TODO:
    # graph app미리 생성

    return {
        'sender': _chat_sender.sender,
        'message': _chat_sender.message,
        'reply': chat_graph.call_chatbot([("user", _chat_sender.message)])
    }
