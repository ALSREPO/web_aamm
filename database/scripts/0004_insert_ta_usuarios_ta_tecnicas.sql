insert IGNORE into `ta_usuarios` (nombre, password, fechaCreacion, email, activo, email_verificado) values
('admin', '$6$rounds=656000$Y02wDfuyBJTLH3FV$XqgAt5et1IWNKNCkiMoPs5qJUo7QT2WvS6q3Vrx9xM4oXOuwjLCMRD/zaD15mtDLOkHhqvjz.Paxvv03nBbkq/', '2026-05-11', 'admin@admin.com', 2, TRUE);
/* 
Usuario: admin
Pass:    admin
*/

INSERT IGNORE INTO `ta_disciplinas` VALUES (1,'BJJ'),(2,'LL');

INSERT IGNORE INTO `ta_etiquetas` VALUES (6,'BJJ'),(7,'LL'),(8,'Ganar espalda'),(9,'Montada'),(10,'100 KG'),(11,'Norte Sur'),(12,'Media guardia'),(13,'Guardia cerrada'),(14,'Finalización'),(15,'Triángulo'),(16,'Llave de brazo'),(17,'Omoplata'),(18,'Raspaje'),(19,'Quimura'),(20,'Americana'),(21,'Guillotina'),(22,'Estrangulamiento'),(23,'Punto de dolor'),(24,'Leg Drag'),(25,'Derribo'),(26,'Bola Kimono'),(27,'Drill'),(28,'Llave de bíceps'),(29,'Llave de pie'),(30,'Llave recta de pie'),(31,'Americana de pie'),(32,'Quimura de pie'),(33,'Control de rodilla'),(34,'De pie'),(35,'Clinch'),(36,'Mano de vaca'),(37,'De la Riva'),(38,'Salida de guardia'),(39,'Llave de gemelo'),(40,'Ezequiel'),(41,'Salida de 100 KG'),(42,'Salida de'),(43,'Contra'),(44,'Esgrima de brazo'),(45,'Guardia araña'),(46,'Guardia mariposa'),(47,'Cuatro apoyos'),(48,'Montada buda'),(49,'Media guardia Mushroom'),(50,'Heel Hook'),(51,'Fifty Fifty'),(52,'Anaconda'),(53,'Snap'),(54,'Video'),(55,'Cervical'),(56,'Single leg'),(57,'Double leg'),(58,'Media guardia escudo'),(59,'Guardia rubber'),(60,'Violín'),(61,'Guardia lazo'),(62,'Mataleón'),(63,'Entrada a pierna'),(64,'Crucifijo'),(65,'Berimbolo'),(72,'CrossFace'),(73,'Darce'),(74,'Guardia X'),(75,'Guardia abierta'),(76,'Llave de rodilla'),(77,'Ninja Roll'),(78,'Kata gatame Triángulo de brazo'),(79,'100 KG elefante'),(80,'Camisa de fuerza'),(81,'Pasar guardia'),(82,'Seminario'),(83,'Defensa'),(84,'Russian tie'),(85,'Ashi Garami');

INSERT IGNORE INTO `ta_tecnicas` VALUES (1,'2026-01-10','Técnica de ejemplo 1','Triángulo desde guardia cerrada'),(2,'2026-05-31','Ejemplo 2','Pasaje de guardia');

INSERT IGNORE INTO `ta_tecnicas_disciplinas` VALUES (1,1),(1,2),(2,1);

INSERT IGNORE INTO `ta_tecnicas_etiquetas` VALUES (6,1), (7,1), (15,1), (6,2), (38,2), (13,2);

INSERT IGNORE INTO `ta_tecnicas_videos` VALUES (1,'triangulo_video_1.mp4',1), (2,'triangulo_video_2.mp4',1);