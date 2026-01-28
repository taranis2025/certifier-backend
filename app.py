# app.py
import os
import hashlib
import json
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
# ✅ CORS configurado para tu dominio
CORS(app, origins=["https://testrobert.work.gd"])

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Almacenamiento temporal (en memoria)
certificaciones = {}

def generar_hash(ruta_archivo, algoritmo='sha256'):
    """Genera hash de un archivo"""
    hash_obj = hashlib.new(algoritmo)
    with open(ruta_archivo, 'rb') as f:
        for bloque in iter(lambda: f.read(4096), b""):
            hash_obj.update(bloque)
    return hash_obj.hexdigest()

@app.route('/')
def home():
    """Ruta raíz para verificar que el backend está activo"""
    return jsonify({
        "status": "ok",
        "mensaje": "Certificador Backend Activo en Back4App"
    })

@app.route('/api/certificar', methods=['POST'])
def certificar():
    """Certifica un archivo y genera hashes"""
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    archivo = request.files['archivo']
    propietario = request.form.get('propietario', 'Usuario').strip() or 'Usuario'

    if archivo.filename == '':
        return jsonify({'error': 'Archivo sin nombre'}), 400

    try:
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            archivo.save(tmp.name)
            ruta_temp = tmp.name

        # Obtener metadatos
        stats = os.stat(ruta_temp)
        nombre_archivo = archivo.filename
        tamanio = stats.st_size

        # Generar hashes
        hashes = {
            'sha256': generar_hash(ruta_temp, 'sha256'),
            'sha1': generar_hash(ruta_temp, 'sha1'),
            'md5': generar_hash(ruta_temp, 'md5')
        }

        # Crear certificación
        certificacion = {
            "nombre_archivo": nombre_archivo,
            "propietario": propietario,
            "fecha_certificacion": datetime.now().isoformat(),
            "tamanio_bytes": tamanio,
            "hashes": hashes,
            "estado": "CERTIFICADO"
        }

        # Guardar en memoria (clave: SHA-256)
        certificaciones[hashes['sha256']] = certificacion
        
        # Limpiar archivo temporal
        os.unlink(ruta_temp)

        return jsonify({
            "success": True,
            "certificacion": certificacion
        })

    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500

@app.route('/api/verificar', methods=['POST'])
def verificar():
    """Verifica la integridad de un archivo comparando hashes"""
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    archivo = request.files['archivo']
    hash_original = request.form.get('hash_original', '').strip()

    if not hash_original:
        return jsonify({'error': 'Hash original no proporcionado'}), 400

    try:
        # Guardar temporalmente el archivo a verificar
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            archivo.save(tmp.name)
            ruta_temp = tmp.name

        # Calcular hash actual (SHA-256)
        hash_actual = generar_hash(ruta_temp, 'sha256')
        
        # Limpiar archivo temporal
        os.unlink(ruta_temp)

        # Comparar hashes
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
    """Genera un archivo JSON descargable con la certificación"""
    try:
        data = request.get_json()
        cert_data = data.get('certificacion')
        
        if not cert_
            return jsonify({'error': 'Datos de certificación no válidos'}), 400

        # Crear JSON descargable
        json_bytes = json.dumps(cert_data, indent=2, ensure_ascii=False).encode('utf-8')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            tmp.write(json_bytes)
            tmp_path = tmp.name

        return send_file(tmp_path, as_attachment=True, download_name='certificado.json')

    except Exception as e:
        return jsonify({'error': f'Error al guardar: {str(e)}'}), 500

# ⚠️ Configuración para Back4App
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
