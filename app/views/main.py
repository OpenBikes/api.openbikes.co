from flask import redirect, send_from_directory

from app import app


@app.route('/')
def index():
    return redirect('http://docs.openbikes.apiary.io/', code=302)


@app.route('/favicon.ico', methods=['GET'])
def favicon_ico():
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route('/robots.txt', methods=['GET'])
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')
