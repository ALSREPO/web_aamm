-- 1. Añadir columna para la categoría principal
ALTER TABLE ta_etiquetas ADD COLUMN categoria_1 VARCHAR(100) DEFAULT NULL;

-- 2. Añadir columna para la subcategoría
ALTER TABLE ta_etiquetas ADD COLUMN categoria_2 VARCHAR(100) DEFAULT NULL;

-- 3. Añadir columna para las notas aclaratorias o histórico de cambios
ALTER TABLE ta_etiquetas ADD COLUMN notas VARCHAR(100) DEFAULT NULL;

-- 4. Añadir columna para el orden posicional en el buscador
ALTER TABLE ta_etiquetas ADD COLUMN orden INT DEFAULT 999999;
