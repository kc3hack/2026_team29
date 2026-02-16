from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello form FastAPI"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
