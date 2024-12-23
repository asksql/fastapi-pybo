from typing import List
from langchain_teddynote.models import LLMs, get_model_name
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
# from starlette.config import Config
from dotenv import load_dotenv

load_dotenv()

# 모델 이름 설정
MODEL_NAME = get_model_name(LLMs.GPT4)


def call_chatbot(messages: List[BaseMessage]) -> dict:

    # LangChain ChatOpenAI 모델을 Agent 로 변경할 수 있습니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 방송광고판매 시스템의 전문 어시스턴트야."
                "Answer in Korean.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    model = ChatOpenAI(model=MODEL_NAME, temperature=0.6)
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"messages": messages})
