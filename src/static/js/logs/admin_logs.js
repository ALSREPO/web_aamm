    let todasLasLineas = [];
    
    // Estado de los filtros (true = visible, false = oculto)
    let filtrosActivos = {
        error: true,
        warning: true,
        info: true,
        debug: true
    };

// 1. Esta función SOLO se encarga de pintar las líneas de texto en la consola
function renderizarLines(listaDeLineas) {
    const contenedor = document.getElementById("contenedor-logs");
    const contador = document.getElementById("contador-lineas");
    
    if (listaDeLineas.length === 0) {
        contenedor.innerHTML = `<div class="text-slate-500 italic p-2">No hay registros que coincidan con los filtros activos.</div>`;
        contador.innerText = "0 líneas";
        return;
    }

    contenedor.innerHTML = listaDeLineas.map(linea => {
        // Colores base adaptados (Gris oscuro en modo claro, Gris claro en modo noche)
        let colorTexto = "text-slate-700 dark:text-slate-300"; 
        
        if (linea.includes("[ERROR]") || linea.includes("[CRITICAL]")) {
            // Rojo oscuro en modo claro, rojo pastel en modo noche
            colorTexto = "text-red-700 dark:text-red-400 font-medium bg-red-50 dark:bg-red-950/10 px-1 rounded";
        } else if (linea.includes("[WARNING]")) {
            // Ocre en modo claro, amarillo en modo noche
            colorTexto = "text-amber-700 dark:text-yellow-400 font-medium bg-amber-50 dark:bg-yellow-950/10 px-1 rounded";
        } else if (linea.includes("[DEBUG]")) {
            // Azul marino en modo claro, azul cielo en modo noche
            colorTexto = "text-blue-700 dark:text-blue-400/80";
        }

        // Modificamos también los resaltados de las identidades para que contrasten bien en ambos fondos
        let lineaFormateada = linea
            .replace(/ID_ADMIN\[(.*?)\]/g, `<span class="text-emerald-600 dark:text-emerald-400 font-semibold">ID_ADMIN[$1]</span>`)
            .replace(/ID_USUARIO\[(.*?)\]/g, `<span class="text-purple-600 dark:text-purple-400 font-semibold">ID_USUARIO[$1]</span>`)
            .replace(/\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]/g, `<span class="text-slate-400 dark:text-slate-500 font-medium">[$1]</span>`);

        return `<div class="${colorTexto} hover:bg-slate-100 dark:hover:bg-slate-900/60 py-0.5 px-1 transition-colors break-all whitespace-pre-wrap">${lineaFormateada}</div>`;
    }).join("");

    contador.innerText = `${listaDeLineas.length} líneas mostradas`;
}

// Analiza en caliente los logs y rellena los selects de IP y Usuarios
function extraerFiltrosDinamicos() {
    const selectIp = document.getElementById("filtro-ip");
    const selectEmail = document.getElementById("filtro-email");

    if (!selectIp || !selectEmail) return;

    // Guardamos la selección actual
    const ipSeleccionada = selectIp.value;
    const emailSeleccionado = selectEmail.value;

    const ipsEncontradas = new Set();
    const identidadesEncontradas = new Set();

    todasLasLineas.forEach(linea => {
        if (!linea) return;

        // 1. Extraer IP estándar
        const matchIp = linea.match(/\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]/);
        if (matchIp) ipsEncontradas.add(matchIp[1]);

        // 2. Extraer Identidades
        const matchUsuario = linea.match(/ID_USUARIO\[(.*?)\]/);
        const matchAdmin = linea.match(/ID_ADMIN\[(.*?)\]/);
        const matchSistema = linea.match(/\[sistema\]/);

        if (matchUsuario) identidadesEncontradas.add(`ID_USUARIO[${matchUsuario[1]}]`);
        else if (matchAdmin) identidadesEncontradas.add(`ID_ADMIN[${matchAdmin[1]}]`);
        else if (matchSistema) identidadesEncontradas.add("[sistema]");
    });

    // Rellenar Select de IPs (Limpiamos el emoji interno de la opción por defecto)
    selectIp.innerHTML = '<option value="" class="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Todas las IPs</option>';
    Array.from(ipsEncontradas).sort().forEach(ip => {
        const option = ModelOption(ip, ip, ip === ipSeleccionada);
        selectIp.add(option);
    });

    // Rellenar Select de Identidades/Emails (Limpiamos el emoji interno)
    selectEmail.innerHTML = '<option value="" class="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">Todos los usuarios</option>';
    Array.from(identidadesEncontradas).sort().forEach(id => {
        const option = ModelOption(id, id, id === emailSeleccionado);
        selectEmail.add(option);
    });
}

