	// Función de utilidad para manejar respuestas y sesiones expiradas
    async function handleResponse(response) {
        if (response.status === 401 || response.status === 403) {
            window.location.href = "/login"; // Redirigir si no hay sesión
            return null;
        }
        return response.ok ? response.json() : null;
    }
    // Variables globales leyendo el "puente" del HTML
    const idtecnica = window.DETALLE_ID_TECNICA;


    document.addEventListener('DOMContentLoaded', async () => {
        try {
            const response = await fetch(`/api/tecnicas/${idtecnica}`);
            if (!response.ok) throw new Error("Técnica no encontrada");
            const t = await response.json();

            // Rellenar textos: nombre, descripción y fecha
            document.getElementById('titulo-tecnica').innerText = t.nombre;
            document.getElementById('desc-tecnica').innerText = t.descripcion;
            // document.getElementById('fecha-tecnica').innerText = new Date(t.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
			
            const fechaFormateada = new Date(t.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
			document.getElementById('fecha-tecnica').innerHTML = `
				<a href="/?fecha=${t.fecha}" class="hover:text-blue-600 transition">${fechaFormateada}</a>
			`;

            // Rellenar Disciplinas y Etiquetas (estilo badges)
            document.getElementById('disciplinas-detalle').innerHTML = t.disciplinas.map(d => `
				<a href="/?disciplina_id=${d.iddisciplina}" 
				   class="bg-slate-900 text-white text-[10px] px-2 py-1 rounded-md font-bold uppercase hover:bg-blue-600 transition">
				   ${d.disciplina}
				</a>
			`).join('');

			document.getElementById('etiquetas-detalle').innerHTML = t.etiquetas.map(e => `
				<a href="/?etiqueta_id=${e.idetiqueta}" 
				   class="text-blue-600 dark:text-blue-400 text-[10px] font-bold bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded border border-blue-100 dark:border-blue-800 hover:border-blue-500 transition">
				   #${e.etiqueta}
				</a>
			`).join('');


             // Lógica de vídeos
            const wrapperVideo = document.getElementById('wrapper-video');
			const mainVideo = document.getElementById('main-video');

			if (t.videos && t.videos.length > 0) {
				// Si hay vídeos, mostramos el contenedor y cargamos el primero
				wrapperVideo.classList.remove('hidden');
				mainVideo.src = `/static/videos/${t.videos[0].video}`;
				
				if (t.videos.length > 1) {
					document.getElementById('lista-videos').innerHTML = t.videos.map((v, index) => `
						<button onclick="cambiarVideo('/static/videos/${v.video}')" 
							class="flex-none w-32 aspect-video bg-slate-900 rounded-xl overflow-hidden border-2 border-transparent hover:border-blue-500 transition focus:border-blue-500 relative group">
							<div class="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/10 transition text-[10px] text-white font-bold">VÍDEO ${index + 1}</div>
						</button>
					`).join('');
				} else {
					document.getElementById('lista-videos').innerHTML = ''; // Limpiar si solo hay uno
				}
			} else {
				// Si no hay vídeos, el wrapperVideo se queda con 'hidden'
				console.log("Esta técnica no tiene vídeos.");
			}

            document.getElementById('detalle-contenedor').classList.remove('hidden');

        } catch (error) {
            console.error(error);
            document.getElementById('detalle-contenedor').innerHTML = '<p class="text-center py-20">Error al cargar la técnica.</p>';
            document.getElementById('detalle-contenedor').classList.remove('hidden');
        }
    });

    function cambiarVideo(src) {
        const video = document.getElementById('main-video');
        video.src = src;
        video.play();
    }
	
	async function confirmarBorrado(id) {
        if (confirm('¿Estás seguro de que deseas eliminar esta técnica? Esta acción no se puede deshacer.')) {
            try {
                const response = await fetch(`/api/tecnicas/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    window.location.href = '/'; // Redirigir al listado tras borrar
                } else {
                    alert('Error al eliminar la técnica');
                }
            } catch (error) {
                console.error(error);
                alert('Error de conexión');
            }
        }
    }