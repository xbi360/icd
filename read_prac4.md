# Práctica 4 · Máquinas virtuales (Proxmox VE + Apache + Flask + MariaDB)

Resumen de las instrucciones y comandos necesarios para reproducir la práctica.

## 0. Esquema de la infraestructura

| VM    | VMID | Función                 | Software                    | IP               |
|-------|------|-------------------------|-----------------------------|------------------|
| web1  | 100  | Servidor web 1          | Debian 13 + Apache          | 192.168.10.3/24  |
| web2  | 101  | Servidor web 2          | Debian 13 + Apache          | 192.168.10.4/24  |
| flask | 102  | Aplicación web + BD     | Debian 13 + Flask + MariaDB | 192.168.10.5/24  |

- Red: `192.168.10.0/24`, bridge `vmbr0` (puerto `eth0`).
- Proxmox: `192.168.10.2/24`, puerta de enlace `192.168.10.1`, DNS `8.8.8.8`.
- Interfaz web de Proxmox: `https://192.168.10.2:8006` (aceptar el certificado autofirmado).

---

## 1. Instalación del hipervisor

Instrucciones (interfaz gráfica / instalador):

1. Descargar la ISO oficial de Proxmox VE.
2. Crear una máquina virtual en **Hyper-V** y arrancarla con esa ISO.
3. Durante la instalación asignar a Proxmox la IP `192.168.10.2/24` con puerta de enlace `192.168.10.1`.
4. Comprobar que el bridge `vmbr0` queda con: IPv4/CIDR `192.168.10.2/24`, Gateway `192.168.10.1`, Bridge ports `eth0`.

## 2. Acceso a la interfaz web

Desde el navegador:

```
https://192.168.10.2:8006
```

Usuario `root` (reino PAM) con la contraseña definida en la instalación.

## 3. Creación de la VM web1

### 3.1 Subir la ISO de Debian 13

Interfaz web: **local → ISO Images → Upload**.

### 3.2 Asistente "Create VM"

| Pestaña | Valor |
|---------|-------|
| General | VM ID `100`, Name `web1` |
| OS      | ISO de Debian 13 (netinst), tipo Linux |
| Disks   | Bus SCSI (VirtIO SCSI single), almacenamiento `local-lvm`, **20 GB** |
| CPU     | 1 socket, **1 núcleo** |
| Memory  | **2048 MiB** |
| Network | Bridge `vmbr0`, modelo VirtIO |

Después: **Start** → **Console** y completar la instalación de Debian. Iniciar sesión como `root`.

## 4. Configuración de red en web1

Editar el fichero:

```bash
nano /etc/network/interfaces
```

Contenido:

```
auto lo
iface lo inet loopback

allow-hotplug ens18
iface ens18 inet static
    address 192.168.10.3/24
    gateway 192.168.10.1
    dns-nameservers 8.8.8.8
```

Aplicar y comprobar:

```bash
systemctl restart networking
ip address
ping -c 2 192.168.10.2      # conectividad con el hipervisor
ping -c 2 8.8.8.8           # salida a Internet
```

Resultado esperado: 0 % de pérdida en ambos `ping`.

## 5. Apache en web1

```bash
sudo apt update
sudo apt install apache2 -y
sudo systemctl enable --now apache2
systemctl status apache2        # debe indicar: active (running)
curl -I http://localhost        # debe devolver: HTTP/1.1 200 OK
```

Personalizar la página (asignatura, nombre del estudiante e IP del servidor):

```bash
sudo nano /var/www/html/index.html
```

```html
<html lang="es">
<head><meta charset="UTF-8"><title>Servidor Web 1</title></head>
<body>
  <h1>Infraestructura Inform&aacute;tica para Centros de Procesamiento de Datos</h1>
  <h2>Servidor Web 1</h2>
  <p>Estudiante: Luis Mario Laesa</p>
  <p>Direcci&oacute;n IP: 192.168.10.3</p>
</body>
</html>
```

