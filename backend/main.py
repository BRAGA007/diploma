import asyncio
from fastapi import FastAPI
import telebot
import uvicorn

app = FastAPI()

if __name__=="__main__":
    # loop = asyncio.get_event_loop()
    # loop.create_task(start_polling())




    # async def start_polling():
    uvicorn.run(app, host="localhost", port=9000)
