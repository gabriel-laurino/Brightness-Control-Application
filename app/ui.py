"""Qt desktop interface. No display mutations happen in this module."""
from __future__ import annotations

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QGuiApplication, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QButtonGroup, QDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QSlider, QSpinBox,
    QSystemTrayIcon, QVBoxLayout, QWidget, QMenu,
)

from app.config import BrightnessConfig, ConfigStore, PERIODS
from app.monitor import discover_monitors
from app.placement import safe_bottom, taskbar_rectangles

PALETTE = {
    "bg": "#07131e", "surface": "#0d2231", "surface2": "#112b3a",
    "line": "#254652", "text": "#edfafb", "muted": "#94b4bd",
    "cyan": "#69dce9", "mint": "#87f1d1", "blue": "#9aaeff",
}

TEXT = {
    "PT": {
        "tagline": "APPLICATION  /  V2.0.1", "title": "A luz certa,\nna hora certa.",
        "subtitle": "Uma rotina de brilho para o conteúdo SDR dos seus monitores HDR. Clara, previsível e feita para acompanhar o seu dia.",
        "live": "●  ATIVO", "preview": "●  PRÉVIA", "error_badge": "●  ERRO", "now": "AGORA",
        "schedule": "Seu dia, em quatro momentos.", "schedule_sub": "Ajuste cada período. A mudança é aplicada aos HDR ativos após salvar.",
        "periods": ("Manhã", "Tarde", "Entardecer", "Noite"),
        "level": "BRILHO SDR", "active": "EM USO", "monitors": "Monitores",
        "monitor_sub": "Somente os que estão com HDR ativado recebem a correção.",
        "hdr_active": "HDR ATIVO", "sdr_untouched": "TELAS SDR PRESERVADAS", "detecting": "Detectando telas…",
        "no_hdr": "Nenhum HDR ativo detectado", "monitor_error": "Falha ao consultar os monitores",
        "safety": "Proteção por tela", "safety_text": "A rotina verifica o modo HDR atual de cada monitor antes de aplicar qualquer ajuste. Telas SDR ficam fora do alcance.",
        "save": "Salvar e aplicar", "saved": "Configuração salva. A rotina já está atualizando as telas HDR.",
        "pending": "Há ajustes ainda não salvos", "preview_note": "Prévia visual — nenhum ajuste será gravado ou aplicado.",
        "settings": "Horários e idioma", "settings_title": "Personalize a rotina", "settings_sub": "Defina quando começa cada período. O fim é calculado automaticamente.",
        "language": "Idioma", "cancel": "Cancelar", "confirm": "Salvar horários", "invalid": "Os horários devem estar em ordem crescente e não podem se repetir.",
        "open": "Abrir", "exit": "Sair", "tray": "Fechar minimiza para a bandeja do sistema.",
        "worker_ok": "Ajuste automático em execução", "worker_off": "Ajuste automático indisponível",
        "save_error": "Não foi possível salvar a configuração.", "night_hint": "O período noturno termina quando a manhã começa.",
    },
    "EN": {
        "tagline": "APPLICATION  /  V2.0.1", "title": "The right light,\nat the right time.",
        "subtitle": "A brightness routine for SDR content on your HDR displays. Clear, predictable and built around your day.",
        "live": "●  ACTIVE", "preview": "●  PREVIEW", "error_badge": "●  ERROR", "now": "RIGHT NOW",
        "schedule": "Your day, in four moments.", "schedule_sub": "Tune each period. Active HDR displays update after you save.",
        "periods": ("Morning", "Afternoon", "Evening", "Night"),
        "level": "SDR BRIGHTNESS", "active": "ACTIVE", "monitors": "Displays",
        "monitor_sub": "Only displays with HDR currently on receive the adjustment.",
        "hdr_active": "HDR ACTIVE", "sdr_untouched": "SDR DISPLAYS EXCLUDED", "detecting": "Detecting displays…",
        "no_hdr": "No active HDR display detected", "monitor_error": "Could not inspect displays",
        "safety": "Per-display protection", "safety_text": "The routine verifies each display's current HDR mode before adjusting anything. SDR displays are excluded.",
        "save": "Save and apply", "saved": "Settings saved. The routine is updating HDR displays now.",
        "pending": "You have unsaved adjustments", "preview_note": "Visual preview — nothing is saved or applied.",
        "settings": "Schedule and language", "settings_title": "Customize the routine", "settings_sub": "Choose when each period starts. End times are calculated automatically.",
        "language": "Language", "cancel": "Cancel", "confirm": "Save schedule", "invalid": "Start times must be unique and in increasing order.",
        "open": "Open", "exit": "Exit", "tray": "Closing minimizes to the system tray.",
        "worker_ok": "Automatic adjustment running", "worker_off": "Automatic adjustment unavailable",
        "save_error": "Could not save the configuration.", "night_hint": "Night ends when morning begins.",
    },
}

