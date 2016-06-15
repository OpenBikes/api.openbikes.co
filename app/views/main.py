from flask import redirect

from app import app


@app.route('/')
def index():
    return redirect('http://docs.openbikes.apiary.io/', code=302)
