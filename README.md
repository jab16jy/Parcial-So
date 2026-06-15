# SysAdmin Assistant

Herramienta CLI para administración del sistema operativo — monitoreo,
gestión de procesos, organización de archivos, copias de seguridad,
generación de reportes y automatización programada.

Desarrollado para la materia Sistemas Operativos.

## Requisitos

- Python 3.10+
- pip

## Dependencias

Instalar con:

```bash
pip install -r requirements.txt
```

- **psutil** — métricas del sistema y procesos
- **rich** — interfaz CLI con tablas, paneles y barras de progreso
- **schedule** — programación de tareas periódicas

## Cómo ejecutar

```bash
python main.py
```

## Módulos

| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | Información del Sistema | Detalles del SO, hardware y recursos en vivo |
| 2 | Monitor de Procesos | Listar, buscar y finalizar procesos con protección de PIDs del sistema |
| 3 | Organizador de Archivos | Clasificación automática por tipo (Documentos, Imágenes, Videos, Otros) |
| 4 | Copias de Seguridad | Copia recursiva con barra de progreso y registro con timestamp |
| 5 | Generación de Reportes | Exporta info del sistema + lista de procesos a TXT o CSV |
| 6 | Automatización Programada | Programa backups, reportes y organización a intervalos definidos |

## Seguridad

- Los PIDs 0 y 1 están **siempre protegidos** contra finalización.
- Los procesos del usuario root requieren **confirmación adicional** antes de matarlos.
- Todas las operaciones se registran en `logs/sysadmin_events.json`.
