# Organizador de Archivos 📂

## Descripción del Proyecto 🚀

Este es un potente organizador de archivos desarrollado en Python que te permite gestionar y clasificar tus archivos de manera inteligente y automática. Con funciones avanzadas de organización, podrás mantener tus directorios limpios y bien estructurados.

## Características Principales ✨

- 📁 Organización por extensiones de archivo
- 🔍 Clasificación por contenido de nombre de archivo
- 📊 Agrupación por tamaño de archivo
- 📅 Clasificación por fecha de modificación
- 🌳 Generación de árbol de directorios
- 🛠️ Configuración personalizable mediante reglas JSON
- 💻 Interfaz de línea de comandos intuitiva
- 🖥️ Soporte para selección de directorio mediante diálogo

## Requisitos Previos 🔧

- Python 3.7+
- Tkinter (generalmente incluido con Python)
- PyQt5 (opcional para interfaz gráfica)

## Instalación 💾

1. Clona el repositorio:
```bash
git clone https://github.com/markbus-ai/organize-folder.git
cd organize-folder
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso Básico 🖱️

### Organizar Directorio
```bash
python main.py                  # Organiza el directorio actual
python main.py -d /ruta/carpeta # Organiza un directorio específico
```

### Seleccionar Directorio
```bash
python main.py -s  # Abre un diálogo para seleccionar directorio
```

### Generar Árbol de Directorios
```bash
python main.py -t                 # Genera árbol en tree.txt
python main.py -t mi_arbol.txt    # Genera árbol en archivo personalizado
```

### Gestión de Reglas 📋

#### Listar Reglas Actuales
```bash
python main.py -l
```

#### Agregar Regla por Extensión
```bash
python main.py -e .pdf documentos  # Mueve archivos .pdf a carpeta 'documentos'
```

#### Agregar Regla por Contenido
```bash
python main.py -c "proyecto" proyectos  # Mueve archivos con "proyecto" a carpeta 'proyectos'
```

### Exportar/Importar Configuración
```bash
python main.py -x config_backup.json   # Exportar configuración
python main.py -i config_backup.json   # Importar configuración
```

## Configuración Personalizada 🛠️

El archivo `rules.json` permite configuraciones avanzadas:

```json
{
    "endwith": {
        ".pdf": "documentos",
        ".jpg": "imagenes"
    },
    "contains": {
        "proyecto": "proyectos"
    },
    "size_ranges": {
        "0-10": "pequeños",
        "10-100": "medianos"
    },
    "date_ranges": {
        "30": "antiguos"
    }
}
```


## Licencia 📜

Este proyecto se encuentra bajo la licencia [MIT](LICENSE).

**Nota:** Este script modifica archivos en tu sistema. Se recomienda hacer una copia de seguridad antes de usarlo.
