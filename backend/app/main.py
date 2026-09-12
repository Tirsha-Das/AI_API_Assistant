import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def read_root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
