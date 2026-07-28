from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

import theme
from widgets.components import add_shadow


class OfflineScreen(QWidget):
    """
    Polished offline state. Never crashes or blocks the app — the user
    can retry the connectivity check or continue in offline/local mode,
    since auditing itself does not require internet access.
    """

    retry = Signal()
    continue_offline = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("root")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        panel = QWidget()
        panel.setFixedWidth(440)
        panel.setProperty("class", "card")
        panel.setStyleSheet(
            f"background-color:{theme.BG_CARD}; border:1px solid {theme.BORDER}; border-radius:18px;"
        )
        add_shadow(panel, blur=40, alpha=150, y_offset=14)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(36, 36, 36, 32)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("⚠")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"color:{theme.WARNING}; font-size:34px;")
        layout.addWidget(icon)

        title = QLabel("Internet connection not detected")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:17px; font-weight:700;")
        layout.addWidget(title)

        body = QLabel(
            "Please reconnect to continue. AI Token Auditor will automatically "
            "resume as soon as a connection is available."
        )
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12.5px;")
        layout.addWidget(body)

        layout.addSpacing(10)

        retry_btn = QPushButton("Retry Connection")
        retry_btn.setObjectName("primaryButton")
        retry_btn.setCursor(Qt.PointingHandCursor)
        retry_btn.clicked.connect(self.retry.emit)
        layout.addWidget(retry_btn)

        continue_btn = QPushButton("Continue in Offline Mode")
        continue_btn.setObjectName("secondaryButton")
        continue_btn.setCursor(Qt.PointingHandCursor)
        continue_btn.clicked.connect(self.continue_offline.emit)
        layout.addWidget(continue_btn)

        hint = QLabel("Auditing runs locally, so offline mode still produces full reports.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:10.5px;")
        layout.addWidget(hint)

        outer.addWidget(panel, alignment=Qt.AlignCenter)
