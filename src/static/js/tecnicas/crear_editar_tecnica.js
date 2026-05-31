	// Función de utilidad para manejar respuestas y sesiones expiradas
    async function handleResponse(response) {
        if (response.status === 401 || response.status === 403) {
            window.location.href = "/login"; // Redirigir si no hay sesión
            return null;
        }
        return response.ok ? response.json() : null;
    }

	const urlParams = new URLSearchParams(window.location.search);
	const idEditar = urlParams.get('idtecnica');
    let todosLosArchivos = [];
    let seleccionados = [];

    document.addEventListener('DOMContentLoaded', async () => {
		// Poner fecha de hoy por defecto
		document.getElementById('fecha').valueAsDate = new Date();

		// 2. Cargamos TODO y esperamos a que termine
		const [resDisc, resEtiq, resArchivos] = await Promise.all([
			fetch('/api/tecnicas/disciplinas'),
			fetch('/api/tecnicas/etiquetas'),
			fetch('/api/videos/archivos-videos')
		]);

        const disciplinas = await resDisc.json();
		const etiquetas = await resEtiq.json();
		todosLosArchivos = await resArchivos.json();

        // 3. Renderizamos los checkboxes

        document.getElementById('container-disciplinas').innerHTML = disciplinas.map(d => `
            <label class="flex items-center gap-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 px-3 py-1 rounded-full cursor-pointer hover:border-blue-500 transition">
                <input type="checkbox" name="disciplinas" value="${d.iddisciplina}" class="rounded">
                <span class="text-xs font-bold">${d.disciplina}</span>
            </label>
        `).join('');
        
        document.getElementById('container-etiquetas').innerHTML = etiquetas.map(e => `
            <label class="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-1 rounded cursor-pointer hover:border-blue-500 transition">
                <input type="checkbox" name="etiquetas" value="${e.idetiqueta}" class="rounded">
                <span class="text-[11px] font-medium">#${e.etiqueta}</span>
            </label>
        `).join('');


		// 4. AHORA SÍ, si hay ID, cargamos los datos de la técnica
		if (idEditar) {
			document.querySelector('h1').innerText = "Editar Técnica";
			await cargarDatosEdicion(idEditar);
		}
	
        // 2. Lógica del buscador de vídeos
		const inputBusqueda = document.getElementById('busqueda-video');
		const listaSugerencias = document.getElementById('sugerencias-videos');

		inputBusqueda.addEventListener('input', (e) => {
			const query = e.target.value.toLowerCase().trim();
			
			if (query.length < 2) { // Empezar a buscar a partir de 2 letras
				listaSugerencias.classList.add('hidden');
				return;
			}

			// Filtramos los archivos que coinciden y que NO han sido seleccionados ya
			const filtrados = todosLosArchivos.filter(f => 
				f.toLowerCase().includes(query) && !seleccionados.includes(f)
			);

			if (filtrados.length > 0) {
				listaSugerencias.innerHTML = filtrados.map(f => `
					<div onclick="seleccionarVideo('${f}')" 
						 class="px-4 py-3 hover:bg-blue-50 dark:hover:bg-blue-900/30 cursor-pointer text-sm text-slate-700 dark:text-slate-300 border-b border-slate-100 dark:border-slate-700 last:border-0">
						${f}
					</div>
				`).join('');
				listaSugerencias.classList.remove('hidden');
			} else {
				listaSugerencias.innerHTML = '<div class="px-4 py-3 text-sm text-slate-400">No se encontraron archivos</div>';
				listaSugerencias.classList.remove('hidden');
			}
		});
		
		// Cerrar sugerencias si se hace clic fuera
		document.addEventListener('click', (e) => {
			if (!inputBusqueda.contains(e.target) && !listaSugerencias.contains(e.target)) {
				listaSugerencias.classList.add('hidden');
			}
		});
		
		
		// funciones para subir vídeos desde ordenador local al servidor
		const inputSubir = document.getElementById('input-subir-archivo');
		const progresoContainer = document.getElementById('progreso-subida-container');
		const barraProgreso = document.getElementById('barra-progreso');
		const textoProgreso = document.getElementById('texto-progreso');

		inputSubir.addEventListener('change', function() {
			if (this.files.length === 0) return;

			const file = this.files[0];
			const formData = new FormData();
			formData.append('file', file);

			// Mostrar barra de progreso
			progresoContainer.classList.remove('hidden');
			barraProgreso.style.width = '0%';
			textoProgreso.innerText = `Subiendo: ${file.name} (0%)`;

			const xhr = new XMLHttpRequest();

			// Monitorizar progreso
			xhr.upload.addEventListener('progress', (e) => {
				if (e.lengthComputable) {
					const porcentaje = Math.round((e.loaded / e.total) * 100);
					barraProgreso.style.width = porcentaje + '%';
					textoProgreso.innerText = `Subiendo: ${file.name} (${porcentaje}%)`;
				}
			});

			// Finalizar subida
			xhr.onload = function() {
				if (xhr.status === 200) {
					const res = JSON.parse(xhr.responseText);
					
					// 1. Añadir el nuevo archivo a la lista global de "todos" para que el buscador lo conozca
					if (!todosLosArchivos.includes(res.filename)) {
						todosLosArchivos.push(res.filename);
					}
					
					// 2. Seleccionarlo automáticamente para la técnica
					seleccionarVideo(res.filename);

					// 3. Limpiar y ocultar barra
					setTimeout(() => {
						progresoContainer.classList.add('hidden');
						inputSubir.value = ''; // Reset input
					}, 1500);
					
					textoProgreso.innerText = "¡Subida completada!";
				} else {
					alert("Error al subir el archivo");
					progresoContainer.classList.add('hidden');
				}
			};

			xhr.open('POST', '/api/videos/subir-video'); // Asegúrate de que la ruta coincida con tu API
			xhr.send(formData);
		});


		
    });

	async function cargarDatosEdicion(id) {
		const res = await fetch(`/api/tecnicas/${id}`);
		if (!res.ok) return;
		const t = await res.json();

		document.getElementById('nombre').value = t.nombre;
		document.getElementById('descripcion').value = t.descripcion;
		document.getElementById('fecha').value = t.fecha;

		// Marcar Disciplinas
		t.disciplinas.forEach(d => {
			const cb = document.querySelector(`input[name="disciplinas"][value="${d.iddisciplina}"]`);
			if (cb) cb.checked = true;
		});

		// Marcar Etiquetas
		t.etiquetas.forEach(e => {
			const cb = document.querySelector(`input[name="etiquetas"][value="${e.idetiqueta}"]`);
			if (cb) cb.checked = true;
		});

		seleccionados = t.videos.map(v => v.video);
		renderizarSeleccionados();
	}

    function seleccionarVideo(nombre) {
        seleccionados.push(nombre);
        document.getElementById('busqueda-video').value = '';
        document.getElementById('sugerencias-videos').classList.add('hidden');
        renderizarSeleccionados();
    }

    function deseleccionarVideo(nombre) {
        seleccionados = seleccionados.filter(f => f !== nombre);
        renderizarSeleccionados();
    }

    function renderizarSeleccionados() {
        document.getElementById('videos-seleccionados').innerHTML = seleccionados.map(v => `
            <div class="flex items-center bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-3 py-1.5 rounded-full text-xs font-bold border border-blue-200 dark:border-blue-800">
                <span class="mr-2">${v}</span>
                <button type="button" onclick="deseleccionarVideo('${v}')" class="hover:text-red-500 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        `).join('');
    }

    // 3. Envío del formulario
    document.getElementById('form-tecnica').onsubmit = async (e) => {
		e.preventDefault();

		const payload = {
			nombre: document.getElementById('nombre').value,
			descripcion: document.getElementById('descripcion').value,
			fecha: document.getElementById('fecha').value,
			disciplinas_ids: Array.from(document.querySelectorAll('input[name="disciplinas"]:checked')).map(i => parseInt(i.value)),
			etiquetas_ids: Array.from(document.querySelectorAll('input[name="etiquetas"]:checked')).map(i => parseInt(i.value)),
			videos_nombres: seleccionados
		};
		
		// Verificamos idEditar para elegir URL y Método
		const url = idEditar ? `/api/tecnicas/${idEditar}` : '/api/tecnicas/';
		const metodo = idEditar ? 'PUT' : 'POST';

		try {
			const response = await fetch(url, {
				method: metodo,
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			if (response.ok) {
				const data = await response.json();
				window.location.href = `/tecnica/${data.idtecnica}`;
			} else {
				const errorData = await response.json();
				alert("Error: " + (errorData.detail || "No se pudo guardar"));
			}
		} catch (error) {
			console.error(error);
			alert("Error de conexión");
		}
    };