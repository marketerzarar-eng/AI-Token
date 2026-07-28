from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

import theme
from widgets.components import Card, Divider


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 28)
        root.setAlignment(Qt.AlignTop)

        card = Card()
        title = QLabel("AI Token Auditor")
        title.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:18px; font-weight:800;")
        card.layout.addWidget(title)

        version = QLabel("Version 1.0.0")
        version.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11.5px;")
        card.layout.addWidget(version)

        card.layout.addWidget(Divider())

        body = QLabel(
            "AI Token Auditor analyzes prompts and AI-generated responses for token "
            "efficiency and output quality. It runs entirely on your machine — no text "
            "you audit is sent anywhere.\n\n"
            "Checks performed: token count estimation, prompt efficiency, verbosity, "
            "repeated wording, logic failure detection, inconsistency detection, "
            "hallucination risk indicators, clarity, and structure."
        )
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12.5px; line-height:150%;")
        card.layout.addWidget(body)

        root.addWidget(card)
