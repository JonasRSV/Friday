from typing import Mapping, Set
from flask import Flask
from flask import render_template, send_from_directory
from flask import request, Response
import random
import time

app = Flask(__name__, template_folder=".", static_url_path='')


class Friday:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __hash__(self):
        return hash(self.url)


DB: Mapping[str, Set[Friday]] = {}


@app.route('/')
def home():

    items = []
    if request.remote_addr in DB:
        items = [(friday.url, friday.name)
                 for friday in DB[request.remote_addr]]

    return render_template('index.html', items=items)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/ping', methods=["PUT"])
def ping():
    req = request.json
    # This server will be running in dev-mode
    # So all quests is executed serially
    # No danger of race conditions
    if request.remote_addr in DB:
        DB[request.remote_addr].add(Friday(req["name"], req["url"]))
    else:
        DB[request.remote_addr] = set([Friday(req["name"], req["url"])])

    return Response(status=200)


app.run(host="0.0.0.0", port="7000")
