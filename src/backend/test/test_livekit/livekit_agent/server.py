# server.py
import os
from livekit import api
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/getToken")
async def get_token():
    token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
        .with_identity("identity") \
        .with_name("my name") \
        .with_grants(api.VideoGrants(
        room_join=True,
        room="my-room",
    ))
    return {"token": token.to_jwt()}