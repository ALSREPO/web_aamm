    let todasLasLineas = [];
    
    // Estado de los filtros (true = visible, false = oculto)
    let filtrosActivos = {
        error: true,
        warning: true,
        info: true,
        debug: true
    };

    async function cargarLogs() {
        const contenedor = document.getElementById("contenedor-logs");
        const contador = document.getElementById("contador-lineas");
        const cantidadLineas = document.getElementById("selector-lineas").value;

        contador.innerText = "Sincronizando...";
        
        try {
            const respuesta = await fetch(`/api/logs/?lineas=${cantidadLineas}`);
            if (!respuesta.ok) throw new Error("Error en la respuesta del servidor");
            
            const datos = await respuesta.json();
            todasLasLineas = datos.logs;
            
            // Resetear el buscador visual al recargar
            document.getElementById("buscador-logs").value = "";
            
            // Aplicar filtros combinados
            procesarYFiltrarLogs();

        } catch (error) {
            console.error(error);
            contenedor.innerHTML = `<div class="text-red-400 font-bold">❌ Error al conectar con la API de logs: ${error.message}</div>`;
            contador.innerText = "Error";
        }
    }

    // Función que se ejecuta al hacer clic en cualquier botón LED
    function alternarFiltro(nivel) {
        // Invertimos el estado del filtro seleccionado
        filtrosActivos[nivel] = !filtrosActivos[nivel];
        
        // Seleccionamos el punto LED y el botón para cambiarles el diseño visual
        const led = document.getElementById(`led-${nivel}`);
        const btn = document.getElementById(`btn-f-${nivel}`);
        
        if (filtrosActivos[nivel]) {
            // LED Encendido: Devolvemos sus colores y su brillo shadow nativo de Tailwind
            led.classList.remove("bg-slate-600", "shadow-none");
            if (nivel === 'error') led.classList.add("bg-red-500", "shadow-[0_0_8px_rgba(239,68,68,0.5)]");
            if (nivel === 'warning') led.classList.add("bg-yellow-500", "shadow-[0_0_8px_rgba(234,179,8,0.5)]");
            if (nivel === 'info') led.classList.add("bg-emerald-500", "shadow-[0_0_8px_rgba(16,185,129,0.5)]");
            if (nivel === 'debug') led.classList.add("bg-blue-500", "shadow-[0_0_8px_rgba(59,130,246,0.5)]");
            btn.classList.remove("opacity-40");
        } else {
            // LED Apagado: Lo volvemos gris apagado y bajamos la opacidad del botón
            led.classList.remove("bg-red-500", "bg-yellow-500", "bg-emerald-500", "bg-blue-500", "shadow-[0_0_8px_rgba(239,68,68,0.5)]", "shadow-[0_0_8px_rgba(234,179,8,0.5)]", "shadow-[0_0_8px_rgba(16,185,129,0.5)]", "shadow-[0_0_8px_rgba(59,130,246,0.5)]");
            led.classList.add("bg-slate-600", "shadow-none");
            btn.classList.add("opacity-40");
        }
        
        // Volvemos a calcular qué líneas deben mostrarse
        procesarYFiltrarLogs();
    }

    // Centraliza el filtrado combinando el Buscador + Botones LED
    function procesarYFiltrarLogs() {
        const termino = document.getElementById("buscador-logs").value.toLowerCase().trim();
        
        // 1. Filtrar primero por los niveles de los botones LED activos
        let lineasFiltradas = todasLasLineas.filter(linea => {
            if (linea.includes("[ERROR]") || linea.includes("[CRITICAL]")) return filtrosActivos.error;
            if (linea.includes("[WARNING]")) return filtrosActivos.warning;
            if (linea.includes("[DEBUG]")) return filtrosActivos.debug;
            // Por defecto asumimos que es [INFO]
            return filtrosActivos.info;
        });

        // 2. Si además hay texto en el buscador, filtramos sobre lo anterior
        if (termino) {
            lineasFiltradas = lineasFiltradas.filter(linea => 
                linea.toLowerCase().includes(termino)
            );
        }

        // 3. Mandamos la lista final resultante a pintar en la pantalla
        renderizarLines(lineasFiltradas);
    }

    // Esta función se ejecuta en tiempo real cada vez que se escribe en el input
    function filtrarLogs() {
        procesarYFiltrarLogs();
    }

    function renderizarLines(listaDeLineas) {
        const contenedor = document.getElementById("contenedor-logs");
        const contador = document.getElementById("contador-lineas");
        
        if (listaDeLineas.length === 0 || (listaDeLineas.length === 1 && listaDeLineas[0].includes("no se ha creado"))) {
            contenedor.innerHTML = `<div class="text-slate-500 italic p-2">No hay registros que coincidan con los filtros activos.</div>`;
            contador.innerText = "0 líneas";
            return;
        }

        contenedor.innerHTML = listaDeLineas.map(linea => {
            let colorTexto = "text-slate-300";
            
            if (linea.includes("[ERROR]") || linea.includes("[CRITICAL]")) {
                colorTexto = "text-red-400 font-medium bg-red-950/10 px-1 rounded";
            } else if (linea.includes("[WARNING]")) {
                colorTexto = "text-yellow-400 font-medium bg-yellow-950/10 px-1 rounded";
            } else if (linea.includes("[DEBUG]")) {
                colorTexto = "text-blue-400/80";
            }

            let lineaFormateada = linea
                .replace(/ID_ADMIN\[(.*?)\]/g, `<span class="text-emerald-400 font-semibold">ID_ADMIN[$1]</span>`)
                .replace(/ID_USUARIO\[(.*?)\]/g, `<span class="text-purple-400 font-semibold">ID_USUARIO[$1]</span>`)
                .replace(/\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]/g, `<span class="text-slate-500 font-medium">[$1]</span>`);

            return `<div class="${colorTexto} hover:bg-slate-900/60 py-0.5 px-1 transition-colors break-all whitespace-pre-wrap">${lineaFormateada}</div>`;
        }).join("");

        contador.innerText = `${listaDeLineas.length} líneas mostradas`;
    }

    document.addEventListener("DOMContentLoaded", cargarLogs);

    function reestablecerTodo() {
        // 1. Vaciar el buscador
        document.getElementById("buscador-logs").value = "";
        
        // 2. Encender todos los filtros LED si estaban apagados
        for (const nivel in filtrosActivos) {
            if (!filtrosActivos[nivel]) {
                alternarFiltro(nivel); // Esto invierte el estado y actualiza el diseño visual
            }
        }
        
        // 3. Si ya estaban todos encendidos, simplemente refrescamos la vista
        procesarYFiltrarLogs();
    }