import sys
from PyQt5.QtWidgets import (
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
    QAction,
    QMainWindow,
    QDesktopWidget,
    QMenu,
    QWIDGETSIZE_MAX,
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound

ICON_PATH = "pomodor_icon.png"
SETTINGS_STRING = "Configurações"


class BreakWidget(QWidget):
    def __init__(self, on_close, on_skip, on_postpone, timer_label):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove a barra do título
        screen_geometry = QDesktopWidget().availableGeometry()
        width = int(screen_geometry.width() * 0.4)
        height = int(screen_geometry.height() * 0.4)
        self.setGeometry(0, 0, width, height)

        self.on_close = on_close
        self.on_skip = on_skip
        self.on_postpone = on_postpone

        self.label = QLabel("Descanso!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 72px;")

        close_button = QPushButton("Fechar", self)
        close_button.clicked.connect(self.close_widget)

        skip_button = QPushButton("Pular Descanso", self)
        skip_button.clicked.connect(self.skip_break)

        postpone_button = QPushButton("Adiar Descanso", self)
        postpone_button.clicked.connect(self.postpone_break)

        button_layout = QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.addWidget(skip_button)
        button_layout.addWidget(postpone_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(timer_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
        """
        )
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.center()

    def center(self):
        screen = QDesktopWidget().availableGeometry().center()
        size = self.geometry()
        self.move(int(screen.x() - size.width() / 2), int(screen.y() - size.height() / 2))

    def close_widget(self):
        self.on_close()
        self.close()

    def skip_break(self):
        self.on_skip()
        self.close()

    def postpone_break(self):
        self.on_postpone()
        self.close()


class ConfigWidget(QWidget):
    def __init__(self, on_save, on_quit):
        super().__init__()
        self.setWindowTitle(SETTINGS_STRING)
        self.setGeometry(100, 100, 200, 250)
        self.setWindowIcon(QIcon(ICON_PATH))  # Define o ícone da janela
        # self.setWindowFlags(Qt.FramelessWindowHint)  # Remove a barra do título

        # Estilo do tema escuro
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                border-radius: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QSpinBox {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: none;
                padding: 5px;
            }
        """
        )

        self.on_save = on_save
        self.on_quit = on_quit

        self.cycle_count_spinbox = QSpinBox(self)
        self.cycle_count_spinbox.setRange(1, 10)
        self.cycle_count_spinbox.setValue(4)

        self.work_duration_spinbox = QSpinBox(self)
        self.work_duration_spinbox.setRange(1, 60)  # Tempo de trabalho em minutos
        self.work_duration_spinbox.setValue(25)

        self.short_break_spinbox = QSpinBox(self)
        self.short_break_spinbox.setRange(1, 60)
        self.short_break_spinbox.setValue(5)

        self.long_break_spinbox = QSpinBox(self)
        self.long_break_spinbox.setRange(1, 60)
        self.long_break_spinbox.setValue(20)

        self.fullscreen_checkbox = QCheckBox("Exibir Descanso em Tela Cheia", self)
        self.always_on_top_checkbox = QCheckBox("Sempre no Topo", self)

        config_layout = QFormLayout()
        config_layout.addRow("Ciclos:", self.cycle_count_spinbox)
        config_layout.addRow("Tempo de Trabalho (min):", self.work_duration_spinbox)
        config_layout.addRow("Pausa Curta (min):", self.short_break_spinbox)
        config_layout.addRow("Pausa Longa (min):", self.long_break_spinbox)

        config_layout.addRow("", self.fullscreen_checkbox)  # Adiciona o checkbox
        config_layout.addRow("", self.always_on_top_checkbox)  # Adiciona o checkbox

        self.save_button = QPushButton("Salvar", self)
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
            self.fullscreen_checkbox.isChecked(),
            self.always_on_top_checkbox.isChecked(),
        )
        self.close()

    def closeEvent(self, event):
        self.on_quit()
        self.close()


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pymodoro")
        self.setGeometry(100, 100, 250, 200)

        # Estilo do tema escuro
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                border-radius: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QSpinBox {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: none;
                padding: 5px;
            }
        """
        )

        self.setWindowIcon(QIcon(ICON_PATH))  # Define o ícone da janela

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.timer_label = QLabel("25:00", self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px;")

        self.timer_label_break = QLabel("5:00", self)
        self.timer_label_break.setAlignment(Qt.AlignCenter)
        self.timer_label_break.setStyleSheet("font-size: 48px;")

        self.timer_container = QWidget(self)
        self.timer_container.setStyleSheet(
            """
            QWidget {
                background-color: #3C3C3C;
                border-radius: 15px;
            }
            """
        )

        # Settings variables (default values)
        self.cycle_count = 4
        self.work_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 20 * 60
        self.fullscreen = False
        self.always_on_top = True
        self.end_of_cycle = False

        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)

        timer_layout = QVBoxLayout()
        timer_layout.addWidget(self.timer_label)
        self.timer_container.setLayout(timer_layout)

        self.cycle_label = QLabel("Ciclo: 1 - Trabalho", self)
        self.cycle_label.setAlignment(Qt.AlignCenter)
        self.cycle_label.setStyleSheet("font-size: 12px;")

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.toggle_timer)

        self.next_cycle_button = QPushButton("Next Step", self)
        self.next_cycle_button.clicked.connect(lambda: self.next_cycle(autostart=True))

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

        self.config_widget = ConfigWidget(self.save_config, self.quit_config)
        self.total_seconds = self.work_duration
        self.running = False
        self.cycle = 1
        self.is_work_cycle = True

        # Widget de descanso
        self.break_widget = BreakWidget(
            self.close_break_widget, self.skip_break, self.postpone_break, self.timer_label_break
        )

        # Sistema de bandeja
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(ICON_PATH))
        self.tray_icon.setVisible(True)

        # Som de notificação
        self.notification_sound = QSound("notification.wav")  # Altere o caminho se necessário

        # Menu bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.setMenuBar(self.menu_bar)

        config_action = QAction(SETTINGS_STRING, self)
        self.minimalist_action = QAction("Small", self)
        exit_action = QAction("Sair", self)
        config_action.triggered.connect(self.show_config_widget)
        self.minimalist_action.triggered.connect(self.show_minimalist_mode)
        exit_action.triggered.connect(self.close)
        self.menu_bar.addAction(config_action)
        self.menu_bar.addAction(self.minimalist_action)
        self.menu_bar.addAction(exit_action)
        self.adjustSize()  # Ajusta o tamanho da janela ao menor possível

        self.minimalist = False
        self.old_size = self.size()

        # Variáveis para mover a janela
        self._is_moving = False
        self._start_pos = None

        self.menu = QMenu(self)
        self.tray_icon_actions()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_moving = True
            self._start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_moving:
            self.move(event.globalPos() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
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

    def pause_timer(self):
        self.running = False
        self.timer.stop()
        self.start_button.setText("Resume")

    def update_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1
            minutes, seconds = divmod(self.total_seconds, 60)
            self.timer_label.setText(f"{minutes:02}:{seconds:02}")
            if not self.is_work_cycle:
                self.timer_label_break.setText(f"{minutes:02}:{seconds:02}")
                if self.total_seconds == 0:
                    self.break_widget.close()
            self.update_tray_tooltip()
        if self.total_seconds == 0:
            self.timer.stop()
            self.next_cycle(autostart=True)

    def update_tray_tooltip(self):
        minutes, seconds = divmod(self.total_seconds, 60)
        if self.is_work_cycle:
            self.tray_icon.setToolTip(f"Tempo restante: {minutes:02}:{seconds:02} - Trabalho")
        else:
            self.tray_icon.setToolTip(f"Tempo restante: {minutes:02}:{seconds:02} - Descanso")

    # TODO: reduzir complexidade do método
    def next_cycle(self, autostart: bool = True):
        short_break_duration = self.short_break  # em segundos
        long_break_duration = self.long_break  # em segundos
        cycles_to_complete = self.cycle_count

        if self.is_work_cycle:
            if self.cycle % cycles_to_complete == 0:  # Cada X ciclos de trabalho
                self.total_seconds = long_break_duration
                self.cycle_label.setText(f"Ciclo: {self.cycle} - Descanso Longo")
                if self.fullscreen:
                    self.show_break_widget_fullscreen()
                else:
                    self.show_break_widget()
                self.show_notification("Descanso Longo")
                self.end_of_cycle = True
            else:
                self.total_seconds = short_break_duration
                self.cycle_label.setText(f"Ciclo: {self.cycle} - Descanso Curto")
                if self.fullscreen:
                    self.show_break_widget_fullscreen()
                else:
                    self.show_break_widget()
                self.show_notification("Descanso Curto")
        else:
            # Avançar para o próximo ciclo de trabalho
            if self.end_of_cycle:
                self.cycle = 1
                # self.timer.stop()
                self.start_button.setText("Start")
                self.end_of_cycle = False
                self.running = False
                self.show_notification("Fim do Ciclo")
            else:
                self.cycle += 1
                # self.timer.start(1000)
                self.show_notification("Trabalho")
            self.total_seconds = self.work_duration
            self.cycle_label.setText(f"Ciclo: {self.cycle} - Trabalho")

        self.is_work_cycle = not self.is_work_cycle
        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")
        self.timer_label_break.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")

        if autostart:
            self.running = True
        else:
            self.running = False

        if self.running:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def tray_icon_actions(self):
        # Adiciona ações ao ícone da bandeja
        next_step_action = QAction("Next Step", self)
        next_step_action.triggered.connect(self.next_cycle)
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_timer)
        settings_action = QAction(SETTINGS_STRING, self)
        settings_action.triggered.connect(self.show_config_widget)
        small_mode_action = QAction("Small", self)
        small_mode_action.triggered.connect(self.show_minimalist_mode)
        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(self.close)
        self.menu.addAction(next_step_action)
        self.menu.addAction(reset_action)
        self.menu.addAction(settings_action)
        self.menu.addAction(small_mode_action)
        self.menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.menu)

    def show_notification(self, message):
        self.tray_icon.showMessage("Pomodoro Timer", message, QIcon(ICON_PATH), 3000)
        self.notification_sound.play()  # Toca o som ao mostrar a notificação

    def show_break_widget(self):
        self.break_widget.show()  # Exibe o widget normalmente

    def show_break_widget_fullscreen(self):
        self.break_widget.showFullScreen()  # Exibe o widget em tela cheia

    def close_break_widget(self):
        self.break_widget.hide()

    def skip_break(self):
        # Avança para o próximo ciclo de trabalho, se estivermos em um ciclo de descanso
        if not self.is_work_cycle:
            self.next_cycle(autostart=True)

    def postpone_break(self):
        # Adia o descanso, adicionando 5 minutos de trabalho ao timer
        self.total_seconds = 300  # Adiciona 5 minutos (300 segundos)
        self.cycle_label.setText(f"Ciclo: {self.cycle} - Trabalho")
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
        self.cycle_label.setText("Ciclo: 1 - Trabalho")
        self.start_button.setText("Start")

    def show_config_widget(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.config_widget.move(self.pos())
        self.config_widget.show()
        self.hide()

    def show_minimalist_mode(self):
        if not self.minimalist:
            self.old_size = self.size()
            self.cycle_label.setStyleSheet("font-size: 12px;")
            self.timer_label.setStyleSheet("font-size: 24px;")
            self.setFixedSize(210, 150)
            self.minimalist = True
            self.minimalist_action.setText("Normal")
            self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.show()
        else:
            self.setMinimumSize(QSize(0, 0))  # Remove restrições de tamanho mínimo
            self.setMaximumSize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))  # Remove restrições de tamanho máximo
            self.resize(self.old_size)
            self.minimalist = False
            self.minimalist_action.setText("Small")
            self.setWindowFlags(
                Qt.WindowTitleHint
                | Qt.WindowSystemMenuHint
                | Qt.WindowMinimizeButtonHint
                | Qt.WindowMaximizeButtonHint
                | Qt.WindowCloseButtonHint
            )  # Restaura a barra do título e os botões de controle
            self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)
            self.show()

    def save_config(self, cycle_count, work_duration, short_break, long_break, fullscreen, always_on_top):
        self.cycle_count = cycle_count
        self.work_duration = work_duration * 60
        self.short_break = short_break * 60
        self.long_break = long_break * 60
        self.fullscreen = fullscreen
        self.always_on_top = always_on_top
        self.total_seconds = self.work_duration
        self.timer_label.setText(f"{self.total_seconds // 60:02}:{self.total_seconds % 60:02}")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)
        self.move(self.config_widget.pos())
        self.show()

    def quit_config(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec_())
