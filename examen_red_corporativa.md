# Guía de práctica · Examen parcial de laboratorio GIIROB-ICD (modelo red corporativa 10/10)

> Guía **para estudiar y practicar**. El enunciado indica que durante el examen no se permiten apuntes ni chuletas.

## 0. Qué te piden (orden lógico)

1. Puente `vmbrintra` → segmento `192.168.50.0/24`.
2. Puente `vmbrdmz` → segmento `192.168.25.0/24`.
3. Cuatro MV: web DMZ (ID 300, mensaje "DMZ"), web intranet (ID 400 `webserverintranet`, mensaje "intranet"), BBDD (ID 500 `servidorbbdd`), Flask (ID 600 `servidorflask`).
4. Conectar 400, 500 y 600 a `vmbrintra` y hacer que se comuniquen.
5. Aplicación Flask (600) conectada a la BBDD (500).
6. MV con pfSense con 3 tarjetas (WAN, intranet, DMZ).
7. Responder la pregunta final, generar el zip, subirlo y limpiar.

### Ideas clave antes de empezar

- La **MAC del Anexo A** es la que tiene reservada tu puesto en el DHCP del laboratorio. Una MV con esa MAC en `vmbr0` recibe una IP `158.42.181.x` y tiene Internet.
- **Solo una MV a la vez** puede usar esa MAC. Por eso el enunciado dice, tras cada MV: *apagar y poner la MAC en automático*.
- Instala todo el software **mientras la MV está en `vmbr0` con la MAC del anexo** (necesita Internet) y, al terminar, pásala a `vmbrintra` con MAC automática.
- Tu puesto (VM 200 "DebianLEM…") ya usa una MAC de la serie `1D:12:xx`. Para las MV del examen probablemente debas usar la de la otra serie (`1D:11:xx`, tu número ECOMPxx). Confírmalo con el profesor.
- Mira si la **VM 999 (`plantilla-pra…`)** es una plantilla de Debian. Si lo permiten, clonarla ahorra tres instalaciones de Debian.

### Plan de tiempo sugerido

| Tarea | Minutos |
|-------|---------|
| Puentes + MV 300 (Apache) | 10 |
| MV 400, 500, 600 | 20 |
| Red intranet + Flask + BBDD | 10 |
| pfSense + prueba de Internet | 15 |
| Capturas, Word, zip, entrega | 30 |

---

## 1. Primera parte · Puentes de red

Interfaz de Proxmox: nodo `ecompXX` → **System → Network → Create → Linux Bridge**.

| Name        | IPv4/CIDR | Bridge ports | Comment            |
|-------------|-----------|--------------|--------------------|
| `vmbrintra` | (vacío)   | (vacío)      | 192.168.50.0/24    |
| `vmbrdmz`   | (vacío)   | (vacío)      | 192.168.25.0/24    |

Después pulsar **Apply Configuration**.

**Capturas:** Figura 1 (vmbrintra) y Figura 2 (vmbrdmz), con la lista de redes del nodo.

---

## 2. Segunda parte · MV 300 (servidor web DMZ)

### 2.1 Crear la MV

**Create VM**: VM ID `300`, ISO de Debian, disco ~8 GB, 1 núcleo, 1–2 GB de RAM.

En la pestaña **Network**: Bridge `vmbr0`, modelo VirtIO, y en *Advanced* poner la **MAC del Anexo A**.

**Capturas:** Figura 3 (MV con ID 300) y Figura 4 (configuración de red con la MAC).

### 2.2 Portapapeles (en Proxmox)

**Hardware → Display → Edit**: Graphic card `SPICE`, Clipboard `VNC`.

### 2.3 Dentro de la MV 300 (como `root`)

```bash
apt update && apt upgrade -y && apt install -y spice-vdagent wget curl
systemctl enable --now spice-vdagent      # el enunciado escribe "systemclt": es un error
reboot
```

### 2.4 Servidor web con el mensaje "DMZ"

```bash
apt install -y apache2
echo "DMZ" > /var/www/html/index.html
systemctl enable --now apache2
systemctl status apache2
curl http://localhost                     # debe mostrar: DMZ
ip -br a                                  # anota la IP 158.42.181.x
```

