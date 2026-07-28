"""
AI Token Auditor - Core Analysis Engine
-----------------------------------------
Pure-logic, offline-capable auditing of AI prompts/responses.
No network calls are made here; everything is computed locally so the
audit itself never depends on connectivity (only the app shell does).
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass, field
from collections import Counter
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# Optional precise tokenizer. Falls back gracefully if tiktoken isn't
# installed, so the app never crashes because of a missing dependency.
# ---------------------------------------------------------------------------
try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        if not text:
            return 0
        return len(_ENC.encode(text))

    TOKENIZER_MODE = "tiktoken (cl100k_base)"
except Exception:  # pragma: no cover - fallback path
    _ENC = None

    def count_tokens(text: str) -> int:
        """Approximate GPT-style token count: ~4 chars/token, word-aware."""
        if not text:
            return 0
        words = re.findall(r"\S+", text)
        approx = 0
        for w in words:
            approx += max(1, math.ceil(len(w) / 4))
        return approx

    TOKENIZER_MODE = "heuristic estimate (~4 chars/token)"


FILLER_WORDS = {
    "basically", "actually", "essentially", "literally", "really", "very",
    "just", "simply", "obviously", "clearly", "of course", "in fact",
    "needless to say", "as we know", "it goes without saying",
}

UNSUPPORTED_CLAIM_MARKERS = [
    "everyone knows", "it is well known", "obviously", "clearly the best",
    "studies show", "research proves", "experts agree", "always true",
    "never fails", "100% guaranteed", "undeniably", "without question",
]

CONTRADICTION_CONNECTORS = [
    "however", "but", "on the other hand", "although", "yet", "despite",
    "conversely", "in contrast", "whereas",
]

HALLUCINATION_MARKERS = [
    "according to a study", "a recent report", "scientists found",
    "as reported by", "cited in", "published in", "official statistics show",
    "government data indicates",
]

HEDGE_WORDS = {"might", "could", "may", "possibly", "perhaps", "likely", "seems"}

PASSIVE_PATTERN = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE
)


def _sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


@dataclass
class AuditResult:
    model_name: str
    token_count: int
    tokenizer_mode: str
    word_count: int
    sentence_count: int
    prompt_efficiency: float          # 0-100
    verbosity_score: float            # 0-100 (higher = more verbose/bloated)
    repeated_phrases: List[Tuple[str, int]]
    logic_failures: List[Dict[str, str]]
    inconsistencies: List[Dict[str, str]]
    hallucination_risk: float         # 0-100
    hallucination_flags: List[str]
    clarity_score: float              # 0-100
    structure_score: float            # 0-100
    overall_score: float              # 0-100
    grade: str
    summary: str


def _repeated_phrases(words: List[str]) -> List[Tuple[str, int]]:
    found: Counter = Counter()
    for n in (2, 3, 4):
        grams = _ngrams(words, n)
        c = Counter(grams)
        for phrase, count in c.items():
            if count > 1 and len(phrase.split()) >= 2:
                found[phrase] = max(found[phrase], count)
    # Keep the most significant repeats, drop tiny/trivial overlaps
    ranked = sorted(found.items(), key=lambda x: (-x[1], -len(x[0])))
    deduped: List[Tuple[str, int]] = []
    seen_spans = []
    for phrase, count in ranked:
        if any(phrase in s or s in phrase for s in seen_spans):
            continue
        seen_spans.append(phrase)
        deduped.append((phrase, count))
    return deduped[:8]


def _detect_logic_failures(sentences: List[str]) -> List[Dict[str, str]]:
    issues = []
    for i, sent in enumerate(sentences):
        low = sent.lower()

        for marker in UNSUPPORTED_CLAIM_MARKERS:
            if marker in low:
                issues.append({
                    "type": "Unsupported Claim",
                    "location": f"Sentence {i + 1}",
                    "detail": f"Asserts certainty (\"{marker}\") without evidence or citation.",
                    "excerpt": sent[:140],
                })
                break

        if low.startswith(("therefore", "thus", "so,")) and i == 0:
            issues.append({
                "type": "Missing Premise",
                "location": f"Sentence {i + 1}",
                "detail": "Draws a conclusion before any supporting premise is introduced.",
                "excerpt": sent[:140],
            })

        if re.search(r"\b(all|every|none|always|never)\b", low) and not re.search(
            r"\b(most|often|typically|generally|usually)\b", low
        ):
            issues.append({
                "type": "Overgeneralization",
                "location": f"Sentence {i + 1}",
                "detail": "Uses an absolute quantifier (all/none/always/never) that is rarely defensible without qualification.",
                "excerpt": sent[:140],
            })

    # Contradiction check: connector sentence following a numeric claim that
    # conflicts with an earlier numeric claim about the same rough subject.
    numeric_claims = []
    for i, sent in enumerate(sentences):
        nums = re.findall(r"\b\d+(?:\.\d+)?%?\b", sent)
        if nums:
            numeric_claims.append((i, sent, nums))

    for j in range(1, len(numeric_claims)):
        i0, s0, n0 = numeric_claims[j - 1]
        i1, s1, n1 = numeric_claims[j]
        if set(n0) and set(n1) and set(n0) != set(n1):
            shared_words = set(_words(s0)[:6]) & set(_words(s1)[:6])
            if len(shared_words) >= 2:
                issues.append({
                    "type": "Possible Numeric Inconsistency",
                    "location": f"Sentences {i0 + 1} & {i1 + 1}",
                    "detail": f"Differing figures ({', '.join(n0)} vs {', '.join(n1)}) referenced for what appears to be the same subject.",
                    "excerpt": f"{s0[:70]}... / {s1[:70]}...",
                })

    return issues[:10]


def _detect_inconsistencies(text: str, sentences: List[str]) -> List[Dict[str, str]]:
    issues = []
    connector_hits = 0
    for i, sent in enumerate(sentences):
        low = sent.lower()
        for c in CONTRADICTION_CONNECTORS:
            if low.startswith(c) or f" {c} " in low:
                connector_hits += 1
                break
    if connector_hits >= max(2, len(sentences) // 4) and len(sentences) > 3:
        issues.append({
            "type": "Frequent Reversals",
            "location": "Overall response",
            "detail": f"{connector_hits} contrast/contradiction connectors detected relative to {len(sentences)} sentences — the argument may be flip-flopping rather than building a clear line of reasoning.",
            "excerpt": "",
        })

    # Yes/no flip detection
    if re.search(r"\byes\b", text, re.IGNORECASE) and re.search(r"\bno\b", text, re.IGNORECASE):
        yes_idx = [i for i, s in enumerate(sentences) if re.search(r"\byes\b", s, re.IGNORECASE)]
        no_idx = [i for i, s in enumerate(sentences) if re.search(r"\bno\,?\b", s, re.IGNORECASE)]
        if yes_idx and no_idx and abs(yes_idx[0] - no_idx[0]) <= 3:
            issues.append({
                "type": "Direct Answer Conflict",
                "location": f"Sentences {yes_idx[0] + 1} & {no_idx[0] + 1}",
                "detail": "A 'yes' and a 'no' appear close together, suggesting the response may be answering its own question inconsistently.",
                "excerpt": "",
            })

    return issues


def _hallucination_risk(text: str, sentences: List[str]) -> Tuple[float, List[str]]:
    flags = []
    hits = 0
    for marker in HALLUCINATION_MARKERS:
        if marker in text.lower():
            hits += 1
            flags.append(f"Vague authority reference: \"{marker}\" — no verifiable source named.")

    specific_numbers = re.findall(r"\b\d{1,4}(?:,\d{3})*(?:\.\d+)?%?\b", text)
    unique_numbers = set(specific_numbers)
    if len(unique_numbers) > max(4, len(sentences) // 2):
        hits += 1
        flags.append(f"High density of specific numbers ({len(unique_numbers)} unique values) with no cited source — verify each figure.")

    fake_citation = re.findall(r"\([A-Z][a-z]+(?:\s(?:&|and)\s[A-Z][a-z]+)?,?\s*(?:19|20)\d{2}\)", text)
    if fake_citation:
        flags.append(f"{len(fake_citation)} inline citation(s) formatted like academic references — confirm these sources actually exist.")
        hits += len(fake_citation)

    hedges = sum(1 for w in _words(text) if w in HEDGE_WORDS)
    confident_absolutes = len(re.findall(r"\b(definitely|certainly|guaranteed|proven fact)\b", text, re.IGNORECASE))
    if confident_absolutes and hedges == 0:
        flags.append("Confident/absolute language used throughout with zero hedging — often correlates with unverified generation.")
        hits += 1

    risk = min(100.0, hits * 14.0)
    return risk, flags[:8]


def _clarity_score(sentences: List[str], words: List[str]) -> float:
    if not sentences:
        return 0.0
    avg_len = sum(len(_words(s)) for s in sentences) / len(sentences)
    # Sweet spot ~ 14-20 words/sentence
    len_penalty = min(40.0, abs(avg_len - 17) * 2.2)

    passive_hits = len(PASSIVE_PATTERN.findall(" ".join(sentences)))
    passive_ratio = passive_hits / max(1, len(sentences))
    passive_penalty = min(25.0, passive_ratio * 60)

    filler_hits = sum(1 for w in words if w in FILLER_WORDS)
    filler_ratio = filler_hits / max(1, len(words))
    filler_penalty = min(20.0, filler_ratio * 400)

    score = 100 - len_penalty - passive_penalty - filler_penalty
    return round(max(0.0, min(100.0, score)), 1)


def _structure_score(text: str, sentences: List[str]) -> float:
    score = 55.0
    if re.search(r"^\s*#{1,6}\s", text, re.MULTILINE):
        score += 12
    if re.search(r"^\s*[-*•]\s", text, re.MULTILINE):
        score += 12
    if re.search(r"^\s*\d+[\.\)]\s", text, re.MULTILINE):
        score += 10
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        score += 8
    if len(sentences) > 0:
        first, last = sentences[0].lower(), sentences[-1].lower()
        if any(w in first for w in ("first", "to begin", "overview", "let's", "here")):
            score += 4
        if any(w in last for w in ("summary", "conclusion", "overall", "in short", "to sum")):
            score += 4
    return round(max(0.0, min(100.0, score)), 1)


def _prompt_efficiency(token_count: int, word_count: int, sentence_count: int) -> float:
    if word_count == 0:
        return 0.0
    tok_per_word = token_count / word_count
    # Efficient English text is usually ~1.2-1.4 tokens/word.
    efficiency = 100 - min(60.0, max(0.0, (tok_per_word - 1.3) * 120))
    if sentence_count and (word_count / sentence_count) > 35:
        efficiency -= 10  # run-on sentences waste tokens
    return round(max(0.0, min(100.0, efficiency)), 1)


def _verbosity_score(words: List[str], sentences: List[str], repeated: List[Tuple[str, int]]) -> float:
    if not sentences:
        return 0.0
    avg_len = sum(len(_words(s)) for s in sentences) / len(sentences)
    length_component = min(50.0, max(0.0, (avg_len - 18) * 2.5))
    filler_hits = sum(1 for w in words if w in FILLER_WORDS)
    filler_component = min(25.0, (filler_hits / max(1, len(words))) * 500)
    repetition_component = min(25.0, sum(c for _, c in repeated) * 1.5)
    return round(min(100.0, length_component + filler_component + repetition_component), 1)


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def run_audit(text: str, model_name: str) -> AuditResult:
    text = text or ""
    sentences = _sentences(text)
    words = _words(text)

    token_count = count_tokens(text)
    word_count = len(words)
    sentence_count = len(sentences)

    repeated = _repeated_phrases(words)
    logic_failures = _detect_logic_failures(sentences)
    inconsistencies = _detect_inconsistencies(text, sentences)
    halluc_risk, halluc_flags = _hallucination_risk(text, sentences)
    clarity = _clarity_score(sentences, words)
    structure = _structure_score(text, sentences)
    efficiency = _prompt_efficiency(token_count, word_count, sentence_count)
    verbosity = _verbosity_score(words, sentences, repeated)

    penalty = (
        len(logic_failures) * 4
        + len(inconsistencies) * 5
        + (halluc_risk * 0.25)
        + (verbosity * 0.15)
    )
    base = (clarity * 0.30) + (structure * 0.25) + (efficiency * 0.25) + (max(0, 100 - verbosity) * 0.20)
    overall = max(0.0, min(100.0, base - penalty))
    overall = round(overall, 1)
    grade = _grade(overall)

    issues_total = len(logic_failures) + len(inconsistencies)
    if issues_total == 0 and halluc_risk < 15:
        summary = (
            f"Clean pass. No structural logic failures or contradictions detected. "
            f"Hallucination risk is low ({halluc_risk:.0f}/100). "
            f"Token usage looks {'efficient' if efficiency >= 70 else 'moderate'}."
        )
    else:
        summary = (
            f"{issues_total} reasoning issue(s) flagged and hallucination risk at "
            f"{halluc_risk:.0f}/100. "
            f"{'Verbosity is elevated — trimming filler could cut token cost.' if verbosity >= 50 else 'Verbosity is within a reasonable range.'}"
        )

    return AuditResult(
        model_name=model_name or "Unspecified Model",
        token_count=token_count,
        tokenizer_mode=TOKENIZER_MODE,
        word_count=word_count,
        sentence_count=sentence_count,
        prompt_efficiency=efficiency,
        verbosity_score=verbosity,
        repeated_phrases=repeated,
        logic_failures=logic_failures,
        inconsistencies=inconsistencies,
        hallucination_risk=halluc_risk,
        hallucination_flags=halluc_flags,
        clarity_score=clarity,
        structure_score=structure,
        overall_score=overall,
        grade=grade,
        summary=summary,
    )
