# Guía Rápida de Comandos SQL para MariaDB

Para entrar a la consola de MariaDB desde la terminal de tu servidor:
```bash
mariadb -u usuario -p
```
*(Si es el usuario root del sistema, a veces basta con usar `sudo mariadb`).*

---

## 1. Gestión de Base de Datos y Usuarios

* **Listar bases de datos existentes:**
  ```sql
  SHOW DATABASES;
  ```
* **Crear una nueva base de datos:**
  ```sql
  CREATE DATABASE nombre_base_datos;
  ```
* **Seleccionar / Usar una base de datos:**
  ```sql
  USE nombre_base_datos;
  ```
* **Crear un nuevo usuario con contraseña:**
  ```sql
  CREATE USER 'usuario'@'localhost' IDENTIFIED BY 'tu_contraseña';
  ```
* **Otorgar todos los privilegios sobre una base de datos:**
  ```sql
  GRANT ALL PRIVILEGES ON nombre_base_datos.* TO 'usuario'@'localhost';
  FLUSH PRIVILEGES;
  ```

---

## 2. Gestión de Tablas (DDL)

* **Listar las tablas de la base de datos actual:**
  ```sql
  SHOW TABLES;
  ```
* **Ver la estructura/columnas de una tabla:**
  ```sql
  DESCRIBE nombre_tabla;
  # O también: SHOW COLUMNS FROM nombre_tabla;
  ```
* **Crear una tabla básica:**
  ```sql
  CREATE TABLE usuarios (
      id INT AUTO_INCREMENT PRIMARY KEY,
      nombre VARCHAR(50) NOT NULL,
      email VARCHAR(100) UNIQUE,
      creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
* **Modificar una tabla (Añadir una columna):**
  ```sql
  ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20);
  ```
* **Eliminar una tabla por completo:**
  ```sql
  DROP TABLE nombre_tabla;
  ```

---

## 3. Manipulación de Datos (DML)

* **Insertar datos (Crear):**
  ```sql
  INSERT INTO usuarios (nombre, email) VALUES ('Juan Pérez', 'juan@example.com');
  ```
* **Consultar datos (Leer):**
  ```sql
  SELECT * FROM usuarios;
  SELECT nombre, email FROM usuarios WHERE id = 1;
  ```
* **Actualizar datos (Modificar):**
  ```sql
  UPDATE usuarios SET email = 'nuevo_email@example.com' WHERE id = 1;
  ```
* **Borrar registros (Eliminar):**
  ```sql
  DELETE FROM usuarios WHERE id = 1;
  ```

---

## 4. Utilidades de Terminal (Importar / Exportar)

Estos comandos se ejecutan directamente en la **terminal de Linux/Host**, NO dentro de la consola SQL:

* **Exportar (Hacer un Backup / Dump):**
  ```bash
  mariadb-dump -u usuario -p nombre_base_datos > respaldo.sql
  ```
* **Importar un archivo .sql:**
  ```bash
  mariadb -u usuario -p nombre_base_datos < respaldo.sql
  ```
