import re
import unicodedata
from difflib import SequenceMatcher
from typing import List


_WHITESPACE_RE = re.compile(r"\s+")
_TOKEN_SPLIT_RE = re.compile(r"[^0-9a-zA-Z가-힣]+")
_COMPACT_RE = re.compile(r"[^0-9a-zA-Z가-힣]+")
_NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def normalize_text(value: str) -> str:
    """사용자 입력/정답 텍스트를 비교 가능한 형태로 정규화합니다."""
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return _WHITESPACE_RE.sub(" ", normalized)


def split_answer_candidates(answer_field: str) -> List[str]:
    """DB answer 컬럼(`/` 구분)을 개별 정답 후보로 분리합니다."""
    normalized = normalize_text(answer_field)
    if not normalized:
        return []

    candidates: List[str] = []
    for part in normalized.split("/"):
        candidate = normalize_text(part)
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def is_answer_accepted(user_answer: str, answer_field: str) -> bool:
    """허용 오차를 반영한 정답 판정."""
    user = normalize_text(user_answer)
    if not user:
        return False

    for candidate in split_answer_candidates(answer_field):
        if _is_single_answer_match(user, candidate):
            return True
    return False


def _is_single_answer_match(user: str, candidate: str) -> bool:
    if user == candidate:
        return True

    user_compact = _compact(user)
    candidate_compact = _compact(candidate)
    if not user_compact or not candidate_compact:
        return False

    if user_compact == candidate_compact:
        return True

    # 숫자형 답변은 엄격하게 비교하되, 소수 오차는 소폭 허용
    user_number = _extract_single_number(user_compact)
    candidate_number = _extract_single_number(candidate_compact)
    if user_number is not None and candidate_number is not None:
        return abs(user_number - candidate_number) <= 0.01

    user_tokens = _tokenize(user)
    candidate_tokens = _tokenize(candidate)
    if user_tokens and candidate_tokens and user_tokens == candidate_tokens:
        return True

    similarity = SequenceMatcher(None, user_compact, candidate_compact).ratio()
    threshold = _similarity_threshold(max(len(user_compact), len(candidate_compact)))
    if similarity < threshold:
        return False

    # 짧은 영문 단어는 양 끝 문자가 같은 경우만 오타 허용
    if _is_ascii_word(user_compact) and _is_ascii_word(candidate_compact):
        if len(candidate_compact) <= 3:
            return False
        return user_compact[0] == candidate_compact[0] and user_compact[-1] == candidate_compact[-1]

    return True


def _compact(value: str) -> str:
    return _COMPACT_RE.sub("", value)


def _tokenize(value: str) -> List[str]:
    return [token for token in _TOKEN_SPLIT_RE.split(value) if token]


def _extract_single_number(value: str) -> float | None:
    matches = _NUMBER_RE.findall(value.replace(",", ""))
    if len(matches) != 1:
        return None
    try:
        return float(matches[0])
    except ValueError:
        return None


def _similarity_threshold(length: int) -> float:
    if length <= 3:
        return 1.0
    if length <= 5:
        return 0.8
    if length <= 8:
        return 0.75
    return 0.72


def _is_ascii_word(value: str) -> bool:
    return value.isascii() and value.isalpha()
