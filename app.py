# app.py
from flask import Flask, render_template, request, jsonify, send_file
import hashlib
import os
import json
import tempfile
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
# ✅ Restringimos CORS solo a tu dominio
CORS(app, origins=["https://testrobert.work.gd"])

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Almacenamiento en memoria (suficiente para demo)
certificaciones = {}

def generar_hash(ruta_archivo, algoritmo='sha256'):
    hash_obj = hashlib.new(algoritmo)
    with open(ruta_archivo, 'rb') as f:
        for bloque in iter(lambda: f.read(4096), b""):
            hash_obj.update(bloque)
    return hash_obj.hexdigest()

@app.route('/')
def home():
    return jsonify({"mensaje": "Certificador de Archivos - Backend Activo"})

@app.route('/api/certificar', methods=['POST'])
def certificar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    archivo = request.files['archivo']
    propietario = request.form.get('propietario', 'Usuario').strip() or 'Usuario'
    
    if archivo.filename == '':
        return jsonify({'error': 'Archivo sin nombre'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            archivo.save(tmp.name)
            ruta_temp = tmp.name

        stats = os.stat(ruta_temp)
        nombre_archivo = archivo.filename
        tamanio = stats.st_size
        fecha_mod = datetime.fromtimestamp(stats.st_mtime).isoformat()

        hashes = {
            'sha256': generar_hash(ruta_temp, 'sha256'),
            'sha1': generar_hash(ruta_temp, 'sha1'),
            'md5': generar_hash(ruta_temp, 'md5')
        }

        certificaciones[hashes['sha256']] = {
            "nombre_archivo": nombre_archivo,
            "propietario": propietario,
            "fecha_certificacion": datetime.now().isoformat(),
            "tamanio_bytes": tamanio,
            "fecha_modificacion": fecha_mod,
            "hashes": hashes,
            "estado": "CERTIFICADO"
        }

        os.unlink(ruta_temp)

        return jsonify({
            "success": True,
            "certificacion": certificaciones[hashes['sha256']]
        })

    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500

@app.route('/api/verificar', methods=['POST'])
def verificar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    archivo = request.files['archivo']
    hash_original = request.form.get('hash_original', '').strip()

    if not hash_original:
        return jsonify({'error': 'Hash original no proporcionado'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            archivo.save(tmp.name)
            ruta_temp = tmp.name

        hash_actual = generar_hash(ruta_temp, 'sha256')
        os.unlink(ruta_temp)

        integro = hash_actual == hash_original

        return jsonify({
            "success": True,
            "integro": integro,
            "hash_original": hash_original,
            "hash_actual": hash_actual,
            "verificacion_fecha": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'Error en verificación: {str(e)}'}), 500

@app.route('/api/guardar-certificado', methods=['POST'])
def guardar_certificado():
    data = request.get_json()
    cert_data = data.get('certificacion')
    
    if not cert_data:
        return jsonify({'error': 'Datos de certificación no válidos'}), 400

    json_bytes = json.dumps(cert_data, indent=2, ensure_ascii=False).encode('utf-8')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        tmp.write(json_bytes)
        tmp_path = tmp.name

    return send_file(tmp_path, as_attachment=True, download_name='certificado.json')

# ⚠️ ¡ESTO ES CLAVE PARA RENDER!
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
