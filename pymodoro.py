import sys
import os
import platform
import random
import json
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSpinBox,
    QFormLayout,
    QSystemTrayIcon,
    QCheckBox,
    QMenuBar,
    QMainWindow,
    QMenu,
    QToolTip,
    QWIDGETSIZE_MAX,
)
from PyQt6.QtCore import QTimer, Qt, QSize, QUrl, QFile, QTextStream, QIODevice
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtMultimedia import QSoundEffect

# Se estivermos no ambiente de desenvolvimento do VSCode
if "vscode" in os.environ.get("TERM_PROGRAM", ""):
    ICON_PATH = "utils/pymodoro_icon.ico"
    TRAY_ICON_PATH = "utils/pymodoro_tray_icon.ico"
    DARKMODE_PATH = "utils/pymodoro_darkmode.qss"
    LIGHTMODE_PATH = "utils/pymodoro_lightmode.qss"
    NOTIFICATION_SOUND_PATH = "utils/notification.wav"
    SETTINGS_PATH = "utils/pymodoro_settings.json"
else:
    if platform.system() == "Linux":
        from pwd import getpwnam  # type: ignore

        HOME_PATH = getpwnam(os.getlogin()).pw_dir
        UTILS_PATH = f"{HOME_PATH}/.local/bin/pymodoro_utils"
        ICON_PATH = f"{UTILS_PATH}/pymodoro_icon.ico"
        TRAY_ICON_PATH = f"{UTILS_PATH}/pymodoro_tray_icon.ico"
        DARKMODE_PATH = f"{UTILS_PATH}/pymodoro_darkmode.qss"
        LIGHTMODE_PATH = f"{UTILS_PATH}/pymodoro_lightmode.qss"
        NOTIFICATION_SOUND_PATH = f"{UTILS_PATH}/notification.wav"
        SETTINGS_PATH = f"{UTILS_PATH}/pymodoro_settings.json"
    elif platform.system() == "Windows":
        UTILS_PATH = f"C:/Users/{os.getenv('USERNAME')}/AppData/Local/Pymodoro/pymodoro_utils"
        ICON_PATH = f"{UTILS_PATH}/pymodoro_icon.ico"
        TRAY_ICON_PATH = f"{UTILS_PATH}/pymodoro_tray_icon.ico"
        DARKMODE_PATH = f"{UTILS_PATH}/pymodoro_darkmode.qss"
        LIGHTMODE_PATH = f"{UTILS_PATH}/pymodoro_lightmode.qss"
        NOTIFICATION_SOUND_PATH = f"{UTILS_PATH}/notification.wav"
        SETTINGS_PATH = f"{UTILS_PATH}/pymodoro_settings.json"
    else:
        raise NotImplementedError("Sistema operacional não suportado")


