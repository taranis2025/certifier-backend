// static/script.js
const BACKEND_URL = 'https://certifier-backend.onrender.com'; // ✅ URL correcta para Render

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

    // ✅ Función para calcular hash en el navegador (sin backend)
    async function calcularHashArchivo(archivo, algoritmo = 'SHA-256') {
        const buffer = await archivo.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest(algoritmo, buffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    // ✅ Certificar usando backend
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
📅 FECHA CERTIFICACIÓN: ${c.fecha_certificacion.split('T')[0]}
💾 TAMAÑO: ${c.tamanio_bytes} bytes

🔐 HASHES DE SEGURIDAD:
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

    // ✅ Verificar integridad (sin backend — todo en el navegador)
    async function verificar() {
        const archivo = archivoInput.files[0];
        if (!archivo) {
            alert('Selecciona un archivo primero');
            return;
        }

        try {
            // Obtener hash actual del archivo
            const hashActual = await calcularHashArchivo(archivo, 'SHA-256');

            // Buscar hash original en la pantalla (si ya se certificó)
            let hashOriginal = null;
            const textoResultados = resultadosDiv.textContent;
            
            // Extraer SHA-256 de la pantalla (formato: "SHA-256: abcdef...")
            const match = textoResultados.match(/SHA-256:\s*([a-f0-9]{64})/);
            if (match) {
                hashOriginal = match[1];
            }

            if (!hashOriginal) {
                // Si no hay hash en pantalla, pedir al usuario
                hashOriginal = prompt('Ingresa el hash SHA-256 original:');
                if (!hashOriginal || hashOriginal.length !== 64 || !/^[a-f0-9]+$/.test(hashOriginal)) {
                    alert('Hash SHA-256 inválido (debe tener 64 caracteres hexadecimales)');
                    return;
                }
            }

            const integro = hashActual === hashOriginal;
            const estado = integro ? '✅ INTEGRIDAD VERIFICADA' : '❌ INTEGRIDAD COMPROMETIDA';

            const resultado = `
=== RESULTADO DE VERIFICACIÓN ===
Estado: ${estado}
Fecha: ${new Date().toISOString().split('T')[0]}

Hash original: ${hashOriginal}
Hash actual:   ${hashActual}
                `.trim();

            mostrarResultado(resultado, !integro);

        } catch (err) {
            console.error('Error al verificar:', err);
            mostrarResultado(`❌ Error: ${err.message}`, true);
        }
    }

    // ✅ Guardar certificación (usando backend)
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
