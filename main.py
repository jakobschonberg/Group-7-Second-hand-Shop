from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from typing import Annotated, Literal
from dotenv import load_dotenv
from pathlib import Path as pathlibPath
from os import getenv, path as osPath
from fastapi import Header, Depends
from json import load, dump

app = FastAPI()

