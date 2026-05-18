import sqlite3
import jwt
import threading
import json
from functools import wraps
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flasgger import Swagger

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['JSON_SORT_KEYS'] = False
Swagger(app)

SECRET_KEY = "chave_secreta_projeto"
DB_PATH = 'db/test_database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def verificar_jwt(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"erro": "Token em falta"}), 401
        try:
            token = token.split(" ")[1]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"erro": "Token invalido"}), 401
        return f(*args, **kwargs)
    return decorador

def processar_alertas_assincrono(equipamento_id, temp0, temp1, temp2):
    def tarefa():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT Sensor_tipo, Min_val, Max_val FROM limites_sensores")
            limites = {linha['Sensor_tipo']: (linha['Min_val'], linha['Max_val']) for linha in cursor.fetchall()}

            leituras = {'temp0': temp0, 'temp1': temp1, 'temp2': temp2}

            for sensor, valor in leituras.items():
                if valor is not None and sensor in limites:
                    min_v, max_v = limites[sensor]
                    if float(valor) < float(min_v) or float(valor) > float(max_v):
                        cursor.execute("""
                            INSERT INTO alertas_sensores (Equipamento_ID, Sensor_tipo, Leitura, Mensagem)
                            VALUES (?, ?, ?, ?)
                        """, (equipamento_id, sensor, float(valor), "Anomalia detetada"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao processar alerta: {e}")

    thread = threading.Thread(target=tarefa)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ==================== EQUIPAMENTOS ====================

@app.route('/api/equipamentos', methods=['GET'])
def listar_equipamentos():
    """
    Lista todos os equipamentos
    ---
    responses:
      200:
        description: Lista de equipamentos
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.ID, e.NumeroSerie, pe.Cliente_NIF, pe.DataInicio
            FROM Equipamento e
            LEFT JOIN PropriedadeEquipamento pe ON e.ID = pe.Equipamento_ID AND pe.DataFim IS NULL
            ORDER BY e.ID DESC
        """)
        equipamentos = cursor.fetchall()
        conn.close()

        lista = []
        for equip in equipamentos:
            lista.append({
                "id": equip['ID'],
                "numero_serie": equip['NumeroSerie'],
                "cliente_nif": equip['Cliente_NIF'],
                "data_inicio": equip['DataInicio']
            })
        return jsonify(lista), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/equipamento/<int:id>', methods=['GET'])
def obter_equipamento(id):
    """
    Obter equipamento por ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
    responses:
      200:
        description: Dados do equipamento
      404:
        description: Equipamento não encontrado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.ID, e.NumeroSerie, pe.Cliente_NIF, pe.DataInicio
            FROM Equipamento e
            LEFT JOIN PropriedadeEquipamento pe ON e.ID = pe.Equipamento_ID AND pe.DataFim IS NULL
            WHERE e.ID = ?
        """, (id,))
        equip = cursor.fetchone()
        conn.close()

        if not equip:
            return jsonify({"erro": "Equipamento não encontrado"}), 404

        return jsonify({
            "id": equip['ID'],
            "numero_serie": equip['NumeroSerie'],
            "cliente_nif": equip['Cliente_NIF'],
            "data_inicio": equip['DataInicio']
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/equipamento', methods=['POST'])
@verificar_jwt
def criar_equipamento():
    """
    Criar novo equipamento
    ---
    parameters:
      - in: body
        schema:
          type: object
          required:
            - numero_serie
            - cliente_nif
          properties:
            numero_serie:
              type: string
            cliente_nif:
              type: string
    responses:
      201:
        description: Equipamento criado
      400:
        description: Dados inválidos
      404:
        description: Cliente não encontrado
    """
    dados = request.get_json()

    if not dados or not dados.get('numero_serie') or not dados.get('cliente_nif'):
        return jsonify({"erro": "Campos obrigatórios: numero_serie, cliente_nif"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT NIF FROM Cliente WHERE NIF = ?", (dados['cliente_nif'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Cliente não encontrado"}), 404

        cursor.execute("INSERT INTO Equipamento (NumeroSerie) VALUES (?)", (dados['numero_serie'],))
        equip_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO PropriedadeEquipamento (Equipamento_ID, Cliente_NIF) VALUES (?, ?)",
            (equip_id, dados['cliente_nif'])
        )
        conn.commit()
        conn.close()

        return jsonify({"id": equip_id, "mensagem": "Equipamento criado"}), 201
    except sqlite3.IntegrityError as e:
        if 'UNIQUE' in str(e):
            return jsonify({"erro": "Número de série já existe"}), 400
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/equipamento/<int:id>', methods=['DELETE'])
@verificar_jwt
def apagar_equipamento(id):
    """
    Apagar equipamento
    ---
    parameters:
      - name: id
        in: path
        type: integer
    security:
      - Bearer: []
    responses:
      200:
        description: Equipamento apagado
      404:
        description: Equipamento não encontrado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Equipamento WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Equipamento não encontrado"}), 404

        cursor.execute("DELETE FROM Equipamento WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Equipamento apagado com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/equipamento/<int:id>', methods=['PATCH'])
@verificar_jwt
def mudar_cliente_equipamento(id):
    """
    Mudar cliente do equipamento
    ---
    parameters:
      - name: id
        in: path
        type: integer
      - in: body
        schema:
          type: object
          required:
            - cliente_nif
          properties:
            cliente_nif:
              type: string
    security:
      - Bearer: []
    responses:
      200:
        description: Cliente atualizado
      400:
        description: Dados inválidos
      404:
        description: Recurso não encontrado
    """
    dados = request.get_json()
    if not dados or 'cliente_nif' not in dados:
        return jsonify({"erro": "Formato JSON incorreto ou campos em falta"}), 400

    novo_nif = dados['cliente_nif']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Equipamento WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Equipamento não encontrado"}), 404

        cursor.execute("SELECT NIF FROM Cliente WHERE NIF = ?", (novo_nif,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Cliente não encontrado"}), 404

        cursor.execute("UPDATE PropriedadeEquipamento SET Cliente_NIF = ? WHERE Equipamento_ID = ?",
                      (novo_nif, id))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Cliente atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==================== CLIENTES ====================

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    """
    Lista todos os clientes
    ---
    responses:
      200:
        description: Lista de clientes
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cliente ORDER BY Nome ASC")
        clientes = cursor.fetchall()
        conn.close()

        lista = []
        for cli in clientes:
            lista.append({
                "nif": cli['NIF'],
                "nome": cli['Nome'],
                "morada": cli['Morada'],
                "codigo_postal": cli['CodigoPostal'],
                "localidade": cli['Localidade'],
                "area": cli['Area'],
                "zona": cli['Zona']
            })
        return jsonify(lista), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/cliente/<nif>', methods=['GET'])
def obter_cliente(nif):
    """
    Obter cliente por NIF
    ---
    parameters:
      - name: nif
        in: path
        type: string
    responses:
      200:
        description: Dados do cliente
      404:
        description: Cliente não encontrado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cliente WHERE NIF = ?", (nif,))
        cli = cursor.fetchone()
        conn.close()

        if not cli:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        return jsonify({
            "nif": cli['NIF'],
            "nome": cli['Nome'],
            "morada": cli['Morada'],
            "codigo_postal": cli['CodigoPostal'],
            "localidade": cli['Localidade'],
            "area": cli['Area'],
            "zona": cli['Zona']
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/cliente', methods=['POST'])
@verificar_jwt
def criar_cliente():
    """
    Criar novo cliente
    ---
    parameters:
      - in: body
        schema:
          type: object
          required:
            - nif
            - nome
          properties:
            nif:
              type: string
            nome:
              type: string
            morada:
              type: string
            codigo_postal:
              type: string
            localidade:
              type: string
            area:
              type: string
            zona:
              type: string
    responses:
      201:
        description: Cliente criado
      400:
        description: Dados inválidos
    """
    dados = request.get_json()

    if not dados or not dados.get('nif') or not dados.get('nome'):
        return jsonify({"erro": "Campos obrigatórios: nif, nome"}), 400

    if len(str(dados['nif']).strip()) != 12:
        return jsonify({"erro": "NIF deve ter 12 caracteres"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Cliente (NIF, Nome, Morada, CodigoPostal, Localidade, Area, Zona)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dados['nif'],
            dados['nome'],
            dados.get('morada', ''),
            dados.get('codigo_postal', ''),
            dados.get('localidade', ''),
            dados.get('area', ''),
            dados.get('zona', '')
        ))
        conn.commit()
        conn.close()
        return jsonify({"nif": dados['nif'], "mensagem": "Cliente criado"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": "NIF já existe"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==================== TEMPERATURAS E ALERTAS ====================

@app.route('/temperatura', methods=['POST'])
@verificar_jwt
def registar_temperatura():
    """
    Registar temperatura de equipamento
    ---
    parameters:
      - in: body
        schema:
          type: object
          required:
            - equipamento_id
          properties:
            equipamento_id:
              type: integer
            temp0:
              type: number
            temp1:
              type: number
            temp2:
              type: number
    responses:
      201:
        description: Temperatura registada
      400:
        description: Dados inválidos
      404:
        description: Equipamento não encontrado
    """
    dados = request.get_json()
    if not dados or 'equipamento_id' not in dados:
        return jsonify({"erro": "Equipamento_ID obrigatório"}), 400

    equipamento_id = dados['equipamento_id']
    temp0 = dados.get('temp0')
    temp1 = dados.get('temp1')
    temp2 = dados.get('temp2')

    if temp0 is None and temp1 is None and temp2 is None:
        return jsonify({"erro": "Pelo menos uma temperatura deve ser fornecida"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ID FROM Equipamento WHERE ID = ?", (equipamento_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Equipamento não encontrado"}), 404

        cursor.execute("""
            INSERT INTO Temperatura (Equipamento_ID, Temp0, Temp1, Temp2)
            VALUES (?, ?, ?, ?)
        """, (equipamento_id, temp0, temp1, temp2))
        conn.commit()
        conn.close()

        processar_alertas_assincrono(equipamento_id, temp0, temp1, temp2)

        return jsonify({"mensagem": "Temperatura registada com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/alertas', methods=['GET'])
@verificar_jwt
def listar_alertas():
    """
    Listar histórico de alertas
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de alertas
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alertas_sensores
            ORDER BY DataHora DESC
            LIMIT 100
        """)
        alertas = cursor.fetchall()
        conn.close()

        lista_alertas = []
        for alerta in alertas:
            lista_alertas.append({
                "id": alerta['id'],
                "equipamento_id": alerta['Equipamento_ID'],
                "sensor": alerta['Sensor_tipo'],
                "leitura": alerta['Leitura'],
                "data": alerta['DataHora'],
                "mensagem": alerta['Mensagem']
            })
        return jsonify(lista_alertas), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/temperaturas/<int:equipamento_id>', methods=['GET'])
def listar_temperaturas_equipamento(equipamento_id):
    """
    Listar temperaturas de um equipamento
    ---
    parameters:
      - name: equipamento_id
        in: path
        type: integer
    responses:
      200:
        description: Lista de temperaturas
      404:
        description: Equipamento não encontrado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ID FROM Equipamento WHERE ID = ?", (equipamento_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Equipamento não encontrado"}), 404

        cursor.execute("""
            SELECT * FROM Temperatura
            WHERE Equipamento_ID = ?
            ORDER BY DataHora DESC
            LIMIT 50
        """, (equipamento_id,))
        temps = cursor.fetchall()
        conn.close()

        lista = []
        for temp in temps:
            lista.append({
                "id": temp['ID'],
                "equipamento_id": temp['Equipamento_ID'],
                "data": temp['DataHora'],
                "temp0": temp['Temp0'],
                "temp1": temp['Temp1'],
                "temp2": temp['Temp2']
            })
        return jsonify(lista), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==================== GERAR TOKEN ====================

@app.route('/api/gerar-token', methods=['GET', 'POST'])
def gerar_token():
    """
    Gerar token JWT
    ---
    responses:
      200:
        description: Token gerado
    """
    token = jwt.encode({"user": "admin", "role": "user"}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SERVIDOR INICIADO - Sistema de Monitorização de Equipamentos")
    print("="*70)
    print("Acesso: http://localhost:5000")
    print("Swagger: http://localhost:5000/api/docs")
    print("="*70 + "\n")
    app.run(debug=True, port=5000)
