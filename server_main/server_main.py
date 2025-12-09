#
# Descr.:
# Servidor HTTP principal
#
# Uso:
# $ python ./server_main.py
#
# Autor:
# Jose G. Faisca
#

from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, g
from flask_socketio import SocketIO
import sqlite3

DATABASE = '../db/test_database.db'

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

host = '0.0.0.0'
port = 8080

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        nif = request.form['nif']
        nome = request.form['nome']
        morada = request.form['morada']
        codigo_postal = request.form['codigo_postal']
        localidade = request.form['localidade']
        area = request.form['area']
        zona = request.form['zona']
        cursor.execute('''
            INSERT INTO Cliente (NIF, Nome, Morada, CodigoPostal, Localidade, Area, Zona)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (nif, nome, morada, codigo_postal, localidade, area, zona))
        db.commit()

        return redirect(url_for('index'))

    return render_template('cliente_form.html')

@app.route('/equipamento', methods=['GET', 'POST'])
def equipamento():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        id = request.form.get('id')
        numero_serie = request.form['numero_serie']
        cliente_nif = request.form['cliente_nif']

        if id:
            cursor.execute('''
                INSERT INTO Equipamento (ID, NumeroSerie, Cliente_NIF)
                VALUES (?, ?, ?)''', (id, numero_serie, cliente_nif))
        else:
            cursor.execute('''
                INSERT INTO Equipamento (NumeroSerie, Cliente_NIF)
                VALUES (?, ?)''', (numero_serie, cliente_nif))
        db.commit()

        return redirect(url_for('listar_equipamentos'))

    cursor.execute("SELECT NIF FROM Cliente")
    clientes = [row[0] for row in cursor.fetchall()]

    return render_template('equipamento_form.html', clientes=clientes)

@app.route('/equipamento/json', methods=['POST'])
def equipamento_json():
    db = get_db()
    cursor = db.cursor()
    data = request.get_json()
    id = data.get('id')
    numero_serie = data['numero_serie']
    cliente_nif = data['cliente_nif']

    if id:
        cursor.execute('''
            INSERT INTO Equipamento (ID, NumeroSerie, Cliente_NIF)
            VALUES (?, ?, ?)''',
            (id, numero_serie, cliente_nif))
    else:
        cursor.execute('''
            INSERT INTO Equipamento (NumeroSerie, Cliente_NIF)
            VALUES (?, ?)''', (numero_serie, cliente_nif))
    db.commit()
    return jsonify({"message": "Dados inseridos com sucesso"}), 201

@app.route('/equipamentos_cliente', methods=['GET'])
def equipamentos_cliente():
    db = get_db()
    cursor = db.cursor()
    cliente_nif = request.args.get('cliente_nif') or request.headers.get('cliente_nif')
    if cliente_nif:
        cursor.execute('SELECT * FROM Equipamento WHERE Cliente_NIF = ?', (cliente_nif,))
        equipamentos = cursor.fetchall()
        return render_template('listar_equipamentos.html', equipamentos=equipamentos)
    else:
        return jsonify({'error': 'Necessario o parametro cliente_nif'}), 400

@app.route('/equipamentos_cliente/json', methods=['POST'])
def equipamentos_cliente_json():
    db = get_db()
    cursor = db.cursor()
    data = request.get_json()
    cliente_nif = data.get('cliente_nif')
    if cliente_nif:
        cursor.execute('SELECT * FROM Equipamento WHERE Cliente_NIF = ?', (cliente_nif,))
        equipamentos = [
            {"id": row[0], "numero_serie": row[1], "cliente_nif": row[2]}
            for row in cursor.fetchall()
        ]
        return jsonify(equipamentos)
    else:
        return jsonify({'error': 'Necessario o parametro cliente_nif no corpo JSON'}), 400

@app.route('/equipamento_temperaturas', methods=['GET'])
def equipamentos_temperaturas():
    db = get_db()
    cursor = db.cursor()
    equipamento_id = request.args.get('equipamento_id') or request.headers.get('equipamento_id')
    if equipamento_id:
        page = request.args.get('page', 1, type=int)
        per_page = 12
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT COUNT(*) FROM Temperatura WHERE Equipamento_ID = ?''', 
            (equipamento_id,))
        total = cursor.fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        cursor.execute('''
            SELECT * FROM Temperatura WHERE Equipamento_ID = ? ORDER BY DataHora DESC LIMIT ? OFFSET ? ''', 
            (equipamento_id, per_page, offset))
            temperaturas = cursor.fetchall()      
        return render_template('listar_temperaturas.html',
                           temperaturas=temperaturas,
                           page=page,
                           total_pages=total_pages,
                           equipamento_id=equipamento_id)
    else:
        return jsonify({'error': 'Necessario o parametro equipamento_id'}), 400

