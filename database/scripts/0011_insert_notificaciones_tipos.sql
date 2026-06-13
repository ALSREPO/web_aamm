INSERT INTO `notificaciones_tipos` (`nombre_clave`, `nombre_pantalla`, `descripcion`) 
VALUES (
    'nueva_tecnica', 
    'Nuevas técnicas de entrenamiento', 
    'Recibe una alerta cada vez que se suba una nueva lección a la plataforma.'
) ON DUPLICATE KEY UPDATE `nombre_pantalla` = VALUES(`nombre_pantalla`);