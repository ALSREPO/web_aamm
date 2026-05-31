document.getElementById('registroForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password_confirm').value;
    const errorMsg = document.getElementById('errorPassword');

    // VALIDACIÓN FRONTEND
    if (password !== passwordConfirm) {
        errorMsg.classList.remove('hidden');
        document.getElementById('password_confirm').focus();
        return; // Detenemos el envío
    } else {
        errorMsg.classList.add('hidden');
    }

    try {
        const response = await fetch('/api/autenticacion/registro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, email, password })
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('registroForm').classList.add('hidden');
            document.getElementById('mensajeExito').classList.remove('hidden');
        } else {
            alert("Error: " + result.detail);
        }
    } catch (error) {
        alert("Error de conexión");
    }
});