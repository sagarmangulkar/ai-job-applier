# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Problem Statement

Create a standalone web-app UI to replace the current CLI script. Users should be able to upload a resume and provide a job description through a browser interface, trigger the tailoring pipeline, and download the resulting PDF — without touching the command line.

## Project Overview

AI-powered tool that automatically adapts a resume PDF to a specific job description. Takes a resume PDF and a job posting URL as input, produces a tailored PDF resume as output.

## Running the Project

```bash
# Install Python dependencies
pip install PyPDF2 requests pdfkit beautifulsoup4 groq

# Install system dependency (required by pdfkit)
brew install --cask wkhtmltopdf  # macOS
# apt-get install wkhtmltopdf   # Ubuntu

# Set required env var
export GROQ_API_KEY="your_api_key_here"

# Run
python resume_modifier.py path/to/resume.pdf "https://job-posting-url.com"
```

Output is written to `output_resume.pdf` in the current directory.

## Architecture

The entire project is a single script: `resume_modifier.py`. It implements a sequential pipeline:

1. **PDF → Markdown** (`convert_pdf_to_markdown`) — reads the resume PDF via PyPDF2, then uses the Groq API to convert raw extracted text into clean Markdown
2. **Fetch JD** (`get_jd`) — scrapes the job posting URL with BeautifulSoup, stripping scripts/styles to get plain text
3. **Adapt resume** (`adapt_markdown`) — calls Groq API with both the Markdown resume and job description to produce a tailored Markdown resume
4. **Markdown → HTML** (`convert_markdown_to_html`) — Groq API converts the Markdown to HTML with inline CSS styling
5. **HTML → PDF** (`convert_html_to_pdf`) — pdfkit/wkhtmltopdf renders the final PDF

## Collaboration Rules

- **Code change explanations**: Before every code change, provide a one-liner explanation of what is being changed and why.

## Key Details

- **LLM**: Groq API using `llama-3.2-3b-preview`. Prior models `llama3-8b-8192` and `llama-3.1-70b-versatile` are commented out in the file if you want to switch.
- **Auth**: `GROQ_API_KEY` environment variable must be set; the Groq client reads it automatically.
- **No requirements.txt** exists — dependencies are listed above and must be installed manually.
- **No tests or linting** configuration exists in this project.
