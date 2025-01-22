from hashlib import sha1
import os
import shutil
import json
import subprocess
import argparse
import datetime
from pathlib import Path
import re
import logging
import sys
from PyQt5.QtWidgets import QApplication

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_rules(rules_file="rules.json"):
    """Load rules from a JSON file with error handling."""
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # Validate rules structure
        if not all(key in rules for key in ["endwith", "contains"]):
            raise ValueError("El archivo de configuración no tiene el formato correcto")
        
        return rules
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error al cargar reglas: {e}")
        # Provide a default configuration if loading fails
        return {
            "endwith": {},
            "contains": {},
            "size_ranges": {},
            "date_ranges": {}
        }

def order_extensions(directory, rules):
    rules = rules["endwith"]
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Saltar si es un directorio
        if os.path.isdir(file_path):
            continue

        # Obtener la extensión del archivo
        _, extension = os.path.splitext(filename)

        # Verificar si tenemos una regla para esta extensión
        if extension in rules:
            # Crear el directorio de destino si no existe
            target_dir = os.path.join(directory, rules[extension])
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # Mover el archivo
            target_path = os.path.join(target_dir, filename)
            try:
                shutil.move(file_path, target_path)
            except Exception as e:
                logging.error(f"Error al mover archivo {filename}: {e}")

def order_by_in(directory, content, output_dir):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Saltar si es un directorio
        if os.path.isdir(file_path):
            continue
        if content in filename:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            try:
                subprocess.Popen(["mv", filename, output_dir])
            except Exception as e:
                logging.error(f"Error al mover archivo {filename}: {e}")
            continue

def generate_tree(directory, prefix="", is_last=True, max_depth=None, current_depth=0):
    """
    Generate a directory tree representation.
    
    Args:
        directory (str): Path to the directory to generate tree for
        prefix (str, optional): Prefix for tree formatting. Defaults to "".
        is_last (bool, optional): Whether this is the last item in its level. Defaults to True.
        max_depth (int, optional): Maximum depth to traverse. Defaults to None.
        current_depth (int, optional): Current depth of traversal. Defaults to 0.
    
    Returns:
        str: Formatted directory tree as a string
    """
    # Check max depth
    if max_depth is not None and current_depth > max_depth:
        return ""
    
    # Get the base name of the directory
    base_name = os.path.basename(directory)
    
    # Start the output with the current directory
    output = prefix + ("└── " if is_last else "├── ") + base_name + "\n"
    
    # If it's a directory, list its contents
    if os.path.isdir(directory):
        try:
            # Get sorted list of items in the directory
            items = sorted([os.path.join(directory, item) for item in os.listdir(directory)])
            
            # Separate folders and files
            folders = [item for item in items if os.path.isdir(item)]
            files = [item for item in items if os.path.isfile(item)]
            
            # Recursively add folders
            for i, folder in enumerate(folders):
                is_last_folder = (i == len(folders) - 1) and not files
                new_prefix = prefix + ("    " if is_last else "│   ")
                output += generate_tree(
                    folder, 
                    new_prefix, 
                    is_last_item=is_last_folder, 
                    max_depth=max_depth, 
                    current_depth=current_depth + 1
                )
            
            # Add files
            for i, file in enumerate(files):
                is_last_file = i == len(files) - 1
                output += prefix + ("└── " if is_last_file and not folders else "├── ") + os.path.basename(file) + "\n"
        
        except PermissionError:
            # Handle directories with no read permissions
            output += prefix + "│   [Acceso denegado]\n"
        except Exception as e:
            # Handle other potential errors
            output += prefix + f"│   [Error: {str(e)}]\n"
    
    return output

def save_tree(directory, output_file, max_depth=None):
    """
    Save the directory tree to a file.
    
    Args:
        directory (str): Path to the directory to generate tree for
        output_file (str): Path to the output file
        max_depth (int, optional): Maximum depth to traverse. Defaults to None.
    """
    try:
        tree = generate_tree(directory, max_depth=max_depth)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Árbol de Directorios generado el: {datetime.datetime.now()}\n")
            f.write("=" * 50 + "\n")
            f.write(tree)
        
        logging.info(f"Árbol de directorios guardado en: {output_file}")
    except Exception as e:
        logging.error(f"Error al guardar el árbol de directorios: {e}")

def order_by_size(directory, rules):
    size_rules = rules.get("size_ranges", {})
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            for size_range, folder in size_rules.items():
                min_size, max_size = map(lambda x: int(x) * 1024 * 1024, size_range.split('-'))
                if min_size <= size <= max_size:
                    target_dir = os.path.join(directory, folder)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    try:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                    except Exception as e:
                        logging.error(f"Error al mover archivo {filename}: {e}")
                    break

