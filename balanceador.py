import os
import requests
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Lista de servidores backend
SERVERS = [
    {"url": "http://127.0.0.1:8001", "up": True, "connections": 0},
    {"url": "http://127.0.0.1:8002", "up": True, "connections": 0},
    {"url": "http://127.0.0.1:8003", "up": True, "connections": 0},
]

# ÍNDICE para Round Robin
rr_index = 0

# Escolha do algoritmo por variável de ambiente
ALGORITHM = os.getenv("ALGORITMO", "ROUND_ROBIN").upper()

print(f"[BALANCEADOR] Algoritmo selecionado: {ALGORITHM}")

# -----------------------------
# Função para checar se servidores estão vivos
# -----------------------------
def health_check():
    for server in SERVERS:
        try:
            requests.get(server["url"], timeout=0.5)
            if not server["up"]:
                print(f"[RECUPERADO] {server['url']} voltou!")
            server["up"] = True
        except:
            if server["up"]:
                print(f"[CAIU] {server['url']} ficou indisponível!")
            server["up"] = False


# -----------------------------
# Algoritmo: Round Robin
# -----------------------------
def get_server_round_robin():
    global rr_index
    alive = [s for s in SERVERS if s["up"]]

    if not alive:
        return None

    server = alive[rr_index % len(alive)]
    rr_index += 1
    return server


# -----------------------------
# Algoritmo: Least Connections
# -----------------------------
def get_server_least_connections():
    alive = [s for s in SERVERS if s["up"]]

    if not alive:
        return None

    # escolhe o servidor com MENOS conexões
    return min(alive, key=lambda s: s["connections"])


# -----------------------------
# Rota principal do balanceador
# -----------------------------
@app.route("/")
def balancear():
    health_check()

    # Seleciona algoritmo
    if ALGORITHM == "LEAST_CONNECTIONS":
        server = get_server_least_connections()
    else:
        server = get_server_round_robin()

    if not server:
        return jsonify({"erro": "Nenhum servidor disponível"}), 503

    # Incrementa conexões ativas
    server["connections"] += 1

    print(f"[REQUISIÇÃO] Enviando para {server['url']}  | conexões: {server['connections']}")

    try:
        response = requests.get(server["url"], timeout=2)
        data = response.json()
    except:
        server["up"] = False
        print(f"[ERRO] {server['url']} falhou durante requisição")
        server["connections"] -= 1
        return jsonify({"erro": "Falha ao conectar ao servidor"}), 503

    # Libera a conexão
    server["connections"] -= 1

    return jsonify({
        "balanceador": "ok",
        "algoritmo": ALGORITHM,
        "resposta_do_servidor": data
    })


# -----------------------------
# Inicia o balanceador
# -----------------------------
if __name__ == "__main__":
    print("[BALANCEADOR] Rodando em http://127.0.0.1:8080")
    app.run(port=8080)
