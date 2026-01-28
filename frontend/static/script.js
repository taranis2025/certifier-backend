// test-script.js
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
        
        // Scroll to results
        resultadosDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // ✅ FUNCION CERTIFICAR
    function certificar() {
        const archivo = archivoInput.files[0];
        const propietario = propietarioInput.value || 'Usuario de Prueba';

        if (!archivo) {
            alert('⚠️ Selecciona un archivo primero');
            return;
        }

        mostrarResultado('🔄 Certificando archivo...');

        const formData = new FormData();
        formData.append('archivo', archivo);
        formData.append('propietario', propietario);

        fetch(`${BACKEND_URL}/api/certificar`, {
            method: 'POST',
            body: formData
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (data.success) {
                ultimaCertificacion = data.certificacion;
                const c = data.certificacion;
                const reporte = `
✅ CERTIFICACIÓN EXITOSA

📄 ARCHIVO: ${c.nombre_archivo}
👤 PROPIETARIO: ${c.propietario}
📅 FECHA: ${c.fecha_certificacion.split('T')[0]}
💾 TAMAÑO: ${c.tamanio_bytes} bytes

🔐 HASHES DE SEGURIDAD:
   • SHA-256: ${c.hashes.sha256}
   • SHA-1:   ${c.hashes.sha1}
   • MD5:     ${c.hashes.md5}

💡 Copia el hash SHA-256 para la verificación
                `.trim();
                mostrarResultado(reporte);
            } else {
                mostrarResultado(`❌ ERROR DE CERTIFICACIÓN:\n${data.error}`, true);
            }
        })
        .catch(err => {
            console.error('Error de certificación:', err);
            mostrarResultado(`❌ ERROR DE RED:\n${err.message}\n\nVerifica que el backend esté activo en:\n${BACKEND_URL}`, true);
        });
    }

    // ✅ FUNCION VERIFICAR
    function verificarIntegridad() {
        const archivo = archivoInput.files[0];
        if (!archivo) {
            alert('⚠️ Selecciona un archivo primero');
            return;
        }

        const hashOriginal = prompt('🔐 Ingresa el hash SHA-256 original:');
        if (!hashOriginal) {
            alert('⚠️ Operación cancelada');
            return;
        }

        if (hashOriginal.length !== 64 || !/^[a-f0-9]+$/.test(hashOriginal.toLowerCase())) {
            alert('❌ Hash SHA-256 inválido!\nDebe tener 64 caracteres hexadecimales.');
            return;
        }

        mostrarResultado('🔍 Verificando integridad...');

        const formData = new FormData();
        formData.append('archivo', archivo);
        formData.append('hash_original', hashOriginal.toLowerCase());

        fetch(`${BACKEND_URL}/api/verificar`, {
            method: 'POST',
            body: formData
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (data.success) {
                const estado = data.integro ? '✅ INTEGRIDAD VERIFICADA' : '❌ INTEGRIDAD COMPROMETIDA';
                const resultado = `
${estado}

📊 RESULTADO DE VERIFICACIÓN:
Fecha: ${data.verificacion_fecha.split('T')[0]}

Hash original: ${data.hash_original}
Hash actual:   ${data.hash_actual}

${data.integro ? '✅ El archivo NO ha sido modificado' : '⚠️ El archivo HA SIDO MODIFICADO'}
                `.trim();
                mostrarResultado(resultado, !data.integro);
            } else {
                mostrarResultado(`❌ ERROR DE VERIFICACIÓN:\n${data.error}`, true);
            }
        })
        .catch(err => {
            console.error('Error de verificación:', err);
            mostrarResultado(`❌ ERROR DE RED:\n${err.message}\n\nVerifica que el backend esté activo en:\n${BACKEND_URL}`, true);
        });
    }

    // ✅ FUNCION GUARDAR
    function guardarCertificado() {
        if (!ultimaCertificacion) {
            alert('⚠️ Primero certifica un archivo');
            return;
        }

        fetch(`${BACKEND_URL}/api/guardar-certificado`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ certificacion: ultimaCertificacion })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al generar el certificado');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `certificado_${ultimaCertificacion.hashes.sha256.substring(0, 8)}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            mostrarResultado('✅ Certificado descargado exitosamente!');
        })
        .catch(err => {
            console.error('Error al guardar:', err);
            alert('❌ Error al descargar: ' + err.message);
        });
    }
});
