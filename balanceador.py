from flask import Flask, jsonify
import requests
import threading

app = Flask(__name__)

# Servidores registrados
SERVERS = [
    {"url": "http://127.0.0.1:8001", "active": True, "connections": 0},
    {"url": "http://127.0.0.1:8002", "active": True, "connections": 0},
    {"url": "http://127.0.0.1:8003", "active": True, "connections": 0},
]

ALGORITHM = "round_robin"  
rr_index = 0
lock = threading.Lock()
timeout = 1 




def pick_server_round_robin():
    global rr_index
    with lock:
        active = [s for s in SERVERS if s["active"]]
        if not active:
            return None
        chosen = active[rr_index % len(active)]
        rr_index += 1
        return chosen


def pick_server_least_conn():
    active = [s for s in SERVERS if s["active"]]
    if not active:
        return None
    return min(active, key=lambda s: s["connections"])


def pick_server():
    if ALGORITHM == "round_robin":
        return pick_server_round_robin()
    else:
        return pick_server_least_conn()




@app.route("/")
def root():
    server = pick_server()

    if server is None:
        return jsonify({"error": "Nenhum servidor disponível"}), 503

    # Incrementa conexões
    server["connections"] += 1

    try:
        r = requests.get(server["url"], timeout=timeout)
        server["connections"] -= 1
        return r.text, r.status_code, r.headers.items()

    except:
        # Marca como inativo se der falha
        server["active"] = False
        server["connections"] -= 1
        return jsonify({"error": "Falha ao acessar " + server["url"]}), 503


@app.route("/status")
def status():
    return jsonify(SERVERS)


@app.route("/set_algorithm/<alg>")
def set_alg(alg):
    global ALGORITHM

    if alg not in ["round_robin", "least_conn"]:
        return "Algoritmo inválido!"

    ALGORITHM = alg
    return f"Algoritmo definido como {alg}"


app.run(port=8080)
