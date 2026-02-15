#------------------------------------------------------
# STANDARD PYTHON LIBRARIES (Built-in)
#------------------------------------------------------
#Enable asynchronous programing to handle multples concurrent request avoiding block
import asyncio

#Enable a way to interact with the Operating System such as reading environment variables
import os

#Enable random numbers or selecting random elements from a list (we will use that to simulate the LLM's freatures such as time response)
import random

#------------------------------------------------------
# THIRD-PARTY FRAMEWORKS AND TOOLS (Installation requires via requirements.txt)
#------------------------------------------------------
#FastAPI is the core web framework / HTTPException is used to return error responses such as 404
from fastapi import FastAPI, HTTPException

#Middleware to manage Cross-Origin resource sharing (cors), allows a channel between frontend and backend to comunnicate (allows frontend to talk to backend)
from fastapi.middleware.cors import CORSMiddleware

#BaseModel is used to define data schemas and ensure incoming request data is validated correctly
from pydantic import BaseModel

#Loads environment variables from ".env" file to keep sensitive credentials (API Keys) secure.
from dotenv import load_dotenv