def order_by_date(directory, rules):
    date_rules = rules.get("date_ranges", {})
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            mtime = os.path.getmtime(file_path)
            file_date = datetime.datetime.fromtimestamp(mtime)
            for date_range, folder in date_rules.items():
                days = int(date_range.split('-')[0])
                cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
                if file_date >= cutoff_date:
                    target_dir = os.path.join(directory, folder)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    try:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                    except Exception as e:
                        logging.error(f"Error al mover archivo {filename}: {e}")
                    break

def order_by_regex(directory, rules):
    regex_rules = rules.get("regex", {})
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            for pattern, folder in regex_rules.items():
                if re.search(pattern, filename):
                    target_dir = os.path.join(directory, folder)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    try:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                    except Exception as e:
                        logging.error(f"Error al mover archivo {filename}: {e}")
                    break

def order_files(directory, rules_file="rules.json"):
    """Organize files based on rules from a JSON file."""
    rules = load_rules(rules_file)
    
    # Validate directory
    if not os.path.isdir(directory):
        logging.error(f"Error: {directory} no es un directorio válido")
        return

    # Primero mover todos los archivos al directorio principal
    for subdirectory in os.listdir(directory):
        subdirectory_path = os.path.join(directory, subdirectory)
        if os.path.isdir(subdirectory_path):
            for item in os.listdir(subdirectory_path):
                item_path = os.path.join(subdirectory_path, item)
                if os.path.isfile(item_path):
                    try:
                        shutil.move(item_path, directory)
                    except Exception as e:
                        logging.error(f"Error al mover archivo {item}: {e}")

    # Apply different organization strategies
    try:
        order_extensions(directory, rules)
        for content in rules.get("contains", {}).keys():
            order_by_in(directory, content, rules["contains"][content])
        order_by_size(directory, rules)
        order_by_date(directory, rules)
        order_by_regex(directory, rules)
        
        logging.info(f"Archivos organizados exitosamente en: {directory}")
    except Exception as e:
        logging.error(f"Error durante la organización de archivos: {e}")
        import traceback
        traceback.print_exc()

    # Generar árbol si está configurado
    if rules.get("generate_tree", False):
        save_tree(directory, os.path.join(directory, "directory_tree.txt"), 
                 max_depth=rules.get("tree_max_depth", None))

def export_config(rules, output_file):
    """Export current configuration to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
        logging.info(f"Configuración exportada a: {output_file}")
    except Exception as e:
        logging.error(f"Error al exportar configuración: {e}")

def import_config(input_file):
    """Import configuration from a JSON file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            new_rules = json.load(f)
        
        # Validate the imported configuration
        if not all(key in new_rules for key in ["endwith", "contains"]):
            raise ValueError("El archivo de configuración no tiene el formato correcto")
        
        # Update the main rules file
        with open("rules.json", "w", encoding='utf-8') as f:
            json.dump(new_rules, f, indent=4, ensure_ascii=False)
        
        logging.info(f"Configuración importada desde: {input_file}")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error al importar configuración: {e}")

