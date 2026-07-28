from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
    QPushButton, QScrollArea, QGridLayout, QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Signal

import theme
from core.analyzer import run_audit, AuditResult
from widgets.components import Card, ScoreBar, Badge, MetricTile, Divider, IssueRow


MODEL_OPTIONS = [
    "GPT-4.1", "GPT-4o", "GPT-4o mini", "o3", "Claude Opus 4.5",
    "Claude Sonnet 4.5", "Claude Haiku 4.5", "Gemini 2.5 Pro",
    "Gemini 2.5 Flash", "Llama 3.3", "Mistral Large", "Custom / Other",
]


class Dashboard(QWidget):
    audit_completed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 28)
        root.setSpacing(22)

        # -------- Left: input panel --------
        left = QVBoxLayout()
        left.setSpacing(16)

        input_card = Card()
        model_label = QLabel("MODEL BEING AUDITED")
        model_label.setProperty("class", "cardTitle")
        input_card.layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(MODEL_OPTIONS)
        self.model_combo.setEditable(True)
        input_card.layout.addWidget(self.model_combo)

        input_card.layout.addSpacing(6)

        text_label = QLabel("PROMPT OR AI RESPONSE TEXT")
        text_label.setProperty("class", "cardTitle")
        input_card.layout.addWidget(text_label)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Paste the prompt or AI-generated response you want audited…"
        )
        self.text_input.setMinimumHeight(320)
        input_card.layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run Audit")
        self.run_btn.setObjectName("primaryButton")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self._on_run_clicked)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        input_card.layout.addSpacing(4)
        input_card.layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color:{theme.DANGER}; font-size:11.5px;")
        self.status_label.setWordWrap(True)
        input_card.layout.addWidget(self.status_label)

        left.addWidget(input_card)
        left_wrap = QWidget()
        left_wrap.setLayout(left)
        left_wrap.setFixedWidth(420)
        root.addWidget(left_wrap)

        # -------- Right: report panel (scrollable) --------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setSpacing(16)
        self.report_layout.setContentsMargins(2, 2, 2, 2)
        self.report_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.report_container)

        root.addWidget(self.scroll, stretch=1)

        self._render_empty_state()

    # ------------------------------------------------------------------
    def _clear_report(self):
        while self.report_layout.count():
            item = self.report_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render_empty_state(self):
        self._clear_report()
        card = Card(flat=True)
        card.layout.setAlignment(Qt.AlignCenter)
        icon = QLabel("◈")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"color:{theme.ACCENT}; font-size:30px;")
        title = QLabel("No report yet")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:14px; font-weight:700;")
        body = QLabel("Paste text on the left and run an audit to see the full breakdown here.")
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:12px;")
        card.layout.addWidget(icon)
        card.layout.addWidget(title)
        card.layout.addWidget(body)
        card.setMinimumHeight(420)
        self.report_layout.addWidget(card)

    # ------------------------------------------------------------------
    def _on_clear_clicked(self):
        self.text_input.clear()
        self.status_label.setText("")
        self._render_empty_state()

    def _on_run_clicked(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            self.status_label.setText("Enter a prompt or response before running the audit.")
            return
        self.status_label.setText("")
        model_name = self.model_combo.currentText().strip() or "Unspecified Model"
        result = run_audit(text, model_name)
        self._render_report(result)
        self.audit_completed.emit(result)

    # ------------------------------------------------------------------
    def _render_report(self, r: AuditResult):
        self._clear_report()

        # Header summary card
        header = Card()
        top_row = QHBoxLayout()
        model_lbl = QLabel(r.model_name)
        model_lbl.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:16px; font-weight:800;")
        grade_badge = Badge(f"Grade {r.grade}", theme.grade_color(r.grade))
        top_row.addWidget(model_lbl)
        top_row.addStretch()
        top_row.addWidget(grade_badge)
        header.layout.addLayout(top_row)

        overall_row = QHBoxLayout()
        overall_lbl = QLabel(f"{r.overall_score:.0f}")
        overall_lbl.setStyleSheet(
            f"color:{theme.score_color(r.overall_score)}; font-size:40px; font-weight:800;"
        )
        overall_caption = QVBoxLayout()
        oc1 = QLabel("OVERALL AUDIT SCORE")
        oc1.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px; font-weight:700; letter-spacing:1px;")
        oc2 = QLabel(r.summary)
        oc2.setWordWrap(True)
        oc2.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px;")
        overall_caption.addWidget(oc1)
        overall_caption.addWidget(oc2)
        overall_row.addWidget(overall_lbl)
        overall_row.addSpacing(14)
        overall_row.addLayout(overall_caption, stretch=1)
        header.layout.addSpacing(6)
        header.layout.addLayout(overall_row)

        self.report_layout.addWidget(header)

        # Metric tiles grid
        grid = QGridLayout()
        grid.setSpacing(14)
        tiles = [
            ("Token Count", f"{r.token_count:,}", r.tokenizer_mode, None),
            ("Word Count", f"{r.word_count:,}", f"{r.sentence_count} sentences", None),
            ("Prompt Efficiency", f"{r.prompt_efficiency:.0f}", "tokens used per idea expressed", theme.score_color(r.prompt_efficiency)),
            ("Verbosity", f"{r.verbosity_score:.0f}", "higher = more bloated", theme.score_color(100 - r.verbosity_score)),
        ]
        for i, (title, val, cap, accent) in enumerate(tiles):
            tile = MetricTile(title, val, cap, accent)
            grid.addWidget(tile, 0, i)
        grid_wrap = QWidget()
        grid_wrap.setLayout(grid)
        self.report_layout.addWidget(grid_wrap)

        # Score bars card
        scores_card = Card()
        scores_title = QLabel("QUALITY SCORES")
        scores_title.setProperty("class", "cardTitle")
        scores_card.layout.addWidget(scores_title)
        scores_card.layout.addWidget(ScoreBar("Clarity", r.clarity_score))
        scores_card.layout.addWidget(ScoreBar("Structure", r.structure_score))
        scores_card.layout.addWidget(ScoreBar("Prompt Efficiency", r.prompt_efficiency))
        scores_card.layout.addWidget(
            ScoreBar("Hallucination Risk", r.hallucination_risk)
        )
        self.report_layout.addWidget(scores_card)

        # Repeated phrases
        if r.repeated_phrases:
            rep_card = Card()
            rep_title = QLabel("REPEATED WORDING")
            rep_title.setProperty("class", "cardTitle")
            rep_card.layout.addWidget(rep_title)
            for phrase, count in r.repeated_phrases:
                row = QHBoxLayout()
                p = QLabel(f"“{phrase}”")
                p.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:12.5px;")
                c = Badge(f"×{count}", theme.WARNING)
                row.addWidget(p)
                row.addStretch()
                row.addWidget(c)
                row_wrap = QWidget()
                row_wrap.setLayout(row)
                rep_card.layout.addWidget(row_wrap)
            self.report_layout.addWidget(rep_card)

        # Logic failures
        if r.logic_failures:
            logic_card = Card()
            logic_title = QLabel(f"LOGIC FAILURES ({len(r.logic_failures)})")
            logic_title.setProperty("class", "cardTitle")
            logic_card.layout.addWidget(logic_title)
            for issue in r.logic_failures:
                logic_card.layout.addWidget(
                    IssueRow(issue["type"], issue["location"], issue["detail"],
                             issue.get("excerpt", ""), color=theme.DANGER)
                )
            self.report_layout.addWidget(logic_card)
        else:
            self._add_clean_badge("No logic failures detected.")

        # Inconsistencies
        if r.inconsistencies:
            inc_card = Card()
            inc_title = QLabel(f"INCONSISTENCIES ({len(r.inconsistencies)})")
            inc_title.setProperty("class", "cardTitle")
            inc_card.layout.addWidget(inc_title)
            for issue in r.inconsistencies:
                inc_card.layout.addWidget(
                    IssueRow(issue["type"], issue["location"], issue["detail"],
                             issue.get("excerpt", ""), color=theme.WARNING)
                )
            self.report_layout.addWidget(inc_card)

        # Hallucination flags
        if r.hallucination_flags:
            hal_card = Card()
            hal_title = QLabel("HALLUCINATION RISK INDICATORS")
            hal_title.setProperty("class", "cardTitle")
            hal_card.layout.addWidget(hal_title)
            for flag in r.hallucination_flags:
                lbl = QLabel(f"•  {flag}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px;")
                hal_card.layout.addWidget(lbl)
            self.report_layout.addWidget(hal_card)

        self.report_layout.addSpacing(6)

    def _add_clean_badge(self, text: str):
        card = Card(flat=True)
        row = QHBoxLayout()
        dot = QLabel("✓")
        dot.setStyleSheet(f"color:{theme.SUCCESS}; font-size:14px; font-weight:800;")
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12.5px;")
        row.addWidget(dot)
        row.addSpacing(6)
        row.addWidget(lbl)
        row.addStretch()
        card.layout.addLayout(row)
        self.report_layout.addWidget(card)
