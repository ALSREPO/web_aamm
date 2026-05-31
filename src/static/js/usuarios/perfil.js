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


    // LÓGICA PARA ELIMINAR LA CUENTA
    document.getElementById('btn-eliminar-cuenta').onclick = async () => {
        const seguro = confirm("⚠️ ¿Estás absolutamente seguro de que quieres eliminar tu cuenta?\nEsta acción es irreversible y perderás el acceso a esta web.");
        
        if (!seguro) return;

        const res = await fetch('/api/usuarios/eliminar-mi-cuenta', {
            method: 'DELETE'
        });

        if (res.ok) {
            alert("🔒 Tu cuenta ha sido eliminada con éxito. Gracias por tu tiempo.");
            // Redirigimos a la página de inicio (al no tener cookie, el sistema lo mandará al login)
            window.location.href = "/";
        } else {
            const error = await res.json();
            alert("❌ " + (error.detail || "No se pudo procesar la eliminación de la cuenta"));
        }
    };