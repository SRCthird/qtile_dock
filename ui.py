import subprocess
import tempfile
import cairosvg
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image


def convert_svg_to_png(svg_path):
    """Converts an SVG file to PNG format."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
        cairosvg.svg2png(url=svg_path, write_to=temp_png.name)
        return temp_png.name


def scale_image(image_path, size=(64, 64)):
    """Scales an image to the specified size."""
    with Image.open(image_path) as img:
        img = img.resize(size, Image.Resampling.LANCZOS)
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_img.name)
        return temp_img.name


class DockUI(QtWidgets.QWidget):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, apps, non_root_user=None):
        super().__init__()
        self.non_root_user = non_root_user
        self.apps = apps
        self.initUI(apps)
        self.stop_signal.connect(self.handle_stop_signal)

    def initUI(self, apps):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #333;
                border-radius: 20px;
            }
        """)
        self.layout = QtWidgets.QHBoxLayout(self.frame)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        self.buttons = []
        for app in apps[:6]:
            icon_path = app["Main Entry"]["Icon"]
            if icon_path:
                if icon_path.endswith(".svg"):
                    icon_path = convert_svg_to_png(icon_path)
                icon_path = scale_image(icon_path)
                btn = QtWidgets.QPushButton()
                btn.setIcon(QtGui.QIcon(icon_path))
                btn.setIconSize(QtCore.QSize(64, 64))
                btn.setFixedSize(74, 74)
                btn.setStyleSheet(
                    "border-radius: 10px; border: none; background-color: #333;")
                btn.clicked.connect(
                    lambda _, cmd=app["Main Entry"]["Exec"]: self.launch_app(cmd))
                self.layout.addWidget(btn)
                self.buttons.append((btn, app))

        self.frame.setLayout(self.layout)
        self.frame.adjustSize()

        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.frame.width()) // 2
        y = int(screen_geometry.height() * 0.9) - self.frame.height()
        self.setGeometry(x, y, self.frame.width(), self.frame.height())

        self.selected_index = 0
        self.update_selection()

    def launch_app(self, exec_cmd):
        self.hide()
        try:
            if self.non_root_user is None:
                subprocess.Popen(exec_cmd.split())
            else:
                if 'flatpak run' in exec_cmd:
                    print('flatpak apps are not supported in sudo mode')
                else:
                    subprocess.Popen(
                        ['sudo', '-u', self.non_root_user] + exec_cmd.split())
        except Exception as e:
            print(f"Failed to launch {exec_cmd}: {e}")

    def show_actions_menu(self, actions):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #333;
                color: white;
                border: 1px solid white;
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 10px;
                margin: 5px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #444;
            }
        """)

        for action in actions:
            action_name = action["Name"]
            action_exec = action["Exec"]
            action_icon = action.get("Icon")
            if action_icon and action_icon.endswith(".svg"):
                action_icon = convert_svg_to_png(action_icon)
            action_icon = scale_image(action_icon) if action_icon else None

            menu_action = QtWidgets.QAction(action_name, self)
            if action_icon:
                menu_action.setIcon(QtGui.QIcon(action_icon))
            menu_action.triggered.connect(
                lambda _, cmd=action_exec: self.launch_app(cmd))
            menu.addAction(menu_action)

        # Get the position of the selected button
        selected_button = self.buttons[self.selected_index][0]
        button_pos = selected_button.mapToGlobal(
            QtCore.QPoint(0, selected_button.height()))

        menu.exec_(button_pos)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.setFocus()

    def update_selection(self):
        for i, (btn, _) in enumerate(self.buttons):
            if i == self.selected_index:
                btn.setStyleSheet(
                    "border-radius: 10px; border: 2px solid #FFF; background-color: #333;")
            else:
                btn.setStyleSheet(
                    "border-radius: 10px; border: none; background-color: #333;")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.update_selection()
        elif event.key() == QtCore.Qt.Key_Left:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.update_selection()
        elif event.key() == QtCore.Qt.Key_Return:
            _, app = self.buttons[self.selected_index]
            self.launch_app(app["Main Entry"]["Exec"])
        elif event.key() == QtCore.Qt.Key_Down:
            _, app = self.buttons[self.selected_index]
            actions = app.get("Actions", [])
            if actions:
                self.show_actions_menu(actions)

    def handle_stop_signal(self):
        print("Stopping the application...")
        QtWidgets.QApplication.quit()
