    document.getElementById('form-password').onsubmit = async (e) => {
        e.preventDefault();
        
        const pActual = document.getElementById('pass_actual').value;
        const pNueva = document.getElementById('pass_nueva').value;
        const pRepetida = document.getElementById('pass_repeticion').value;
        const errorDiv = document.getElementById('mensaje-error');

        // VALIDACIÓN FRONTEND
        if (pNueva !== pRepetida) {
            errorDiv.classList.remove('hidden');
            return;
        } else {
            errorDiv.classList.add('hidden');
        }

        const res = await fetch(`/api/usuarios/cambiar-password?pass_actual=${encodeURIComponent(pActual)}&pass_nueva=${encodeURIComponent(pNueva)}`, {
            method: 'PUT'
        });

        if (res.ok) {
            alert("✅ Contraseña actualizada correctamente");
            e.target.reset();
        } else {
            const error = await res.json();
            alert("❌ " + (error.detail || "Error al cambiar contraseña"));
        }
    };