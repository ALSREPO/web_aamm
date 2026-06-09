INSERT INTO `notificaciones_tipos` (`nombre_clave`, `nombre_pantalla`, `descripcion`) 
VALUES (
    'nuevo_video', 
    'Nuevos vídeos de entrenamiento', 
    'Recibe una alerta en tiempo real cada vez que se suba una nueva lección o videotutorial a la plataforma.'
) ON DUPLICATE KEY UPDATE `nombre_pantalla` = VALUES(`nombre_pantalla`);