STYLE = """
QWidget { color: #eef8f8; font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 12px; }
QLabel { background: transparent; }
QFrame#appShell, QFrame#detailShell { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #112937,stop:0.45 #0b1d2b,stop:1 #091824); border: 1px solid #31505b; border-radius: 21px; }
QFrame#topbar, QFrame#detailHeader { background: transparent; border: 0; }
QFrame#heroPanel { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #173e49,stop:0.55 #11313c,stop:1 #183444); border: 1px solid #3b6970; border-radius: 17px; }
QFrame#schedulePanel { background: #102835; border: 1px solid #294653; border-radius: 17px; }
QFrame#separator { background: #24434d; border: 0; max-height: 1px; }
QFrame#languagePicker, QFrame#meridiemPicker { background: #102b37; border: 1px solid #365965; border-radius: 12px; }
QLabel#brand { color: #f3fbfa; font-size: 13px; font-weight: 800; letter-spacing: 1px; }
QLabel#brandSub { color: #7be1cb; font-size: 9px; font-weight: 800; letter-spacing: 1px; }
QLabel#sectionTitle { color: #f0fbfc; font-size: 21px; font-weight: 750; }
QLabel#bodyMuted { color: #9cb5be; font-size: 11px; }
QLabel#cardTitle { color: #effafa; font-size: 14px; font-weight: 700; }
QLabel#cardTime { color: #9dbbc3; font-size: 10px; }
QLabel#compactValue { color: #c7fae7; font-size: 17px; font-weight: 800; }
QLabel#heroValue { color: #dbfff0; font-size: 37px; font-weight: 800; }
QLabel#smallCaps { color: #92e8d4; font-size: 9px; font-weight: 800; letter-spacing: 1px; }
QLabel#activeDot { color: #83eed0; font-size: 11px; }
QLabel#statusBadge { color: #a9f1db; font-size: 10px; font-weight: 800; }
QLabel#monitorName { color: #eaf9f8; font-size: 13px; font-weight: 700; }
QLabel#goodBadge { color: #98f4d5; background: #16483f; border-radius: 8px; padding: 5px 8px; font-size: 9px; font-weight: 800; }
QLabel#neutralBadge { color: #9fb2be; background: #1b3340; border-radius: 8px; padding: 5px 8px; font-size: 9px; font-weight: 800; }
QPushButton { border: 1px solid #315462; background: #183747; color: #e7faf6; border-radius: 10px; padding: 8px 13px; font-size: 11px; font-weight: 700; }
QPushButton:hover { background: #245262; border-color: #70d8cb; }
QPushButton:pressed { background: #1f4552; }
QPushButton#subtleButton { background: transparent; border: 0; color: #9fc8ca; padding: 5px 7px; }
QPushButton#subtleButton:hover { color: #e7fff3; background: #21424b; }
QPushButton#closeButton { background: transparent; border: 0; color: #91b5be; border-radius: 9px; padding: 0; font-size: 19px; }
QPushButton#closeButton:hover { color: white; background: #954657; }
QPushButton#languageChoice { color: #a8c4c9; background: transparent; border: 0; border-radius: 9px; padding: 5px 12px; font-size: 11px; font-weight: 700; }
QPushButton#languageChoice:hover:!checked { color: #effff8; background: #21414c; }
QPushButton#languageChoice:checked { color: #092a34; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #80e4e7,stop:1 #9cf2d5); }
QPushButton#meridiemChoice { color: #a8c4c9; background: transparent; border: 0; border-radius: 8px; padding: 4px 6px; font-size: 10px; font-weight: 700; }
QPushButton#meridiemChoice:hover:!checked { color: #effff8; background: #21414c; }
QPushButton#meridiemChoice:checked { color: #092a34; background: #9cf2d5; }
QPushButton#saveButton { color: #092c35; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #79e2ea,stop:0.58 #89edcf,stop:1 #b0f5dc); border: 0; font-size: 12px; font-weight: 800; padding: 9px 15px; }
QPushButton#saveButton:hover { background: #b2f7df; }
QPushButton#saveButton:disabled { color: #a9c3c7; background: #25414a; }
QSpinBox { color: #d8f8ea; background: transparent; border: 0; border-bottom: 1px solid #4a7378; border-radius: 0; padding: 5px 3px; font-size: 13px; font-weight: 700; }
QSpinBox:hover, QSpinBox:focus { border-bottom: 2px solid #8cead0; }
QMessageBox { background: #091927; }
"""