@app.route('/equipamento_temperaturas/json', methods=['POST'])
def equipamento_temperaturas_json():
    db = get_db()
    cursor = db.cursor()
    data = request.get_json()
    equipamento_id = data.get('equipamento_id')
    if equipamento_id:
        cursor.execute(''' 
            SELECT * FROM Temperatura WHERE Equipamento_ID = ? ORDER BY DataHora DESC ''',
            (equipamento_id,))
        temperaturas = cursor.fetchall()
        temperaturas_json = [
            {"id": row[0], "equipamento_id": row[1], "valor": row[2], "datahora": row[3]}
            for row in temperaturas
        ]
        return jsonify(temperaturas_json)
    else:
        return jsonify({'error': 'Necessario o parametro equipamento_id no corpo JSON'}), 400

@app.route('/temperatura', methods=['POST', 'GET'])
def handle_temperatura():
    if request.method == 'POST':
        input_data = request.data.decode('utf-8')
    elif request.method == 'GET':
        input_data = request.args.get('data', '')
    else:
        return jsonify({'error': 'Metodo nao suportado'}), 405

    return handle_data(input_data)

def handle_data(input_data):
    data = input_data.strip().split(',')
    if len(data) == 5:
        equipment_id, current_time, temp0, temp1, temp2 = data

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO Temperatura (Equipamento_ID, DataHora, Temp0, Temp1, Temp2)
            VALUES (?, ?, ?, ?, ?)''',
            (equipment_id.strip(), current_time.strip(), float(temp0), float(temp1), float(temp2)))
        db.commit()

        notifica_atualiza_temperaturas()

        return jsonify({'message': 'Dados inseridos com sucesso.'}), 200
    else:
        return jsonify({'error': 'Formato de dados invalido.'}), 400

@app.route('/listar_clientes')
def listar_clientes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Cliente")
    clientes = cursor.fetchall()
    return render_template('listar_clientes.html', clientes=clientes)

@app.route('/listar_equipamentos')
def listar_equipamentos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Equipamento")
    equipamentos = cursor.fetchall()
    return render_template('listar_equipamentos.html', equipamentos=equipamentos)

@app.route('/listar_equipamentos/json')
def listar_equipamentos_json():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Equipamento")
    equipamentos = [
        {"id": row[0], "numero_serie": row[1], "cliente_nif": row[2]}
        for row in cursor.fetchall()
    ]
    return jsonify(equipamentos)
    
@app.route('/listar_temperaturas')
def listar_temperaturas():
    db = get_db()
    cursor = db.cursor()
    # Obter pagina corrente a partir de query string, 1 por defeito
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page
    # Obter total para controlo de pagina
    cursor.execute('SELECT COUNT(*) FROM Temperatura')
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    # Query da pagina corrente
    cursor.execute('''
        SELECT * FROM Temperatura ORDER BY DataHora DESC LIMIT ? OFFSET ?
    ''', (per_page, offset))
    temperaturas = cursor.fetchall()

    return render_template('listar_temperaturas.html',
                           temperaturas=temperaturas,
                           page=page,
                           total_pages=total_pages)

def notifica_atualiza_temperaturas(page=1):
    db = get_db()
    cursor = db.cursor()
    per_page = 12
    offset = (page - 1) * per_page
    cursor.execute(f"SELECT COUNT(*) FROM Temperatura")
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    cursor.execute('SELECT * FROM Temperatura ORDER BY DataHora DESC LIMIT ? OFFSET ?', (per_page, offset))
    temperaturas = cursor.fetchall()
    data_to_send = [tuple(row) for row in temperaturas]
    socketio.emit('atualiza_temperaturas', {
        'temperaturas': data_to_send,
        'page': page,
        'total_pages': total_pages
    })

if __name__ == "__main__":
    socketio.run(app, host=host, port=port, debug=True)
