from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, AnyUrl
from typing import Any
from utils import CoverLetterGenerator
# import pdfplumber
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="/Users/alexmcgraw/Documents/Resumes:Cover Letters:Case_stuff/"), name="static")

class RequiredDocs(BaseModel):
    resume_path: Any
    job_post_url: AnyUrl


class OpenAIKey(BaseModel):
    key: str

@app.put("/apikey")
async def return_key(key: OpenAIKey): 
    return {"message": f"Your API key is {key.key}"}

@app.put("/put_document_locations")
async def return_document_locations(docs: RequiredDocs):
    return{"message": f"Your resume path is {docs.resume_path} and your job post URL is {docs.job_post_url}"}

# @app.put("/generate_cover_letter")
# async def generate_cover_letter(docs: RequiredDocs):
#     clg = CoverLetterGenerator(resume_path=read_item(docs.resume_path),  # docs.resume_path,
#                                job_posting_url=docs.job_post_url)
#     cover_letter = clg.generate_cover_letter()
#     return {"cover_letter": cover_letter}

# @app.get("/static/{file_path:path}")
# async def read_item(file_path: UploadFile=File()):
#     opened_file = pdfplumber.open(file_path)
#     page = opened_file.pages[0]
#     resume = page.extract_text()
#     return FileResponse(resume)

# https://medium.com/@saverio3107/build-a-pdf-text-extractor-with-fastapi-mongodb-50cbae2c2db5
# ^^ Testing link above. Functions "process_pdf_file" and "process_pdf". Test if these work to read in the text itself. 

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    with open(file.filename, 'wb') as f:
        f.write(contents)
    return {"filename": file.read}

# Mount the static files endpoint
# app.mount("/static", StaticFiles(directory="", html=True), name="static")


class Order(BaseModel):
    product: str
    units: int

class Product(BaseModel):
    name: str
    notes: str

@app.get("/ok")
async def ok_endpoint():
    return {"message": "ok"}

@app.get("/hello")
async def hello_endpoint(name: str = 'World'):
    return {"message": f"Hello, {name}!"}

@app.post("/orders")
async def place_order(product: str, units: int):
    return {"message": f"Order for {units} units of {product} placed successfully."}

@app.post("/orders_pydantic")
async def place_order(order: Order):
    return {"message": f"Order for {order.units} units of {order.product} placed successfully."}