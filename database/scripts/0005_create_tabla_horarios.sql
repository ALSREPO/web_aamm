CREATE TABLE IF NOT EXISTS ta_horarios (
    idhorario INT AUTO_INCREMENT PRIMARY KEY,
    actividad VARCHAR(100) NOT NULL,
    dia_semana TINYINT NOT NULL, -- 1: Lunes, 2: Martes, etc.
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;