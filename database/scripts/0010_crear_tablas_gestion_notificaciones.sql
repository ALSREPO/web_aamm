-- 1. Tabla de Catálogo de Eventos/Notificaciones
CREATE TABLE IF NOT EXISTS `notificaciones_tipos` (
  `idtipo` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `nombre_clave` varchar(50) NOT NULL,
  `nombre_pantalla` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idtipo`),
  UNIQUE KEY `uq_nombre_clave` (`nombre_clave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2. Tabla de Configuración y Preferencias de los Usuarios
CREATE TABLE IF NOT EXISTS `usuarios_notificaciones_config` (
  `idconfig` int unsigned NOT NULL AUTO_INCREMENT,
  `idusuario` mediumint unsigned NOT NULL,
  `idtipo` tinyint unsigned NOT NULL,
  `canal_push` boolean NOT NULL DEFAULT TRUE,
  `canal_email` boolean NOT NULL DEFAULT FALSE,
  `actualizado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idconfig`),
  UNIQUE KEY `uq_usuario_tipo` (`idusuario`, `idtipo`), -- Evita que un usuario tenga la misma preferencia duplicada
  CONSTRAINT `fk_config_usuario` FOREIGN KEY (`idusuario`) REFERENCES `ta_usuarios` (`idusuario`) ON DELETE CASCADE,
  CONSTRAINT `fk_config_tipo` FOREIGN KEY (`idtipo`) REFERENCES `notificaciones_tipos` (`idtipo`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3. Tabla de Suscripciones Web Push (La que ya tenías operativa)
CREATE TABLE IF NOT EXISTS `suscripciones_push` (
  `idsuscripcion` int unsigned NOT NULL AUTO_INCREMENT,
  `idusuario` mediumint unsigned NOT NULL,
  `endpoint` text NOT NULL,
  `p256dh` varchar(250) NOT NULL,
  `auth` varchar(100) NOT NULL,
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idsuscripcion`),
  CONSTRAINT `fk_suscripcion_usuario` FOREIGN KEY (`idusuario`) REFERENCES `ta_usuarios` (`idusuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;