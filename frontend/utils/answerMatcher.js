const WHITESPACE_REGEX = /\s+/g;
const TOKEN_SPLIT_REGEX = /[^0-9a-zA-Z가-힣]+/g;
const COMPACT_REGEX = /[^0-9a-zA-Z가-힣]+/g;
const NUMBER_REGEX = /[-+]?\d+(?:\.\d+)?/g;

const MATCH_PRIORITY = {
  exact: 5,
  compact: 4,
  number: 4,
  token: 4,
  similarity: 3,
  none: 0,
};

const normalizeText = (value = "") =>
  value
    .normalize("NFKC")
    .toLowerCase()
    .trim()
    .replace(WHITESPACE_REGEX, " ");

const compactText = (value = "") => value.replace(COMPACT_REGEX, "");

const splitAnswerCandidates = (answerField = "") => {
  const normalized = normalizeText(answerField);
  if (!normalized) return [];

  const seen = new Set();
  return normalized
    .split("/")
    .map((part) => normalizeText(part))
    .filter((part) => {
      if (!part || seen.has(part)) return false;
      seen.add(part);
      return true;
    });
};

const tokenize = (value = "") => value.split(TOKEN_SPLIT_REGEX).filter(Boolean);

const extractSingleNumber = (value = "") => {
  const matches = value.replace(/,/g, "").match(NUMBER_REGEX);
  if (!matches || matches.length !== 1) return null;
  const numeric = Number(matches[0]);
  return Number.isNaN(numeric) ? null : numeric;
};

const similarityThreshold = (length) => {
  if (length <= 3) return 1.0;
  if (length <= 5) return 0.8;
  if (length <= 8) return 0.75;
  return 0.72;
};

const levenshteinDistance = (a = "", b = "") => {
  const aLen = a.length;
  const bLen = b.length;
  if (aLen === 0) return bLen;
  if (bLen === 0) return aLen;

  const matrix = Array.from({ length: aLen + 1 }, () => Array(bLen + 1).fill(0));
  for (let i = 0; i <= aLen; i += 1) matrix[i][0] = i;
  for (let j = 0; j <= bLen; j += 1) matrix[0][j] = j;

  for (let i = 1; i <= aLen; i += 1) {
    for (let j = 1; j <= bLen; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  return matrix[aLen][bLen];
};

const similarityRatio = (a = "", b = "") => {
  const maxLength = Math.max(a.length, b.length);
  if (maxLength === 0) return 1;
  const distance = levenshteinDistance(a, b);
  return 1 - distance / maxLength;
};

const isAsciiWord = (value = "") => /^[a-z]+$/i.test(value);

const evaluateSingleAnswer = (userRaw = "", candidateRaw = "") => {
  const user = normalizeText(userRaw);
  const candidate = normalizeText(candidateRaw);
  const defaultResult = {
    accepted: false,
    matchType: "none",
    similarity: 0,
    threshold: null,
    matchedAnswer: candidateRaw,
  };
  if (!user || !candidate) return defaultResult;
  if (user === candidate) {
    return {
      accepted: true,
      matchType: "exact",
      similarity: 1,
      threshold: 1,
      matchedAnswer: candidateRaw,
    };
  }

  const userCompact = compactText(user);
  const candidateCompact = compactText(candidate);
  if (!userCompact || !candidateCompact) return defaultResult;
  if (userCompact === candidateCompact) {
    return {
      accepted: true,
      matchType: "compact",
      similarity: 1,
      threshold: 1,
      matchedAnswer: candidateRaw,
    };
  }

  const userNumber = extractSingleNumber(userCompact);
  const candidateNumber = extractSingleNumber(candidateCompact);
  if (userNumber !== null && candidateNumber !== null) {
    const accepted = Math.abs(userNumber - candidateNumber) <= 0.01;
    return {
      accepted,
      matchType: accepted ? "number" : "none",
      similarity: accepted ? 1 : 0,
      threshold: null,
      matchedAnswer: candidateRaw,
    };
  }

  const userTokens = tokenize(user);
  const candidateTokens = tokenize(candidate);
  if (
    userTokens.length > 0 &&
    candidateTokens.length > 0 &&
    userTokens.length === candidateTokens.length &&
    userTokens.every((token, index) => token === candidateTokens[index])
  ) {
    return {
      accepted: true,
      matchType: "token",
      similarity: 1,
      threshold: null,
      matchedAnswer: candidateRaw,
    };
  }

  const ratio = similarityRatio(userCompact, candidateCompact);
  const threshold = similarityThreshold(Math.max(userCompact.length, candidateCompact.length));
  if (ratio < threshold) {
    return {
      accepted: false,
      matchType: "none",
      similarity: ratio,
      threshold,
      matchedAnswer: candidateRaw,
    };
  }

  if (isAsciiWord(userCompact) && isAsciiWord(candidateCompact)) {
    if (candidateCompact.length <= 3) {
      return {
        accepted: false,
        matchType: "none",
        similarity: ratio,
        threshold,
        matchedAnswer: candidateRaw,
      };
    }
    const accepted =
      userCompact[0] === candidateCompact[0] &&
      userCompact[userCompact.length - 1] === candidateCompact[candidateCompact.length - 1];
    return {
      accepted,
      matchType: accepted ? "similarity" : "none",
      similarity: ratio,
      threshold,
      matchedAnswer: candidateRaw,
    };
  }

  return {
    accepted: true,
    matchType: "similarity",
    similarity: ratio,
    threshold,
    matchedAnswer: candidateRaw,
  };
};

const pickBestResult = (evaluations = []) => {
  if (evaluations.length === 0) {
    return {
      accepted: false,
      matchType: "none",
      similarity: 0,
      threshold: null,
      matchedAnswer: "",
    };
  }

  const acceptedList = evaluations.filter((item) => item.accepted);
  if (acceptedList.length > 0) {
    return acceptedList.sort((a, b) => {
      const priorityDiff = MATCH_PRIORITY[b.matchType] - MATCH_PRIORITY[a.matchType];
      if (priorityDiff !== 0) return priorityDiff;
      return b.similarity - a.similarity;
    })[0];
  }

  return evaluations.sort((a, b) => b.similarity - a.similarity)[0];
};

export const evaluateAnswer = (userAnswer = "", answerField = "") => {
  const user = normalizeText(userAnswer);
  if (!user) {
    return {
      accepted: false,
      userAnswer,
      normalizedUserAnswer: "",
      matchedAnswer: "",
      matchType: "none",
      similarity: 0,
      threshold: null,
      criteriaLabel: "미입력",
      usedTolerance: false,
    };
  }

  const candidates = splitAnswerCandidates(answerField);
  const evaluations = candidates.map((candidate) => evaluateSingleAnswer(user, candidate));
  const best = pickBestResult(evaluations);

  const criteriaLabel = {
    exact: "완전 일치",
    compact: "공백/기호 무시 일치",
    number: "숫자 오차 ±0.01",
    token: "토큰 단위 일치",
    similarity: `유사도 ${Math.round((best.threshold ?? 0) * 100)}% 이상`,
    none: "정답 기준 미충족",
  }[best.matchType];

  return {
    accepted: best.accepted,
    userAnswer,
    normalizedUserAnswer: user,
    matchedAnswer: best.matchedAnswer || "",
    matchType: best.matchType,
    similarity: best.similarity,
    threshold: best.threshold,
    criteriaLabel,
    usedTolerance: best.accepted && best.matchType !== "exact",
  };
};

export const isAnswerAccepted = (userAnswer = "", answerField = "") =>
  evaluateAnswer(userAnswer, answerField).accepted;
