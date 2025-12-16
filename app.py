# app.py
from flask import Flask, request, jsonify
import hashlib
import os
import tempfile
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

# Permitir solicitudes desde tu dominio (ajusta si usas otro)
CORS(app, origins=["https://testrobert.work.gd"])

def generar_hash(archivo, algoritmo='sha256'):
    """Genera el hash de un objeto de archivo en memoria."""
    hash_obj = hashlib.new(algoritmo)
    archivo.seek(0)  # Asegurar que leemos desde el inicio
    for bloque in iter(lambda: archivo.read(4096), b""):
        hash_obj.update(bloque)
    archivo.seek(0)  # Restablecer puntero para reutilización si es necesario
    return hash_obj.hexdigest()

@app.route('/')
def home():
    return jsonify({
        "mensaje": "Certificador de Archivos - Backend en Railway",
        "status": "ok"
    })

@app.route('/api/certificar', methods=['POST'])
def certificar():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    archivo = request.files['archivo']
    propietario = request.form.get('propietario', 'Usuario').strip() or 'Usuario'

    if archivo.filename == '':
        return jsonify({'error': 'Archivo sin nombre'}), 400

    try:
        # Lee metadata del archivo en memoria (sin guardarlo)
        archivo.seek(0, os.SEEK_END)
        tamanio = archivo.tell()
        archivo.seek(0)

        # Generar hashes
        hashes = {
            'sha256': generar_hash(archivo, 'sha256'),
            'sha1': generar_hash(archivo, 'sha1'),
            'md5': generar_hash(archivo, 'md5')
        }

        resultado = {
            "nombre_archivo": archivo.filename,
            "propietario": propietario,
            "fecha_certificacion": datetime.utcnow().isoformat() + "Z",
            "tamanio_bytes": tamanio,
            "hashes": hashes,
            "estado": "CERTIFICADO"
        }

        return jsonify({
            "success": True,
            "certificacion": resultado
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

# Puerto dinámico para Railway y otros proveedores
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
