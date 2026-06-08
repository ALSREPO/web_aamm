CREATE TABLE IF NOT EXISTS `suscripciones_push` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `idusuario` mediumint unsigned NOT NULL,
  `endpoint` TEXT NOT NULL,
  `p256dh` VARCHAR(255) NOT NULL,
  `auth` VARCHAR(255) NOT NULL,
  `creado_en` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`idusuario`) REFERENCES `ta_usuarios`(`idusuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;