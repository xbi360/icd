# Guía de Gestión de Máquinas Virtuales (qm) y Contenedores (pct) en Proxmox VE

En Proxmox VE, **`qm` (Qemu Server)** se utiliza para gestionar Máquinas Virtuales (VM) y **`pct` (Proxmox Container Toolkit)** para Contenedores LXC. Ambos comandos se ejecutan directamente en la terminal (Shell) del nodo principal de Proxmox.

---

## Tabla Comparativa de Comandos Esenciales

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

## Comandos Especiales y Avanzados

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

Si una tarea (como un backup o una replicación) falla o se interrumpe, el recurso puede quedarse bloqueado. Puedes liberarlo con:

```bash
qm unlock <VMID>
pct unlock <CTID>
```
