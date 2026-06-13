document.addEventListener('DOMContentLoaded', function() {
    cargarPreferenciasUsuario();
    actualizarEstadoBotonPush();
    
    const btn = document.getElementById('btn-notificaciones');
    if (btn) {
        btn.addEventListener('click', function(e) {
            const permisoActual = Notification.permission;

            if (permisoActual === 'granted') {
                mostrarToast("Las alertas ya están activas en este navegador. Si deseas silenciarlas por completo, puedes hacerlo revocando el permiso desde los ajustes del candado en la barra de direcciones.");
            } 
            else if (permisoActual === 'denied') {
                mostrarToast("Las notificaciones están bloqueadas en este navegador. Haz clic en el icono del candado junto a la URL para volver a activarlas.");
            } 
            else {
                // Estado 'default': Primera vez. Bloqueamos interfaz y dejamos actuar al prompt nativo
                btn.disabled = true;
                btn.innerText = "Esperando confirmación...";
                
                if (window.inicializarPush) {
                    window.inicializarPush()
                        .then(() => {
                            // Se ejecuta si el alumno acepta el prompt del sistema 🌟
                            actualizarEstadoBotonPush();
                        })
                        .catch(err => {
                            console.error("Error al registrar de primeras:", err);
                            actualizarEstadoBotonPush();
                        });
                } else {
                    // Fallback de contingencia si push-client.js expone la lógica por eventos alternativos
                    setTimeout(actualizarEstadoBotonPush, 1500);
                }
            }
        });
    }

    // Si vuelve a la pestaña tras cambiar algo en el candado, refresca dinámicamente
    window.addEventListener('focus', actualizarEstadoBotonPush);
});

function actualizarEstadoBotonPush() {
    const btn = document.getElementById('btn-notificaciones');
    const txt = document.getElementById('txt-estado-dispositivo');
    
    if (!btn || !txt) return;

    if (!('Notification' in window)) {
        txt.innerText = "Este navegador no es compatible con las notificaciones push.";
        btn.innerHTML = "❌ No compatible";
        btn.className = "w-full sm:w-auto bg-amber-500 text-white font-bold text-xs py-2.5 px-4 rounded-xl cursor-not-allowed shadow-sm";
        btn.disabled = true;
        return;
    }

    const permisoActual = Notification.permission;

    if (permisoActual === 'granted') {
        txt.innerText = "Las alertas ya están activas en este dispositivo. Si deseas silenciarlas, debes hacerlo revocando el permiso desde los ajustes del navegador.";
        btn.innerHTML = "✓ Activado";
        btn.className = "w-full sm:w-auto bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-bold text-xs py-2.5 px-4 rounded-xl border border-emerald-200 dark:border-emerald-900/60 shadow-none transition-all";
        btn.disabled = false; // Permitimos clic para que salte la nota explicativa
    } 
    else if (permisoActual === 'denied') {
        txt.innerText = "Has bloqueado las notificaciones en este dispositivo. Revisa los ajustes del navegador para restablecerlas.";
        btn.innerHTML = "⚠️ Bloqueado";
        btn.className = "w-full sm:w-auto bg-red-100 dark:bg-red-950/30 text-red-600 dark:text-red-400 font-bold text-xs py-2.5 px-4 rounded-xl border border-red-200 dark:border-red-900/30 shadow-none transition-all";
        btn.disabled = false; // Permitimos clic para instruir con la nota
    } 
    else {
        txt.innerText = "Activa los permisos para recibir alertas inmediatas en este equipo.";
        btn.innerHTML = "🔔 Activar";
        btn.className = "w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2.5 px-4 rounded-xl transition-all shadow-sm";
        btn.disabled = false;
    }
}

// Función auxiliar para desplegar el Toast animado con Tailwind 🚀
function mostrarToast(mensaje) {
    const toast = document.getElementById('toast-notificacion');
    const toastMsg = document.getElementById('toast-mensaje');
    
    if (!toast || !toastMsg) return;

    toastMsg.innerText = mensaje;
    
    // Quitamos clases de ocultación y lo movemos hacia abajo con transiciones fluidas
    toast.classList.remove('opacity-0', 'translate-y-[-20px]', 'pointer-events-none');
    toast.classList.add('opacity-100', 'translate-y-0');

    // Desvanecer automáticamente a los 6 segundos para dar tiempo a leerlo entero
    setTimeout(() => {
        toast.classList.remove('opacity-100', 'translate-y-0');
        toast.classList.add('opacity-0', 'translate-y-[-20px]', 'pointer-events-none');
    }, 6000);
}

// Carga de preferencias de la tabla (Se mantiene limpia)
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
