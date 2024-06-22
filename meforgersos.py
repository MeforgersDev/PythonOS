import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QTextEdit, QVBoxLayout, QWidget, QMessageBox, QTreeView, QFileSystemModel, QInputDialog, QLabel, QHBoxLayout, QPushButton, QDesktopWidget, QSystemTrayIcon, QStyle, QMenuBar, QStatusBar, QToolBar, QLineEdit, QListView
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDir, Qt, QAbstractListModel, QModelIndex, QVariant, QUrl

# Sanal Dosya Sistemi için kök dizin
VIRTUAL_FS_ROOT = "virtual_fs"

class VirtualFileSystemModel(QAbstractListModel):
    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        self.root_path = root_path
        self.file_list = []
        self.load_files()

    def load_files(self):
        self.file_list = os.listdir(self.root_path)

    def rowCount(self, parent=QModelIndex()):
        return len(self.file_list)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.file_list[index.row()]

    def add_file(self, filename):
        with open(os.path.join(self.root_path, filename), 'w') as f:
            f.write('')
        self.load_files()
        self.layoutChanged.emit()

    def delete_file(self, filename):
        os.remove(os.path.join(self.root_path, filename))
        self.load_files()
        self.layoutChanged.emit()

    def add_folder(self, foldername):
        os.mkdir(os.path.join(self.root_path, foldername))
        self.load_files()
        self.layoutChanged.emit()

    def get_full_path(self, filename):
        return os.path.join(self.root_path, filename)

