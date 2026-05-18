#!/usr/bin/env python3
"""
Script de Teste Automatizado - Sistema de Monitorização de Equipamentos
Simula: criação de clientes, equipamentos, registos de temperatura e verificação de alertas
"""

import requests
import json
import time
from datetime import datetime

# ===== CONFIGURAÇÃO =====
API_URL = "http://127.0.0.1:5000"

# ===== DADOS DE TESTE =====
CLIENTES_TESTE = [
    {"nif": "111111111111", "nome": "Cliente Teste A", "localidade": "Lisboa", "zona": "Norte"},
    {"nif": "222222222222", "nome": "Cliente Teste B", "localidade": "Porto", "zona": "Sul"},
    {"nif": "333333333333", "nome": "Cliente Teste C", "localidade": "Covilhã", "zona": "Centro"}
]

def obter_token():
    """Obtém token JWT do servidor"""
    try:
        resp = requests.get(f"{API_URL}/api/gerar-token")
        if resp.status_code == 200:
            return resp.json()['token']
    except:
        pass
    return None

def log(msg, tipo="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {tipo}: {msg}")

def test_listar_equipamentos(headers):
    """Teste: Listar equipamentos (GET /api/equipamentos)"""
    try:
        resp = requests.get(f"{API_URL}/api/equipamentos")
        if resp.status_code == 200:
            dados = resp.json()
            log(f"✓ Listar equipamentos: {len(dados)} encontrados", "OK")
            return dados
        else:
            log(f"✗ Erro ao listar equipamentos: {resp.status_code}", "ERROR")
            return []
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return []

def test_criar_cliente(nif, nome, headers):
    """Teste: Criar cliente (POST /api/cliente)"""
    try:
        payload = {"nif": nif, "nome": nome, "localidade": "Teste"}
        resp = requests.post(f"{API_URL}/api/cliente", json=payload, headers=headers)
        if resp.status_code == 201:
            log(f"✓ Cliente criado: {nif}", "OK")
            return True
        elif resp.status_code == 400:
            log(f"⚠ Cliente já existe: {nif}", "WARN")
            return True
        else:
            log(f"✗ Erro: {resp.status_code} - {resp.json().get('erro')}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return False

def test_criar_equipamento(serie, nif, headers):
    """Teste: Criar equipamento (POST /api/equipamento)"""
    try:
        payload = {"numero_serie": serie, "cliente_nif": nif}
        resp = requests.post(f"{API_URL}/api/equipamento", json=payload, headers=headers)
        if resp.status_code == 201:
            equip_id = resp.json()['id']
            log(f"✓ Equipamento criado: ID={equip_id}", "OK")
            return equip_id
        elif resp.status_code == 400:
            log(f"⚠ Equipamento já existe: {serie}", "WARN")
            return None
        else:
            log(f"✗ Erro: {resp.status_code} - {resp.json().get('erro')}", "ERROR")
            return None
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return None

def test_registar_temperatura(equip_id, temp0, temp1, temp2, headers):
    """Teste: Registar temperatura (POST /temperatura)"""
    try:
        payload = {
            "equipamento_id": equip_id,
            "temp0": temp0,
            "temp1": temp1,
            "temp2": temp2
        }
        resp = requests.post(f"{API_URL}/temperatura", json=payload, headers=headers)
        if resp.status_code == 201:
            log(f"✓ Temperatura registada: {temp0}°C, {temp1}°C, {temp2}°C", "OK")
            return True
        else:
            log(f"✗ Erro: {resp.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return False

def test_listar_alertas(headers):
    """Teste: Listar alertas (GET /api/alertas)"""
    try:
        resp = requests.get(f"{API_URL}/api/alertas", headers=headers)
        if resp.status_code == 200:
            dados = resp.json()
            log(f"✓ Alertas listados: {len(dados)} encontrados", "OK")
            return dados
        else:
            log(f"✗ Erro: {resp.status_code}", "ERROR")
            return []
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return []

def test_mudar_cliente_equipamento(equip_id, novo_nif, headers):
    """Teste: Mudar cliente (PATCH /api/equipamento/<id>)"""
    try:
        payload = {"cliente_nif": novo_nif}
        resp = requests.patch(f"{API_URL}/api/equipamento/{equip_id}", json=payload, headers=headers)
        if resp.status_code == 200:
            log(f"✓ Cliente atualizado para: {novo_nif}", "OK")
            return True
        else:
            log(f"✗ Erro: {resp.status_code} - {resp.json().get('erro')}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return False

def test_obter_equipamento(equip_id):
    """Teste: Obter equipamento (GET /api/equipamento/<id>)"""
    try:
        resp = requests.get(f"{API_URL}/api/equipamento/{equip_id}")
        if resp.status_code == 200:
            dados = resp.json()
            log(f"✓ Equipamento obtido: Série={dados['numero_serie']}", "OK")
            return dados
        else:
            log(f"✗ Erro: {resp.status_code}", "ERROR")
            return None
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return None

def test_apagar_equipamento(equip_id, headers):
    """Teste: Apagar equipamento (DELETE /api/equipamento/<id>)"""
    try:
        resp = requests.delete(f"{API_URL}/api/equipamento/{equip_id}", headers=headers)
        if resp.status_code == 200:
            log(f"✓ Equipamento apagado: ID={equip_id}", "OK")
            return True
        else:
            log(f"✗ Erro: {resp.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ Exceção: {e}", "ERROR")
        return False

def main():
    """Executa suite de testes"""
    log("="*70, "INFO")
    log("SUITE DE TESTES - SISTEMA DE MONITORIZAÇÃO DE EQUIPAMENTOS", "INFO")
    log("="*70, "INFO")

    # Obter token
    token = obter_token()
    if not token:
        log("✗ Erro fatal: Não foi possível obter token", "ERROR")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    log(f"✓ Token obtido: {token[:30]}...", "INFO")
    time.sleep(1)

    test_listar_equipamentos(headers)

    for cliente in CLIENTES_TESTE:
        test_criar_cliente(cliente["nif"], cliente["nome"], headers)
        time.sleep(0.5)

    equipamentos = []
    for i, cliente in enumerate(CLIENTES_TESTE[:2]):
        equip_id = test_criar_equipamento(f"SER_TEST_{i+1}", cliente["nif"], headers)
        if equip_id:
            equipamentos.append(equip_id)
        time.sleep(0.5)

    time.sleep(1)

    if equipamentos:
        equip_id = equipamentos[0]
        test_registar_temperatura(equip_id, 25.5, 26.0, 24.5, headers)
        time.sleep(1)
        test_registar_temperatura(equip_id, 120.0, 25.0, -50.0, headers)
        time.sleep(1)

    test_listar_alertas(headers)

    if equipamentos:
        test_obter_equipamento(equipamentos[0])
        if len(CLIENTES_TESTE) > 2:
            test_mudar_cliente_equipamento(equipamentos[0], CLIENTES_TESTE[2]["nif"], headers)

    if len(equipamentos) > 1:
        test_apagar_equipamento(equipamentos[1], headers)

    log("="*70, "INFO")
    log("FIM DA SUITE DE TESTES", "INFO")
    log("="*70, "INFO")

if __name__ == "__main__":
    main()