**Capturas:** Figura 5 (red de la MV, `ip -br a`) y Figura 6 (`curl` mostrando "DMZ").

### 2.5 Al terminar

```bash
poweroff
```

Proxmox: **Hardware → Network Device (net0) → Edit** → borrar la MAC (dejar en modo **auto**).

---

## 3. MV 400 `webserverintranet`

1. **Create VM**: ID `400`, Name `webserverintranet`, `vmbr0`, MAC del Anexo A, Display SPICE/VNC. → **Captura Figura 7**.
2. Dentro de la MV:

```bash
apt update && apt upgrade -y && apt install -y spice-vdagent wget curl apache2
systemctl enable --now spice-vdagent
echo "intranet" > /var/www/html/index.html
systemctl enable --now apache2
curl http://localhost                     # debe mostrar: intranet
```

→ **Captura Figura 8**.

3. `poweroff` y poner la MAC en automático.

---

## 4. MV 500 `servidorbbdd`

1. **Create VM**: ID `500`, Name `servidorbbdd`, `vmbr0`, MAC del anexo. → **Captura Figura 9**.
2. Dentro de la MV:

```bash
apt update && apt upgrade -y && apt install -y spice-vdagent wget curl mariadb-server
systemctl enable --now spice-vdagent
systemctl enable --now mariadb
```

3. Escuchar fuera del localhost:

```bash
nano /etc/mysql/mariadb.conf.d/50-server.cnf     # bind-address = 0.0.0.0
systemctl restart mariadb
ss -tulpn | grep 3306                            # debe verse 0.0.0.0:3306
```

4. Crear la BBDD, las tablas de la aplicación Flask y el usuario:

```bash
mariadb
```

```sql
CREATE DATABASE IF NOT EXISTS gestor_tareas CHARACTER SET utf8mb4;
USE gestor_tareas;
CREATE TABLE IF NOT EXISTS tareas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  descripcion TEXT,
  completada BOOLEAN DEFAULT 0
);
INSERT INTO tareas (nom, descripcion) VALUES ('Prueba', 'Fila de ejemplo');

CREATE USER IF NOT EXISTS 'lm'@'192.168.50.%' IDENTIFIED BY 'lm';
GRANT ALL PRIVILEGES ON gestor_tareas.* TO 'lm'@'192.168.50.%';
FLUSH PRIVILEGES;

SHOW TABLES;
SELECT * FROM tareas;
```

→ **Captura Figura 10** (SGBD en marcha y tablas creadas).

5. `poweroff` y MAC en automático.

---

## 5. MV 600 `servidorflask`

1. **Create VM**: ID `600`, Name `servidorflask`, `vmbr0`, MAC del anexo. → **Captura Figura 11**.
2. Dentro de la MV:

```bash
apt update && apt upgrade -y && apt install -y spice-vdagent wget curl python3 python3-venv python3-pip
systemctl enable --now spice-vdagent
mkdir -p /opt/gestor && cd /opt/gestor
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy pymysql
python --version
pip list | grep -i -E "flask|pymysql|sqlalchemy"
```

→ **Captura Figura 12** (software de Flask instalado).

3. `poweroff` y MAC en automático.

---

## 6. Conectar 400, 500 y 600 a `vmbrintra`

Para cada una (apagada): **Hardware → Network Device (net0) → Edit** → Bridge `vmbrintra`, MAC en **auto**.

→ **Captura Figura 13** (las tres MV con `vmbrintra`).

---

## 7. Comunicación entre las MV (recuadro de respuesta)

Arranca las tres y configura IP fija en cada una (comprueba el nombre de la interfaz con `ip -br a`; suele ser `ens18`):

```bash
nano /etc/network/interfaces
```

| MV  | Dirección          |
|-----|--------------------|
| 400 | 192.168.50.4/24    |
| 500 | 192.168.50.5/24    |
| 600 | 192.168.50.6/24    |

Ejemplo (MV 400):

```
auto lo
iface lo inet loopback

allow-hotplug ens18
iface ens18 inet static
    address 192.168.50.4/24
    gateway 192.168.50.1
    dns-nameservers 8.8.8.8
```

