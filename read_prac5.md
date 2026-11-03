# Práctica 5 · pfSense, DMZ e intranet corporativa sobre Proxmox VE

Resumen de las instrucciones y comandos necesarios para reproducir la práctica.

## 0. Esquema de la infraestructura

Proxmox VE 8.4.0 · nodo `pve` · `192.168.10.2/24` · puerta de enlace de la red local `192.168.10.1`.

| VMID | Nombre   | Tipo        | Función                 | Bridge             | Dirección                                   |
|------|----------|-------------|-------------------------|--------------------|---------------------------------------------|
| 103  | pfSense  | VM          | Cortafuegos / router    | vmbr0, vmbr1, vmbr2| 192.168.10.3 (DHCP) · 192.168.100.1 · 192.168.50.1 |
| 100  | srv-sgbd | Contenedor  | MariaDB                 | vmbr1              | 192.168.100.3                               |
| 101  | web-dmz  | Contenedor  | Apache (DMZ)            | vmbr2              | 192.168.50.2                                |
| 102  | appflask | Contenedor  | Aplicación Flask        | vmbr1              | 192.168.100.2                               |
| 104  | srv-web  | Contenedor  | Apache (intranet)       | vmbr1              | 192.168.100.4                               |

Segmentos:

| Interfaz pfSense | Segmento   | Red               | Bridge |
|------------------|------------|-------------------|--------|
| vtnet0           | WAN        | DHCP (red local)  | vmbr0  |
| vtnet1           | LAN / Intranet | 192.168.100.0/24 | vmbr1 |
| vtnet2           | OPT1 → DMZ | 192.168.50.0/24   | vmbr2  |

---

## 1. Creación de la VM pfSense y de los contenedores (interfaz web de Proxmox)

**VM 103 (pfSense)** — *Create VM*:

- ISO: `pfSense-CE-2.7.2-RELEASE-amd64.iso` (subir antes en **local → ISO Images → Upload**).
- Memoria: 2 GB · CPU: 2 núcleos (tipo por defecto).
- Disco: 5 GB en `local-lvm`.
- Red: **tres** dispositivos VirtIO → `net0` = `vmbr0`, `net1` = `vmbr1`, `net2` = `vmbr2`.

**Contenedores LXC (Debian)** — *Create CT*:

- `100` srv-sgbd · `101` web-dmz · `102` appflask · `104` srv-web.
- Una sola interfaz de red por contenedor y firewall de Proxmox activado en ella (valor por defecto).

## 2. Creación de los bridges internos

Interfaz web: **Datacenter → Node → Network → Create → Linux Bridge**, dejando **vacío el campo "Bridge ports"** (vmbr1 y vmbr2). Después pulsar **Apply Configuration**.

Resultado en `/etc/network/interfaces` del anfitrión (extracto). No se asigna IP al anfitrión en vmbr1 ni en vmbr2:

```
auto vmbr1
iface vmbr1 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
# Intranet corporativa 192.168.100.0/24

auto vmbr2
iface vmbr2 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
# Zona desmilitarizada 192.168.50.0/24
```

## 3. Instalación de pfSense y asignación de interfaces

1. Arrancar la VM 103 desde la ISO y completar el instalador sobre el disco de 5 GB; reiniciar.
2. En el **menú de consola**, elegir la opción **1) Assign Interfaces** y responder:

```
Should VLANs be set up now [y|n]?            n
Enter the WAN interface name (or 'a'):       vtnet0
Enter the LAN interface name:                vtnet1
Enter the Optional 1 interface name:         vtnet2
Do you want to proceed [y|n]?                y
```

Resultado:

```
WAN  (wan)  -> vtnet0
LAN  (lan)  -> vtnet1
OPT1 (opt1) -> vtnet2
```

## 4. Direccionamiento de las interfaces internas

Menú de consola → **2) Set interface(s) IP address**:

| Interfaz | IPv4            | DHCP de la consola | IPv6      |
|----------|-----------------|--------------------|-----------|
| LAN      | 192.168.100.1/24| No                 | Desactivado |
| OPT1     | 192.168.50.1/24 | No                 | Desactivado |
| WAN      | **DHCP** (recibe 192.168.10.3) | — | — |

> **Importante:** no fijar `192.168.10.1` en la WAN (es la puerta de enlace de la red local); dejarla en DHCP.

## 5. Conexión de los contenedores a los bridges

Interfaz web: **CT → Network → Edit**.

- `srv-sgbd` (100), `appflask` (102) y `srv-web` (104) → bridge **vmbr1**.
- `web-dmz` (101) → bridge **vmbr2**.
- Anotar la **dirección MAC** de cada contenedor (se necesita para las reservas DHCP).

