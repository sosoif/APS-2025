from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'
socketio = SocketIO(app)

# Banco de dados fictício de usuários
usuarios = {
    'cliente1': 'senha1',
    'cliente2': 'senha2'
}

# Palavras proibidas
palavras_proibidas = ['boboca', 'idiota', 'burro', 'palavrão']

# Lista de usuários conectados
usuarios_conectados = {}

# Middleware para proteger rota do chat
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'usuario' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

# Rota da tela de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in usuarios and usuarios[usuario] == senha:
            session['usuario'] = usuario
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos.')
    return render_template('login.html')

# Rota do chat (protegida)
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', usuario=session['usuario'])

# Rota de logout
@app.route('/logout')
def logout():
    usuario = session.pop('usuario', None)
    return redirect(url_for('login'))

# Filtro de palavrões
def filtrar_palavras(msg):
    for palavra in palavras_proibidas:
        msg = msg.replace(palavra, '***')
    return msg

# Evento WebSocket para mensagens
@socketio.on('message')
def handle_message(msg):
    usuario = session.get('usuario', 'Anônimo')
    msg_filtrada = filtrar_palavras(msg)
    mensagem_final = f"{usuario}: {msg_filtrada}"
    print(f"[{usuario}] {msg}")
    send(mensagem_final, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
