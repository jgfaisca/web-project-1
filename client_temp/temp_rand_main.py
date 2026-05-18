import time
import random
import requests
import sys
import json

TOKEN_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE3Nzk5NzE3MzR9.fGB_kcqGP6phxnALNptSG7SVr9R9hb7f0GIIknqUIys"
URL = "http://127.0.0.1:5000/temperatura"

def gerar_temperaturas(equipamento_id):
    print(f"Iniciando monitorização para equipamento ID: {equipamento_id}")
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
                "Authorization": f"Bearer {TOKEN_JWT}",
                "Content-Type": "application/json"
            }

            resposta = requests.post(URL, json=dados, headers=headers, timeout=5)
            contador += 1
            print(f"[{contador}] Status: {resposta.status_code} | {dados}")

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