MACs de la práctica:

| Contenedor | MAC               | Bridge | IP reservada   |
|------------|-------------------|--------|----------------|
| appflask   | BC:24:11:4D:ED:17 | vmbr1  | 192.168.100.2  |
| srv-sgbd   | BC:24:11:6B:AD:C4 | vmbr1  | 192.168.100.3  |
| srv-web    | BC:24:11:23:75:5B | vmbr1  | 192.168.100.4  |
| web-dmz    | BC:24:11:0E:E1:59 | vmbr2  | 192.168.50.2   |

## 6. Acceso a la webConfigurator de pfSense

### Vía A — regla en la WAN con `easyrule`

En la consola de pfSense, opción **8) Shell**:

```bash
easyrule pass wan tcp 192.168.10.1 192.168.10.3 80
```

Navegador: `https://192.168.10.3` · usuario `admin` · contraseña por defecto `pfsense` (aceptar el certificado autofirmado).

### Vía B — túnel SSH a través del anfitrión Proxmox (sin abrir puertos en la WAN)

```bash
# en el anfitrión Proxmox
ip addr add 192.168.100.250/24 dev vmbr1
ping -c 2 192.168.100.1

# en el equipo de trabajo
ssh -L 8080:192.168.100.1:80 root@192.168.10.2

# en el navegador
http://localhost:8080
```

> El aviso rojo sobre la contraseña por defecto desaparece al cambiarla en **System → User Manager**.

## 7. Renombrar OPT1 como DMZ

**Interfaces → OPT1**: cambiar solo el campo **Description** a `DMZ`. Mantener IPv4 en *Static IPv4* `192.168.50.1/24` e IPv6 en *None*. Guardar y aplicar cambios.

## 8. Servidor DHCP

### 8.1 LAN (intranet)

**Services → DHCP Server → LAN**:

- Enable DHCP server on LAN interface.
- Address Pool Range: `192.168.100.100` – `192.168.100.200`.
- Gateway: `192.168.100.1` · DNS server: `192.168.100.1` · Domain name: `practica.local`.

**Static Mappings** (pestaña inferior → *Add*), con MAC, IP y hostname:

| MAC               | IP            | Hostname | Descripción        |
|-------------------|---------------|----------|--------------------|
| bc:24:11:4d:ed:17 | 192.168.100.2 | appflask | Aplicación Flask   |
| bc:24:11:6b:ad:c4 | 192.168.100.3 | srv-sgbd | Servidor MariaDB   |
| bc:24:11:23:75:5b | 192.168.100.4 | srv-web  | Servidor Web Intranet |

### 8.2 DMZ

**Services → DHCP Server → DMZ**:

- Enable DHCP server on DMZ interface.
- Address Pool Range: `192.168.50.100` – `192.168.50.200`.
- Gateway: `192.168.50.1` · DNS server: `192.168.50.1`.
- Static Mapping: `bc:24:11:0e:e1:59` → `192.168.50.2`, hostname `web-dmz`.

> Las reservas deben quedar **fuera** del rango dinámico.

## 9. Cambiar los contenedores a DHCP

Para cada contenedor: **CT → Network → Edit** → IPv4 = **DHCP** (sin indicar gateway). Reiniciar el contenedor y comprobar:

```bash
ip a                  # la IP debe coincidir con la reserva y aparecer como "dynamic"
ip route              # default via 192.168.100.1  (o 192.168.50.1 en la DMZ)
cat /etc/resolv.conf  # nameserver 192.168.100.1   (o 192.168.50.1 en la DMZ)
```

## 10. Configuración del DNS

### 10.1 System → General Setup

| Parámetro     | Valor          |
|---------------|----------------|
| Hostname      | pfSense        |
| Domain        | practica.local |
| DNS primario  | 8.8.8.8        |
| DNS secundario| 1.1.1.1        |

Desmarcar la opción que permite que el DHCP de la WAN sustituya la lista de DNS.

### 10.2 Services → DNS Resolver

- Habilitar el DNS Resolver (escucha en interfaces internas, salida por WAN).
- Marcar **Register DHCP leases in the DNS Resolver** y **Register DHCP static mappings in the DNS Resolver**.
- **Host Overrides** (dominio `practica.local`):

| Host      | IP            |
|-----------|---------------|
| flask     | 192.168.100.2 |
| sgbd      | 192.168.100.3 |
| web-dmz   | 192.168.50.2  |
| web-intra | 192.168.100.4 |

(`pfsense.practica.local` se resuelve solo gracias a hostname + dominio.)

### 10.3 Comprobación (desde srv-sgbd)

