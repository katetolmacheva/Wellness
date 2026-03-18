from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Role = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str = Field(min_length=1)


class ChatIn(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1)


class TitleIn(BaseModel):
    text: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"ok": True, "mode": "mock"}


@app.post("/generate-title")
def generate_title(body: TitleIn):
    text = body.text.strip()
    title = text[:20].strip() or "Новый чат"
    return {"title": title}


@app.post("/chat")
def chat(body: ChatIn):
    last = body.messages[-1].content.strip()
    return {
        "answer": f"Тестовый ответ бота: {last}",
        "reasoning": None,
        "sources": [],
    }