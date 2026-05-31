    // Variables globales leyendo el "puente" del HTML
    let skip = 0;
    const limit = window.CONFIG_LIMIT || 10; // Si falla, por defecto usa 10
    let filtrosActuales = "";

    const userRole = window.CONFIG_USER_ROLE || 0; // Si falla, por defecto usa rol 0
    const grid = document.getElementById('grid-tecnicas');
    const statusFiltros = document.getElementById('status-filtros');
    const textoFiltro = document.getElementById('texto-filtro');

    // Carga inicial
    document.addEventListener('DOMContentLoaded', () => cargarTecnicas());
	document.addEventListener('DOMContentLoaded', async () => {
		// 1. Leer parámetros de la URL (si venimos de otra página, por ejmplo, el detalle)
		const urlParams = new URLSearchParams(window.location.search);
		
		// 2. Si hay parámetros, guardarlos en nuestra variable global y cargar
		if (urlParams.toString()) {
			filtrosActuales = urlParams.toString();
			
			// Opcional: Rellenar visualmente el input de fecha si viene en la URL
			if(urlParams.has('fecha')) document.getElementById('input-fecha').value = urlParams.get('fecha');
			
			cargarTecnicas(filtrosActuales);
		} else {
			cargarTecnicas(); // Carga normal sin filtros
		}

		await cargarAuxiliares(); // Cargar los checkboxes de etiquetas/disciplinas
	});


    // 1. Cargar datos del buscador (Disciplinas y Etiquetas)
    async function cargarAuxiliares() {
        const [resD, resE] = await Promise.all([
            fetch('/api/tecnicas/disciplinas'),
            fetch('/api/tecnicas/etiquetas')
        ]);
        const disciplinas = await resD.json();
        const etiquetas = await resE.json();

        // Disciplinas (checkbox para multiselección)
        document.getElementById('container-disciplinas').innerHTML = disciplinas.map(d => `
            <label class="flex items-center gap-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 px-3 py-1 rounded-full cursor-pointer hover:border-blue-500 transition">
                <input type="checkbox" name="disciplina_id" value="${d.iddisciplina}" class="rounded">
                <span class="text-xs font-bold">${d.disciplina}</span>
            </label>
        `).join('');

        // Etiquetas (checkbox para multiselección)
        document.getElementById('container-etiquetas').innerHTML = etiquetas.map(e => `
            <label class="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-1 rounded cursor-pointer hover:border-blue-500 transition">
                <input type="checkbox" name="etiqueta_id" value="${e.idetiqueta}" class="rounded">
                <span class="text-[11px] font-medium">#${e.etiqueta}</span>
            </label>
        `).join('');
    }
    // Llamar al inicio
    cargarAuxiliares();

    // 2. Función para ocultar/mostrar buscador
    function toggleBuscador() {
        const panel = document.getElementById('panel-buscador');
        const texto = document.getElementById('btn-buscador-texto');
        panel.classList.toggle('hidden');
        texto.innerText = panel.classList.contains('hidden') ? 'Mostrar Buscador' : 'Ocultar Buscador';
    }


    // 3. Variable para el icono del sentido (Fecha, ID, Nombre)
    function toggleSentido() {
        const input = document.getElementById('input-sentido');
        const icon = document.getElementById('icon-sentido');
        
        // 1. Alternar valores
        if (input.value === 'desc') {
            input.value = 'asc';
            icon.innerText = '↑';
        } else {
            input.value = 'desc';
            icon.innerText = '↓';
        }
        
        // 2. Disparar la búsqueda automáticamente
        // Llamamos al submit del formulario de forma programada
        document.getElementById('form-busqueda').requestSubmit();
    }

    // 4. Manejar el envío del formulario de búsqueda	
    document.getElementById('form-busqueda').onsubmit = (e) => {
        e.preventDefault();
        const params = new URLSearchParams();

        const q = document.getElementById('input-q').value;
        const fecha = document.getElementById('input-fecha').value;
        const orden = document.getElementById('select-orden').value;
        const sentido = document.getElementById('input-sentido').value;

        if(q) params.append('q', q);
        if(fecha) params.append('fecha', fecha);
        params.append('ordenar_por', orden);
        params.append('sentido', sentido);
        
        // Disciplinas y Etiquetas (recorrer checkboxes como antes)
        const formData = new FormData(e.target);
        formData.getAll('disciplina_id').forEach(id => params.append('disciplina_id', id));
        formData.getAll('etiqueta_id').forEach(id => params.append('etiqueta_id', id));

        filtrosActuales = params.toString();
        cargarTecnicas(filtrosActuales);
    };

    // 5. Función cargarTecnicas con paginación y gestión de resultados
    async function cargarTecnicas(parametros = "", esCargaMas = false) {
        const grid = document.getElementById('grid-tecnicas');
        const statusFiltros = document.getElementById('status-filtros');
        const textoFiltro = document.getElementById('texto-filtro');

        // 1. Gestionar el inicio de la carga
        if (!esCargaMas) {
            skip = 0; // Reiniciamos el contador si es búsqueda nueva
            grid.innerHTML = '<div class="col-span-full text-center py-10"><p class="animate-pulse">Buscando técnicas...</p></div>';
        }

        try {
            // 2. Construir la URL con paginación
            const url = `/api/tecnicas/?${parametros}&skip=${skip}&limit=${limit}`;
            const response = await fetch(url);
            
            // Importante: Aquí recibimos el objeto PaginaTecnicas
            const data = await response.json(); 

            // 3. Actualizar el contador con data.total
            if (parametros || data.total > 0) {
                statusFiltros.classList.remove('hidden');
                textoFiltro.innerText = `Se han encontrado ${data.total} técnicas en total.`;
            } else {
                statusFiltros.classList.add('hidden');
            }

            // 4. Si no hay resultados
            if (data.resultados.length === 0 && !esCargaMas) {
                grid.innerHTML = '<div class="col-span-full text-center py-20 text-slate-500">No hay resultados para esta búsqueda. <br> <button onclick="limpiarFiltros()" class="text-blue-700 dark:text-blue-300 hover:underline text-sm font-bold">Limpiar todos los filtros</button> </div></div>';
                return;
            }

            // 5. Renderizar las tarjetas usando data.resultados
            const html = data.resultados.map(t => generarCard(t)).join('');
            
            if (esCargaMas) {
                grid.insertAdjacentHTML('beforeend', html);
            } else {
                grid.innerHTML = html;
            }

            // 6. Actualizar el skip y gestionar el botón "Ver más"
            skip += data.resultados.length;
            gestionarBotonVerMas(data.total);

        } catch (error) {
            console.error("Fallo en el renderizado:", error);
            grid.innerHTML = '<p class="text-red-500 text-center col-span-full font-bold">Error al procesar los datos de la biblioteca.</p>';
        }
    }


    // 6. Función que genera las tarjetas con la información de cada técnica, incluyendo disciplinas, etiquetas y botones de admin si el usuario tiene permisos
    function generarCard(t) {
        // 1. Formatear la fecha para que no de error
        const fechaStr = t.fecha ? new Date(t.fecha).toLocaleDateString('es-ES') : 'Sin fecha';
        
        // Importante: t.fecha viene como "2025-04-18" (formato ISO)
        const fechaVisual = new Date(t.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });

        // 2. Badges de Disciplinas (¡CUIDADO AQUÍ CON EL NOMBRE DEL CAMPO!)
        // En tu JSON es d.disciplina, NO d.nombre
        const disciplinasHTML = (t.disciplinas || []).map(d => `
            <span onclick="event.stopPropagation(); cargarTecnicas('disciplina_id=${d.iddisciplina}')" 
                class="cursor-pointer bg-slate-800 dark:bg-slate-700 hover:bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded transition-colors uppercase">
                ${d.disciplina} 
            </span>
        `).join('');

        // 3. Badges de Etiquetas
        // En tu JSON es e.etiqueta, NO e.nombre
        const etiquetasHTML = (t.etiquetas || []).map(e => `
            <span onclick="event.stopPropagation(); cargarTecnicas('etiqueta_id=${e.idetiqueta}')" 
                class="cursor-pointer text-blue-600 dark:text-blue-400 text-[10px] font-bold bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-800 hover:bg-blue-100 transition-colors">
                #${e.etiqueta}
            </span>
        `).join('');

        // 4. Botones Admin
        const botonesAdmin = userRole >= 2 ? `
            <div class="flex gap-2 mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                <button onclick="event.stopPropagation(); editarTecnica(${t.idtecnica})" class="flex-1 text-slate-600 dark:text-slate-300 text-xs font-bold py-2 bg-slate-100 dark:bg-slate-700 rounded-lg hover:bg-slate-200 transition">EDITAR</button>
                <button onclick="event.stopPropagation(); borrarTecnica(${t.idtecnica})" class="flex-1 text-red-600 text-xs font-bold py-2 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 transition">BORRAR</button>
            </div>
        ` : '';

        // 5. El retorno del HTML (asegúrate de que los campos t.nombre y t.descripcion coincidan)
        return `
            <div class="group bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col h-full hover:shadow-xl hover:border-blue-300 dark:hover:border-blue-500 transition-all duration-300 cursor-pointer" 
                onclick="location.href='/tecnica/${t.idtecnica}'">
                
                <div class="p-5 flex-grow">
                    <div class="flex justify-between items-center mb-4">
                        <span onclick="event.stopPropagation(); filtrarPorFecha('${t.fecha}')" 
                            class="cursor-pointer hover:text-blue-600 transition-colors text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                            ${fechaVisual}
                        </span>
                        
                        ${t.cantidad_videos > 0 ? `
                            <div class="flex items-center gap-1 text-amber-500 bg-amber-50 dark:bg-amber-900/20 px-2 py-1 rounded-md">
                                <span class="text-[10px] font-black">${t.cantidad_videos} VIDEO/S</span>
                            </div>
                        ` : ''}
                    </div>

                    <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600 transition-colors">${t.nombre}</h3>
                    
                    <div class="flex flex-wrap gap-1.5 mb-4">
                        ${disciplinasHTML}
                    </div>

                    <p class="text-sm text-slate-600 dark:text-slate-400 line-clamp-3 mb-4 leading-relaxed">
                        ${t.descripcion}
                    </p>

                    <div class="flex flex-wrap gap-1.5 mt-auto">
                        ${etiquetasHTML}
                    </div>
                </div>

                <div class="px-5 pb-5">
                    ${botonesAdmin}
                </div>
            </div>
        `;
    }

    // 7. Función para filtrar por fecha al hacer click en la fecha de la tarjeta (esto es solo un ejemplo, puedes adaptarlo para que filtre por otros campos también)
    function filtrarPorFecha(fechaIso) {
        // Ponemos la fecha en el input para que el usuario vea qué filtró
        document.getElementById('input-fecha').value = fechaIso;
        // Ejecutamos la carga
        cargarTecnicas(`fecha=${fechaIso}`);
    }

    // 8. Función para gestionar el botón "Cargar más" o mostrar mensaje de final de resultados
    function gestionarBotonVerMas(total) {
        // 1. Buscamos y eliminamos el contenedor entero (que incluye al botón)
        const contenedorBtn = document.getElementById('btn-container');
        if (contenedorBtn) contenedorBtn.remove();
        
        // Por si acaso quedó algún mensaje final de "Has llegado al final" de antes, lo limpiamos también
        const mensajeFinal = document.getElementById('mensaje-final-biblioteca');
        if (mensajeFinal) mensajeFinal.remove();

        // 2. Si aún no hemos cargado todas las técnicas existentes
        if (skip < total) {
            const btnHtml = `
                <div id="btn-container" class="col-span-full flex justify-center py-8">
                    <button id="btn-cargar-mas" onclick="cargarMas()" 
                        class="bg-slate-800 text-white px-10 py-3 rounded-xl font-bold hover:bg-blue-600 transition-all shadow-lg">
                        Cargar más técnicas
                    </button>
                </div>`;
            grid.insertAdjacentHTML('afterend', btnHtml);
        } else {
            // 3. Si llegamos al final, metemos el mensaje envuelto en su propio contenedor para mantener el diseño limpio
            const finalHtml = `
                <div id="mensaje-final-biblioteca" class="col-span-full text-center py-8">
                    <p class="text-slate-400 text-sm">Has llegado al final de la biblioteca</p>
                </div>`;
            grid.insertAdjacentHTML('afterend', finalHtml);
        }
    }

	function cargarMas() {
		// Usamos los filtros actuales para que el "Ver más" mantenga la búsqueda
		cargarTecnicas(filtrosActuales, true);
	}

    // 9. Función para limpiar todos los filtros y volver al estado original
	function limpiarFiltros() {
		// 1. Resetear el formulario completo (esto limpia inputs de texto, fecha y checkboxes)
		const form = document.getElementById('form-busqueda');
		form.reset();

		// 2. Resetear el sentido del orden manualmente (volver a por defecto: DESC)
		const inputSentido = document.getElementById('input-sentido');
		const iconSentido = document.getElementById('icon-sentido');
		inputSentido.value = 'desc';
		iconSentido.innerText = '↓';

		// 3. Limpiar la variable global de filtros para que el "Cargar más" funcione bien
		filtrosActuales = "";

		// 4. Recargar el listado original (sin parámetros)
		cargarTecnicas();

		// 5. (Opcional) Si quieres que el buscador se cierre al limpiar
		// toggleBuscador();
	}

	// 10 .Funciones para botones admin
	function editarTecnica(id) {
		// Redirige al formulario con el ID
		window.location.href = `/admin/tecnica?idtecnica=${id}`;
	}
 
	 async function borrarTecnica(id) {
		if (!confirm('¿Seguro que quieres borrar esta técnica?')) return;

		try {
			const response = await fetch(`/api/tecnicas/${id}`, {
				method: 'DELETE'
			});

			if (response.ok) {
				// En lugar de recargar toda la página, volvemos a llamar a la función que carga el listado
				// para que desaparezca la tarjeta visualmente.
				cargarTecnicas(filtrosActuales); 
			} else {
				alert('No se pudo borrar la técnica');
			}
		} catch (error) {
			console.error(error);
			alert('Error al conectar con el servidor');
		}
	}
