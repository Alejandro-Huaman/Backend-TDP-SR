from fastapi import FastAPI
from routes.recommendation import recommendation

app = FastAPI()

app.include_router(recommendation)