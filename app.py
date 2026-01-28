# app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Crear la aplicación
app = Flask(__name__)
CORS(app, origins=["https://testrobert.work.gd"])

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Backend activo"})

@app.route('/api/test')
def test():
    return jsonify({"test": "funciona"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor en puerto {port}")  # Este mensaje aparecerá en los logs
    app.run(host='0.0.0.0', port=port, debug=False)
