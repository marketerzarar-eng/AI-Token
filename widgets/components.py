from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar,
    QGraphicsDropShadowEffect, QSizePolicy,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

import theme


def add_shadow(widget: QWidget, blur=28, color="#000000", alpha=140, y_offset=8):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    c = QColor(color)
    c.setAlpha(alpha)
    effect.setColor(c)
    effect.setOffset(0, y_offset)
    widget.setGraphicsEffect(effect)


class Card(QFrame):
    """A soft-elevated container card with consistent padding."""

    def __init__(self, flat: bool = False, parent=None):
        super().__init__(parent)
        self.setProperty("class", "cardFlat" if flat else "card")
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 18, 20, 18)
        self.layout.setSpacing(10)
        if not flat:
            add_shadow(self, blur=32, alpha=90, y_offset=10)


class Badge(QLabel):
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "badge")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"background-color: rgba(0,0,0,0); "
            f"color: {color}; "
            f"border: 1px solid {color}; "
            f"border-radius: 8px; padding: 3px 10px; font-size: 11px; font-weight: 700;"
        )


class ScoreBar(QWidget):
    """Labeled metric with an animated colored progress bar."""

    def __init__(self, label: str, value: float, suffix: str = "/100", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        row = QHBoxLayout()
        name = QLabel(label)
        name.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px; font-weight:600;")
        val = QLabel(f"{value:.0f}{suffix}")
        color = theme.score_color(value) if suffix == "/100" else theme.TEXT_PRIMARY
        val.setStyleSheet(f"color:{color}; font-size:12px; font-weight:800;")
        row.addWidget(name)
        row.addStretch()
        row.addWidget(val)
        layout.addLayout(row)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        color_for_bar = theme.score_color(value) if suffix == "/100" else theme.ACCENT
        bar.setStyleSheet(
            f"QProgressBar {{ background-color:{theme.BORDER_SOFT}; border-radius:4px; }}"
            f"QProgressBar::chunk {{ background-color:{color_for_bar}; border-radius:4px; }}"
        )
        layout.addWidget(bar)

        self._bar = bar
        self._anim = QPropertyAnimation(bar, b"value")
        self._anim.setDuration(650)
        self._anim.setStartValue(0)
        self._anim.setEndValue(int(min(100, max(0, value))))
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()


class MetricTile(Card):
    """Small dashboard tile: big number + caption."""

    def __init__(self, title: str, value: str, caption: str = "", accent: str = None, parent=None):
        super().__init__(parent=parent)
        t = QLabel(title.upper())
        t.setProperty("class", "cardTitle")
        v = QLabel(value)
        v.setProperty("class", "metricValue")
        if accent:
            v.setStyleSheet(f"color:{accent}; font-size:26px; font-weight:800;")
        self.layout.addWidget(t)
        self.layout.addWidget(v)
        if caption:
            c = QLabel(caption)
            c.setProperty("class", "metricCaption")
            c.setWordWrap(True)
            self.layout.addWidget(c)
        self.layout.addStretch()


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("divider")
        self.setFixedHeight(1)


class IssueRow(QFrame):
    """A single flagged issue: type badge + explanation + excerpt."""

    def __init__(self, issue_type: str, location: str, detail: str, excerpt: str = "",
                 color: str = None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "cardFlat")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        color = color or theme.DANGER
        header = QHBoxLayout()
        badge = Badge(issue_type, color)
        loc = QLabel(location)
        loc.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
        header.addWidget(badge)
        header.addStretch()
        header.addWidget(loc)
        layout.addLayout(header)

        detail_lbl = QLabel(detail)
        detail_lbl.setWordWrap(True)
        detail_lbl.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:12.5px;")
        layout.addWidget(detail_lbl)

        if excerpt:
            ex = QLabel(f"“{excerpt.strip()}”")
            ex.setWordWrap(True)
            ex.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11.5px; font-style: italic;")
            layout.addWidget(ex)
