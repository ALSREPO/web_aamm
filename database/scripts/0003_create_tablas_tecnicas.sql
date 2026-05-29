--
-- Table structure for table `ta_disciplinas`
--

CREATE TABLE IF NOT EXISTS `ta_disciplinas` (
  `iddisciplina` int unsigned NOT NULL AUTO_INCREMENT,
  `disciplina` varchar(255) NOT NULL,
  PRIMARY KEY (`iddisciplina`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `ta_etiquetas`
--

CREATE TABLE IF NOT EXISTS `ta_etiquetas` (
  `idetiqueta` int unsigned NOT NULL AUTO_INCREMENT,
  `etiqueta` varchar(255) NOT NULL,
  PRIMARY KEY (`idetiqueta`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `ta_tecnicas`
--

CREATE TABLE IF NOT EXISTS `ta_tecnicas` (
  `idtecnica` int unsigned NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  PRIMARY KEY (`idtecnica`),
  FULLTEXT KEY `nombre` (`nombre`),
  FULLTEXT KEY `descripcion` (`descripcion`),
  FULLTEXT `idx_buscador_global` (`nombre`, `descripcion`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `ta_tecnicas_disciplinas`
--

CREATE TABLE IF NOT EXISTS `ta_tecnicas_disciplinas` (
  `iddisciplina` int unsigned NOT NULL,
  `idtecnica` int unsigned NOT NULL,
  PRIMARY KEY (`iddisciplina`,`idtecnica`),
  KEY `idtecnica` (`idtecnica`),
  CONSTRAINT `ta_tecnicas_disciplinas_ibfk_1` FOREIGN KEY (`iddisciplina`) REFERENCES `ta_disciplinas` (`iddisciplina`) ON UPDATE CASCADE,
  CONSTRAINT `ta_tecnicas_disciplinas_ibfk_2` FOREIGN KEY (`idtecnica`) REFERENCES `ta_tecnicas` (`idtecnica`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `ta_tecnicas_etiquetas`
--

CREATE TABLE IF NOT EXISTS `ta_tecnicas_etiquetas` (
  `idetiqueta` int unsigned NOT NULL,
  `idtecnica` int unsigned NOT NULL,
  PRIMARY KEY (`idetiqueta`,`idtecnica`),
  KEY `idtecnica` (`idtecnica`),
  CONSTRAINT `ta_tecnicas_etiquetas_ibfk_1` FOREIGN KEY (`idetiqueta`) REFERENCES `ta_etiquetas` (`idetiqueta`) ON UPDATE CASCADE,
  CONSTRAINT `ta_tecnicas_etiquetas_ibfk_2` FOREIGN KEY (`idtecnica`) REFERENCES `ta_tecnicas` (`idtecnica`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `ta_tecnicas_videos`
--

CREATE TABLE IF NOT EXISTS `ta_tecnicas_videos` (
  `idvideo` int unsigned NOT NULL AUTO_INCREMENT,
  `video` varchar(500) NOT NULL,
  `idtecnica` int unsigned NOT NULL,
  PRIMARY KEY (`idvideo`,`idtecnica`),
  KEY `idtecnica` (`idtecnica`),
  CONSTRAINT `ta_tecnicas_videos_ibfk_1` FOREIGN KEY (`idtecnica`) REFERENCES `ta_tecnicas` (`idtecnica`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=139 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
