import os
import sys
import PyPDF2

from groq import Groq

#client = Groq(api_key="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")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

resume_pdf = sys.argv[1]

def convert_pdf_to_markdown(resume_pdf):
    # Open the PDF file in read-binary mode
    with open(resume_pdf, "rb") as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the number of pages
        num_pages = len(pdf_reader.pages)

        # Extract text from each page
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            print(text)

    # Convert PDF to Markdown
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Can you convert my resume to markdown? " + text + ".",
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

markdown = convert_pdf_to_markdown(resume_pdf)
print(markdown)