```bash
nslookup web-dmz.practica.local 192.168.100.1     # -> 192.168.50.2
nslookup web-intra.practica.local 192.168.100.1   # -> 192.168.100.4
nslookup flask.practica.local 192.168.100.1       # -> 192.168.100.2
nslookup sgbd.practica.local 192.168.100.1        # -> 192.168.100.3
```

## 11. Reglas de firewall de la DMZ

**Firewall → Rules → DMZ**, en este orden (pfSense aplica la **primera** regla que coincide):

| Orden | Acción   | Protocolo | Origen      | Destino        | Puerto   | Descripción               |
|-------|----------|-----------|-------------|----------------|----------|---------------------------|
| 1     | Pass     | TCP/UDP   | DMZ subnets | This Firewall (self) | 53 (DNS) | DNS a pfSense        |
| 2     | **Block**| Any       | DMZ subnets | LAN subnets    | Any      | DMZ no accede a la LAN    |
| 3     | Pass     | Any       | DMZ subnets | Any            | Any      | DMZ a Internet            |

- Si alguna regla queda mal colocada, reordenarla arrastrándola; luego **Save** y **Apply Changes**.
- **LAN**: se mantiene la regla por defecto *Default allow LAN to any*.
- **DHCP** no necesita regla.

## 12. Publicación de servicios con NAT (Port Forward)

**Firewall → NAT → Port Forward → Add** (una regla por servicio). En todas: Interface `WAN`, Protocol `TCP`, Destination `WAN address`, y **Filter rule association = Add associated filter rule**.

| Servicio      | Puerto WAN | Redirect target IP | Puerto destino |
|---------------|------------|--------------------|----------------|
| Web DMZ       | 80         | 192.168.50.2       | 80             |
| Web intranet  | 8080       | 192.168.100.4      | 80             |
| Flask         | 5000       | 192.168.100.2      | 5000           |

Revisar las reglas asociadas en **Firewall → Rules → WAN**.

> Al publicar el puerto 80 hacia la DMZ, la regla de `easyrule` deja de ser necesaria: administrar pfSense desde entonces por el túnel SSH (apartado 6, vía B).

## 13. Servidores web Apache (contenedores `web-dmz` y `srv-web`)

En cada contenedor:

```bash
sudo apt update
sudo apt install apache2 -y
sudo systemctl enable --now apache2
sudo nano /var/www/html/index.html
```