class BreakWidget(QWidget):
    def __init__(self, pomodor):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Remove a barra do título
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        width = int(screen_geometry.width() * 0.4)
        height = int(screen_geometry.height() * 0.4)
        self.setGeometry(0, 0, width, height)

        self.on_close = pomodor.close_break_widget
        self.on_skip = pomodor.skip_break
        self.on_postpone = pomodor.postpone_break

        self.label = QLabel("Break!", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 72px;")

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close_widget)

        skip_button = QPushButton("Skip", self)
        skip_button.clicked.connect(self.skip_break)

        postpone_button = QPushButton("Postpone", self)
        postpone_button.clicked.connect(self.postpone_break)

        button_layout = QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.addWidget(skip_button)
        button_layout.addWidget(postpone_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(pomodor.timer_label_break)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet(pomodor.dark_mode())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.center()

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry().center()
        size = self.geometry()
        self.move(int(screen.x() - size.width() / 2), int(screen.y() - size.height() / 2))

    def close_widget(self):
        self.on_close()
        self.hide()

    def skip_break(self):
        self.on_skip()
        self.hide()

    def postpone_break(self):
        self.on_postpone()
        self.hide()


class ConfigWidget(QWidget):
    def __init__(self, pomodor):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(ICON_PATH))  # Define o ícone da janela

        # Estilo do tema escuro
        self.setStyleSheet(pomodor.dark_mode())

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, pomodor.always_on_top)

        self.on_save = pomodor.save_config

        self.pomodor = pomodor

        self.cycle_count_spinbox = QSpinBox(self)

        self.work_duration_spinbox = QSpinBox(self)

        self.short_break_spinbox = QSpinBox(self)

        self.long_break_spinbox = QSpinBox(self)

        self.show_break_widget_checkbox = QCheckBox("Show Break Widget", self)
        self.fullscreen_checkbox = QCheckBox("Full Screen Break", self)
        self.always_on_top_checkbox = QCheckBox("Always on top", self)
        self.autostart_break_checkbox = QCheckBox("Autostart Break", self)
        self.autostart_work_checkbox = QCheckBox("Autostart Work", self)
        self.dark_mode_checkbox = QCheckBox("Dark Mode", self)

        self.always_on_top_checkbox.setChecked(pomodor.always_on_top)
        if not pomodor.show_break_widget_opt:
            self.fullscreen_checkbox.setChecked(False)
            self.fullscreen_checkbox.setEnabled(False)
        else:
            self.fullscreen_checkbox.setChecked(pomodor.fullscreen)
            self.fullscreen_checkbox.setEnabled(True)
        self.show_break_widget_checkbox.setChecked(pomodor.show_break_widget_opt)
        self.autostart_break_checkbox.setChecked(pomodor.autostart_break)
        self.autostart_work_checkbox.setChecked(pomodor.autostart_work)
        self.dark_mode_checkbox.setChecked(pomodor.dark_mode_config)
        self.cycle_count_spinbox.setValue(pomodor.cycle_count)
        self.work_duration_spinbox.setValue(pomodor.work_duration // 60)
        self.long_break_spinbox.setValue(pomodor.long_break // 60)
        self.short_break_spinbox.setValue(pomodor.short_break // 60)
        self.show_break_widget_checkbox.stateChanged.connect(self.on_change_show_break_widget)

        config_layout = QFormLayout()
        config_layout.addRow("Cycles:", self.cycle_count_spinbox)
        config_layout.addRow("Work Time (min):", self.work_duration_spinbox)
        config_layout.addRow("Short Break (min):", self.short_break_spinbox)
        config_layout.addRow("Long Break (min):", self.long_break_spinbox)

        config_layout.addRow("", self.show_break_widget_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.fullscreen_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.always_on_top_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.autostart_work_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.autostart_break_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.dark_mode_checkbox)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_config)

        layout = QVBoxLayout()
        layout.addLayout(config_layout)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def save_config(self):
        self.on_save(
            self.cycle_count_spinbox.value(),
            self.work_duration_spinbox.value(),
            self.short_break_spinbox.value(),
            self.long_break_spinbox.value(),
            self.show_break_widget_checkbox.isChecked(),
            self.fullscreen_checkbox.isChecked(),
            self.always_on_top_checkbox.isChecked(),
            self.autostart_work_checkbox.isChecked(),
            self.autostart_break_checkbox.isChecked(),
            self.dark_mode_checkbox.isChecked(),
        )
        self.hide()
        self.pomodor.show()

    def closeEvent(self, event):
        self.hide()

    def on_change_show_break_widget(self):
        if not self.show_break_widget_checkbox.isChecked():
            self.fullscreen_checkbox.setChecked(False)
            self.fullscreen_checkbox.setEnabled(False)
        else:
            self.fullscreen_checkbox.setEnabled(True)


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pymodoro")

        self.setWindowIcon(QIcon(ICON_PATH))  # Define o ícone da janela

        self.timer_label = QLabel("", self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label_break = QLabel("", self)
        self.timer_label_break.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label_break.setStyleSheet("font-size: 48px;")

        self.timer_container = QWidget(self)

        # Settings variables (default values)
        self.set_settings()

        self.config_widget = ConfigWidget(self)
        self.break_widget = BreakWidget(self)

        timer_layout = QVBoxLayout()
        timer_layout.addWidget(self.timer_label)
        self.timer_container.setLayout(timer_layout)

        self.cycle_label = QLabel("Cycle: 1 - Work", self)
        self.cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.toggle_timer)

        self.next_cycle_button = QPushButton("Next", self)
        self.next_cycle_button.clicked.connect(self.next_cycle)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.next_cycle_button)
        button_layout.addWidget(self.reset_button)

        layout = QVBoxLayout()
        layout.addWidget(self.cycle_label)
        layout.addWidget(self.timer_container)
        layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.total_seconds = self.work_duration
        self.running = False
        self.cycle = 1
        self.is_work_cycle = True

        # Sistema de bandeja
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(ICON_PATH))
        self.tray_icon.setVisible(True)
        self.on_tray = False

        # Som de notificação
        self.notification_sound = QSoundEffect()
        self.notification_sound.setSource(QUrl.fromLocalFile(NOTIFICATION_SOUND_PATH))

        # Menu bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.setMenuBar(self.menu_bar)

        config_action = QAction("⚙️", self)
        config_action.setToolTip("Settings")
        config_action.hovered.connect(self.show_tooltip)
        self.minimalist_action = QAction("⏬", self)
        self.minimalist_action.setToolTip("Toggle Minimalist Mode")
        self.minimalist_action.hovered.connect(self.show_tooltip)
        minimize_on_tray = QAction("↘️", self)
        minimize_on_tray.setToolTip("Minimize on Tray")
        minimize_on_tray.hovered.connect(self.show_tooltip)
        self.darkmode_action = QAction("🌒", self)
        self.darkmode_action.setToolTip("Toggle Dark Mode")
        self.darkmode_action.hovered.connect(self.show_tooltip)
        config_action.triggered.connect(self.show_config_widget)
        self.minimalist_action.triggered.connect(self.show_minimalist_mode)
        minimize_on_tray.triggered.connect(self.on_tray_option)
        self.darkmode_action.triggered.connect(self.toggle_dark_mode)
        self.menu_bar.addAction(config_action)
        self.menu_bar.addAction(self.minimalist_action)
        self.menu_bar.addAction(minimize_on_tray)
        self.menu_bar.addAction(self.darkmode_action)

        self.minimalist = False
        self.old_size = self.size()

        # Variáveis para mover a janela
        self._is_moving = False
        self._start_pos = None

        self.menu = QMenu(self)
        self.tray_icon_actions()
        self.update_tray_tooltip()

        self.update_settings()

        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")

    def close_app(self):
        self.show()
        self.close()

    def show_tooltip(self):
        act = self.sender()
        if isinstance(act, QAction):
            QToolTip.showText(QCursor.pos(), act.toolTip(), self)

    def set_settings(self):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            settings = json.load(file)
            self.cycle_count = settings["cycle_count"]
            self.work_duration = settings["work_duration"] * 60
            self.short_break = settings["short_break"] * 60
            self.long_break = settings["long_break"] * 60
            self.show_break_widget_opt = settings["show_break_widget"]
            self.fullscreen = settings["fullscreen_break"]
            self.always_on_top = settings["always_on_top"]
            self.autostart_work = settings["autostart_work"]
            self.autostart_break = settings["autostart_break"]
            self.dark_mode_config = settings["dark_mode"]
            self.break_quotes = settings["break_quotes"]
            self.window_size = (settings["window_size"]["width"], settings["window_size"]["height"])

    def update_settings(self):
        self.setStyleSheet(self.dark_mode())
        self.config_widget.setStyleSheet(self.dark_mode())
        self.break_widget.setStyleSheet(self.dark_mode())
        self.timer_container.setStyleSheet(self.dark_mode(timer_container=True))
        self.darkmode_action.setText("🌒" if self.dark_mode_config else "🌖")
        self.resize(self.window_size[0], self.window_size[1])
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)

    def toggle_dark_mode(self):
        self.dark_mode_config = not self.dark_mode_config
        self.setStyleSheet(self.dark_mode())
        self.config_widget.setStyleSheet(self.dark_mode())
        self.break_widget.setStyleSheet(self.dark_mode())
        self.timer_container.setStyleSheet(self.dark_mode(timer_container=True))
        self.config_widget.dark_mode_checkbox.setChecked(self.dark_mode_config)

        self.darkmode_action.setText("🌒" if self.dark_mode_config else "🌖")

        self.save_config(
            self.cycle_count,
            self.work_duration // 60,
            self.short_break // 60,
            self.long_break // 60,
            self.show_break_widget_opt,
            self.fullscreen,
            self.always_on_top,
            self.autostart_work,
            self.autostart_break,
            self.dark_mode_config,
        )

    def dark_mode(self, timer_container=False):
        if timer_container:
            if self.dark_mode_config:
                return """
                    QWidget {
                        background-color: #232323;
                        border-radius: 15px;
                    }
                    """
            else:
                return """
                    QWidget {
                        background-color: #f0f0f0;
                        border-radius: 15px;
                    }
                    """
        else:
            if self.dark_mode_config:
                file = QFile(DARKMODE_PATH)
            else:
                file = QFile(LIGHTMODE_PATH)
            file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text)  # type: ignore
            stream = QTextStream(file)

        return stream.readAll()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_moving = True
            self._start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_moving:
            self.move(event.globalPosition().toPoint() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_moving = False
            event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_font_sizes()

    def update_font_sizes(self):
        width = self.width()

        # Ajusta o tamanho da fonte com base nas dimensões da janela
        cycle_font_size = max(12, width // 20)
        timer_font_size = max(24, width // 10)

        self.cycle_label.setStyleSheet(f"font-size: {cycle_font_size}px;")
        self.timer_label.setStyleSheet(f"font-size: {timer_font_size}px;")

    def toggle_timer(self):
        if not self.running:
            self.start_timer()
        else:
            self.pause_timer()

    def start_timer(self):
        self.running = True
        self.timer.start(1000)
        self.start_button.setText("Pause")
        self.start_action.setText("Pause")

    def pause_timer(self):
        self.running = False
        self.timer.stop()
        self.start_button.setText("Resume")
        self.start_action.setText("Resume")

    def update_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1
            minutes, seconds = divmod(self.total_seconds, 60)
            self.timer_label.setText(f"{minutes:02}:{seconds:02}")
            if not self.is_work_cycle:
                self.timer_label_break.setText(f"{minutes:02}:{seconds:02}")
                if self.total_seconds == 0:
                    self.break_widget.hide()
            self.update_tray_tooltip()
        if self.total_seconds == 0:
            self.timer.stop()
            self.next_cycle()

    def update_tray_tooltip(self):
        minutes, seconds = divmod(self.total_seconds, 60)
        if self.is_work_cycle:
            self.tray_icon.setToolTip(f"Cycle {self.cycle} - Work: {minutes:02}:{seconds:02}")
        elif not self.is_work_cycle:
            self.tray_icon.setToolTip(f" Cycle {self.cycle} - Break: {minutes:02}:{seconds:02}")
        else:
            self.tray_icon.setToolTip("Pomodoro Timer")

    # TODO: reduzir complexidade do método
    def next_cycle(self):
        short_break_duration = self.short_break  # em segundos
        long_break_duration = self.long_break  # em segundos
        cycles_to_complete = self.cycle_count

        if self.is_work_cycle:
            if self.cycle % cycles_to_complete == 0:  # Cada X ciclos de trabalho
                self.total_seconds = long_break_duration
                self.cycle_label.setText(f"Cycle: {self.cycle} - Long Break")
                if self.fullscreen:
                    self.show_break_widget_fullscreen()
                else:
                    self.show_break_widget()
                phrase = self.get_random_quote()
                self.show_notification(f"Long Break - {phrase}")
                self.end_of_cycle = True
            else:
                self.total_seconds = short_break_duration
                self.cycle_label.setText(f"Cycle: {self.cycle} - Short Break")
                if self.fullscreen:
                    self.show_break_widget_fullscreen()
                else:
                    self.show_break_widget()
                phrase = self.get_random_quote()
                self.show_notification(f"Short Break - {phrase}")
                self.end_of_cycle = False
        else:
            # Avançar para o próximo ciclo de trabalho
            if self.end_of_cycle:
                self.cycle = 1
                self.start_button.setText("Start")
                self.start_action.setText("Start")
                self.end_of_cycle = False
                self.running = False
                self.show_notification("End of Cycle")
            else:
                self.cycle += 1
                self.show_notification("Work")
            self.total_seconds = self.work_duration
            self.cycle_label.setText(f"Cycle: {self.cycle} - Work")

        self.is_work_cycle = not self.is_work_cycle
        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")
        self.timer_label_break.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")

        if self.is_work_cycle and self.autostart_work and not self.end_of_cycle:
            self.running = True
        elif not self.is_work_cycle and self.autostart_break:
            self.running = True
        else:
            self.running = False

        if self.running:
            self.start_button.setText("Pause")
            self.start_action.setText("Pause")
            self.timer.start(1000)
        else:
            self.start_button.setText("Start")
            self.start_action.setText("Start")
            self.timer.stop()

    def tray_icon_actions(self):
        # Adiciona ações ao ícone da bandeja
        self.start_action = QAction("Start", self)
        self.start_action.triggered.connect(self.toggle_timer)
        next_step_action = QAction("Next", self)
        next_step_action.triggered.connect(self.next_cycle)
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_timer)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.close_app)
        self.menu.addAction(self.start_action)
        self.menu.addAction(next_step_action)
        self.menu.addAction(reset_action)
        self.menu.addAction(quit_action)
        self.tray_icon.activated.connect(self.on_tray_icon_click)
        self.tray_icon.setContextMenu(self.menu)

    def on_tray_icon_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.setVisible(True)
            self.activateWindow()
            self.update_widget_infos()
            self.on_tray = False

    def update_widget_infos(self):
        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")
        if self.is_work_cycle:
            self.cycle_label.setText(f"Cycle: {self.cycle} - Work")
        else:
            self.cycle_label.setText(f"Cycle: {self.cycle} - Break")

        if self.running:
            self.start_button.setText("Pause")
            self.start_action.setText("Pause")
        else:
            self.start_button.setText("Resume")
            self.start_action.setText("Resume")

    def show_notification(self, message):
        self.tray_icon.showMessage("Pomodoro Timer", message, QIcon(ICON_PATH), 3000)
        self.notification_sound.play()  # Toca o som ao mostrar a notificação

    def show_break_widget(self):
        if self.show_break_widget_opt:
            self.break_widget.show()  # Exibe o widget normalmente
            self.break_widget.label.setText(self.get_random_quote())

    def get_random_quote(self):
        return self.break_quotes[random.randint(0, len(self.break_quotes) - 1)]

    def show_break_widget_fullscreen(self):
        if self.show_break_widget_opt:
            self.break_widget.showFullScreen()  # Exibe o widget em tela cheia

    def close_break_widget(self):
        self.break_widget.hide()

    def skip_break(self):
        # Avança para o próximo ciclo de trabalho, se estivermos em um ciclo de descanso
        if not self.is_work_cycle:
            self.next_cycle()

    def postpone_break(self):
        # Adia o descanso, adicionando 5 minutos de trabalho ao timer
        self.total_seconds = 300  # Adiciona 5 minutos (300 segundos)
        self.cycle_label.setText(f"Cycle: {self.cycle} - Work")
        self.is_work_cycle = True  # Define que agora é um ciclo de trabalho
        if self.running:
            self.timer.start(1000)

    def reset_timer(self):
        self.timer.stop()
        self.running = False
        self.cycle = 1
        self.is_work_cycle = True
        self.total_seconds = self.work_duration
        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")
        self.cycle_label.setText("Cycle: 1 - Work")
        self.start_button.setText("Start")
        self.start_action.setText("Start")

    def on_tray_option(self):
        self.hide()
        self.on_tray = True

    def show_config_widget(self):
        if not self.on_tray:
            self.config_widget.move(self.pos())
        self.config_widget.show()

    def show_minimalist_mode(self):
        if not self.minimalist:
            self.old_size = self.size()
            self.setFixedSize(210, 170)
            self.minimalist = True
            self.minimalist_action.setText("⏫")
            self.show()
        else:
            self.setMinimumSize(QSize(0, 0))  # Remove restrições de tamanho mínimo
            self.setMaximumSize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))  # Remove restrições de tamanho máximo
            self.resize(self.old_size)
            self.minimalist = False
            self.minimalist_action.setText("⏬")
            self.show()

    def save_config(
        self,
        cycle_count,
        work_duration,
        short_break,
        long_break,
        show_break_widget,
        fullscreen,
        always_on_top,
        autostart_work,
        autostart_break,
        dark_mode,
    ):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
            settings = {
                "cycle_count": cycle_count,
                "work_duration": work_duration,
                "short_break": short_break,
                "long_break": long_break,
                "show_break_widget": show_break_widget,
                "fullscreen_break": fullscreen,
                "always_on_top": always_on_top,
                "autostart_work": autostart_work,
                "autostart_break": autostart_break,
                "dark_mode": dark_mode,
                "break_quotes": self.break_quotes,
                "window_size": {"width": self.width(), "height": self.height()},
            }
            json.dump(settings, file)

        self.set_settings()
        self.update_settings()

    def closeEvent(self, event):
        self.save_config(
            self.cycle_count,
            self.work_duration // 60,
            self.short_break // 60,
            self.long_break // 60,
            self.show_break_widget_opt,
            self.fullscreen,
            self.always_on_top,
            self.autostart_work,
            self.autostart_break,
            self.dark_mode_config,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec())
