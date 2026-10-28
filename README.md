# \# Grounded Visual Resume

# 

# A one-page visual resume with a built-in chat assistant that answers recruiter questions \*\*only from facts I have approved\*\*. If the answer is not in my resume, it says so instead of guessing.

# 

# Built with Python and Flask. Target role: \*\*Python Backend Developer\*\*.

# 

# \## Why this project

# 

# AI assistants can sound confident while making things up. On a resume, one invented claim can cost an interview. This project shows a safer pattern:

# 

# \- One approved file (`data/resume.json`) is the single source of truth.

# \- The chat assistant can only repeat facts from that file, and shows which section each answer came from.

# \- Anything it cannot find gets an honest "I don't have verified information about that."

# \- A fact-check script lists every claim before the site goes public.

# 

# \## Features

# 

# \- Responsive visual resume: hero section, key points, projects, experience timeline, skills and education

# \- Profile shown as a live "API response" card, with hover and scroll effects

# \- Grounded chat assistant with source labels on every answer

# \- Unknown terms are named, never guessed (for example, "Her resume does not mention: kubernetes")

# \- Placeholder text (`TODO`) is hidden from both the page and the chat until verified

# \- Resume PDF download button (appears when the PDF is added)

# \- Fact-check script that can compare claims against the resume PDF

# \- Automated tests for grounding, refusals and routes

# 

# \## Tech stack

# 

# Python, Flask, Jinja2 templates, vanilla JavaScript, HTML and CSS, unittest, Gunicorn for deployment.

# 

# \## How the grounding works

# 

# 1\. `data/resume.json` holds every fact, grouped by section.

# 2\. `grounded.py` flattens it into small citable facts and skips anything still marked `TODO`.

# 3\. A question is matched to facts with keyword scoring and simple synonyms.

# 4\. Matching facts are returned word for word, with their source labels.

# 5\. If nothing matches, or the question is about something not in the file, the assistant says it does not know.

# 

# No language model is called at answer time, so the assistant cannot invent new claims.

# 

# \## Run it locally

# 

# ```bash

# pip install -r requirements.txt

# python app.py

# ```

# 

# Open http://127.0.0.1:5000

# 

# \## Test it

# 

# ```bash

# python -m unittest -v

# ```

# 

# \## Fact-check before publishing

# 

# ```bash

# pip install pypdf

# python factcheck.py --pdf static/Roma\_Singh\_Resume.pdf

# ```

# 

# The script lists every claim and every unfinished `TODO`, and flags terms that do not appear in the resume PDF.

# 

# \## Project structure

# 

# ```

# app.py            Flask routes: page, chat API, resume download

# grounded.py       Fact extraction and grounded question answering

# factcheck.py      Pre-publish claim checker

# test\_app.py       Automated tests

# data/resume.json  Approved resume content (single source of truth)

# templates/        Page template

# static/           Styles, chat and visual-effect scripts

# ```

# 

# \## Deploy

# 

# Works on Render or PythonAnywhere (both have free plans).

# Render: build command `pip install -r requirements.txt`, start command `gunicorn app:app`.

# 

# \## Built with AI assistance

# 

# I built this project with AI assistance (Claude) and then reviewed, ran, tested and customized it myself. All resume content is mine and is checked against my own resume before publishing.

# 

# \## Author

# 

# Roma Singh, Python Backend Developer.

