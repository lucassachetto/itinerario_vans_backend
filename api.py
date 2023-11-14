from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
import main

app = FastAPI()

class Addresses(BaseModel):
    orig: list
    dest: list
    steps: list

@app.get("/hello")
async def root():
    return {"message": "Hello World"}

@app.post("/getRoute/")
async def read_item(addresses : Addresses):
    return main.calcula_rota(addresses.orig, addresses.dest, addresses.steps)