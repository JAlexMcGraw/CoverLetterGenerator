from fastapi import FastAPI, Depends, File, UploadFile, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, AnyUrl
# from fpdf2 import FPDF
from typing import Any
from utils import CoverLetterGenerator
# import pdfplumber
import os
import io

app = FastAPI()

# app.mount("/static", StaticFiles(directory="/Users/alexmcgraw/Documents/Resumes:Cover Letters:Case_stuff/"), name="static")

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

# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     contents = await file.read()
#     # results = []
#     # async with file.file as f:
#     #     async for line in io.TextIOWrapper(f, encoding='utf-8'):
#     #         results.append(len(line))

#     # return results
#     # with open(file.filename, 'wb') as f:
#     #     f.write(contents)
#     return {"filename": file.filename,
#             "content": contents}

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename,
            "file": file.file}

@app.post("/get_uploadfile/")
async def get_create_upload_file(file: UploadFile):
    contents = await file.read()
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(contents, headers=headers, media_type="application/pdf")

# def create_PDF(text):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font('helvetica', 'B', 16)
#     pdf.cell(10, 30, text)
#     return pdf.output()

    
# @app.get('/')
# def get_pdf():
#     out = create_PDF('Hello World!')
#     headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
#     return Response(bytes(out, encoding="latin-1"), headers=headers, media_type='application/pdf')

# The following code is based on this stackoverflow link "https://stackoverflow.com/questions/76195784/how-to-generate-and-return-a-pdf-file-from-in-memory-buffer-using-fastapi"
# def create_pdf()
@app.post("/uploadfile_test/")
async def create_upload_file_test(file: UploadFile):
    contents = await file.read()
    async with open(file.filename, 'wb') as f:
        f.write(contents)
    
    file.close()
    return {"message": f"File {file.filename} uploaded successfully",
            "content": f"{contents}"}

# Following code is from this article "https://medium.com/@saverio3107/build-a-pdf-text-extractor-with-fastapi-mongodb-50cbae2c2db5"
from io import BytesIO
import requests
@app.post("/process_pdf_file/")
async def process_pdf_file(file: UploadFile = File(...)):
    # Save file locally for processing
    contents = await file.read()
    with open(file.filename, 'wb') as f:
        f.write(contents)
    
    # Process saved file
    return await process_pdf(file.filename, is_local_file=True)

async def process_pdf(pdf_source, is_local_file=False):
    # Process the PDF from URL or local file
    file = BytesIO(requests.get(pdf_source).content) if not is_local_file else open(pdf_source, 'rb')

    # Extract text from PDF
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page).extractText()
    
    if is_local_file:
        file.close()

    return {"status": "Processing completed"}
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