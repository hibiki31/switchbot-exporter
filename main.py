import base64
import hashlib
import hmac
import os
import time
import uuid

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

SWITCHBOT_TOKEN = os.environ["SWITCHBOT_TOKEN"]
SWITCHBOT_SECRET = os.environ["SWITCHBOT_SECRET"]
API_HOST = "https://api.switch-bot.com"

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/metric")
def read_root():
    device_id = "70041D7FE4BA"
    res = httpx.get(f"{API_HOST}/v1.1/devices/{device_id}/status", headers=make_header())
    print(res.text)

    return """
# TYPE vm_counter counter
"""


@app.get("/device")
def get_device():
    res = httpx.get(f"{API_HOST}/v1.1/devices", headers=make_header())
    return res.json()


@app.get("/items/{item_id}")
def read_item(item_id: int) -> dict:
    return {"item_id": item_id}


def make_header():
    secret_key = bytes(SWITCHBOT_SECRET, "utf-8")
    time_int = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())

    string_to_sign = bytes(f"{SWITCHBOT_TOKEN}{time_int}{nonce}", "utf-8")
    sign = base64.b64encode(hmac.new(secret_key, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    return {
        "Authorization": SWITCHBOT_TOKEN,
        "sign": sign,
        "t": time_int,
        "nonce": nonce,
        "Content-Type": "application/json; charset=utf-8",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
