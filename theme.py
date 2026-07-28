"""
Premium dark theme for AI Token Auditor.
Single source of truth for color tokens + the global QSS stylesheet.
"""

# ---- Color tokens -----------------------------------------------------
BG_BASE       = "#0B0E14"   # app background
BG_SURFACE    = "#12161F"   # panels
BG_CARD       = "#161B26"   # cards
BG_CARD_HOVER = "#1A2130"
BG_SIDEBAR    = "#0E1118"
BORDER        = "#232A38"
BORDER_SOFT   = "#1B2130"

TEXT_PRIMARY   = "#EDEFF5"
TEXT_SECONDARY = "#9AA3B5"
TEXT_MUTED     = "#6B7284"

ACCENT         = "#7C5CFF"   # violet
ACCENT_SOFT    = "#5B8CFF"   # blue
ACCENT_GRADIENT_START = "#7C5CFF"
ACCENT_GRADIENT_END   = "#5B8CFF"

SUCCESS = "#3DD68C"
WARNING = "#F5B942"
DANGER  = "#FF5C7A"
INFO    = "#5B8CFF"

FONT_FAMILY = "Segoe UI, Inter, -apple-system, sans-serif"


def grade_color(grade: str) -> str:
    return {
        "A": SUCCESS,
        "B": SUCCESS,
        "C": WARNING,
        "D": WARNING,
        "F": DANGER,
    }.get(grade, TEXT_SECONDARY)


def score_color(score: float) -> str:
    if score >= 80:
        return SUCCESS
    if score >= 60:
        return WARNING
    return DANGER


STYLESHEET = f"""
* {{
    font-family: {FONT_FAMILY};
    outline: none;
}}

QMainWindow, QWidget#root {{
    background-color: {BG_BASE};
}}

QWidget {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}

/* ---------------- Sidebar ---------------- */
QWidget#sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER_SOFT};
}}

QLabel#brandTitle {{
    color: {TEXT_PRIMARY};
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#brandSubtitle {{
    color: {TEXT_MUTED};
    font-size: 11px;
    letter-spacing: 1.5px;
}}

QPushButton#navButton {{
    text-align: left;
    padding: 11px 16px;
    border-radius: 10px;
    color: {TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 600;
    background-color: transparent;
    border: none;
}}
QPushButton#navButton:hover {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_PRIMARY};
}}
QPushButton#navButton:checked {{
    background-color: rgba(124, 92, 255, 0.16);
    color: {TEXT_PRIMARY};
    border: 1px solid rgba(124, 92, 255, 0.35);
}}

QLabel#statusDot {{
    border-radius: 4px;
}}

QLabel#statusLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

/* ---------------- Top bar ---------------- */
QWidget#topbar {{
    background-color: {BG_BASE};
    border-bottom: 1px solid {BORDER_SOFT};
}}

QLabel#pageTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#pageSubtitle {{
    font-size: 12px;
    color: {TEXT_MUTED};
}}

/* ---------------- Cards ---------------- */
QFrame.card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame.cardFlat {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_SOFT};
    border-radius: 12px;
}}

QLabel.cardTitle {{
    font-size: 12px;
    font-weight: 700;
    color: {TEXT_MUTED};
    letter-spacing: 1px;
}}

QLabel.metricValue {{
    font-size: 26px;
    font-weight: 800;
    color: {TEXT_PRIMARY};
}}

QLabel.metricCaption {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
}}

/* ---------------- Inputs ---------------- */
QComboBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    min-height: 22px;
}}
QComboBox:hover {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox QAbstractItemView {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    selection-background-color: rgba(124, 92, 255, 0.25);
    color: {TEXT_PRIMARY};
    outline: none;
    padding: 4px;
    border-radius: 8px;
}}

QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: rgba(124, 92, 255, 0.35);
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

/* ---------------- Buttons ---------------- */
QPushButton#primaryButton {{
    background-color: {ACCENT};
    color: white;
    font-weight: 700;
    font-size: 13px;
    border-radius: 11px;
    padding: 12px 22px;
    border: none;
}}
QPushButton#primaryButton:hover {{ background-color: #8E72FF; }}
QPushButton#primaryButton:pressed {{ background-color: #6C4CEB; }}
QPushButton#primaryButton:disabled {{ background-color: #35394A; color: {TEXT_MUTED}; }}

QPushButton#secondaryButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 12px;
    border-radius: 10px;
    padding: 10px 16px;
    border: 1px solid {BORDER};
}}
QPushButton#secondaryButton:hover {{
    border: 1px solid {ACCENT};
    color: {TEXT_PRIMARY};
}}

/* ---------------- Scrollbars ---------------- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 5px;
    min-width: 30px;
}}

/* ---------------- Progress / score bars ---------------- */
QProgressBar {{
    background-color: {BORDER_SOFT};
    border-radius: 6px;
    height: 10px;
    border: none;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    border-radius: 6px;
    background-color: {ACCENT};
}}

/* ---------------- Badges ---------------- */
QLabel.badge {{
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QFrame#divider {{
    background-color: {BORDER_SOFT};
    max-height: 1px;
    min-height: 1px;
}}

QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 6px 10px;
    border-radius: 6px;
}}
"""
