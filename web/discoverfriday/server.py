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

    def __eq__(self, other):
        return self.url == other.url


DB: Mapping[str, Mapping[str, str]] = {}


@app.route('/')
def home():

    remote_addr = None
    if "X-Real-IP" in request.headers:
        remote_addr = request.headers["X-Real-IP"]
    else:
        remote_addr = request.remote_addr

    items = []
    if remote_addr in DB:
        items = [(url, name)
                 for url, name in DB[remote_addr].items()]

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

    # So if this lies behind nginx the remote_addr will just
    # be the addr to the nginx reverse proxy
    # but the nginx if it is nice will include the remote ip as a header
    # we check for that first

    remote_addr = None
    if "X-Real-IP" in request.headers:
        remote_addr = request.headers["X-Real-IP"]
    else:
        remote_addr = request.remote_addr

    print("req", req, "db", DB)
    if remote_addr not in DB:
        DB[remote_addr] = {}

    DB[remote_addr][req["url"]] = req["name"]

    return Response(status=200)


app.run(host="0.0.0.0", port="7000")
