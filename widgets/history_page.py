from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout
from PySide6.QtCore import Qt

import theme
from widgets.components import Card, Badge


class HistoryPage(QWidget):
    """Session-only history of completed audits (no disk/network I/O)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 28)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.container = QWidget()
        self.layout_ = QVBoxLayout(self.container)
        self.layout_.setSpacing(12)
        self.layout_.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)

        self._render_empty()

    def _clear(self):
        while self.layout_.count():
            item = self.layout_.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render_empty(self):
        self._clear()
        card = Card(flat=True)
        lbl = QLabel("Audits you run this session will appear here.")
        lbl.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:12.5px;")
        card.layout.addWidget(lbl)
        self.layout_.addWidget(card)

    def add_entry(self, result):
        self._entries.insert(0, result)
        self._render()

    def _render(self):
        self._clear()
        if not self._entries:
            self._render_empty()
            return
        for r in self._entries[:25]:
            card = Card()
            row = QHBoxLayout()
            model = QLabel(r.model_name)
            model.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:13px; font-weight:700;")
            badge = Badge(f"Grade {r.grade}", theme.grade_color(r.grade))
            row.addWidget(model)
            row.addStretch()
            row.addWidget(badge)
            card.layout.addLayout(row)

            detail = QLabel(
                f"{r.token_count:,} tokens · Overall {r.overall_score:.0f}/100 · "
                f"{len(r.logic_failures)} logic issue(s) · Hallucination risk {r.hallucination_risk:.0f}/100"
            )
            detail.setWordWrap(True)
            detail.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:11.5px;")
            card.layout.addWidget(detail)
            self.layout_.addWidget(card)
