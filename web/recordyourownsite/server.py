from flask import Flask
from flask import render_template
from flask import request, Response
import random
import time

ROOT = "recordings"
BASE = "abcdefghijklmnopqrstuvxyz1234567890"

WORDS = [
    "tänd ljuset",
    "släck ljuset",
    "godnatt",
    "godmorgon",
    "friday",
    "status",
    "tänd lampan",
    "släck lampan",
    "blått ljus",
    "rött ljus",
    "grönt ljus",
    "rosa ljus",
    "gult ljus",
    "vitt ljus",
    "vad är klockan",
    "vilken tid är det",
    "stäng av",
    "sätt på",
    "slå på",
    "sätt larm",
    "sätt tidigt larm",
    "sätt sent larm",
    "stoppa larm",
    "sätt timer",
    "hejdå",
    "läggdags"
]


def random_base_part(k):
    return "".join(random.choices(BASE, k=k))


def get_uuid() -> str:
    return f"{random_base_part(5)}-{random_base_part(5)}-{random_base_part(5)}-{random_base_part(5)}"


app = Flask(__name__, template_folder=".")


@app.route('/')
def home():
    return render_template('index.html', keyword=random.choice(WORDS))


@app.route('/recording', methods=["POST"])
def recv_audio_file():
    timestamp = time.time()
    keyword = request.form['keyword'].replace(" ", "_")
    data = request.files['data']
    data.save(f"{ROOT}/{keyword}-{get_uuid()}.wav")

    print(f"reciving audio file: {time.time() - timestamp}")
    return Response(status=200)


@app.route('/next-word')
def next_word():
    return Response(random.choice(WORDS), status=200, content_type="text/plain")


#app.run(host="0.0.0.0", port="8000")
app.run(host="127.0.0.1", port="8000", debug=True)
