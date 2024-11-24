import os
import sys
import PyPDF2
import requests
import pdfkit
from urllib.request import urlopen
from bs4 import BeautifulSoup
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

resume_pdf = sys.argv[1]
jd_link = sys.argv[2]

def convert_pdf_to_markdown(resume_pdf):
    # Open the PDF file in read-binary mode
    with open(resume_pdf, "rb") as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Get the number of pages
        num_pages = len(pdf_reader.pages)
        # Extract text from each page
        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = text + page.extract_text()
    # Convert PDF to Markdown
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Can you convert my resume to markdown? " + text + ".",
            }
        ],
        #model="llama3-8b-8192",
        #model="llama-3.2-3b-preview",
        model="llama-3.1-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def adapt_markdown(markdown, jd):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "I have a resume in Markdown format and a job description. Please adapt my resume to better align with the job description. Ensure the language reflects the key skills and responsibilities from the job posting while retaining the structure of my resume. Tailor bullet points to demonstrate direct relevance to the job requirements. Highlight transferable skills and experience that make me an excellent candidate. And do not add your note in the output. \n Here is my resume:\n " + markdown + "\n\n Here is the job description:\n" + jd + ".",
            }
        ],
        #model="llama3-8b-8192",
        #model="llama-3.2-3b-preview",
        model="llama-3.1-70b-versatile",
        #temperature=1,
    )
    return chat_completion.choices[0].message.content

def get_jd(jd_link):
    html = urlopen(jd_link).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def convert_markdown_to_html(adapted_markdown):
    # Convert Markdown to html
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Can you convert resume (markdown) to html? \n" + adapted_markdown + ".",
            }
        ],
        #model="llama3-8b-8192",
        #model="llama-3.2-3b-preview",
        model="llama-3.1-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def convert_html_to_pdf(html):
    # Convert Markdown to html
    pdfkit.from_string(html, 'output_resume.pdf')

markdown = convert_pdf_to_markdown(resume_pdf)
jd = get_jd(jd_link)
adapted_markdown = adapt_markdown(markdown, jd)
html = convert_markdown_to_html(adapted_markdown)
convert_html_to_pdf(html)
print("Adapted Resume PDF Genaration Successful.")
