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

 