class DesktopEnvironment(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initVirtualFS()

    def initUI(self):
        self.setWindowTitle('MeforgersOS')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2E3436;")

        # Masaüstü arka planı
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Görev çubuğu
        self.create_taskbar()

        # Masaüstü simgeleri
        self.create_desktop_icons()

        # Başlat menüsü
        self.create_start_menu()

    def create_taskbar(self):
        self.taskbar = QHBoxLayout()
        self.taskbar.setSpacing(0)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.open_start_menu)
        self.taskbar.addWidget(self.start_button)

        self.taskbar.addStretch()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.show()

        self.central_widget.setLayout(self.taskbar)

    def create_desktop_icons(self):
        icons_layout = QVBoxLayout()

        notepad_icon = QPushButton("Notepad", self)
        notepad_icon.clicked.connect(self.open_notepad)
        icons_layout.addWidget(notepad_icon)

        browser_icon = QPushButton("Web Browser", self)
        browser_icon.clicked.connect(self.open_browser)
        icons_layout.addWidget(browser_icon)

        terminal_icon = QPushButton("Terminal", self)
        terminal_icon.clicked.connect(self.open_terminal)
        icons_layout.addWidget(terminal_icon)

        file_explorer_icon = QPushButton("File Explorer", self)
        file_explorer_icon.clicked.connect(self.open_file_explorer)
        icons_layout.addWidget(file_explorer_icon)

        spacer = QVBoxLayout()
        spacer.addStretch(1)
        icons_layout.addLayout(spacer)

        self.layout.addLayout(icons_layout)

    def create_start_menu(self):
        self.start_menu = QMenu('Start', self)

        self.note_app_action = QAction('Notepad', self)
        self.note_app_action.triggered.connect(self.open_notepad)
        self.start_menu.addAction(self.note_app_action)

        self.browser_action = QAction('Web Browser', self)
        self.browser_action.triggered.connect(self.open_browser)
        self.start_menu.addAction(self.browser_action)

        self.terminal_action = QAction('Terminal', self)
        self.terminal_action.triggered.connect(self.open_terminal)
        self.start_menu.addAction(self.terminal_action)

        self.file_explorer_action = QAction('File Explorer', self)
        self.file_explorer_action.triggered.connect(self.open_file_explorer)
        self.start_menu.addAction(self.file_explorer_action)

        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.close)
        self.start_menu.addAction(self.exit_action)

    def open_start_menu(self):
        self.start_menu.exec_(self.mapToGlobal(self.start_button.pos()))

    def open_notepad(self):
        self.notepad = Notepad()
        self.notepad.show()

    def open_browser(self):
        self.browser = Browser()
        self.browser.show()

    def open_terminal(self):
        self.terminal = Terminal()
        self.terminal.show()

    def open_file_explorer(self):
        self.file_explorer = FileExplorer()
        self.file_explorer.show()

    def initVirtualFS(self):
        if not os.path.exists(VIRTUAL_FS_ROOT):
            os.mkdir(VIRTUAL_FS_ROOT)

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Notepad')
        self.setGeometry(150, 150, 600, 400)

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')

        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_file)
        self.file_menu.addAction(self.new_action)

        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self.save_file)
        self.file_menu.addAction(self.save_action)

        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)

    def new_file(self):
        self.text_edit.clear()
        self.current_file_path = None

    def save_file(self):
        if self.current_file_path:
            with open(self.current_file_path, 'w') as file:
                file.write(self.text_edit.toPlainText())
            QMessageBox.information(self, "Save File", f"Note saved as {self.current_file_path}")
        else:
            file_name, ok = QInputDialog.getText(self, 'Save File', 'Enter file name:')
            if ok and file_name:
                self.current_file_path = os.path.join(VIRTUAL_FS_ROOT, file_name)
                with open(self.current_file_path, 'w') as file:
                    file.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Save File", f"Note saved as {self.current_file_path}")

    def open_file(self, file_path=None):
        if not file_path:
            file_path, ok = QInputDialog.getText(self, 'Open File', 'Enter file name:')
            if not ok or not file_path:
                return
        full_path = os.path.join(VIRTUAL_FS_ROOT, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as file:
                self.text_edit.setText(file.read())
            self.current_file_path = full_path
        else:
            QMessageBox.warning(self, "Open File", f"File {file_path} does not exist")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Web Browser')
        self.setGeometry(150, 150, 800, 600)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://www.google.com'))
        self.setCentralWidget(self.browser)

class Terminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Terminal')
        self.setGeometry(200, 200, 600, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setStyleSheet("background-color: black; color: white;")
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)
        self.command_line = QLineEdit(self)
        self.command_line.setStyleSheet("background-color: black; color: white;")
        self.layout().addWidget(self.command_line)

        self.command_line.returnPressed.connect(self.process_command)

        self.text_edit.append("Welcome to MeforgersOS Terminal\n")

    def process_command(self):
        command = self.command_line.text().strip()
        self.command_line.clear()
        self.run_command(command)

    def run_command(self, command):
        self.text_edit.append(f"> {command}")
        if command == "clear":
            self.text_edit.clear()
        elif command == "help":
            self.text_edit.append("Available commands: clear, help, ls, cd, pwd, echo [text], mkdir [dir], touch [file], rm [file]")
        elif command.startswith("ls"):
            self.list_directory(command)
        elif command.startswith("cd"):
            self.change_directory(command)
        elif command == "pwd":
            self.print_working_directory()
        elif command.startswith("echo"):
            self.echo_command(command)
        elif command.startswith("mkdir"):
            self.make_directory(command)
        elif command.startswith("touch"):
            self.create_file(command)
        elif command.startswith("rm"):
            self.remove_file(command)
        else:
            self.text_edit.append(f"Command not found: {command}")

    def list_directory(self, command):
        try:
            args = command.split()
            path = args[1] if len(args) > 1 else VIRTUAL_FS_ROOT
            files = os.listdir(path)
            self.text_edit.append("\n".join(files))
        except Exception as e:
            self.text_edit.append(str(e))

    def change_directory(self, command):
        try:
            args = command.split()
            path = args[1] if len(args) > 1 else VIRTUAL_FS_ROOT
            os.chdir(path)
            self.text_edit.append(f"Changed directory to {os.getcwd()}")
        except Exception as e:
            self.text_edit.append(str(e))

    def print_working_directory(self):
        self.text_edit.append(os.getcwd())

    def echo_command(self, command):
        try:
            args = command.split(' ', 1)
            if len(args) > 1:
                self.text_edit.append(args[1])
        except Exception as e:
            self.text_edit.append(str(e))

    def make_directory(self, command):
        try:
            args = command.split()
            if len(args) > 1:
                os.mkdir(os.path.join(os.getcwd(), args[1]))
                self.text_edit.append(f"Directory {args[1]} created")
        except Exception as e:
            self.text_edit.append(str(e))

    def create_file(self, command):
        try:
            args = command.split()
            if len(args) > 1:
                with open(os.path.join(os.getcwd(), args[1]), 'w') as f:
                    f.write('')
                self.text_edit.append(f"File {args[1]} created")
        except Exception as e:
            self.text_edit.append(str(e))

    def remove_file(self, command):
        try:
            args = command.split()
            if len(args) > 1:
                os.remove(os.path.join(os.getcwd(), args[1]))
                self.text_edit.append(f"File {args[1]} removed")
        except Exception as e:
            self.text_edit.append(str(e))

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history = []
        self.current_path = VIRTUAL_FS_ROOT
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Explorer')
        self.setGeometry(150, 150, 800, 600)

        self.model = VirtualFileSystemModel(self.current_path)

        self.view = QListView(self)
        self.view.setModel(self.model)
        self.view.clicked.connect(self.on_item_clicked)
        self.setCentralWidget(self.view)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')

        self.new_file_action = QAction('New File', self)
        self.new_file_action.triggered.connect(self.new_file)
        self.file_menu.addAction(self.new_file_action)

        self.new_folder_action = QAction('New Folder', self)
        self.new_folder_action.triggered.connect(self.new_folder)
        self.file_menu.addAction(self.new_folder_action)

        self.delete_action = QAction('Delete', self)
        self.delete_action.triggered.connect(self.delete_item)
        self.file_menu.addAction(self.delete_action)

        self.back_action = QAction('Back', self)
        self.back_action.triggered.connect(self.go_back)
        self.file_menu.addAction(self.back_action)

        self.refresh_action = QAction('Refresh', self)
        self.refresh_action.triggered.connect(self.refresh)
        self.file_menu.addAction(self.refresh_action)

    def new_file(self):
        file_name, ok = QInputDialog.getText(self, 'New File', 'Enter file name:')
        if ok and file_name:
            self.model.add_file(file_name)

    def new_folder(self):
        folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Enter folder name:')
        if ok and folder_name:
            self.model.add_folder(folder_name)

    def delete_item(self):
        index = self.view.currentIndex()
        if index.isValid():
            file_name = self.model.data(index, Qt.DisplayRole)
            self.model.delete_file(file_name)

    def on_item_clicked(self, index):
        file_name = self.model.data(index, Qt.DisplayRole)
        full_path = self.model.get_full_path(file_name)
        if os.path.isdir(full_path):
            self.history.append(self.current_path)
            self.current_path = full_path
            self.model.root_path = full_path
            self.model.load_files()
            self.model.layoutChanged.emit()
        elif os.path.isfile(full_path):
            if full_path.endswith('.txt'):
                self.notepad = Notepad()
                self.notepad.open_file(full_path)
                self.notepad.show()

    def go_back(self):
        if self.history:
            self.current_path = self.history.pop()
            self.model.root_path = self.current_path
            self.model.load_files()
            self.model.layoutChanged.emit()

    def refresh(self):
        self.model.load_files()
        self.model.layoutChanged.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = DesktopEnvironment()
    desktop.show()
    sys.exit(app.exec_())