def label(text: str, name: str | None = None, wrap: bool = False) -> QLabel:
    result = QLabel(text)
    if name:
        result.setObjectName(name)
    result.setWordWrap(wrap)
    return result


def icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    background = QLinearGradient(4, 4, 60, 60)
    background.setColorAt(0, QColor("#ffe3a1"))
    background.setColorAt(1, QColor("#efa86e"))
    painter.setBrush(background)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 17, 17)
    painter.setPen(QPen(QColor("#173642"), 3.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    for step in range(8):
        angle = math.tau * step / 8
        inner = (32 + math.cos(angle) * 19, 32 + math.sin(angle) * 19)
        outer = (32 + math.cos(angle) * 23, 32 + math.sin(angle) * 23)
        painter.drawLine(round(inner[0]), round(inner[1]), round(outer[0]), round(outer[1]))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#173642"))
    painter.drawEllipse(20, 20, 24, 24)
    painter.end()
    return QIcon(pixmap)


class SmoothSlider(QSlider):
    """Native keyboard semantics with a precisely painted, unclipped control."""

    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(0, 100)
        self.setSingleStep(1)
        self.setPageStep(5)
        self.setFixedHeight(22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.valueChanged.connect(self.update)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, right = 8.0, float(self.width() - 8)
        center_y = self.height() / 2
        fraction = (self.value() - self.minimum()) / max(1, self.maximum() - self.minimum())
        handle_x = left + (right - left) * fraction
        painter.setPen(QPen(QColor("#315260"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(round(left), round(center_y), round(right), round(center_y))
        gradient = QLinearGradient(left, 0, right, 0)
        gradient.setColorAt(0, QColor("#73dce8"))
        gradient.setColorAt(1, QColor("#a7f4cf"))
        painter.setPen(QPen(gradient, 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(round(left), round(center_y), round(handle_x), round(center_y))
        painter.setBrush(QColor("#e9fff4"))
        painter.setPen(QPen(QColor("#7addcf"), 2))
        painter.drawEllipse(round(handle_x - 7), round(center_y - 7), 14, 14)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#a3f6e1"), 1))
            painter.drawEllipse(round(handle_x - 10), round(center_y - 10), 20, 20)

    def _set_from_pointer(self, x: float) -> None:
        fraction = max(0.0, min(1.0, (x - 8) / max(1, self.width() - 16)))
        self.setValue(round(self.minimum() + fraction * (self.maximum() - self.minimum())))

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.button() == Qt.MouseButton.LeftButton:
            self._set_from_pointer(event.position().x())
            self.setSliderDown(True)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt API
        if self.isSliderDown():
            self._set_from_pointer(event.position().x())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.button() == Qt.MouseButton.LeftButton:
            self.setSliderDown(False)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class PeriodRow(QWidget):
    changed = Signal(str, int)

    def __init__(self, key: str, name: str, time_range: str, value: int):
        super().__init__()
        self.key = key
        self.setFixedHeight(57)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(9, 3, 9, 3)
        outer.setSpacing(0)
        top = QHBoxLayout()
        top.setSpacing(4)
        self.dot = label("●", "activeDot")
        self.dot.setFixedWidth(12)
        top.addWidget(self.dot)
        title = label(name, "cardTitle")
        top.addWidget(title)
        top.addSpacing(3)
        self.time_label = label(time_range, "cardTime")
        top.addWidget(self.time_label)
        top.addStretch()
        self.value_label = label(f"{value}%", "compactValue")
        top.addWidget(self.value_label)
        outer.addLayout(top)
        self.slider = SmoothSlider()
        self.slider.setValue(value)
        self.slider.setAccessibleName(f"{name} SDR brightness")
        self.slider.valueChanged.connect(self._on_change)
        outer.addWidget(self.slider)

    def _on_change(self, value: int) -> None:
        self.value_label.setText(f"{value}%")
        self.changed.emit(self.key, value)

    def set_active(self, active: bool) -> None:
        self.dot.setStyleSheet("color:#8df1d2" if active else "color:#476572")


class MonitorSignals(QObject):
    updated = Signal(object, object)


class ScheduleHourInput(QWidget):
    """Localized editor that always stores hours in the existing 0–23 format."""

    def __init__(self, hour: int, language: str, name: str):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)
        self.spin24 = QSpinBox()
        self.spin24.setRange(0, 23)
        self.spin24.setValue(hour)
        self.spin24.setSuffix(":00")
        self.spin24.setFixedWidth(77)
        self.spin12 = QSpinBox()
        self.spin12.setRange(1, 12)
        self.spin12.setSuffix(":00")
        self.spin12.setFixedWidth(51)
        for spin in (self.spin24, self.spin12):
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.setAccessibleName(f"{name} start hour")
        row.addWidget(self.spin24)
        row.addWidget(self.spin12)
        meridiem = QFrame()
        meridiem.setObjectName("meridiemPicker")
        meridiem_row = QHBoxLayout(meridiem)
        meridiem_row.setContentsMargins(2, 2, 2, 2)
        meridiem_row.setSpacing(1)
        self.meridiem_group = QButtonGroup(self)
        self.meridiem_group.setExclusive(True)
        self.meridiem_buttons = {}
        for period in ("AM", "PM"):
            button = QPushButton(period)
            button.setObjectName("meridiemChoice")
            button.setCheckable(True)
            button.setFixedSize(31, 25)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(f"{name} {period}")
            self.meridiem_group.addButton(button)
            self.meridiem_buttons[period] = button
            meridiem_row.addWidget(button)
        row.addWidget(meridiem)
        self.meridiem = meridiem
        self._language = "PT"
        self.set_language(language)

    def hour(self) -> int:
        if self._language == "PT":
            return self.spin24.value()
        return self.spin12.value() % 12 + (12 if self.meridiem_buttons["PM"].isChecked() else 0)

    def set_language(self, language: str) -> None:
        if language not in ("PT", "EN"):
            raise ValueError("Language must be PT or EN.")
        hour = self.hour()
        self.spin24.setValue(hour)
        self.spin12.setValue(hour % 12 or 12)
        self.meridiem_buttons["AM" if hour < 12 else "PM"].setChecked(True)
        self._language = language
        self.spin24.setVisible(language == "PT")
        self.spin12.setVisible(language == "EN")
        self.meridiem.setVisible(language == "EN")


class SettingsDialog(QDialog):
    def __init__(self, config: BrightnessConfig, monitors: list[dict], monitor_error=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.words = TEXT[config.language]
        self.setWindowTitle(self.words["settings_title"])
        self.setWindowIcon(icon())
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(464)
        canvas = QVBoxLayout(self)
        canvas.setContentsMargins(8, 8, 8, 8)
        shell = QFrame()
        shell.setObjectName("detailShell")
        canvas.addWidget(shell)
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(24, 17, 24, 23)
        layout.setSpacing(10)
        header = QFrame()
        header.setObjectName("detailHeader")
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.addWidget(label(self.words["settings_title"], "sectionTitle"))
        header_row.addStretch()
        close = QPushButton("×")
        close.setObjectName("closeButton")
        close.setFixedSize(29, 29)
        close.setAccessibleName(self.words["cancel"])
        close.clicked.connect(self.reject)
        header_row.addWidget(close)
        layout.addWidget(header)
        self._drag_handle = header
        layout.addWidget(label(self.words["settings_sub"], "bodyMuted", True))
        self.hour_inputs = []
        for index, (name, value) in enumerate(zip(self.words["periods"], config.starts)):
            row = QHBoxLayout()
            row.addWidget(label(f"0{index + 1}  {name}", "cardTitle"))
            row.addStretch()
            hour_input = ScheduleHourInput(value, config.language, name)
            row.addWidget(hour_input)
            layout.addLayout(row)
            self.hour_inputs.append(hour_input)
        layout.addWidget(label(self.words["night_hint"], "bodyMuted"))
        language_row = QHBoxLayout()
        language_row.addWidget(label(self.words["language"], "cardTitle"))
        language_row.addStretch()
        picker = QFrame()
        picker.setObjectName("languagePicker")
        picker.setFixedHeight(38)
        picker_layout = QHBoxLayout(picker)
        picker_layout.setContentsMargins(3, 3, 3, 3)
        picker_layout.setSpacing(2)
        self.language_group = QButtonGroup(self)
        self.language_group.setExclusive(True)
        self.language_buttons = {}
        for code, caption in (("PT", "Português"), ("EN", "English")):
            choice = QPushButton(caption)
            choice.setObjectName("languageChoice")
            choice.setCheckable(True)
            choice.setFixedHeight(30)
            choice.setCursor(Qt.CursorShape.PointingHandCursor)
            choice.setProperty("language", code)
            choice.setAccessibleName(f"{self.words['language']}: {caption}")
            choice.setChecked(code == config.language)
            choice.clicked.connect(lambda _checked=False, selected=code: self._change_language(selected))
            self.language_group.addButton(choice)
            self.language_buttons[code] = choice
            picker_layout.addWidget(choice)
        language_row.addWidget(picker)
        layout.addLayout(language_row)
        layout.addSpacing(4)
        layout.addWidget(label(self.words["monitors"], "cardTitle"))
        layout.addWidget(label(self.words["monitor_sub"], "bodyMuted", True))
        if monitor_error:
            layout.addWidget(label(self.words["monitor_error"], "bodyMuted"))
        elif not monitors:
            layout.addWidget(label(self.words["detecting"], "bodyMuted"))
        else:
            for item in monitors:
                monitor_row = QHBoxLayout()
                monitor_row.addWidget(label(str(item.get("FriendlyName") or item.get("DeviceName")), "monitorName"))
                monitor_row.addStretch()
                active = item.get("HdrActive") and item.get("HdrSupported")
                monitor_row.addWidget(label(self.words["hdr_active"] if active else "SDR", "goodBadge" if active else "neutralBadge"))
                layout.addLayout(monitor_row)
        layout.addWidget(label("✦  " + self.words["safety_text"], "bodyMuted", True))
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton(self.words["cancel"])
        confirm = QPushButton(self.words["confirm"])
        confirm.setObjectName("saveButton")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self._validate)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addSpacing(8)
        layout.addLayout(buttons)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 57:
            self._drag_origin = event.globalPosition().toPoint() - self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.buttons() & Qt.MouseButton.LeftButton and getattr(self, "_drag_origin", None) is not None:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._drag_origin = None
        super().mouseReleaseEvent(event)

    def _validate(self) -> None:
        starts = tuple(hour_input.hour() for hour_input in self.hour_inputs)
        if tuple(sorted(set(starts))) != starts:
            QMessageBox.warning(self, self.words["settings_title"], self.words["invalid"])
            return
        self.starts = starts
        self.language = self.language_group.checkedButton().property("language")
        self.accept()

    def _change_language(self, language: str) -> None:
        for hour_input in self.hour_inputs:
            hour_input.set_language(language)


class MainWindow(QMainWindow):
    def __init__(self, store: ConfigStore, monitor_script, runner=None, preview=False):
        super().__init__()
        self.store = store
        self.monitor_script = monitor_script
        self.runner = runner
        self.preview = preview
        self.config = store.load()
        self.levels = dict(self.config.levels)
        self.monitors = []
        self.monitor_error = None
        self._exit_requested = False
        self._tray_open_queued = False
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="monitor-probe")
        self.signals = MonitorSignals(self)
        self.signals.updated.connect(self._monitors_updated)
        self.setWindowTitle("Brightness Control Application v2.0.1")
        self.setWindowIcon(icon())
        window_type = Qt.WindowType.Window if self.preview else Qt.WindowType.Tool
        self.setWindowFlags(window_type | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(402, 520)
        self.setStyleSheet(STYLE)
        self._build()
        self.tray = self._create_tray()
        self._place_near_tray()
        self.clock = QTimer(self)
        self.clock.timeout.connect(self._update_active)
        self.clock.start(15000)
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._refresh_monitors)
        self.monitor_timer.start(60000)
        self._update_active()
        self._refresh_monitors()
        if runner is not None:
            runner.status_changed.connect(self._worker_status)
            runner.start()

    @property
    def words(self) -> dict:
        return TEXT[self.config.language]

    def _build(self) -> None:
        words = self.words
        canvas = QWidget()
        canvas.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(7, 7, 7, 7)
        shell = QFrame()
        shell.setObjectName("appShell")
        canvas_layout.addWidget(shell)
        outer = QVBoxLayout(shell)
        outer.setContentsMargins(15, 11, 15, 13)
        outer.setSpacing(7)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        top = QHBoxLayout(topbar)
        top.setContentsMargins(0, 0, 0, 0)
        mark = QLabel()
        mark.setPixmap(icon().pixmap(29, 29))
        mark.setFixedSize(29, 29)
        mark.setAccessibleName("Sol" if self.config.language == "PT" else "Sun")
        top.addWidget(mark)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        brand_title = label("BRIGHTNESS CONTROL", "brand")
        brand.addWidget(brand_title)
        brand.addWidget(label(words["tagline"], "brandSub"))
        top.addSpacing(5)
        top.addLayout(brand)
        top.addStretch()
        self.top_badge = label(words["preview" if self.preview else "live"], "statusBadge")
        top.addWidget(self.top_badge)
        self.settings_button = QPushButton("Ajustes" if self.config.language == "PT" else "Settings")
        self.settings_button.setObjectName("subtleButton")
        self.settings_button.setFixedHeight(30)
        self.settings_button.setToolTip(words["settings"])
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(self._open_settings)
        top.addWidget(self.settings_button)
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(28, 28)
        close_button.setAccessibleName("Fechar" if self.config.language == "PT" else "Close")
        close_button.setToolTip(words["tray"])
        close_button.clicked.connect(self.close)
        top.addWidget(close_button)
        outer.addWidget(topbar)

        hero_panel = QFrame()
        hero_panel.setObjectName("heroPanel")
        hero_panel.setFixedHeight(82)
        hero = QHBoxLayout(hero_panel)
        hero.setContentsMargins(15, 10, 15, 10)
        current = QVBoxLayout()
        current.setSpacing(3)
        current.addWidget(label(words["now"], "smallCaps"))
        self.current_period_label = label("", "cardTitle")
        self.current_period_label.setStyleSheet("font-size:17px; font-weight:750")
        current.addWidget(self.current_period_label)
        self.monitor_summary = label(words["detecting"], "bodyMuted")
        current.addWidget(self.monitor_summary)
        hero.addLayout(current, 1)
        self.current_value_label = label("", "heroValue")
        hero.addWidget(self.current_value_label)
        outer.addWidget(hero_panel)

        outer.addWidget(label(words["schedule"], "smallCaps"))

        self.cards = {}
        schedule = QFrame()
        schedule.setObjectName("schedulePanel")
        schedule_layout = QVBoxLayout(schedule)
        schedule_layout.setContentsMargins(8, 3, 8, 3)
        schedule_layout.setSpacing(0)
        for index, key in enumerate(PERIODS):
            card = PeriodRow(key, words["periods"][index],
                             self.config.time_range(key), self.levels[key])
            card.changed.connect(self._level_changed)
            schedule_layout.addWidget(card)
            if index < len(PERIODS) - 1:
                separator = QFrame()
                separator.setObjectName("separator")
                separator.setFixedHeight(1)
                schedule_layout.addWidget(separator)
            self.cards[key] = card
        outer.addWidget(schedule)

        footer = QVBoxLayout()
        footer.setSpacing(4)
        self.info_label = label(words["preview_note"] if self.preview else words["tray"], "bodyMuted", True)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.addWidget(self.info_label)
        self.save_button = QPushButton(words["save"])
        self.save_button.setObjectName("saveButton")
        self.save_button.setFixedHeight(36)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save)
        footer.addWidget(self.save_button)
        outer.addLayout(footer)
        self.setCentralWidget(canvas)
        self._render_monitors()

    def _create_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable() or self.preview:
            return None
        tray = QSystemTrayIcon(icon(), self)
        menu = QMenu(self)
        open_action = menu.addAction(self.words["open"])
        open_action.triggered.connect(self._queue_show_from_tray)
        exit_action = menu.addAction(self.words["exit"])
        exit_action.triggered.connect(self._quit)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()
        return tray

    def _update_active(self) -> None:
        key = self.config.current_period(datetime.now().hour)
        for card_key, card in self.cards.items():
            card.set_active(card_key == key)
        index = PERIODS.index(key)
        self.current_period_label.setText(self.words["periods"][index] + "  ·  " + self.config.time_range(key, compact=True))
        self.current_value_label.setText(f"{self.levels[key]}%")

    def _level_changed(self, key: str, value: int) -> None:
        self.levels[key] = value
        self._update_active()
        if not self.preview:
            dirty = self.levels != self.config.levels
            self.save_button.setEnabled(dirty)
            self.info_label.setText(self.words["pending"] if dirty else self.words["tray"])

    def _save(self) -> None:
        updated = BrightnessConfig(self.config.language, dict(self.levels), self.config.starts, self.config.raw)
        try:
            self.store.save(updated)
            self.config = self.store.load()
        except Exception as exc:
            logging.exception("Could not save brightness settings")
            QMessageBox.critical(self, self.words["save_error"], str(exc))
            return
        self.save_button.setEnabled(False)
        self.info_label.setText(self.words["saved"])
        QTimer.singleShot(6500, lambda: self.info_label.setText(self.words["tray"]))

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.config, self.monitors, self.monitor_error, self)
        dialog.setStyleSheet(STYLE)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if self.preview:
            return
        updated = BrightnessConfig(dialog.language, dict(self.levels), dialog.starts, self.config.raw)
        try:
            self.store.save(updated)
            self.config = self.store.load()
        except Exception as exc:
            logging.exception("Could not save schedule")
            QMessageBox.critical(self, self.words["save_error"], str(exc))
            return
        if self.tray is not None:
            self.tray.hide()
            self.tray.deleteLater()
        self._build()
        self.tray = self._create_tray()
        self._update_active()

    def _refresh_monitors(self) -> None:
        if getattr(self, "_monitor_pending", False):
            return
        self._monitor_pending = True
        future = self.executor.submit(discover_monitors, self.monitor_script)
        def finished(item):
            try:
                self.signals.updated.emit(item.result(), None)
            except Exception as exc:
                self.signals.updated.emit(None, str(exc))
        future.add_done_callback(finished)

    def _monitors_updated(self, data, error) -> None:
        self._monitor_pending = False
        self.monitors = data or []
        self.monitor_error = error
        self._render_monitors()

    def _render_monitors(self) -> None:
        if not hasattr(self, "monitor_summary"):
            return
        if self.monitor_error:
            self.monitor_summary.setText(self.words["monitor_error"])
            return
        if not self.monitors:
            self.monitor_summary.setText(self.words["detecting"])
            return
        active = [item for item in self.monitors if item.get("HdrActive") and item.get("HdrSupported")]
        if not active:
            self.monitor_summary.setText(self.words["no_hdr"])
            return
        if self.config.language == "PT":
            self.monitor_summary.setText(f"● {len(active)} HDR ativos  ·  {len(self.monitors) - len(active)} SDR fora do ajuste")
        else:
            self.monitor_summary.setText(f"● {len(active)} HDR active  ·  {len(self.monitors) - len(active)} SDR excluded")

    def _worker_status(self, running: bool, detail: str) -> None:
        if self.preview:
            return
        self.top_badge.setText(self.words["live" if running else "error_badge"])
        self.top_badge.setToolTip(self.words["worker_ok"] if running else self.words["worker_off"])
        if detail:
            self.top_badge.setToolTip(detail)

    def _place_near_tray(self) -> None:
        screen = None
        if self.tray is not None:
            tray_rect = self.tray.geometry()
            if tray_rect.isValid():
                screen = QGuiApplication.screenAt(tray_rect.center())
        if screen is None:
            screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            try:
                bottom = safe_bottom(screen.geometry(), area, taskbar_rectangles())
            except OSError:
                logging.exception("Could not inspect taskbar geometry")
                bottom = area.bottom() + 1 - 60  # Conservative fallback for auto-hide.
            self.move(area.right() - self.width() - 11, bottom - self.height())

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 56:
            self._drag_origin = event.globalPosition().toPoint() - self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.buttons() & Qt.MouseButton.LeftButton and getattr(self, "_drag_origin", None) is not None:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._drag_origin = None
        super().mouseReleaseEvent(event)

    def _on_tray_activated(self, reason) -> None:
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self._queue_show_from_tray()

    def _queue_show_from_tray(self) -> None:
        if self._exit_requested or self._tray_open_queued:
            return
        # Leave the native tray/menu callback before moving or activating a window.
        # Windows can emit Trigger and DoubleClick for the same interaction.
        self._tray_open_queued = True
        QTimer.singleShot(0, self._show_from_tray)

    def _show_from_tray(self) -> None:
        self._tray_open_queued = False
        if self._exit_requested:
            return
        logging.info("Opening popup from tray")
        try:
            self._place_near_tray()
        except Exception:
            logging.exception("Could not position popup; opening at its current position")
        try:
            self.showNormal()
            self.raise_()
            self.activateWindow()
        except Exception:
            logging.exception("Could not reopen popup from tray")
        else:
            logging.info("Popup opened from tray")

    def _quit(self) -> None:
        logging.info("Exit requested from tray")
        self._exit_requested = True
        self.clock.stop()
        self.monitor_timer.stop()
        self.executor.shutdown(wait=False, cancel_futures=True)
        if self.runner is not None:
            self.runner.stop()
        if self.tray is not None:
            self.tray.hide()
        QApplication.instance().quit()

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        if self.tray is not None and not self._exit_requested:
            logging.info("Popup hidden to tray")
            event.ignore()
            self.hide()
        else:
            self._quit()
            event.accept()
