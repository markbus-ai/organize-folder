import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTableWidget, QTableWidgetItem, QTabWidget, 
                           QMessageBox, QStyle, QHeaderView, QCheckBox, QTextEdit,
                           QFileDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QPalette
import json
import os
from main import order_files
import re

class ModernButton(QPushButton):
    def __init__(self, text, icon_name=None):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        if icon_name:
            icon = self.style().standardIcon(getattr(QStyle, icon_name))
            self.setIcon(icon)
        self.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(35)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E5E7EB;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6B7280;
            }
        """)

class ModernTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                background-color: white;
                gridline-color: #E5E7EB;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #F3F4F6;
                color: black;
            }
            QHeaderView::section {
                background-color: #6B7280;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.verticalHeader().setVisible(False)

class OrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de Archivos")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        self.load_rules()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
            }
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #4B5563;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #6B7280;
                color: white;
            }
            QLabel {
                font-size: 14px;
                color: #374151;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Crear pestañas
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Pestañas existentes
        self.setup_extensions_tab()
        self.setup_content_tab()
        self.setup_size_tab()
        self.setup_date_tab()
        self.setup_regex_tab()
        self.setup_tree_tab()
        self.setup_organize_tab()
        
        # Botón principal de organizar
        self.organize_btn = ModernButton("Organizar Archivos", "SP_DialogApplyButton")
        self.organize_btn.setMinimumHeight(50)
        self.organize_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        layout.addWidget(self.organize_btn)
        self.organize_btn.clicked.connect(self.organize_files)

    def setup_size_tab(self):
        size_tab = QWidget()
        self.tab_widget.addTab(size_tab, "Tamaño")
        layout = QVBoxLayout(size_tab)
        
        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)
        
        input_layout.addWidget(QLabel("Rango (MB):"))
        self.size_range_entry = ModernLineEdit()
        self.size_range_entry.setPlaceholderText("ej: 0-10")
        input_layout.addWidget(self.size_range_entry)
        
        input_layout.addWidget(QLabel("Carpeta:"))
        self.size_folder_entry = ModernLineEdit()
        input_layout.addWidget(self.size_folder_entry)
        
        add_btn = ModernButton("Agregar", "SP_FileDialogNewFolder")
        input_layout.addWidget(add_btn)
        add_btn.clicked.connect(self.add_size_rule)
        
        self.size_table = ModernTable()
        self.size_table.setColumnCount(2)
        self.size_table.setHorizontalHeaderLabels(["Rango (MB)", "Carpeta"])
        layout.addWidget(self.size_table)
        
        del_btn = ModernButton("Eliminar Seleccionado", "SP_TrashIcon")
        layout.addWidget(del_btn)
        del_btn.clicked.connect(self.delete_size_rule)

    def setup_date_tab(self):
        date_tab = QWidget()
        self.tab_widget.addTab(date_tab, "Fecha")
        layout = QVBoxLayout(date_tab)
        
        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)
        
        input_layout.addWidget(QLabel("Días:"))
        self.days_entry = ModernLineEdit()
        self.days_entry.setPlaceholderText("ej: 30")
        input_layout.addWidget(self.days_entry)
        
        input_layout.addWidget(QLabel("Carpeta:"))
        self.date_folder_entry = ModernLineEdit()
        input_layout.addWidget(self.date_folder_entry)
        
        add_btn = ModernButton("Agregar", "SP_FileDialogNewFolder")
        input_layout.addWidget(add_btn)
        add_btn.clicked.connect(self.add_date_rule)
        
        self.date_table = ModernTable()
        self.date_table.setColumnCount(2)
        self.date_table.setHorizontalHeaderLabels(["Últimos días", "Carpeta"])
        layout.addWidget(self.date_table)
        
        del_btn = ModernButton("Eliminar Seleccionado", "SP_TrashIcon")
        layout.addWidget(del_btn)
        del_btn.clicked.connect(self.delete_date_rule)

    def setup_regex_tab(self):
        regex_tab = QWidget()
        self.tab_widget.addTab(regex_tab, "Regex")
        layout = QVBoxLayout(regex_tab)
        
        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)
        
        input_layout.addWidget(QLabel("Patrón:"))
        self.regex_entry = ModernLineEdit()
        self.regex_entry.setPlaceholderText("ej: .*_backup.*")
        input_layout.addWidget(self.regex_entry)
        
        input_layout.addWidget(QLabel("Carpeta:"))
        self.regex_folder_entry = ModernLineEdit()
        input_layout.addWidget(self.regex_folder_entry)
        
        add_btn = ModernButton("Agregar", "SP_FileDialogNewFolder")
        input_layout.addWidget(add_btn)
        add_btn.clicked.connect(self.add_regex_rule)
        
        self.regex_table = ModernTable()
        self.regex_table.setColumnCount(2)
        self.regex_table.setHorizontalHeaderLabels(["Patrón", "Carpeta"])
        layout.addWidget(self.regex_table)
        
        del_btn = ModernButton("Eliminar Seleccionado", "SP_TrashIcon")
        layout.addWidget(del_btn)
        del_btn.clicked.connect(self.delete_regex_rule)

    def setup_tree_tab(self):
        tree_tab = QWidget()
        self.tab_widget.addTab(tree_tab, "Árbol")
        layout = QVBoxLayout(tree_tab)
        
        # Checkbox para habilitar generación de árbol
        self.tree_enabled = QCheckBox("Generar árbol de directorios")
        self.tree_enabled.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #374151;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout.addWidget(self.tree_enabled)
        
        # Profundidad máxima
        depth_layout = QHBoxLayout()
        layout.addLayout(depth_layout)
        
        depth_layout.addWidget(QLabel("Profundidad máxima:"))
        self.max_depth_entry = ModernLineEdit()
        self.max_depth_entry.setPlaceholderText("Vacío para sin límite")
        depth_layout.addWidget(self.max_depth_entry)
        
        # Vista previa del árbol
        layout.addWidget(QLabel("Vista previa:"))
        self.tree_preview = QTextEdit()
        self.tree_preview.setReadOnly(True)
        self.tree_preview.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.tree_preview)
        
        preview_btn = ModernButton("Actualizar Vista Previa", "SP_BrowserReload")
        layout.addWidget(preview_btn)
        preview_btn.clicked.connect(self.update_tree_preview)

    def update_tree_preview(self):
        try:
            max_depth = int(self.max_depth_entry.text()) if self.max_depth_entry.text() else None
            tree = generate_tree(".", max_depth=max_depth)
            self.tree_preview.setText(tree)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar vista previa: {str(e)}")

    def add_size_rule(self):
        size_range = self.size_range_entry.text().strip()
        folder = self.size_folder_entry.text().strip()
        
        if not size_range or not folder:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        try:
            min_size, max_size = map(float, size_range.split('-'))
        except:
            QMessageBox.warning(self, "Error", "Formato de rango inválido. Use: min-max")
            return
            
        if "size_ranges" not in self.rules:
            self.rules["size_ranges"] = {}
        self.rules["size_ranges"][size_range] = folder
        self.save_rules()
        self.size_range_entry.clear()
        self.size_folder_entry.clear()

    def add_date_rule(self):
        days = self.days_entry.text().strip()
        folder = self.date_folder_entry.text().strip()
        
        if not days or not folder:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        try:
            days_int = int(days)
        except:
            QMessageBox.warning(self, "Error", "Los días deben ser un número entero")
            return
            
        if "date_ranges" not in self.rules:
            self.rules["date_ranges"] = {}
        self.rules["date_ranges"][f"{days}-0"] = folder
        self.save_rules()
        self.days_entry.clear()
        self.date_folder_entry.clear()

    def add_regex_rule(self):
        pattern = self.regex_entry.text().strip()
        folder = self.regex_folder_entry.text().strip()
        
        if not pattern or not folder:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        try:
            re.compile(pattern)
        except:
            QMessageBox.warning(self, "Error", "Patrón regex inválido")
            return
            
        if "regex" not in self.rules:
            self.rules["regex"] = {}
        self.rules["regex"][pattern] = folder
        self.save_rules()
        self.regex_entry.clear()
        self.regex_folder_entry.clear()

    def delete_size_rule(self):
        current_row = self.size_table.currentRow()
        if current_row < 0:
            return
        size_range = self.size_table.item(current_row, 0).text()
        del self.rules["size_ranges"][size_range]
        self.save_rules()

    def delete_date_rule(self):
        current_row = self.date_table.currentRow()
        if current_row < 0:
            return
        days = self.date_table.item(current_row, 0).text()
        del self.rules["date_ranges"][f"{days}-0"]
        self.save_rules()

    def delete_regex_rule(self):
        current_row = self.regex_table.currentRow()
        if current_row < 0:
            return
        pattern = self.regex_table.item(current_row, 0).text()
        del self.rules["regex"][pattern]
        self.save_rules()

    def update_tables(self):
        # Actualizar tablas existentes
        self.ext_table.setRowCount(0)
        for ext, folder in self.rules.get("endwith", {}).items():
            row = self.ext_table.rowCount()
            self.ext_table.insertRow(row)
            self.ext_table.setItem(row, 0, QTableWidgetItem(ext))
            self.ext_table.setItem(row, 1, QTableWidgetItem(folder))
        
        self.content_table.setRowCount(0)
        for content, folder in self.rules.get("contains", {}).items():
            row = self.content_table.rowCount()
            self.content_table.insertRow(row)
            self.content_table.setItem(row, 0, QTableWidgetItem(content))
            self.content_table.setItem(row, 1, QTableWidgetItem(folder))
        
        # Actualizar tabla de tamaños
        self.size_table.setRowCount(0)
        for size_range, folder in self.rules.get("size_ranges", {}).items():
            row = self.size_table.rowCount()
            self.size_table.insertRow(row)
            self.size_table.setItem(row, 0, QTableWidgetItem(size_range))
            self.size_table.setItem(row, 1, QTableWidgetItem(folder))
        
        # Actualizar tabla de fechas
        self.date_table.setRowCount(0)
        for date_range, folder in self.rules.get("date_ranges", {}).items():
            days = date_range.split('-')[0]
            row = self.date_table.rowCount()
            self.date_table.insertRow(row)
            self.date_table.setItem(row, 0, QTableWidgetItem(days))
            self.date_table.setItem(row, 1, QTableWidgetItem(folder))
        
        # Actualizar tabla de regex
        self.regex_table.setRowCount(0)
        for pattern, folder in self.rules.get("regex", {}).items():
            row = self.regex_table.rowCount()
            self.regex_table.insertRow(row)
            self.regex_table.setItem(row, 0, QTableWidgetItem(pattern))
            self.regex_table.setItem(row, 1, QTableWidgetItem(folder))
        
        # Actualizar configuración de árbol
        self.tree_enabled.setChecked(self.rules.get("generate_tree", False))
        max_depth = self.rules.get("tree_max_depth")
        self.max_depth_entry.setText(str(max_depth) if max_depth is not None else "")

    def save_rules(self):
        # Guardar configuración de árbol
        self.rules["generate_tree"] = self.tree_enabled.isChecked()
        try:
            max_depth = int(self.max_depth_entry.text()) if self.max_depth_entry.text() else None
            self.rules["tree_max_depth"] = max_depth
        except:
            self.rules["tree_max_depth"] = None
            
        with open("rules.json", "w", encoding='utf-8') as f:
            json.dump(self.rules, f, indent=4, ensure_ascii=False)
        self.update_tables()

    def load_rules(self):
        try:
            with open("rules.json", "r", encoding='utf-8') as f:
                self.rules = json.load(f)
        except FileNotFoundError:
            self.rules = {"endwith": {}, "contains": {}}
        self.update_tables()

    def setup_extensions_tab(self):
        extensions_tab = QWidget()
        self.tab_widget.addTab(extensions_tab, "Extensiones")
        ext_layout = QVBoxLayout(extensions_tab)
        
        # Input para extensiones
        ext_input_layout = QHBoxLayout()
        ext_layout.addLayout(ext_input_layout)
        
        ext_input_layout.addWidget(QLabel("Extensión:"))
        self.ext_entry = ModernLineEdit()
        ext_input_layout.addWidget(self.ext_entry)
        
        ext_input_layout.addWidget(QLabel("Carpeta:"))
        self.folder_entry = ModernLineEdit()
        ext_input_layout.addWidget(self.folder_entry)
        
        self.add_ext_btn = ModernButton("Agregar", "SP_FileDialogNewFolder")
        ext_input_layout.addWidget(self.add_ext_btn)
        self.add_ext_btn.clicked.connect(self.add_extension_rule)
        
        # Tabla de extensiones
        self.ext_table = ModernTable()
        self.ext_table.setColumnCount(2)
        self.ext_table.setHorizontalHeaderLabels(["Extensión", "Carpeta"])
        ext_layout.addWidget(self.ext_table)
        
        self.del_ext_btn = ModernButton("Eliminar Seleccionado", "SP_TrashIcon")
        ext_layout.addWidget(self.del_ext_btn)
        self.del_ext_btn.clicked.connect(self.delete_extension_rule)

    def setup_content_tab(self):
        content_tab = QWidget()
        self.tab_widget.addTab(content_tab, "Contenido")
        content_layout = QVBoxLayout(content_tab)
        
        # Input para contenido
        content_input_layout = QHBoxLayout()
        content_layout.addLayout(content_input_layout)
        
        content_input_layout.addWidget(QLabel("Contiene:"))
        self.content_entry = ModernLineEdit()
        content_input_layout.addWidget(self.content_entry)
        
        content_input_layout.addWidget(QLabel("Carpeta:"))
        self.content_folder_entry = ModernLineEdit()
        content_input_layout.addWidget(self.content_folder_entry)
        
        self.add_content_btn = ModernButton("Agregar", "SP_FileDialogNewFolder")
        content_input_layout.addWidget(self.add_content_btn)
        self.add_content_btn.clicked.connect(self.add_content_rule)
        
        # Tabla de contenido
        self.content_table = ModernTable()
        self.content_table.setColumnCount(2)
        self.content_table.setHorizontalHeaderLabels(["Contiene", "Carpeta"])
        content_layout.addWidget(self.content_table)
        
        self.del_content_btn = ModernButton("Eliminar Seleccionado", "SP_TrashIcon")
        content_layout.addWidget(self.del_content_btn)
        self.del_content_btn.clicked.connect(self.delete_content_rule)

    def add_extension_rule(self):
        ext = self.ext_entry.text().strip()
        folder = self.folder_entry.text().strip()
        
        if not ext or not folder:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        if not ext.startswith('.'):
            ext = '.' + ext
            
        self.rules["endwith"][ext] = folder
        self.save_rules()
        self.ext_entry.clear()
        self.folder_entry.clear()

    def add_content_rule(self):
        content = self.content_entry.text().strip()
        folder = self.content_folder_entry.text().strip()
        
        if not content or not folder:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        self.rules["contains"][content] = folder
        self.save_rules()
        self.content_entry.clear()
        self.content_folder_entry.clear()

    def delete_extension_rule(self):
        current_row = self.ext_table.currentRow()
        if current_row < 0:
            return
            
        ext = self.ext_table.item(current_row, 0).text()
        del self.rules["endwith"][ext]
        self.save_rules()

    def delete_content_rule(self):
        current_row = self.content_table.currentRow()
        if current_row < 0:
            return
            
        content = self.content_table.item(current_row, 0).text()
        del self.rules["contains"][content]
        self.save_rules()

    def organize_files(self):
        try:
            order_files(".")
            QMessageBox.information(self, "Éxito", "Archivos organizados correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al organizar archivos: {str(e)}")

    def select_directory(self):
        """
        Open a directory selection dialog and update the directory input.
        """
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Selecciona el directorio a organizar", 
            os.path.expanduser('~'),  # Start in user's home directory
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            # Find the directory input field and set its text
            directory_inputs = [
                getattr(self, 'directory_input', None),
                getattr(self, 'organize_directory_input', None)
            ]
            
            for input_field in directory_inputs:
                if input_field and isinstance(input_field, QLineEdit):
                    input_field.setText(directory)
                    break
            
            # Optional: Show a confirmation message
            QMessageBox.information(
                self, 
                "Directorio Seleccionado", 
                f"Directorio seleccionado:\n{directory}"
            )
        
        return directory

    def setup_organize_tab(self):
        """
        Create a tab for file organization with directory selection.
        """
        organize_tab = QWidget()
        organize_layout = QVBoxLayout()

        # Directory selection section
        directory_section = QHBoxLayout()
        self.organize_directory_input = ModernLineEdit()
        self.organize_directory_input.setPlaceholderText("Directorio a organizar")
        
        select_directory_btn = ModernButton("Seleccionar Directorio", "SP_DirOpenIcon")
        select_directory_btn.clicked.connect(self.select_directory)
        
        directory_section.addWidget(self.organize_directory_input)
        directory_section.addWidget(select_directory_btn)
        
        organize_layout.addLayout(directory_section)

        # Organization options
        options_group = QWidget()
        options_layout = QVBoxLayout()
        
        # Extension-based organization
        extension_check = QCheckBox("Organizar por extensión")
        extension_check.setChecked(True)
        options_layout.addWidget(extension_check)
        
        # Content-based organization
        content_check = QCheckBox("Organizar por contenido")
        options_layout.addWidget(content_check)
        
        # Size-based organization
        size_check = QCheckBox("Organizar por tamaño")
        options_layout.addWidget(size_check)
        
        # Date-based organization
        date_check = QCheckBox("Organizar por fecha")
        options_layout.addWidget(date_check)
        
        options_group.setLayout(options_layout)
        organize_layout.addWidget(options_group)

        # Organize button
        organize_btn = ModernButton("Organizar Archivos", "SP_DialogApplyButton")
        organize_btn.clicked.connect(self.organize_files)
        organize_layout.addWidget(organize_btn)

        # Add stretch to push everything to the top
        organize_layout.addStretch(1)
        
        organize_tab.setLayout(organize_layout)
        self.tab_widget.addTab(organize_tab, "Organizar")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = OrganizerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
