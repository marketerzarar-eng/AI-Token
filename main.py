"""
AI Token Auditor
-----------------
Entry point. Wraps startup in a broad exception guard so packaging quirks
(missing optional deps, etc.) never present as a silent crash — the user
always gets a window or a clear message.
"""

import sys
import traceback


def main():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont

    import theme
    from main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("AI Token Auditor")
    app.setOrganizationName("AI Token Auditor")
    app.setStyleSheet(theme.STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail loud in the console/log rather than a silent disappearing
        # process — important for a trustworthy first-run experience.
        traceback.print_exc()
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "AI Token Auditor failed to start. See the log for details.\n\n"
                + traceback.format_exc()[-800:],
                "AI Token Auditor",
                0x10,
            )
        except Exception:
            pass
        sys.exit(1)
