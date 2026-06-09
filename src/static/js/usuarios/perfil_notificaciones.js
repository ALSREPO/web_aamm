document.addEventListener('DOMContentLoaded', function() {
    cargarPreferenciasUsuario();
});

function cargarPreferenciasUsuario() {
    fetch('/api/notificaciones/preferencias')
        .then(response => response.json())
        .then(preferencias => {
            const tbody = document.getElementById('contenedor-preferencias');
            tbody.innerHTML = ''; 

            if (preferencias.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="p-6 text-center text-xs text-slate-400">No hay servicios de alerta configurados.</td></tr>';
                return;
            }

            preferencias.forEach(pref => {
                const fila = document.createElement('tr');
                fila.className = "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300";
                
                fila.innerHTML = `
                    <td class="py-4 px-4">
                        <span class="font-bold text-slate-800 dark:text-slate-200 block">${pref.nombre_pantalla}</span>
                        <span class="text-xs text-slate-400 dark:text-slate-500 block mt-0.5">${pref.descripcion || ''}</span>
                    </td>
                    <td class="py-4 px-4 text-center">
                        <input type="checkbox" 
                               class="check-preferencia h-4 w-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500 bg-slate-50 dark:bg-slate-900" 
                               data-evento="${pref.nombre_clave}" 
                               data-canal="push" 
                               ${pref.canal_push ? 'checked' : ''}>
                    </td>
                    <td class="py-4 px-4 text-center">
                        <span class="inline-flex items-center rounded-md bg-slate-50 dark:bg-slate-900 px-2 py-1 text-[10px] font-black uppercase text-slate-400 dark:text-slate-600 border border-slate-100 dark:border-slate-800/60 select-none">
                            Próximamente
                        </span>
                    </td>
                `;
                tbody.appendChild(fila);
            });

            asignarEventosCheckboxes();
        })
        .catch(err => {
            console.error("Error al renderizar preferencias:", err);
            document.getElementById('contenedor-preferencias').innerHTML = 
                '<tr><td colspan="3" class="p-6 text-center text-xs text-red-500 font-bold uppercase">Error al sincronizar preferencias.</td></tr>';
        });
}

function asignarEventosCheckboxes() {
    const checkboxes = document.querySelectorAll('.check-preferencia');
    checkboxes.forEach(chk => {
        chk.addEventListener('change', function() {
            const nombreClave = this.getAttribute('data-evento');
            const canal = this.getAttribute('data-canal');
            const nuevoValor = this.checked;

            this.disabled = true;

            fetch('/api/notificaciones/preferencias/guardar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre_clave: nombreClave,
                    canal: canal,
                    valor: nuevoValor
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status !== 'ok') {
                    this.checked = !nuevoValor;
                }
            })
            .catch(err => {
                console.error("Error guardando preferencia:", err);
                this.checked = !nuevoValor;
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    });
}



// Añadir al final de tu DOMContentLoaded actual o donde gestiones la inicialización
document.addEventListener('DOMContentLoaded', function() {
    actualizarEstadoBotonPush();
    
    // Si el usuario hace clic, dejamos que tu push-client.js maneje la lógica de suscripción,
    // pero tras un segundo refrescamos la estética del botón por si aceptó el prompt.
    const btn = document.getElementById('btn-notificaciones');
    if (btn) {
        btn.addEventListener('click', function() {
            setTimeout(actualizarEstadoBotonPush, 1200);
        });
    }
});

function actualizarEstadoBotonPush() {
    const btn = document.getElementById('btn-notificaciones');
    const txt = document.getElementById('txt-estado-dispositivo');
    
    if (!btn || !txt) return;

    // 1. Validar si el navegador del alumno soporta Service Workers
    if (!('Notification' in window)) {
        txt.innerText = "Este navegador no es compatible con las notificaciones push.";
        btn.innerHTML = "❌ No compatible";
        btn.className = "w-full sm:w-auto bg-amber-500 text-white font-bold text-xs py-2.5 px-4 rounded-xl cursor-not-allowed shadow-sm";
        btn.disabled = true;
        return;
    }

    // 2. Modificar la interfaz según el permiso otorgado por el sistema operativo
    const permisoActual = Notification.permission;

    if (permisoActual === 'granted') {
        txt.innerText = "Este dispositivo está registrado y listo para recibir alertas instantáneas.";
        btn.innerHTML = "✓ Activado en este dispositivo";
        // Estética gris-verdosa suave de deshabilitado elegante
        btn.className = "w-full sm:w-auto bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-bold text-xs py-2.5 px-4 rounded-xl cursor-default border border-emerald-200 dark:border-emerald-900/60 shadow-none";
        btn.disabled = true; 
    } 
    else if (permisoActual === 'denied') {
        txt.innerText = "Has bloqueado las notificaciones en este navegador. Revisa el candado de la URL para restablecerlas.";
        btn.innerHTML = "❌ Bloqueado en el navegador";
        btn.className = "w-full sm:w-auto bg-red-100 dark:bg-red-950/30 text-red-600 dark:text-red-400 font-bold text-xs py-2.5 px-4 rounded-xl cursor-not-allowed border border-red-200 dark:border-red-900/30 shadow-none";
        btn.disabled = true;
    } 
    else {
        // Estado por defecto: 'default' (Aún no ha decidido)
        txt.innerText = "Activa los permisos para recibir alertas inmediatas en este equipo.";
        btn.innerHTML = "🔔 Activar en este dispositivo";
        btn.className = "w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2.5 px-4 rounded-xl transition-all shadow-sm";
        btn.disabled = false;
    }
}