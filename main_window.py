from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

import theme
from core.connectivity import is_online
from widgets.sidebar import Sidebar
from widgets.dashboard import Dashboard
from widgets.history_page import HistoryPage
from widgets.about_page import AboutPage
from widgets.offline_screen import OfflineScreen


PAGE_TITLES = {
    "dashboard": ("Audit Dashboard", "Paste a prompt or AI response to generate a full quality & token report."),
    "history": ("Report History", "Audits completed during this session."),
    "about": ("About", "How AI Token Auditor works."),
}


class ConnectivityWorker(QThread):
    result_ready = Signal(bool)

    def run(self):
        self.result_ready.emit(is_online())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Token Auditor")
        self.resize(1180, 780)
        self.setMinimumSize(980, 640)

        self.root = QWidget()
        self.root.setObjectName("root")
        self.setCentralWidget(self.root)

        self.outer_layout = QVBoxLayout(self.root)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # ---- App shell (built once, shown after connectivity check) ----
        self.app_shell = QWidget()
        shell_layout = QHBoxLayout(self.app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigate.connect(self._on_navigate)
        shell_layout.addWidget(self.sidebar)

        content_col = QVBoxLayout()
        content_col.setContentsMargins(0, 0, 0, 0)
        content_col.setSpacing(0)

        self.topbar = QWidget()
        self.topbar.setObjectName("topbar")
        self.topbar.setFixedHeight(72)
        top_layout = QVBoxLayout(self.topbar)
        top_layout.setContentsMargins(28, 12, 28, 12)
        top_layout.setSpacing(2)
        top_layout.setAlignment(Qt.AlignVCenter)
        self.page_title = QLabel("Audit Dashboard")
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel("")
        self.page_subtitle.setObjectName("pageSubtitle")
        top_layout.addWidget(self.page_title)
        top_layout.addWidget(self.page_subtitle)
        content_col.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.dashboard = Dashboard()
        self.history_page = HistoryPage()
        self.about_page = AboutPage()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.about_page)
        content_col.addWidget(self.stack, stretch=1)

        content_wrap = QWidget()
        content_wrap.setLayout(content_col)
        shell_layout.addWidget(content_wrap, stretch=1)

        # Hook: log every completed audit into history
        self.dashboard.audit_completed.connect(self.history_page.add_entry)

        # ---- Offline screen ----
        self.offline_screen = OfflineScreen()
        self.offline_screen.retry.connect(self._check_connectivity)
        self.offline_screen.continue_offline.connect(self._enter_app)

        self.outer_layout.addWidget(self.app_shell)
        self.outer_layout.addWidget(self.offline_screen)
        self.app_shell.hide()
        self.offline_screen.hide()

        self._worker = None
        self._checking_label = self._build_checking_state()
        self.outer_layout.addWidget(self._checking_label)

        QTimer.singleShot(150, self._check_connectivity)

    # ------------------------------------------------------------------
    def _build_checking_state(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("AI Token Auditor")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:22px; font-weight:800;")
        sub = QLabel("Checking connection…")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:12px;")
        layout.addWidget(lbl)
        layout.addWidget(sub)
        return w

    # ------------------------------------------------------------------
    def _check_connectivity(self):
        self._checking_label.show()
        self.app_shell.hide()
        self.offline_screen.hide()

        if self._worker and self._worker.isRunning():
            return
        self._worker = ConnectivityWorker()
        self._worker.result_ready.connect(self._on_connectivity_result)
        self._worker.start()

    def _on_connectivity_result(self, online: bool):
        self._checking_label.hide()
        if online:
            self._enter_app(online=True)
        else:
            self.offline_screen.show()

    def _enter_app(self, online: bool = False):
        self._checking_label.hide()
        self.offline_screen.hide()
        self.app_shell.show()
        self.sidebar.set_online_status(online)

    # ------------------------------------------------------------------
    def _on_navigate(self, key: str):
        index_map = {"dashboard": 0, "history": 1, "about": 2}
        self.stack.setCurrentIndex(index_map.get(key, 0))
        title, subtitle = PAGE_TITLES.get(key, ("", ""))
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)
        self.sidebar.set_active(key)