Comprobar desde el navegador: `http://192.168.10.3`

## 6. Clonado de web2

Instrucciones en la interfaz web de Proxmox:

1. Clic derecho sobre `web1` → **Clone** (nombre `web2`, VMID `101`).
2. En **Hardware → Network Device**: dejar la **MAC en modo automático** (así se genera una nueva) y mantener el bridge `vmbr0`.
3. Arrancar `web2` y editar la red (cambia la IP):

```bash
nano /etc/network/interfaces
```

```
allow-hotplug ens18
iface ens18 inet static
    address 192.168.10.4/24
    gateway 192.168.10.1
    dns-nameservers 8.8.8.8
```

```bash
systemctl restart networking
ip address
ping -c 2 192.168.10.2
ping -c 2 8.8.8.8
```

## 7. Apache en web2

Apache ya viene instalado por el clon; solo hay que comprobar y cambiar la página:

```bash
systemctl status apache2
curl -I http://localhost
sudo nano /var/www/html/index.html     # cambiar "Servidor Web 1" por "Servidor Web 2" y la IP por 192.168.10.4
```

Comprobar: `http://192.168.10.4`

> **Nota:** en la Figura 21 del documento la página de web2 muestra la IP `192.168.10.3`; el valor correcto del contenido debe ser `192.168.10.4`.

## 8. Máquina flask y base de datos MariaDB

Crear la VM `flask` (VMID `102`) con el mismo procedimiento que web1 (o clonando web1) y configurar su red:

```
allow-hotplug ens18
iface ens18 inet static
    address 192.168.10.5/24
    gateway 192.168.10.1
    dns-nameservers 8.8.8.8
```

```bash
systemctl restart networking
```

Instalar Python y MariaDB (no se necesita Apache):

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip mariadb-server -y
sudo systemctl enable --now mariadb
systemctl status mariadb
```

Entrar en MariaDB:

```bash
sudo mariadb
```

Y ejecutar:

```sql
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
```

Comprobar:

```sql
USE gestor_tareas;
SELECT * FROM tareas;     -- deben aparecer 5 registros
```

## 9. Aplicación Flask

### 9.1 Entorno virtual y dependencias

```bash
cd ~
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy pymysql
```

### 9.2 Estructura del proyecto

```bash
mkdir -p ~/appflask/templates ~/appflask/static
nano ~/appflask/app.py
nano ~/appflask/templates/index.html
nano ~/appflask/static/style.css
```

```
appflask/
├── app.py
├── templates/
│   └── index.html
└── static/
    └── style.css
```

### 9.3 `app.py`

```python
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Conexión con MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lm:lm@localhost/gestor_tareas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    lista_tareas = Tarea.query.all()
    return render_template('index.html', tareas=lista_tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    nueva_tarea = Tarea(
        nom=request.form['nom'],
        descripcion=request.form['descripcion'],
        completada=False
    )
    db.session.add(nueva_tarea)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/completar/<int:id>')
def completar(id):
    tarea = Tarea.query.get_or_404(id)
    tarea.completada = not tarea.completada
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    if Tarea.query.count() == 0:
        db.session.execute(text("ALTER TABLE tareas AUTO_INCREMENT = 1"))
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='192.168.10.5', port=5000, debug=True)
```

### 9.4 `templates/index.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container">
    <h1>Mis tareas</h1>
    <form action="/agregar" method="POST">
      <div class="form-group">
        <label for="nom">Nombre de la tarea:</label>
        <input type="text" id="nom" name="nom" required>
      </div>
      <div class="form-group">
        <label for="descripcion">Descripción:</label>
        <textarea id="descripcion" name="descripcion"></textarea>
      </div>
      <button type="submit">Guardar tarea</button>
    </form>
    <hr>
    <h2>Lista de pendientes</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Nombre</th><th>Descripción</th>
          <th>Estado</th><th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {% for tarea in tareas %}
        <tr>
          <td>{{ tarea.id }}</td>
          <td class="{% if tarea.completada %}tachado{% endif %}">{{ tarea.nom }}</td>
          <td class="{% if tarea.completada %}tachado{% endif %}">{{ tarea.descripcion }}</td>
          <td>
            {% if tarea.completada %}
              <span class="badge-completada">Completada</span>
            {% else %}
              <span class="badge-pendiente">Pendiente</span>
            {% endif %}
          </td>
          <td>
            <a href="/completar/{{ tarea.id }}" class="btn-accion">
              {% if tarea.completada %}Desmarcar{% else %}Completar{% endif %}
            </a>
            <a href="/eliminar/{{ tarea.id }}" class="btn-eliminar"
               onclick="return confirm('¿Eliminar esta tarea?')">Eliminar</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