def select_directory(method=None):
    """
    Select a directory using multiple methods.
    
    Args:
        method (str, optional): Method of directory selection. 
        Supports 'dialog', 'gui', 'cli', or None (auto-select).
    
    Returns:
        str: Path to the selected directory or None if no directory selected.
    """
    # Try GUI method first
    try:
        from PyQt5.QtWidgets import QFileDialog, QApplication
        import sys
        
        # Ensure QApplication exists
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Open file dialog
        directory = QFileDialog.getExistingDirectory(
            None, 
            "Selecciona el directorio a organizar", 
            os.path.expanduser('~'),  # Start in user's home directory
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            return directory
    except ImportError:
        pass
    
    # Fallback to CLI method
    import readline  # Enable better input editing in CLI
    
    print("\n🗂️  Selección de Directorio 🗂️")
    print("Elige un método de selección:")
    print("1. Ruta absoluta")
    print("2. Ruta relativa")
    print("3. Directorio actual")
    print("4. Directorio de inicio")
    
    while True:
        try:
            choice = input("Selecciona una opción (1-4): ").strip()
            
            if choice == '1':
                # Absolute path
                path = input("Ingresa la ruta absoluta del directorio: ").strip()
                path = os.path.abspath(os.path.expanduser(path))
            
            elif choice == '2':
                # Relative path
                path = input("Ingresa la ruta relativa del directorio: ").strip()
                path = os.path.abspath(os.path.join(os.getcwd(), path))
            
            elif choice == '3':
                # Current directory
                path = os.getcwd()
            
            elif choice == '4':
                # Home directory
                path = os.path.expanduser('~')
            
            else:
                print("Opción inválida. Intenta de nuevo.")
                continue
            
            # Validate directory
            if os.path.isdir(path):
                print(f"✅ Directorio seleccionado: {path}")
                return path
            else:
                print("❌ La ruta no es un directorio válido. Intenta de nuevo.")
        
        except Exception as e:
            print(f"Error: {e}")
            print("Intenta de nuevo.")

def main():
    parser = argparse.ArgumentParser(description='Organizador de archivos')
    parser.add_argument('--directory', '-d', 
                        help='Directorio a organizar')
    parser.add_argument('--select', '-s', action='store_true',
                        help='Abrir diálogo de selección de directorio')
    parser.add_argument('--gui', '-g', action='store_true',
                       help='Iniciar interfaz gráfica')
    parser.add_argument('--add-extension', '-e', nargs=2, metavar=('EXT', 'FOLDER'),
                       help='Agregar regla de extensión (ej: .pdf docs)')
    parser.add_argument('--add-content', '-c', nargs=2, metavar=('CONTENT', 'FOLDER'),
                       help='Agregar regla de contenido (ej: "proyecto" proyectos)')
    parser.add_argument('--list-rules', '-l', action='store_true',
                       help='Listar todas las reglas actuales')
    parser.add_argument('--tree', '-t', nargs='?', const='tree.txt', metavar='OUTPUT_FILE',
                       help='Generar árbol de directorios (por defecto: tree.txt)')
    parser.add_argument('--export-config', '-x', nargs=1, metavar='OUTPUT_FILE',
                       help='Exportar configuración actual a un archivo JSON')
    parser.add_argument('--import-config', '-i', nargs=1, metavar='INPUT_FILE',
                       help='Importar configuración desde un archivo JSON')
    
    args = parser.parse_args()
    
    # Directory selection logic
    directory = None
    
    if args.directory:
        # Use provided directory
        directory = os.path.abspath(os.path.expanduser(args.directory))
        if not os.path.isdir(directory):
            logging.error(f"El directorio {directory} no es válido")
            return
    
    if args.select or not directory:
        # Open directory selection
        directory = select_directory()
        
        if not directory:
            logging.error("No se seleccionó ningún directorio")
            return
    
    # Default to current directory if no directory specified
    directory = directory or os.getcwd()
    
    if args.gui:
        import sys
        from PyQt5.QtWidgets import QApplication
        from gui import OrganizerGUI
        app = QApplication(sys.argv)
        main_window = OrganizerGUI()
        main_window.show()
        sys.exit(app.exec_())

    if args.add_extension:
        ext, folder = args.add_extension
        if not ext.startswith('.'):
            ext = '.' + ext
        with open("rules.json", "r+") as f:
            rules = json.load(f)
            rules["endwith"][ext] = folder
            f.seek(0)
            json.dump(rules, f, indent=4)
            f.truncate()
        logging.info(f"Regla agregada: archivos {ext} -> carpeta {folder}")
        return

    if args.add_content:
        content, folder = args.add_content
        with open("rules.json", "r+") as f:
            rules = json.load(f)
            rules["contains"][content] = folder
            f.seek(0)
            json.dump(rules, f, indent=4)
            f.truncate()
        logging.info(f"Regla agregada: archivos que contienen '{content}' -> carpeta {folder}")
        return

    if args.list_rules:
        with open("rules.json", "r") as f:
            rules = json.load(f)
            logging.info("\nReglas por extensión:")
            for ext, folder in rules["endwith"].items():
                logging.info(f"  {ext} -> {folder}")
            logging.info("\nReglas por contenido:")
            for content, folder in rules["contains"].items():
                logging.info(f"  '{content}' -> {folder}")
        return

    if args.tree:
        save_tree(args.directory, args.tree)
        logging.info(f"Árbol de directorios guardado en: {args.tree}")
        return

    if args.export_config:
        with open("rules.json", "r") as f:
            rules = json.load(f)
        export_config(rules, args.export_config[0])
        return

    if args.import_config:
        import_config(args.import_config[0])
        return

    # Organize files
    order_files(directory)
    logging.info(f"Archivos organizados en el directorio: {directory}")


if __name__ == "__main__":
    main()
