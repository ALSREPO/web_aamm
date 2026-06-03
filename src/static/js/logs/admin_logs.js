        // Guardaremos las líneas originales aquí para poder filtrarlas en local sin volver a llamar a la API
        let todasLasLineas = [];

        async function cargarLogs() {
            const contenedor = document.getElementById("contenedor-logs");
            const contador = document.getElementById("contador-lineas");
            const cantidadLineas = document.getElementById("selector-lineas").value;

            contador.innerText = "Sincronizando...";
            
            try {
                // Hacemos la petición pasando el parámetro ?lineas=X
                const respuesta = await fetch(`/api/logs/?lineas=${cantidadLineas}`);
                
                if (!respuesta.ok) throw new Error("Error en la respuesta del servidor");
                
                const datos = await respuesta.json();
                todasLasLineas = datos.logs;
                
                // Limpiar el buscador cada vez que refrescamos de la API
                document.getElementById("buscador-logs").value = "";
                
                renderizarLines(todasLasLineas);

            } catch (error) {
                console.error(error);
                contenedor.innerHTML = `<div class="text-red-400 font-bold">❌ Error al conectar con la API de logs: ${error.message}</div>`;
                contador.innerText = "Error";
            }
        }

        function renderizarLines(listaDeLineas) {
            const contenedor = document.getElementById("contenedor-logs");
            const contador = document.getElementById("contador-lineas");
            
            if (listaDeLineas.length === 0 || (listaDeLineas.length === 1 && listaDeLineas[0].includes("no se ha creado"))) {
                contenedor.innerHTML = `<div class="text-slate-500 italic">No hay registros que coincidan con los criterios.</div>`;
                contador.innerText = "0 líneas";
                return;
            }

            // Mapeamos las líneas dándoles estilos de color según el tipo de log corporativo
            contenedor.innerHTML = listaDeLineas.map(linea => {
                let colorTexto = "text-slate-300"; // Por defecto (INFO)
                
                if (linea.includes("[ERROR]") || linea.includes("[CRITICAL]")) {
                    colorTexto = "text-red-400 font-medium bg-red-950/20 px-1 rounded";
                } else if (linea.includes("[WARNING]")) {
                    colorTexto = "text-yellow-400 font-medium bg-yellow-950/20 px-1 rounded";
                } else if (linea.includes("[DEBUG]")) {
                    colorTexto = "text-blue-400/80";
                }

                // Resaltar visualmente las traducciones del administrador o usuario para que destaquen
                let lineaFormateada = linea
                    .replace(/ID_ADMIN\[(.*?)\]/g, `<span class="text-emerald-400 font-semibold">ID_ADMIN[$1]</span>`)
                    .replace(/ID_USUARIO\[(.*?)\]/g, `<span class="text-purple-400 font-semibold">ID_USUARIO[$1]</span>`);

                return `<div class="${colorTexto} hover:bg-slate-900/60 py-0.5 px-1 transition-colors break-all whitespace-pre-wrap">${lineaFormateada}</div>`;
            }).join("");

            contador.innerText = `${listaDeLineas.length} líneas mostradas`;
        }

        // Filtro ultra rápido en el cliente (Javascript puro en memoria)
        function filtrarLogs() {
            const termino = document.getElementById("buscador-logs").value.toLowerCase().trim();
            
            if (!termino) {
                renderizarLines(todasLasLineas);
                return;
            }

            const lineasFiltradas = todasLasLineas.filter(linea => 
                linea.toLowerCase().includes(termino)
            );
            
            renderizarLines(lineasFiltradas);
        }

        // Carga inicial automatizada al entrar a la página
        document.addEventListener("DOMContentLoaded", cargarLogs);
