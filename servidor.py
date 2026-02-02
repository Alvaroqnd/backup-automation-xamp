from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
import shutil

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  # necesario para sesiones



# Usuario del sistema operativo
USUARIO_SO = os.getlogin()

# Rutas reales del ordenador (NO del proyecto)
RUTAS_BACKUP = {
    "documentos": f"C:\\Users\\{USUARIO_SO}\\Documents",
    "escritorio": f"C:\\Users\\{USUARIO_SO}\\Desktop",
    "descargas": f"C:\\Users\\{USUARIO_SO}\\Downloads"
}

# Carpeta donde se guardan las copias
DESTINO_BACKUP = "C:\\Backups"
os.makedirs(DESTINO_BACKUP, exist_ok=True)


USUARIO = "asir"
PASSWORD = "1234"

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



@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])



@app.route('/backup', methods=['POST'])
def backup():
    data = request.json
    tipo = data.get('tipo', 'documentos')

    if tipo not in RUTAS_BACKUP:
        return jsonify({"ok": False, "error": "Tipo de copia no válido"}), 400

    origen = RUTAS_BACKUP[tipo]
    fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M")
    nombre_backup = f"backup_{tipo}_{fecha_archivo}"
    ruta_final = os.path.join(DESTINO_BACKUP, nombre_backup)

    try:
        # Crear copia comprimida
        shutil.make_archive(ruta_final, 'zip', origen)

        fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        descripcion = f'Copia de {tipo} realizada correctamente'

        historial.append({
            'fecha': fecha,
            'tipo': 'Copia',
            'descripcion': descripcion
        })

        return jsonify({"ok": True, "historial": historial})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500



@app.route('/restore', methods=['POST'])
def restore():
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    descripcion = 'Restauración completada mediante PowerShell'

    historial.append({
        'fecha': fecha,
        'tipo': 'Restauración',
        'descripcion': descripcion
    })

    return jsonify({"ok": True, "historial": historial})



@app.route('/historial', methods=['GET'])
def get_historial():
    return jsonify(historial)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
