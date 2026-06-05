
    // 1. Manejar el envío del formulario para Crear Clase
    document.getElementById('form-crear-clase').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        try {
            const response = await fetch('/api/horarios/', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                window.location.reload();
            } else {
                const errorData = await response.json();
                alert('Error al guardar: ' + (errorData.detail || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de red al intentar conectar con el servidor.');
        }
    });

    // 2. Manejar el botón de Borrar Clase
    async function borrarClase(idhorario) {
        if (!confirm('¿Seguro que quieres eliminar esta clase del horario?')) return;
        try {
            const response = await fetch(`/api/horarios/${idhorario}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                window.location.reload();
            } else {
                alert('No se pudo eliminar la clase.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de red al intentar eliminar.');
        }
    }

    // 3. Conmutar visualmente entre Modo Vista y Modo Edición (Controlando la papelera)
    function conmutarEdicion(idhorario) {
        const row = document.getElementById(`clase-row-${idhorario}`);
        const vista = row.querySelector('.modo-vista');
        const edicion = row.querySelector('.modo-edicion');
        const btnEditar = row.querySelector('.btn-editar');
        const btnGuardar = row.querySelector('.btn-guardar');
        const btnBorrar = row.querySelector('.btn-borrar');

        if (edicion.classList.contains('hidden')) {
            // Activar edición
            vista.classList.add('hidden');
            btnBorrar.classList.add('hidden'); // Ocultamos papelera por seguridad
            edicion.classList.remove('hidden');
            btnEditar.innerText = '❌';
            btnEditar.title = 'Cancelar';
            btnGuardar.classList.remove('hidden');
        } else {
            // Cancelar edición
            vista.classList.remove('hidden');
            btnBorrar.classList.remove('hidden'); // Recuperamos la papelera
            edicion.classList.add('hidden');
            btnEditar.innerText = '✏️';
            btnEditar.title = 'Editar';
            btnGuardar.classList.add('hidden');
        }
    }

    // 4. Enviar los datos editados mediante un método PUT a la API
    async function guardarEdicion(idhorario) {
        const row = document.getElementById(`clase-row-${idhorario}`);
        const actividad = row.querySelector('.edit-actividad').value;
        const horaInicio = row.querySelector('.edit-inicio').value;
        const horaFin = row.querySelector('.edit-fin').value;

        const params = new URLSearchParams();
        params.append('actividad', actividad);
        params.append('hora_inicio', horaInicio);
        params.append('hora_fin', horaFin);

        try {
            const response = await fetch(`/api/horarios/${idhorario}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'accept': 'application/json'
                },
                body: params
            });

            if (response.ok) {
                window.location.reload();
            } else {
                const err = await response.json();
                alert('Error al actualizar: ' + (err.detail || 'Verifica los datos'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de red al intentar actualizar la clase.');
        }
    }