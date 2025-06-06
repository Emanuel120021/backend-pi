from flask import Flask, request, session, jsonify
import sqlite3
from flask_cors import CORS
import base64
from flasgger import Swagger

app = Flask(__name__)
app.secret_key = 'chave-secreta'
CORS(app, supports_credentials=True)

# Swagger configurado com base no arquivo YAML
swagger = Swagger(app, template_file='swagger.yaml')


def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn 


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha').encode("utf-8")
    senhaBase64 = base64.b64encode(senha).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.execute(
        'SELECT id, nome, login, cargo FROM usuarios WHERE login = ? AND senha = ?',
        (email, senhaBase64)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        session['login'] = email
        return jsonify({'status': True, 'usuario': user['nome'], 'cargo': user['cargo']}), 200
    else:
        return jsonify({'status': False, 'mensagem': 'Usuário ou senha inválidos'}), 401


@app.route('/cadastro', methods=['POST'])
def cadastro():
    data = request.json
    nome = data.get('nome')
    login = data.get('login')
    senha = data.get('senha')

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)',
            (nome, login, senha)
        )
        conn.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Usuário já existe."}), 409
    finally:
        conn.close()


@app.route('/users', methods=['GET'])
def users():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT id, nome FROM usuarios').fetchall()
    conn.close()
    resultado = [dict(usuario) for usuario in usuarios]
    return jsonify(resultado)


from sqlite3 import Error

@app.route('/eventos', methods=['POST'])
def novo_evento():
    try:
        data = request.get_json()
        if not data or 'evento' not in data:
            return jsonify({"erro": "Dados do evento ausentes ou mal formatados."}), 400
        evento = data['evento']
        nome = evento.get('nome')
        categoria = evento.get('categoria')
        data_evento = evento.get('data')
        status = evento.get('status')

        if not all([nome, categoria, data_evento, status]):
            return jsonify({"erro": "Todos os campos do evento são obrigatórios."}), 400

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO eventos (nome, categoria, data, status) VALUES (?, ?, ?, ?)',
            (nome, categoria, data_evento, status)
        )
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Evento criado com sucesso!"}), 201
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500

@app.route('/eventos/<int:evento_id>', methods=['PUT'])
def atualizar_evento(evento_id):
    try:
        data = request.get_json()
        if not data or 'evento' not in data:
            return jsonify({"erro": "Dados do evento ausentes ou mal formatados."}), 400
        evento = data['evento']
        nome = evento.get('nome')
        categoria = evento.get('categoria')
        data_evento = evento.get('data')
        status = evento.get('status')
        if not all([nome, categoria, data_evento, status]):
            return jsonify({"erro": "Todos os campos do evento são obrigatórios."}), 400
        conn = get_db_connection()
        cursor = conn.execute(
            'UPDATE eventos SET nome = ?, categoria = ?, data = ?, status = ? WHERE id = ?',
            (nome, categoria, data_evento, status, evento_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Evento não encontrado."}), 404
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Evento atualizado com sucesso!"}), 200
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500


@app.route('/eventos/<int:evento_id>', methods=['DELETE'])
def deletar_evento(evento_id):
    try:
        if not evento_id:
            return jsonify({"erro": "ID do evento ausente ou mal formatado."}), 400
        conn = get_db_connection()
        cursor = conn.execute('DELETE FROM eventos WHERE id = ?', (evento_id,))
        if cursor.rowcount == 0:
            return jsonify({"erro": "Evento não encontrado."}), 404
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Evento deletado com sucesso!"}), 200
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500


@app.route('/eventos', methods=['GET'])
def eventos():
    conn = get_db_connection()
    eventos = conn.execute('SELECT * FROM eventos').fetchall()
    conn.close()
    resultado = [dict(evento) for evento in eventos]
    return jsonify(resultado)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return jsonify({"message": "Logout efetuado"}), 200


if __name__ == '__main__':
    app.run(debug=True)