// Helper modificado: Ahora añade las clases de Tailwind para soportar el fondo oscuro al desplegar
function ModelOption(texto, valor, seleccionado) {
    const opt = document.createElement('option');
    opt.text = texto;
    opt.value = valor;
    opt.selected = seleccionado;
    
    // Forzamos los estilos de fondo y color para corregir el despliegue en modo noche
    opt.classList.add("bg-white", "dark:bg-slate-900", "text-slate-800", "dark:text-slate-200");
    
    return opt;
}

// 2. Descarga los logs del servidor y los guarda en la variable global "todasLasLineas"
async function cargarLogs() {
    const contenedor = document.getElementById("contenedor-logs");
    const contador = document.getElementById("contador-lineas");
    const labelFichero = document.getElementById("nombre-fichero-log");
    const cantidadLineas = document.getElementById("selector-lineas").value;

    // Asignamos el nombre del fichero inmediatamente desde la variable global de Jinja2
    if (window.LOG_FILE_PATH) {
        labelFichero.innerText = window.LOG_FILE_PATH;
    }

    contador.innerText = "Sincronizando...";
    
    try {
        const respuesta = await fetch(`/api/logs/?lineas=${cantidadLineas}`);
        if (!respuesta.ok) throw new Error("Error en la respuesta del servidor");
        
        const datos = await respuesta.json();
        todasLasLineas = datos.logs;
        
        // Extraemos las nuevas IPs y emails que hayan entrado en este bloque
        extraerFiltrosDinamicos();
        //document.getElementById("buscador-logs").value = "";
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
        const terminoInclusion = document.getElementById("buscador-logs").value.toLowerCase().trim();
        const terminoExclusion = document.getElementById("excluidor-logs").value.toLowerCase().trim();
        const ipSeleccionada = document.getElementById("filtro-ip").value;
        const emailSeleccionado = document.getElementById("filtro-email").value;
        
        // 1. Filtrar primero por los niveles de los botones LED activos
        let lineasFiltradas = todasLasLineas.filter(linea => {
            if (linea.includes("[ERROR]") || linea.includes("[CRITICAL]")) return filtrosActivos.error;
            if (linea.includes("[WARNING]")) return filtrosActivos.warning;
            if (linea.includes("[DEBUG]")) return filtrosActivos.debug;
            // Por defecto asumimos que es [INFO]
            return filtrosActivos.info;
        });

        // FILTRO 2: Filtrado por IP específica (si hay una seleccionada)
    if (ipSeleccionada) {
        lineasFiltradas = lineasFiltradas.filter(linea => linea.includes(`[${ipSeleccionada}]`));
    }

    // FILTRO 3: Filtrado por Email/Identidad específica
    if (emailSeleccionado) {
        lineasFiltradas = lineasFiltradas.filter(linea => linea.includes(emailSeleccionado));
    }

    // FILTRO 4: Buscador de inclusión tradicional
    if (terminoInclusion) {
        lineasFiltradas = lineasFiltradas.filter(linea => 
            linea.toLowerCase().includes(terminoInclusion)
        );
    }

    // FILTRO 5 (NUEVO): Buscador INVERSO de exclusión (Oculta si coincide el texto)
    if (terminoExclusion) {
        lineasFiltradas = lineasFiltradas.filter(linea => 
            !linea.toLowerCase().includes(terminoExclusion)
        );
    }

    // Renderizar resultado final filtrado en pantalla
    renderizarLines(lineasFiltradas);
}

// Ejecución automática en tiempo real
function filtrarLogs() {
    procesarYFiltrarLogs();
}

document.addEventListener("DOMContentLoaded", cargarLogs);

function reestablecerTodo() {
    document.getElementById("buscador-logs").value = "";
    document.getElementById("excluidor-logs").value = "";
    document.getElementById("filtro-ip").value = "";
    document.getElementById("filtro-email").value = "";
    
    for (const nivel in filtrosActivos) {
        if (!filtrosActivos[nivel]) {
            alternarFiltro(nivel);
        }
    }
    
    procesarYFiltrarLogs();
}