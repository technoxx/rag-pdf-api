from fastapi import FastAPI, UploadFile, File
import shutil
import os
from rag import index_pdf, ask_query

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = index_pdf(file_path)
    return result


@app.get("/ask")
def ask(question: str):
    answer = ask_query(question)
    return {
        "question": question,
        "answer": answer
    }