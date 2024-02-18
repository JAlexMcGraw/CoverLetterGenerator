from fastapi import FastAPI, File, UploadFile, Response, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyUrl, HttpUrl
import requests
from io import BytesIO
from typing import Annotated
from utils import CoverLetterGenerator
import PyPDF2   
import os


app = FastAPI()

class RequiredDocs(BaseModel):
    resume: UploadFile = File(...)
    job_post_url: HttpUrl


class OpenAIKey(BaseModel):
    key: Annotated[str, Form()]

@app.put("/apikey")
async def return_key(key: OpenAIKey): 
    return {"message": f"Your API key is {key.key}"}

@app.put("/put_document_locations")
async def return_document_locations(docs: RequiredDocs):
    return{"message": f"Your resume path is {docs.resume_path} and your job post URL is {docs.job_post_url}"}

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.post("/get_uploadfile/")
async def get_create_upload_file(file: UploadFile):
    contents = await file.read()
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(contents, headers=headers, media_type="application/pdf")

@app.post("/uploadfile_test/")
async def create_upload_file_test(file: UploadFile):
    contents = await file.read()
    async with open(file.filename, 'wb') as f:
        f.write(contents)
    
    file.close()
    return {"message": f"File {file.filename} uploaded successfully",
            "content": f"{contents}"}

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

    return {"status": "Processing completed",
            "text": text}

@app.post("/generate_cover_letter/")
async def cover_letter_generate(openai_api_key: Annotated[str, Form()], job_post_url: AnyUrl, resume: UploadFile = File(...)):

    os.environ['OPENAI_API_KEY'] = openai_api_key
    resume = await process_pdf(resume.filename, is_local_file=True)

    cl = CoverLetterGenerator(resume=resume['text'],
                              job_posting_url=job_post_url.unicode_string())
    
    cover_letter = cl.generate_cover_letter()

    return cover_letter
