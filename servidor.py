from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
import subprocess
import ctypes
from ctypes import wintypes

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"

# =====================================================
# RUTAS PROFESIONALES (FUNCIONAN EN EXE E INSTALADO)
# =====================================================

# Carpeta Documentos del usuario
USER_HOME = os.path.expanduser("~")
USER_DOCS = os.path.join(USER_HOME, "Documents")

# Carpeta base de la aplicación
APP_DIR = os.path.join(USER_DOCS, "CORE_SYNC")

# Carpeta de backups (DESTINO REAL)
BACKUPS_DIR = os.path.join(APP_DIR, "backups")

# Carpeta de scripts PowerShell (incluidos en el EXE)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")

os.makedirs(BACKUPS_DIR, exist_ok=True)

# =====================================================
# USUARIO DEMO
# =====================================================
USUARIO = "asir"
PASSWORD = "1234"

# =====================================================
# HISTORIAL EN MEMORIA
# =====================================================
historial = []

# =====================================================
# KNOWN FOLDERS WINDOWS
# =====================================================
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


def _guid_from_str(g: str) -> GUID:
    import re
    m = re.fullmatch(
        r"([0-9A-Fa-f]{8})-([0-9A-Fa-f]{4})-([0-9A-Fa-f]{4})-([0-9A-Fa-f]{4})-([0-9A-Fa-f]{12})",
        g
    )
    if not m:
        raise ValueError("GUID inválido")
    d1 = int(m.group(1), 16)
    d2 = int(m.group(2), 16)
    d3 = int(m.group(3), 16)
    d4a = bytes.fromhex(m.group(4))
    d4b = bytes.fromhex(m.group(5))
    d4 = (ctypes.c_ubyte * 8).from_buffer_copy(d4a + d4b)
    return GUID(d1, d2, d3, d4)


def get_known_folder_path(guid_str: str) -> str:
    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32

    guid = _guid_from_str(guid_str)
    path_ptr = ctypes.c_wchar_p()

    res = shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(path_ptr))
    if res != 0:
        raise OSError(f"SHGetKnownFolderPath fallo HRESULT={res}")

    path = path_ptr.value
    ole32.CoTaskMemFree(path_ptr)
    return path


def get_base_path(tipo: str) -> str:
    if tipo == "documentos":
        return get_known_folder_path("FDD39AD0-238F-46AF-ADB4-6C85480369C7")
    if tipo == "escritorio":
        return get_known_folder_path("B4BFCC3A-DB2C-424C-B029-7FE99A87C641")
    if tipo == "descargas":
        return get_known_folder_path("374DE290-123F-4565-9164-39C4925E467B")
    raise ValueError("Tipo no válido")

# =====================================================
# LOGIN
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == USUARIO and request.form.get("password") == PASSWORD:
            session["user"] = USUARIO
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

# =====================================================
# DASHBOARD
# =====================================================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["user"])

# =====================================================
# BACKUP NORMAL (VERIFICADO)
# =====================================================
@app.route("/backup", methods=["POST"])
def backup():
    data = request.get_json() or {}
    tipo = data.get("tipo", "documentos")

    scripts = {
        "Completa": "backup_completo.ps1",
        "documentos": "backup_documentos.ps1",
        "escritorio": "backup_escritorio.ps1",
        "descargas": "backup_descargas.ps1",
    }

    script_path = os.path.join(SCRIPTS_DIR, scripts.get(tipo, ""))

    before = set(os.listdir(BACKUPS_DIR))

    res = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )

    if res.returncode != 0:
        return jsonify({"ok": False, "error": res.stderr or res.stdout}), 500

    after = set(os.listdir(BACKUPS_DIR))
    new_files = [f for f in after - before if f.lower().endswith(".zip")]

    if not new_files:
        return jsonify({
            "ok": False,
            "error": "El script se ejecutó pero no se generó ningún ZIP.",
            "stdout": res.stdout
        }), 500

    zip_path = os.path.join(BACKUPS_DIR, new_files[0])

    historial.append({
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": "Copia",
        "descripcion": f"Copia {tipo} -> {zip_path}"
    })

    return jsonify({"ok": True, "historial": historial, "zip": zip_path})

# =====================================================
# LISTAR CONTENIDO
# =====================================================
@app.route("/listar", methods=["POST"])
def listar():
    data = request.get_json() or {}
    base = get_base_path(data.get("tipo"))
    items = [{"name": f, "kind": "dir" if os.path.isdir(os.path.join(base, f)) else "file"} for f in os.listdir(base)]
    return jsonify({"ok": True, "items": items})

# =====================================================
# BACKUP SELECTIVO
# =====================================================
@app.route("/backup_selectivo", methods=["POST"])
def backup_selectivo():
    data = request.get_json() or {}
    script_path = os.path.join(SCRIPTS_DIR, "backup_selectivo.ps1")

    res = subprocess.run(
        [
            "powershell", "-ExecutionPolicy", "Bypass",
            "-File", script_path,
            "-Tipo", data.get("tipo"),
            "-ItemsStr", "|".join(data.get("items", []))
        ],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )

    if res.returncode != 0:
        return jsonify({"ok": False, "error": res.stderr or res.stdout}), 500

    return jsonify({"ok": True})

# =====================================================
# RESTORE
# =====================================================
@app.route("/restore", methods=["POST"])
def restore():
    script_path = os.path.join(SCRIPTS_DIR, "restore.ps1")

    res = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )

    if res.returncode != 0:
        return jsonify({"ok": False, "error": res.stderr or res.stdout}), 500

    return jsonify({"ok": True})

# =====================================================
# INFO / ESTADO (PROFESIONAL)
# =====================================================
@app.route("/status")
def status():
    return jsonify({
        "backups_dir": BACKUPS_DIR,
        "backups_files": os.listdir(BACKUPS_DIR)
    })

# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =====================================================
# SERVIDOR (WAITRESS)
# =====================================================
def run_server(host="127.0.0.1", port=5000):
    from waitress import serve
    serve(app, host=host, port=port)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
