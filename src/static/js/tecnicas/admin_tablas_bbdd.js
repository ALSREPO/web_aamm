	// Función de utilidad para manejar respuestas y sesiones expiradas
    async function handleResponse(response) {
        if (response.status === 401 || response.status === 403) {
            window.location.href = "/login"; // Redirigir si no hay sesión
            return null;
        }
        return response.ok ? response.json() : null;
    }
	
    document.addEventListener('DOMContentLoaded', () => {
        cargarTablas();
        ejecutarAuditoria();
    });

    // --- LÓGICA DE TABLAS (Disciplinas/Etiquetas) ---
    async function cargarTablas() {
        const [resD, resE] = await Promise.all([
            fetch('/api/tecnicas/disciplinas'),
            fetch('/api/tecnicas/etiquetas')
        ]);
        
        const disciplinas = await resD.json();
        const etiquetas = await resE.json();

        document.getElementById('lista-disciplinas').innerHTML = disciplinas.map(d => `
            <div class="flex justify-between items-center py-3">
                <span class="font-medium text-slate-700 dark:text-slate-300 uppercase text-xs">${d.disciplina}</span>
                <button onclick="borrarElemento('disciplinas', ${d.iddisciplina})" class="text-slate-300 hover:text-red-500 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
            </div>
        `).join('') || '<p class="text-slate-400 text-xs italic py-4">Vacío</p>';

        document.getElementById('lista-etiquetas').innerHTML = etiquetas.map(e => `
            <div class="flex justify-between items-center py-3">
                <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">#${e.etiqueta}</span>
                <button onclick="borrarElemento('etiquetas', ${e.idetiqueta})" class="text-slate-300 hover:text-red-500 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
            </div>
        `).join('') || '<p class="text-slate-400 text-xs italic py-4">Vacío</p>';
    }

    async function nuevoElemento(tipo) {
        const nombre = prompt(`Nombre para la nueva ${tipo === 'disciplinas' ? 'disciplina' : 'etiqueta'}:`);
        if (!nombre) return;
        const res = await fetch(`/api/tecnicas/${tipo}?nombre=${encodeURIComponent(nombre)}`, { method: 'POST' });
        if (res.ok) cargarTablas();
    }

    async function borrarElemento(tipo, id) {
        if (!confirm("¿Borrar elemento?")) return;
        const res = await fetch(`/api/tecnicas/${tipo}/${id}`, { method: 'DELETE' });
        if (res.ok) cargarTablas();
        else alert("Error: Elemento en uso en alguna técnica.");
    }

    // --- LÓGICA DE AUDITORÍA (Vídeos) ---
    async function ejecutarAuditoria() {
        const res = await fetch('/api/videos/auditoria-videos');
        const data = await res.json();

        // Actualizar Badge en el summary
        const badge = document.getElementById('badge-huerfanos');
        if (data.huerfanos.length > 0) {
            badge.innerText = `${data.huerfanos.length} huérfanos`;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        document.getElementById('stats-auditoria').innerHTML = `
			<div class="p-4 bg-slate-50 dark:bg-slate-900/50 rounded-2xl">
				<p class="text-[10px] font-black text-slate-400 uppercase">Archivos totales</p>
				<p class="text-2xl font-bold text-slate-700 dark:text-slate-200">${data.total_fisicos}</p>
			</div>
			<div class="p-4 bg-slate-50 dark:bg-slate-900/50 rounded-2xl">
				<p class="text-[10px] font-black text-slate-400 uppercase">En uso</p>
				<p class="text-2xl font-bold text-blue-600">${data.total_en_uso}</p>
			</div>
			<div class="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-2xl">
				<p class="text-[10px] font-black text-amber-600 uppercase">Huérfanos</p>
				<p class="text-2xl font-bold text-amber-700 dark:text-amber-400">${data.huerfanos.length}</p>
			</div>
        `;

        const lista = document.getElementById('lista-huerfanos');
        if (data.huerfanos.length === 0) {
            lista.innerHTML = '<p class="col-span-full text-sm py-4 text-emerald-500 font-medium">✨ Servidor optimizado. No hay nada que limpiar.</p>';
            return;
        }

        lista.innerHTML = data.huerfanos.map(f => `
            <div class="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl">
                <span class="text-[10px] font-mono text-slate-500 truncate mr-2">${f}</span>
                <button onclick="borrarArchivoFisico('${f}')" class="text-red-400 hover:text-red-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
            </div>
        `).join('');
    }

    async function borrarArchivoFisico(nombre) {
        if (!confirm(`¿Eliminar ${nombre} del disco?`)) return;
        const res = await fetch(`/api/videos/eliminar-archivo-fisico?filename=${encodeURIComponent(nombre)}`, { method: 'DELETE' });
        if (res.ok) ejecutarAuditoria();
    }