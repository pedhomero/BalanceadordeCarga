from flask import Flask, jsonify
import time

app = Flask(__name__)

INSTANCE_NAME = "servidor3"

@app.route("/")
def index():
    return jsonify({
        "instance": INSTANCE_NAME,
        "time": time.time()
    })

app.run(port=8003)
