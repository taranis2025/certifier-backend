# app.py
from flask import Flask, request, jsonify, send_file
import hashlib
import os
import json
import tempfile
from datetime import datetime
from flask_cors import CORS

# Crear la aplicación Flask
app = Flask(__name__)

# ✅ CORREGIDO: Sin espacios en la URL de origen
CORS(app, origins=["https://testrobert.work.gd"])

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

def generar_hash(archivo, algoritmo='sha256'):
    """Genera el hash de un objeto archivo en memoria."""
    hash_obj = hashlib.new(algoritmo)
    archivo.seek(0)
    for bloque in iter(lambda: archivo.read(4096), b""):
        hash_obj.update(bloque)
    archivo.seek(0)  # Restablecer para reutilización
    return hash_obj.hexdigest()

# ✅ Ruta raíz: obligatoria para Railway
@app.route('/')
def home():
    return jsonify({
        "mensaje": "Certificador de Archivos - Backend Activo",
        "status": "ok"
    })

# Ruta para certificar archivos
@app.route('/api/certificar', methods=['POST'])
def certificar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    archivo = request.files['archivo']
    propietario = request.form.get('propietario', 'Usuario').strip() or 'Usuario'
    
    if archivo.filename == '':
        return jsonify({'error': 'Archivo sin nombre'}), 400

    try:
        # Leer tamaño sin guardar en disco
        archivo.seek(0, os.SEEK_END)
        tamanio = archivo.tell()
        archivo.seek(0)

        # Generar hashes
        hashes = {
            'sha256': generar_hash(archivo, 'sha256'),
            'sha1': generar_hash(archivo, 'sha1'),
            'md5': generar_hash(archivo, 'md5')
        }

        certificacion = {
            "nombre_archivo": archivo.filename,
            "propietario": propietario,
            "fecha_certificacion": datetime.utcnow().isoformat() + "Z",
            "tamanio_bytes": tamanio,
            "hashes": hashes,
            "estado": "CERTIFICADO"
        }

        return jsonify({
            "success": True,
            "certificacion": certificacion
        })

    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500

# Ruta para verificar integridad
@app.route('/api/verificar', methods=['POST'])
def verificar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    archivo = request.files['archivo']
    hash_original = request.form.get('hash_original', '').strip()

    if not hash_original:
        return jsonify({'error': 'Hash original no proporcionado'}), 400

    try:
        hash_actual = generar_hash(archivo, 'sha256')
        integro = hash_actual == hash_original

        return jsonify({
            "success": True,
            "integro": integro,
            "hash_original": hash_original,
            "hash_actual": hash_actual,
            "verificacion_fecha": datetime.utcnow().isoformat() + "Z"
        })

    except Exception as e:
        return jsonify({'error': f'Error en verificación: {str(e)}'}), 500

# Ruta para descargar certificado como JSON
@app.route('/api/guardar-certificado', methods=['POST'])
def guardar_certificado():
    try:
        data = request.get_json()
        cert_data = data.get('certificacion')
        
        # ✅ Corregido: sintaxis válida
        if not cert_data:
            return jsonify({'error': 'Datos de certificación no válidos'}), 400

        # Crear archivo temporal en memoria
        json_bytes = json.dumps(cert_data, indent=2, ensure_ascii=False).encode('utf-8')
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'certificado.json')
        
        with open(temp_path, 'wb') as f:
            f.write(json_bytes)
        
        # Enviar y limpiar
        response = send_file(temp_path, as_attachment=True, download_name='certificado.json')
        os.remove(temp_path)
        return response

    except Exception as e:
        return jsonify({'error': f'Error al guardar: {str(e)}'}), 500

# ⚠️ Puerto dinámico para Railway (¡no lo cambies!)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
