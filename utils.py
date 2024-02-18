import openai
# import pdfplumber
from pydantic import BaseModel
import re
# from dotenv import load_dotenv

# load_dotenv()


from typing import ClassVar, Optional


######
# From the guide for testing
def generate_description(input):
    messages = [
        {"role": "user",
         "content": """As a Product Description Generator, Generate multi paragraph rich text product description with emojis from the information provided to you' \n"""},
    ]

    messages.append({"role": "user", "content": f"{input}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = completion.choices[0].message.content
    return reply
######

class CoverLetterGenerator(BaseModel):

    resume: str
    job_posting_url:str
    default_sys_prompt: ClassVar[str]="""You are a job application assistant. You are to write a cover letter by using the supplied resume, which will come after 'RESUME:', and using the supplied job posting, which
            will come after 'JOB POSTING:'. The resume will be split into different sections in a list, with order of importance descending; the most important section will come first, and least important section coming last.
            Make sure that experiences from the resume tie back to specific points from the job posting.
            Structure the cover letter with an intro that states clearly in your opening sentence the purpose for your letter and a brief professional introduction, 
            specifies why you are interested in that specific position and organization, and provides an overview of the main strengths and skills you will bring to the role.
            For the body of the letter (1-2 paragraphs), cite a couple of examples from your experience that support your ability to be successful in the position,
            try not to simply repeat your resume in paragraph form, complement your resume by offering a little more detail about key experiences, and
            discuss what skills you have developed and connect these back to the target role.
            For the closing paragraph, restate succinctly your interest in the role and why you are a good candidate and thank the reader for their time and consideration.
            Address the cover letter with 'Dear Hiring Manager', and finish the letter with 'Sincerely, \n [YOUR NAME HERE]'
            do not exceed a page in length and do not make any information up.
            """
    # default_user_prompt: ClassVar[str]=f"RESUME: {split_resume_no_header}\n-----\nJOB POSTING: {job_doc}"
    default_user_prompt: str = ""

    def __init__(self, resume: str, job_posting_url: str):
        super().__init__(resume=resume, job_posting_url=job_posting_url)
        self.set_default_user_prompt()

    def set_default_user_prompt(self):
        split_resume_no_header = self._split_resume_into_list()
        job_doc = self._load_job_listing_text()
        self.default_user_prompt = f"RESUME: {split_resume_no_header}\n-----\nJOB POSTING: {job_doc}"

    
    # def _read_resume(self) -> str:
    #     import pdfplumber 

    #     read_in_resume = pdfplumber.open(self.resume_path)
    #     pages = read_in_resume.pages[0]
    #     resume = pages.extract_text()

    #     return resume
    
    def _split_resume_into_list(self) -> list:

        # resume = self._read_resume()
        # Define a regular expression pattern to match all upper case words
        header_pattern = re.compile(r'\n\b[A-Z]+\b')

        # Find all matches of the pattern in the input string
        header_matches = header_pattern.finditer(self.resume)

        # Extract the indices of the matches
        header_indices = [match.start() for match in header_matches]

        # Add the start and end indices of the string to mark the boundaries
        header_indices = [-1] + header_indices + [len(self.resume)]

        # Split the string based on the identified header indices
        result_parts = [self.resume[header_indices[i] + 1:header_indices[i + 1]].strip() for i in range(len(header_indices) - 1)]

        return result_parts[1:]
    
    def _load_job_listing_html(self) -> str:
        from langchain.document_loaders import SeleniumURLLoader

        web_doc = SeleniumURLLoader([self.job_posting_url]).load()

        return web_doc
    
    def _load_job_listing_text(self) -> str:
        from bs4 import BeautifulSoup

        html = self._load_job_listing_html()
        soup = BeautifulSoup(html[0].page_content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        
        return text_content
    
    def generate_cover_letter(self, temperature: float = 0.7) -> str:
        from openai import OpenAI

        split_resume_no_header = self._split_resume_into_list()
        job_doc = self._load_job_listing_text()

        body_messages = [
            {
                "role":"system",
                "content":self.default_sys_prompt
            },
            {
                "role":"user",
                "content":self.default_user_prompt
            }
        ]

        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=body_messages,
            temperature=temperature
        )

        return response.choices[0].message.content
