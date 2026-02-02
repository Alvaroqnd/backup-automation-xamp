from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  # necesario para sesiones

# Historial en memoria
historial = []

# Usuario demo
USUARIO = "asir"
PASSWORD = "1234"

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USUARIO and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

# Backup
@app.route('/backup', methods=['POST'])
def backup():
    tipo = request.json.get('tipo', 'Completa')
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    descripcion = f'Copia {tipo} ejecutada'
    historial.append({'fecha': fecha, 'tipo': 'Copia', 'descripcion': descripcion})
    return jsonify({'historial': historial})

# Restore
@app.route('/restore', methods=['POST'])
def restore():
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    descripcion = 'Restauración completada'
    historial.append({'fecha': fecha, 'tipo': 'Restauración', 'descripcion': descripcion})
    return jsonify({'historial': historial})

# Historial
@app.route('/historial', methods=['GET'])
def get_historial():
    return jsonify(historial)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
