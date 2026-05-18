import time
import random
import requests
import sys
import json

URL_BASE = "http://127.0.0.1:5000"

def obter_token():
    """Gera um novo token JWT"""
    try:
        resp = requests.get(f"{URL_BASE}/api/gerar-token", timeout=5)
        if resp.status_code == 200:
            return resp.json()['token']
    except:
        pass
    return None

def gerar_temperaturas(equipamento_id):
    print(f"Iniciando monitorização para equipamento ID: {equipamento_id}")

    # Obter token
    token = obter_token()
    if not token:
        print("Erro: Não foi possível obter token")
        return

    print(f"Token obtido: {token[:20]}...\n")
    contador = 0

    while True:
        try:
            dados = {
                "equipamento_id": equipamento_id,
                "temp0": round(random.uniform(-40.0, 110.0), 2),
                "temp1": round(random.uniform(-40.0, 110.0), 2),
                "temp2": round(random.uniform(-40.0, 110.0), 2)
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            resposta = requests.post(f"{URL_BASE}/temperatura", json=dados, headers=headers, timeout=5)
            contador += 1
            print(f"[{contador}] Status: {resposta.status_code} | Temp0: {dados['temp0']}°C | Temp1: {dados['temp1']}°C | Temp2: {dados['temp2']}°C")

            if resposta.status_code != 201:
                print(f"    Resposta: {resposta.text}")
        except Exception as erro:
            print(f"[{contador}] Erro: {erro}")

        time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            equip_id = int(sys.argv[1])
            gerar_temperaturas(equip_id)
        except ValueError:
            print("Erro: Forneça um ID numérico válido")
            print("Uso: python temp_rand_main.py <equipamento_id>")
    else:
        print("Uso: python temp_rand_main.py <equipamento_id>")

