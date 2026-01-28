// static/script.js
const BACKEND_URL = 'https://certifier-backend.b4a.app';

document.addEventListener('DOMContentLoaded', () => {
    const archivoInput = document.getElementById('archivo');
    const propietarioInput = document.getElementById('propietario');
    const btnCertificar = document.getElementById('btn-certificar');
    const btnVerificar = document.getElementById('btn-verificar');
    const btnGuardar = document.getElementById('btn-guardar');
    const resultadosDiv = document.getElementById('resultados');

    let ultimaCertificacion = null;

    btnCertificar.addEventListener('click', certificar);
    btnVerificar.addEventListener('click', verificarIntegridad);
    btnGuardar.addEventListener('click', guardarCertificado);

    function mostrarResultado(texto, esError = false) {
        resultadosDiv.textContent = texto;
        resultadosDiv.className = `results ${esError ? 'error' : 'success'}`;
    }

    function certificar() {
        const archivo = archivoInput.files[0];
        const propietario = propietarioInput.value || 'Usuario';

        if (!archivo) {
            alert('Selecciona un archivo primero');
            return;
        }

        const formData = new FormData();
        formData.append('archivo', archivo);
        formData.append('propietario', propietario);

        fetch(`${BACKEND_URL}/api/certificar`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                ultimaCertificacion = data.certificacion;
                const c = data.certificacion;
                const reporte = `
📄 ARCHIVO: ${c.nombre_archivo}
👤 PROPIETARIO: ${c.propietario}
📅 FECHA: ${c.fecha_certificacion.split('T')[0]}
💾 TAMAÑO: ${c.tamanio_bytes} bytes

🔐 HASHES:
   • SHA-256: ${c.hashes.sha256}
   • SHA-1:   ${c.hashes.sha1}
   • MD5:     ${c.hashes.md5}

✅ ESTADO: ${c.estado}
                `.trim();
                mostrarResultado(reporte);
            } else {
                mostrarResultado(`❌ ERROR: ${data.error}`, true);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarResultado(`❌ Error: ${err.message}`, true);
        });
    }

    function verificarIntegridad() {
        const archivo = archivoInput.files[0];
        if (!archivo) {
            alert('Selecciona un archivo primero');
            return;
        }

        const hashOriginal = prompt('Ingresa el hash SHA-256 original:');
        if (!hashOriginal) {
            return;
        }

        const formData = new FormData();
        formData.append('archivo', archivo);
        formData.append('hash_original', hashOriginal);

        fetch(`${BACKEND_URL}/api/verificar`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const estado = data.integro ? '✅ INTEGRIDAD VERIFICADA' : '❌ INTEGRIDAD COMPROMETIDA';
                const resultado = `
=== RESULTADO DE VERIFICACIÓN ===
Estado: ${estado}
Fecha: ${data.verificacion_fecha.split('T')[0]}

Hash original: ${data.hash_original}
Hash actual:   ${data.hash_actual}
                `.trim();
                mostrarResultado(resultado, !data.integro);
            } else {
                mostrarResultado(`❌ ERROR: ${data.error}`, true);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarResultado(`❌ Error: ${err.message}`, true);
        });
    }

    function guardarCertificado() {
        if (!ultimaCertificacion) {
            alert('Primero certifica un archivo');
            return;
        }

        fetch(`${BACKEND_URL}/api/guardar-certificado`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ certificacion: ultimaCertificacion })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'certificado.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(err => {
            console.error('Error al guardar:', err);
            alert('Error al descargar: ' + err.message);
        });
    }
});
