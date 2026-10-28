# Instalación Apache2
```bash
sudo apt update 
sudo apt install apache2 -y 
sudo systemctl enable --now apache2 //poner en marcha
systemctl status apache2 //verificar estado
curl -I http://localhost
```
# Instalación mariadb y demás paquetes
```bash
sudo apt update 
sudo apt install python3 python3-venv python3-pip mariadb-server -y 
sudo systemctl enable --now mariadb 
systemctl status mariadb 
```


# Comandos Git del Proyecto

## Clonar el repositorio
```bash
git clone https://github.com/xbi360/icd.git
```
## Configurar estrategia por defecto
```bash
git config pull.rebase false
git pull origin main --allow-unrelated-histories
```

## Configurar usuario
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@example.com"
```

## Inicializar y preparar
```bash
git init
git branch -M main
```

## Guardar cambios
```bash
git add .
git commit -m "Mensaje de commit"
```
## Configurar remote
```bash
git remote add origin https://github.com/xbi360/icd.git usr: xbi360 pwd: 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
```

## Configurar remote con Token (PAT)
```bash
git remote set-url origin https://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@github.com/xbi360/icd.git
```

## Subir cambios
```bash
git push -u origin main
```



## Ver estado
git status

## Añadir los cambios al inventario:
```bash
git add 
```
```bash
```
## Guardar cambios localmente:

```bash
git commit -m "Mensaje del cambio realizado"
```
## Subir los cambios a GitHub:

```bash
git push -u origin main
```
# Creación / Instación Base de datos
CREATE DATABASE IF NOT EXISTS gestor_tareas 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci; 
USE gestor_tareas; 
CREATE TABLE IF NOT EXISTS tareas ( 
id INT AUTO_INCREMENT PRIMARY KEY, 
nom VARCHAR(100) NOT NULL, 
descripcion TEXT, 
completada BOOLEAN DEFAULT 0 
); 
INSERT INTO tareas (nom, descripcion) VALUES 
('Aprender Flask', 'Crear rutas y conectar con MariaDB'), 
('Configurar entorno virtual', 'Instalar dependencias con pip e inicializar venv'), 
('Diseñar base de datos', 'Definir tablas, relaciones y tipos de datos'), 
('Escribir código HTML', 'Crear las plantillas para las vistas principales'), 
('Probar la aplicación', 'Realizar pruebas locales en el puerto 5000'); 
CREATE USER IF NOT EXISTS 'lm'@'localhost' IDENTIFIED BY 'lm'; 
GRANT ALL PRIVILEGES ON gestor_tareas.* TO 'lm'@'localhost'; 
FLUSH PRIVILEGES; 

## Exportar bbdd
  mysqldump -u tu_usuario -p nombre_de_tu_bd > database.sql
## Importar bbdd
  mysql -u tu_usuario -p nombre_de_tu_bd < database.sql
