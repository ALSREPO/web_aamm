document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // <--- ESTO evita que la URL cambie y la página se recargue
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/autenticacion/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }) // Enviamos el JSON que espera el Schema
        });

        const result = await response.json();

        if (response.ok) {
            // Si el login es exitoso, FastAPI ya nos envió la cookie.
            // Solo tenemos que movernos a la home.
            window.location.href = "/";
        } else {
            // Mostramos el error (ej: "Email o contraseña incorrectos")
			const errorDiv = document.getElementById('error-message');
			errorDiv.textContent = result.detail || "Error al iniciar sesión";
			errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error de conexión con el servidor");
    }
});