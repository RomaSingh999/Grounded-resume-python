# Roma's Grounded Visual Resume (Python / Flask)

A one-page resume site with a chat assistant that answers only from data/resume.json.
No AI model is called, so it cannot make anything up.

## Run it
    pip install -r requirements.txt
    python app.py            # open http://127.0.0.1:5000

## Fill it in (do this first)
1. Open data/resume.json and replace every "TODO: ..." with a real, provable fact.
   TODO items are hidden from the site and chat until you do.
2. Copy your resume PDF to static/Roma_Singh_Resume.pdf (the download button appears automatically).
3. Run the fact-check, read every line, and fix anything untrue:
       python factcheck.py --pdf static/Roma_Singh_Resume.pdf   (needs: pip install pypdf)
4. Run the tests:
       python -m unittest -v

## Publish (free)
PythonAnywhere: upload the folder, create a Flask web app, point WSGI to `from app import app as application`.
Render: new Web Service, build `pip install -r requirements.txt`, start `gunicorn app:app`.
Put the final link on your applications.

## How the "grounding" works
- resume.json is the only source. grounded.py flattens it into small facts.
- A question is matched to facts by keyword scoring. Top facts are returned word for word.
- If nothing matches, it says "I don't have that on Roma's resume." Unknown terms are named, never guessed.
