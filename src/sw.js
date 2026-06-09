// Escuchar el evento 'push' que viene del servidor de Google/Apple
self.addEventListener('push', function(event) {
    if (!event.data) {
        console.log('Petición push sin datos.');
        return;
    }

    const payload = event.data.json();
    const objeto_notificacion = payload.notification;

    const titulo = objeto_notificacion.title || 'Notificación de la Escuela';
    const opciones = {
        body: objeto_notificacion.body,
        icon: objeto_notificacion.icon || '/static/favicon.ico',
        badge: objeto_notificacion.badge || '/static/favicon.ico',
        data: {
            url: objeto_notificacion.data ? objeto_notificacion.data.url : '/'
        }
    };

    event.waitUntil(
        self.registration.showNotification(titulo, opciones)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    const urlDestino = event.notification.data && event.notification.data.url ? event.notification.data.url : '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(windowClients) {
            for (let i = 0; i < windowClients.length; i++) {
                let client = windowClients[i];
                if ('focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(urlDestino);
            }
        })
    );
});
