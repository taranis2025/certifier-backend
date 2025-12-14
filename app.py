import os
import tempfile
from flask import send_file, jsonify
import json

@app.route('/api/guardar-certificado', methods=['POST'])
def guardar_certificado():
    try:
        data = request.get_json()
        cert_data = data.get('certificacion')
        
        # ✅ CORREGIDO: Sintaxis válida
        if not cert_
            return jsonify({'error': 'Datos de certificación no válidos'}), 400

        # Generar JSON como bytes
        json_bytes = json.dumps(cert_data, indent=2, ensure_ascii=False).encode('utf-8')
        
        # Crear archivo temporal Y eliminarlo después de enviar
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'certificado.json')
        
        with open(temp_path, 'wb') as f:
            f.write(json_bytes)
        
        # Enviar y luego eliminar
        def remove_file():
            try:
                os.remove(temp_path)
            except:
                pass

        # Flask >= 2.0 permite "as_attachment" sin problemas
        response = send_file(temp_path, as_attachment=True, download_name='certificado.json')
        remove_file()  # ¡No ideal! Pero suficiente para entornos simples
        return response

    except Exception as e:
        return jsonify({'error': f'Error al guardar: {str(e)}'}), 500
