# Guía de Gestión de Máquinas Virtuales (qm) y Contenedores (pct) en Proxmox VE

En Proxmox VE, **`qm` (Qemu Server)** se utiliza para gestionar Máquinas Virtuales (VM) y **`pct` (Proxmox Container Toolkit)** para Contenedores LXC. Ambos comandos se ejecutan directamente en la terminal (Shell) del nodo principal de Proxmox.

---

## 1. Tabla Comparativa de Comandos Esenciales

| Acción | Máquinas Virtuales (`qm`) | Contenedores LXC (`pct`) |
| :--- | :--- | :--- |
| **Listar todos** | `qm list` | `pct list` |
| **Ver estado** | `qm status <VMID>` | `pct status <CTID>` |
| **Iniciar** | `qm start <VMID>` | `pct start <CTID>` |
| **Apagado seguro** | `qm shutdown <VMID>` | `pct shutdown <CTID>` |
| **Apagado forzado** | `qm stop <VMID>` | `pct stop <CTID>` |
| **Reiniciar** | `qm reboot <VMID>` | `pct reboot <CTID>` |
| **Ver configuración** | `qm config <VMID>` | `pct config <CTID>` |
| **Modificar recursos** | `qm set <VMID> --opciones` | `pct set <CTID> --opciones` |
| **Clonar** | `qm clone <VMID> <NuevoID>` | `pct clone <CTID> <NuevoID>` |
| **Migrar a otro nodo** | `qm migrate <VMID> <Nodo>` | `pct migrate <CTID> <Nodo>` |
| **Eliminar por completo** | `qm destroy <VMID>` | `pct destroy <CTID>` |

---

## 2. Opciones de Modificación (`qm set` y `pct set`)

Las opciones (o flags) te permiten alterar el hardware, la red o el comportamiento del entorno sin necesidad de entrar a la interfaz web.

### Recursos de Hardware (Comunes)

*   **`--memory <Megabytes>`**: Modifica la memoria RAM asignada.
    *   *Ejemplo:* `qm set 100 --memory 2048`
*   **`--cores <Número>`**: Define la cantidad de núcleos (cores) de CPU.
    *   *Ejemplo:* `pct set 102 --cores 4`
*   **`--swap <Megabytes>`** *(Solo en `pct`)*: Modifica la memoria de intercambio del contenedor.
    *   *Ejemplo:* `pct set 102 --swap 512`
*   **`--onboot <1\|0>`**: Configura si el entorno arranca automáticamente al encender el servidor Proxmox.
    *   *Ejemplo:* `qm set 100 --onboot 1`

### Parámetros de Red

*   **Para Contenedores (`pct set --net0 ...`)**: Se configuran múltiples argumentos separados por comas:
    *   *IP Estática:* `pct set 102 --net0 name=eth0,bridge=vmbr0,ip=192.168.1.50/24,gw=192.168.1.1`
    *   *IP por DHCP:* `pct set 102 --net0 name=eth0,bridge=vmbr0,ip=dhcp`
*   **Para Máquinas Virtuales (`qm set --net0 ...`)**:
    *   *Cambiar interfaz/puente:* `qm set 100 --net0 virtio,bridge=vmbr0`
    *   *Configurar IP vía Cloud-Init:* `qm set 100 --ipconfig0 ip=192.168.1.50/24,gw=192.168.1.1`

### Almacenamiento y Discos

*   **Para Máquinas Virtuales (`qm set`)**: Se especifica el bus (`scsi`, `sata`, `ide`) seguido del almacenamiento y tamaño:
    *   *Agregar disco de 32GB:* `qm set 100 --scsi1 local-lvm:32`
    *   *Insertar una ISO:* `qm set 100 --ide2 local:iso/ubuntu.iso,media=cdrom`
*   **Para Contenedores (`pct set`)**: Se gestiona mediante puntos de montaje (`mpX`):
    *   *Añadir punto de montaje:* `pct set 102 --mp0 local-lvm:20,mp=/mnt/datos`

### Administración y Etiquetas

*   **`--name <Texto>`** *(En `qm`)* / **`--hostname <Texto>`** *(En `pct`)*: Cambia el nombre identificativo.
    *   *Ejemplo:* `pct set 102 --hostname mi-servidor`
*   **`--description "Texto"`**: Añade notas explicativas visibles en el panel.
*   **`--tags "tag1,tag2"`**: Agrega etiquetas visuales para organizar la interfaz.
*   **`--protection <1\|0>`**: Activa (1) o desactiva (0) la protección contra borrados accidentales.

---

## 3. Comandos Especiales y Avanzados

A diferencia de las máquinas virtuales, los contenedores LXC comparten el kernel del host, lo que permite interactuar directamente con su sistema de archivos y consola interna.

### Exclusivos para Contenedores (`pct`)

*   **Entrar a la terminal del contenedor:** Abre la consola interna de forma inmediata sin necesidad de SSH o contraseñas.
    ```bash
    pct enter <CTID>
    ```
*   **Ejecutar comando interno:** Corre una instrucción dentro del contenedor directamente desde el host.
    ```bash
    pct exec <CTID> -- apt update
    ```
*   **Montar disco del contenedor:** Monta la raíz del contenedor en una carpeta temporal del host para editar archivos de configuración rápidamente.
    ```bash
    pct mount <CTID>
    ```

### Desbloqueo (Ambos entornos)

Si una tarea (como un backup o una replicación) falla o se interrumpe, el recurso puede quedarse bloqueado en la interfaz. Puedes liberarlo con:

```bash
qm unlock <VMID>
pct unlock <CTID>
```