Página de la **DMZ** (`web-dmz`, IP 192.168.50.2) — para `srv-web` cambiar el rótulo por `Intranet Corporativa` y la IP por `192.168.100.4`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Zona desmilitarizada</title>
  <style>
    body { margin:0; min-height:100vh; display:flex; align-items:center;
           justify-content:center; background:#f4f6fa;
           font-family:"Segoe UI",Arial,sans-serif; color:#1f2937; }
    .tarjeta { width:520px; padding:36px 40px; background:#fff;
               border-radius:12px; box-shadow:0 8px 24px rgba(15,23,42,.10); }
    h1 { margin:0 0 14px; font-size:1.45rem; line-height:1.25; }
    .rotulo { display:flex; align-items:center; gap:8px; margin:0;
              color:#2563eb; font-weight:600; letter-spacing:.04em;
              text-transform:uppercase; }
    .punto { width:8px; height:8px; border-radius:50%; background:#22c55e; }
    hr { border:0; border-top:1px solid #e5e7eb; margin:18px 0; }
    .fila { display:flex; justify-content:space-between; align-items:center;
            background:#eef2f7; padding:12px 16px; border-radius:8px;
            margin-bottom:8px; font-size:.95rem; }
    .ip { background:#0f172a; color:#fff; padding:3px 10px;
          border-radius:6px; font-family:Consolas,monospace; }
  </style>
</head>
<body>
  <div class="tarjeta">
    <h1>Infraestructura Informática para Centros de Procesamiento de Datos</h1>
    <p class="rotulo"><span class="punto"></span>Zona desmilitarizada</p>
    <hr>
    <div class="fila"><span>Estudiante:</span><span>Luis Mario Laesa</span></div>
    <div class="fila"><span>Dirección IP:</span>
      <span class="ip">192.168.50.2</span></div>
  </div>
</body>
</html>
```

Comprobar desde un equipo de la red local:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://192.168.10.3/        # 200
curl -s http://192.168.10.3/ | grep -o "ZONA DESMILITARIZADA"
curl -s -o /dev/null -w "%{http_code}\n" http://192.168.10.3:8080/   # 200
curl -s http://192.168.10.3:8080/ | grep -o "Intranet Corporativa"
```

(El `grep` distingue mayúsculas; el rótulo se muestra en mayúsculas por CSS, pero en el HTML está como "Zona desmilitarizada". Si el `grep` no coincide, buscar sin distinguir mayúsculas con `grep -io`.)

## 14. MariaDB accesible desde la red (contenedor `srv-sgbd`)

```bash
sudo apt update
sudo apt install mariadb-server -y
sudo systemctl enable --now mariadb
```

Editar la configuración para escuchar en todas las interfaces:

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

```
bind-address = 0.0.0.0
```

```bash
sudo systemctl restart mariadb
sudo ss -tulpn | grep 3306        # debe mostrar 0.0.0.0:3306 y no 127.0.0.1:3306
```

Crear la base de datos, la tabla y los datos (mismo SQL que la Práctica 4: `gestor_tareas`, tabla `tareas`) y el usuario **solo desde appflask**:

```sql
CREATE DATABASE IF NOT EXISTS gestor_tareas
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestor_tareas;
CREATE TABLE IF NOT EXISTS tareas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  descripcion TEXT,
  completada BOOLEAN DEFAULT 0
);

CREATE USER 'lm'@'192.168.100.2' IDENTIFIED BY 'lm';
GRANT ALL PRIVILEGES ON gestor_tareas.* TO 'lm'@'192.168.100.2';
FLUSH PRIVILEGES;
```

## 15. Aplicación Flask (contenedor `appflask`)

```bash
sudo apt install python3 python3-venv python3-pip -y
cd /opt
sudo mkdir gestor && sudo chown $USER gestor && cd gestor

python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy pymysql

mkdir templates static
nano app.py                  # ver cambios abajo
nano templates/index.html    # igual que en la Práctica 4
nano static/style.css        # igual que en la Práctica 4
```

`app.py` es **el mismo de la Práctica 4** con solo dos cambios:

```python
# 1) La base de datos está en otro contenedor (no en localhost):
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://lm:lm@192.168.100.3/gestor_tareas'

# 2) Escuchar en todas las interfaces, sin modo debug:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 15.1 Servicio systemd (arranque automático)

```bash
sudo nano /etc/systemd/system/gestor.service
```

```ini
[Unit]
Description=Gestor de tareas Flask
After=network.target

[Service]
User=lm
WorkingDirectory=/opt/gestor
ExecStart=/opt/gestor/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gestor
systemctl status gestor
```

> **Nota:** la unidad usa `User=lm`; ese usuario debe existir en el sistema del contenedor (por ejemplo `sudo useradd -r lm`) y tener acceso de lectura a `/opt/gestor`; si no, el servicio no arrancará. Alternativa: quitar la línea `User=lm`.

Comprobar:

```bash
curl -s http://localhost:5000/ | grep -o "Gestor de Tareas"
```

Desde la red local: `http://192.168.10.3:5000`

## 16. Validación del aislamiento de la DMZ (desde `web-dmz`)

```bash
ping -c 2 8.8.8.8                       # responde: hay salida a Internet
ping -c 2 google.com                    # responde: el DNS de pfSense resuelve
curl --max-time 5 http://192.168.100.4  # debe fallar:
# curl: (28) Connection timed out after 5001 milliseconds
```

Prueba inversa (desde un contenedor de la LAN, debe funcionar):

```bash
curl http://192.168.50.2
```

## 17. Comprobaciones adicionales

En pfSense:

- **Status → DHCP Leases**: deben verse las cuatro reservas con su MAC.
- **Firewall → NAT → Port Forward**: tres reglas activas (80, 8080, 5000).
- **Firewall → Rules → DMZ / WAN / LAN**: reglas según los apartados 11 y 12.

## 18. Resumen de comprobaciones

| Comprobación          | Procedimiento                                      | Resultado esperado                               |
|-----------------------|----------------------------------------------------|--------------------------------------------------|
| Dirección por DHCP    | `ip a` en appflask                                 | 192.168.100.2/24, `dynamic`                      |
| Resolución interna    | `nslookup web-dmz.practica.local 192.168.100.1`    | 192.168.50.2                                     |
| Reglas de reenvío     | Firewall → NAT → Port Forward                      | Tres reglas (80, 8080, 5000)                     |
| Web de la DMZ         | `http://192.168.10.3`                              | Rótulo ZONA DESMILITARIZADA e IP 192.168.50.2    |
| Web de la intranet    | `http://192.168.10.3:8080`                         | Rótulo Intranet Corporativa e IP 192.168.100.4   |
| Aislamiento de la DMZ | `curl --max-time 5 http://192.168.100.4` en web-dmz| `Connection timed out`                           |
| Acceso a MariaDB      | `ss -tulpn \| grep 3306` en srv-sgbd               | Escucha en `0.0.0.0:3306`                        |