```

### 9.5 `static/style.css`

```css
* { box-sizing: border-box; }
body {
  font-family: Arial, Helvetica, sans-serif;
  background: #eef2f7;
  color: #1f2937;
  margin: 0;
  padding: 32px 16px;
}
.container {
  max-width: 860px;
  margin: 0 auto;
  background: #fff;
  padding: 28px 32px;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, .08);
}
h1 { margin-top: 0; color: #1f3864; }
h2 { color: #2e74b5; font-size: 1.15rem; }
.form-group { margin-bottom: 12px; }
label { display: block; font-weight: bold; margin-bottom: 4px; }
input[type="text"], textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #c7d2e0;
  border-radius: 6px;
  font: inherit;
}
textarea { min-height: 70px; resize: vertical; }
button {
  background: #1f3864;
  color: #fff;
  border: 0;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
}
button:hover { background: #2e74b5; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; }
th, td { padding: 8px; border-bottom: 1px solid #e3e8ef; text-align: left; font-size: .95rem; }
th { background: #f2f5fa; color: #1f3864; }
.tachado { text-decoration: line-through; color: #8a94a6; }
.badge-completada, .badge-pendiente {
  padding: 3px 9px;
  border-radius: 12px;
  font-size: .8rem;
}
.badge-completada { background: #d9f2e3; color: #146c43; }
.badge-pendiente { background: #fdf0d5; color: #8a6100; }
.btn-accion, .btn-eliminar { margin-right: 8px; text-decoration: none; font-size: .9rem; }
.btn-accion { color: #2e74b5; }
.btn-eliminar { color: #c0392b; }
```

### 9.6 Ejecución

```bash
cd ~
source venv/bin/activate
python3 appflask/app.py
```

Abrir en el navegador: `http://192.168.10.5:5000`

Probar: alta de tarea, **Completar / Desmarcar**, **Eliminar**, y comprobar en MariaDB que los cambios persisten.

---

## 10. Validación (resumen)

| Comprobación     | Procedimiento                                  | Resultado esperado                     |
|------------------|------------------------------------------------|----------------------------------------|
| Red de web1      | `ping 192.168.10.2` y `ping 8.8.8.8`           | 0 % de pérdida                         |
| Red de web2      | IP `.4/24` y `ping`                            | Sin conflicto de IP ni de MAC          |
| Servidor web1    | `systemctl status apache2` y `curl -I`         | `active (running)` y `HTTP/1.1 200 OK` |
| Página de web1   | Navegador en `http://192.168.10.3`             | Asignatura, nombre e IP                |
| Servidor web2    | `systemctl status apache2` y `curl -I`         | `active (running)`                     |
| Página de web2   | Navegador en `http://192.168.10.4`             | Página personalizada                   |
| Base de datos    | `systemctl status mariadb` y `SELECT`          | Servicio activo y 5 registros          |
| Aplicación Flask | Navegador en `http://192.168.10.5:5000`        | Alta, cambio de estado y borrado OK    |
