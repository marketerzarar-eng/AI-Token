from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PySide6.QtCore import Qt, Signal

import theme
from widgets.components import Divider


NAV_ITEMS = [
    ("dashboard", "Audit"),
    ("history", "Report History"),
    ("about", "About"),
]


class Sidebar(QWidget):
    navigate = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 20)
        layout.setSpacing(4)

        brand_row = QHBoxLayout()
        mark = QLabel("◆")
        mark.setStyleSheet(f"color:{theme.ACCENT}; font-size:20px;")
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("AI Token Auditor")
        title.setObjectName("brandTitle")
        title.setWordWrap(True)
        subtitle = QLabel("USAGE & QUALITY AUDIT")
        subtitle.setObjectName("brandSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        brand_row.addWidget(mark)
        brand_row.addSpacing(8)
        brand_row.addLayout(title_box)
        layout.addLayout(brand_row)

        layout.addSpacing(28)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self._buttons = {}
        for key, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked, k=key: self.navigate.emit(k))
            layout.addWidget(btn)
            self.group.addButton(btn)
            self._buttons[key] = btn

        self._buttons["dashboard"].setChecked(True)

        layout.addStretch()
        layout.addWidget(Divider())
        layout.addSpacing(10)

        status_row = QHBoxLayout()
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(8, 8)
        self.status_dot.setStyleSheet(
            f"background-color:{theme.SUCCESS}; border-radius:4px;"
        )
        self.status_label = QLabel("Connected")
        self.status_label.setObjectName("statusLabel")
        status_row.addWidget(self.status_dot)
        status_row.addSpacing(6)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        layout.addLayout(status_row)

        version = QLabel("v1.0.0")
        version.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:10px;")
        layout.addWidget(version)

    def set_active(self, key: str):
        if key in self._buttons:
            self._buttons[key].setChecked(True)

    def set_online_status(self, online: bool):
        color = theme.SUCCESS if online else theme.DANGER
        self.status_dot.setStyleSheet(f"background-color:{color}; border-radius:4px;")
        self.status_label.setText("Connected" if online else "Offline")
