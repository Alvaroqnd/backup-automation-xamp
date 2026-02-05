from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
import subprocess
import ctypes
from ctypes import wintypes

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"

# ----------------- RUTAS DEL PROYECTO -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUPS_DIR, exist_ok=True)

# ----------------- USUARIO APP (DEMO) -----------------
USUARIO = "asir"
PASSWORD = "1234"

# ----------------- HISTORIAL -----------------
historial = []

# ----------------- KNOWN FOLDERS WINDOWS (rutas reales) -----------------
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

# ----------------- LOGIN -----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USUARIO and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")

# ----------------- DASHBOARD -----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["user"])

# ----------------- BACKUP NORMAL (verifica ZIP real) -----------------
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

    if tipo not in scripts:
        return jsonify({"ok": False, "error": "Tipo de copia no válido"}), 400

    script_path = os.path.join(SCRIPTS_DIR, scripts[tipo])
    if not os.path.exists(script_path):
        return jsonify({"ok": False, "error": f"No existe el script: {script_path}"}), 500

    # Foto ANTES (zips existentes)
    try:
        before = {
            f.lower()
            for f in os.listdir(BACKUPS_DIR)
            if f.lower().endswith(".zip")
        }
    except Exception:
        before = set()

    try:
        res = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        if res.returncode != 0:
            return jsonify({
                "ok": False,
                "error": (res.stderr.strip() or res.stdout.strip() or "Error ejecutando el script")
            }), 500

        # Foto DESPUÉS + detectar zip nuevo
        zip_path = None
        try:
            after_files = [
                f for f in os.listdir(BACKUPS_DIR)
                if f.lower().endswith(".zip")
            ]
            after = {f.lower() for f in after_files}
            new_zips = list(after - before)

            if new_zips:
                candidates = [
                    os.path.join(BACKUPS_DIR, f)
                    for f in after_files
                    if f.lower() in new_zips
                ]
                zip_path = max(candidates, key=os.path.getmtime)
        except Exception:
            zip_path = None

        # Si no se creó ZIP, no lo damos por OK
        if not zip_path:
            return jsonify({
                "ok": False,
                "error": "El script terminó sin error, pero NO se detectó ningún ZIP nuevo en la carpeta 'backups'.",
                "stdout": (res.stdout or "").strip(),
                "stderr": (res.stderr or "").strip(),
                "backups_dir": BACKUPS_DIR,
                "script": script_path
            }), 500

        historial.append({
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": "Copia",
            "descripcion": f"Copia {tipo} realizada correctamente -> {zip_path}"
        })

        return jsonify({"ok": True, "historial": historial, "zip": zip_path})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- LISTAR CONTENIDO (para copia selectiva) -----------------
@app.route("/listar", methods=["POST"])
def listar():
    data = request.get_json() or {}
    tipo = data.get("tipo")

    if tipo not in ("documentos", "escritorio", "descargas"):
        return jsonify({"ok": False, "error": "Tipo no válido para listar"}), 400

    try:
        base = get_base_path(tipo)
        items = []
        for name in os.listdir(base):
            full = os.path.join(base, name)
            items.append({
                "name": name,
                "kind": "dir" if os.path.isdir(full) else "file"
            })

        items.sort(key=lambda x: (0 if x["kind"] == "dir" else 1, x["name"].lower()))
        return jsonify({"ok": True, "base": base, "items": items})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- BACKUP SELECTIVO -----------------
@app.route("/backup_selectivo", methods=["POST"])
def backup_selectivo():
    data = request.get_json() or {}
    tipo = data.get("tipo")
    items = data.get("items", [])

    if tipo not in ("documentos", "escritorio", "descargas"):
        return jsonify({"ok": False, "error": "Tipo no válido para copia selectiva"}), 400

    if not isinstance(items, list) or len(items) == 0:
        return jsonify({"ok": False, "error": "Selecciona al menos un elemento"}), 400

    script_path = os.path.join(SCRIPTS_DIR, "backup_selectivo.ps1")
    if not os.path.exists(script_path):
        return jsonify({"ok": False, "error": f"No existe el script: {script_path}"}), 500

    try:
        items_str = "|".join(items)

        cmd = [
            "powershell", "-ExecutionPolicy", "Bypass",
            "-File", script_path,
            "-Tipo", tipo,
            "-ItemsStr", items_str
        ]

        res = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)

        if res.returncode != 0:
            return jsonify({
                "ok": False,
                "error": (res.stderr.strip() or res.stdout.strip() or "Error en copia selectiva")
            }), 500

        historial.append({
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": "Copia",
            "descripcion": f"Copia selectiva de {tipo}: {', '.join(items)}"
        })

        return jsonify({"ok": True, "historial": historial})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- RESTORE -----------------
@app.route("/restore", methods=["POST"])
def restore():
    script_path = os.path.join(SCRIPTS_DIR, "restore.ps1")
    if not os.path.exists(script_path):
        return jsonify({"ok": False, "error": f"No existe el script: {script_path}"}), 500

    try:
        res = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        if res.returncode != 0:
            return jsonify({"ok": False, "error": (res.stderr.strip() or res.stdout.strip() or "Error ejecutando restore.ps1")}), 500

        historial.append({
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": "Restauración",
            "descripcion": "Restauración realizada correctamente"
        })

        return jsonify({"ok": True, "historial": historial})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- HISTORIAL -----------------
@app.route("/historial", methods=["GET"])
def get_historial():
    return jsonify(historial)

# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ----------------- RUN SERVER (Waitress) -----------------
def run_server(host="127.0.0.1", port=5000):
    from waitress import serve
    serve(app, host=host, port=port)

if __name__ == "__main__":
    # Modo desarrollo (ejecución manual)
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
