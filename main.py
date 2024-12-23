from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from domain.question import question_router
from domain.answer import answer_router
from domain.user import user_router
from domain.chat import chat_router
from domain.doc import document_router
from domain.sql import sql_router

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}


app.include_router(question_router.router)
app.include_router(answer_router.router)
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(document_router.router)
app.include_router(sql_router.router)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))


@app.get("/")
def index():
    return FileResponse("frontend/dist/index.html")
