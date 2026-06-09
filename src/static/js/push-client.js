// 💡 Función auxiliar obligatoria para convertir tu clave VAPID pública a un formato que el navegador entienda
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Reemplaza esto con tu clave pública del .env
const VAPID_PUBLIC_KEY = "BBXsv2DG7tWyXLykOR4FqwbqDHQzkFoAmQqjXH03ZJnXXi6MlbjOgsNN_ks1DmGJRrOZbKMmcMkPnYZMjNGxJ8M"; 

async function inicializarNotificacionesPush() {
    // 1. Verificar si el navegador es compatible
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Las notificaciones push no están soportadas en este navegador.');
        return;
    }

    try {
        // 2. Registrar el Service Worker
        const registro = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registrado con éxito:', registro);

        // 3. Solicitar permisos al usuario si no los ha dado ya
        const permiso = await Notification.requestPermission();
        if (permiso !== 'granted') {
            console.warn('El usuario ha denegado el permiso para recibir notificaciones.');
            return;
        }

        // 4. Suscribir el dispositivo al servidor push del navegador (Google/Apple)
        const opcionesSuscripcion = {
            userVisibleOnly: true, // Obligatorio por seguridad: garantiza que cada push muestre una notificación visual
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        };

        const suscripcion = await registro.pushManager.subscribe(opcionesSuscripcion);
        console.log('Dispositivo suscrito en los servidores push del navegador:', suscripcion);

        // 5. Enviar el JSON resultante a nuestro servidor FastAPI
        // Nota: Al hacer JSON.stringify(suscripcion), JavaScript desestructura automáticamente los campos endpoint, p256dh y auth
        const respuesta = await fetch('/api/push/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Si usas tokens JWT en las cabeceras, añade aquí tu Authorization: 'Bearer ...'
                // 'Authorization': `Bearer ${token}`
            },
            credentials: 'include', // CRUCIAL: Esto le dice al navegador que adjunte la cookie de sesión actual
            body: JSON.stringify(suscripcion)
        });

        const resultado = await respuesta.json();
        if (respuesta.ok) {
            console.log('¡Suscripción guardada con éxito en tu MySQL!', resultado);
        } else {
            console.error('El backend falló al guardar la suscripción:', resultado);
        }

    } catch (error) {
        console.error('Error durante el proceso de suscripción push:', error);
    }
}

// SE ACTIVA CUANDO EL USUARIO HACE CLICK EN EL BOTÓN DE ACTIVAR NOTIFICACIONES (ver perfil.html)
document.addEventListener("DOMContentLoaded", () => {
    const boton = document.getElementById("btn-notificaciones");
    if (boton) {
        boton.addEventListener("click", () => {
            // Ahora sí, nace de un click real del usuario
            inicializarNotificacionesPush();
        });
    }
});