```bash
systemctl restart networking
ip -br a
ping -c 2 192.168.50.5
ping -c 2 192.168.50.6
```

**Respuesta sugerida para el recuadro:**

> Conecté las tres MV al puente `vmbrintra`, asigné una IP estática de la red 192.168.50.0/24 a cada una (400 → .4, 500 → .5, 600 → .6, máscara /24, puerta de enlace 192.168.50.1) en `/etc/network/interfaces`, reinicié la red y verifiqué con `ping` que se alcanzan entre sí.

→ **Captura Figura 14** (los `ping` entre las MV).

---

## 8. Aplicación Flask (600) + BBDD (500)

En la MV 600, `/opt/gestor/app.py`:

```python
from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lm:lm@192.168.50.5/gestor_tareas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)

PAGINA = """
<h1>Mis tareas</h1>
<form action="/agregar" method="POST">
  <input name="nom" placeholder="Nombre" required>
  <input name="descripcion" placeholder="Descripcion">
  <button>Guardar</button>
</form>
<ul>
{% for t in tareas %}
  <li>{{ t.id }} - {{ t.nom }} - {{ t.descripcion }}</li>
{% endfor %}
</ul>
"""

@app.route('/')
def index():
    return render_template_string(PAGINA, tareas=Tarea.query.all())

@app.route('/agregar', methods=['POST'])
def agregar():
    db.session.add(Tarea(nom=request.form['nom'], descripcion=request.form['descripcion']))
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Ejecutar y probar:

```bash
cd /opt/gestor
source venv/bin/activate
python app.py &
curl http://localhost:5000                # debe listar la tarea de ejemplo
```

→ **Captura Figura 15** (la aplicación Flask funciona).

### Evidencia de la BBDD (Figura 16)

Desde la MV 400 (necesita Internet en ese momento, o instálalo antes mientras estaba en `vmbr0`):

```bash
apt install -y mariadb-client
mysql -h 192.168.50.5 -u lm -plm -D gestor_tareas -e "SELECT * FROM tareas LIMIT 10;"
```

> El enunciado dice "BBDD en la MV con ID=600", pero en este diseño la BBDD está en la **MV 500** (192.168.50.5). Apunta a la 500 y, si quieres, aclara en el Word que es una errata.

Si ya no tienes Internet en 400 para instalar el cliente, instálalo en el paso 3, junto con Apache.

---

## 9. pfSense con tres tarjetas

### 9.1 Crear la MV

**Create VM** (ID libre, p. ej. `700`, nombre `pfsense`): ISO `pfSense-CE-2.7.2-RELEASE-amd64.iso`, 2 GB de RAM, 2 núcleos, disco 5–8 GB.

Tres tarjetas de red VirtIO:

| Dispositivo | Bridge      | Uso    | MAC                |
|-------------|-------------|--------|--------------------|
| net0        | `vmbr0`     | WAN    | **MAC del Anexo A**|
| net1        | `vmbrintra` | LAN (intranet) | automática |
| net2        | `vmbrdmz`   | DMZ    | automática         |

> Para que la MAC del anexo no esté duplicada, las MV 300/400/500/600 deben tener ya la MAC en automático.

### 9.2 Instalación y consola

1. Instalar pfSense con las opciones por defecto y reiniciar.
2. Menú **1) Assign Interfaces**:

```
Should VLANs be set up now [y|n]?   n
WAN interface name:                 vtnet0
LAN interface name:                 vtnet1
Optional 1 interface name:          vtnet2
Do you want to proceed [y|n]?       y
```

3. Menú **2) Set interface(s) IP address**:

| Interfaz | IPv4 | Notas |
|----------|------|-------|
| WAN (vtnet0) | DHCP | recibirá una IP `158.42.181.x` |
| LAN (vtnet1) | `192.168.50.1/24` | sin gateway, IPv6 no |
| OPT1 (vtnet2) | `192.168.25.1/24` | sin gateway, IPv6 no |

Para DMZ (opcional): en la interfaz OPT1 pfSense bloquea todo por defecto; añade una regla *Pass* desde `OPT1 subnets` hacia *any* si quieres que la DMZ salga a Internet.

→ **Captura Figura 17**: menú de consola con WAN (IP 158.42.181.x), LAN 192.168.50.1/24 y OPT1 192.168.25.1/24.

### 9.3 Salida a Internet de las MV de la intranet

La LAN de pfSense trae la regla "Default allow LAN to any" y el NAT de salida automático. Con las MV de la intranet usando `gateway 192.168.50.1` y `dns-nameservers 8.8.8.8` (apartado 7), prueba desde la MV 600 (o 400/500):

```bash
ping -c 2 192.168.50.1       # pfSense
ping -c 2 8.8.8.8            # Internet
ping -c 2 google.com         # DNS + Internet
curl -I https://www.upv.es
```

→ **Captura Figura 18** (al menos una MV accede a Internet).

---

## 10. Pregunta final

**¿Qué falta hacer para poder acceder desde Internet a la aplicación Flask?**

**Respuesta sugerida:**

> La MV de Flask está en la intranet (192.168.50.0/24) y solo es accesible desde dentro. Falta publicarla a través de pfSense: crear en *Firewall → NAT → Port Forward* una regla en la WAN que redirija el puerto TCP 5000 de la IP pública de la WAN (158.42.181.x) a 192.168.50.6:5000, con su regla de firewall asociada que permita ese tráfico en la WAN. Además la aplicación debe escuchar en 0.0.0.0 (no solo en localhost) y la MV debe tener a pfSense como puerta de enlace. Opcionalmente, un nombre DNS y HTTPS (proxy inverso con certificado).

---

## 11. Entregable

En la terminal del Debian (VM 200 / usuario `proxmox`, clave `V1rtu4l`):

```bash
mkdir -p /home/proxmox/Documentos/Examen-<usuarioupvnet>
cd /home/proxmox/Documentos/Examen-<usuarioupvnet>
# guarda aquí las capturas (.png) y el Word con tus respuestas
zip <usuarioupvnet>.zip *.png *.docx
```

1. Sube el zip a la tarea de **PoliformaT** indicada por el profesor.
2. Primer acceso (crea tu clave; **no la pierdas**):

```bash
ssh <usuarioupvnet>@giirob-lemus.itaca.upv.es       # clave inicial: tu DNI
exit
```

3. Copia de seguridad en el servidor (desde la carpeta donde está el zip, en tu Debian, no dentro de la sesión ssh):

```bash
scp <usuarioupvnet>.zip <usuarioupvnet>@giirob-lemus.disca.upv.es:~/
```

> Si `zip` no está instalado: `sudo apt install zip` (o comprímelo desde el entorno gráfico).

## 12. Limpieza (solo después de subir y de copiar con `scp`)

Proxmox: seleccionar cada MV creada por ti → **More → Remove**, marcando **Purge from job configurations** y **Destroy unreferenced disks**, y escribir su ID para confirmar.

- Elimina: `300`, `400`, `500`, `600` y la de pfSense.
- **No elimines** la 200 (tu puesto de trabajo), ni la 100 ni la 999. En la figura del enunciado aparece la 200 solo como ejemplo del procedimiento.

---

## Checklist rápido de capturas

| Figura | Contenido |
|--------|-----------|
| 1, 2   | Puentes `vmbrintra` y `vmbrdmz` |
| 3, 4   | MV 300 creada y su red con la MAC del anexo |
| 5, 6   | Red de la MV 300 y servidor web mostrando "DMZ" |
| 7, 8   | MV 400 creada y servidor web mostrando "intranet" |
| 9, 10  | MV 500 creada y SGBD con las tablas |
| 11, 12 | MV 600 creada y software de Flask instalado |
| 13     | MV 400, 500 y 600 en `vmbrintra` |
| 14     | `ping` entre las MV |
| 15     | Aplicación Flask funcionando |
| 16     | `mysql -h ... SELECT` contra la BBDD |
| 17     | pfSense en marcha con WAN, LAN y DMZ |
| 18     | Una MV con acceso a Internet |
