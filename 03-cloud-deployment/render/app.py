from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Agent is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(data: dict):
    question = data.get("question", "")
    return {
        "question": question,
        "answer": f"Bạn vừa hỏi: {question}"
    }