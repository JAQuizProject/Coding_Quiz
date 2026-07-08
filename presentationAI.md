
  최종 추천 주제
  Agentic AI를 우리 회사 업무에 붙이는 현실적인 방법:
  공고 문서를 AI가 읽고, 검증 가능한 draft 데이터로 바꾸기

  이렇게 잡으면 요즘 뜨는 AI Agent 흐름과 연결되면서도, 뜬구름이 아닙니다. 우리 코드에도 이미 bidding AI draft가 있어서 발표 데모가 가능합니다.

  왜 이게 핫한 주제랑 연결되냐면

  - Stack Overflow 2025 조사에서 개발자 84%가 AI 도구를 쓰거나 쓸 계획이고, 전문 개발자 51%는 매일 사용합니다. 그런데 AI 출력 정확도를 불신하는 비율도 46%라서 “AI를 어떻게 검증할 것인가”가
    핵심입니다. Stack Overflow Survey (https://survey.stackoverflow.co/2025/ai)

  - 요즘 기업 AI 키워드는 Agentic AI인데, 최근 리포트/기사들은 공통적으로 “도입은 빠른데 거버넌스와 검증이 부족하다”는 쪽을 말합니다. 즉, AI가 행동하기 전에 권한, 승인, 로그, 복구 가능성이
    필요합니다. TechRadar (https://www.techradar.com/pro/agentic-ai-adoption-outpaces-governance-in-regulated-industries)

  - OpenAI도 단순 JSON mode보다 JSON Schema를 따르게 하는 Structured Outputs를 권장합니다. 이건 우리 기능에서 json_object 응답을 더 안전한 계약 기반 출력으로 발전시키는 포인트가 됩니다. OpenAI
    Structured Outputs (https://platform.openai.com/docs/guides/structured-outputs)

  - 운영 관점에서는 Langfuse 같은 LLM observability 도구들이 prompt, response, token, latency, cost, tool/retrieval step 추적을 강조합니다. 발표 후반에 “AI API도 운영 대상이다”로 자연스럽게
    연결됩니다. Langfuse Observability (https://langfuse.com/docs/observability/overview)

  - MCP도 핫하지만 메인 주제로 잡기엔 아직 추상적입니다. 대신 “다음 단계: AI가 내부 DB/문서/툴에 안전하게 연결되는 표준” 정도로만 언급하면 좋습니다. MCP 공식 문서
    (https://modelcontextprotocol.io/docs/getting-started/intro), Anthropic MCP 소개 (https://www.anthropic.com/news/model-context-protocol)

  발표 제목 후보

  1. AI Agent 시대, 백엔드는 무엇을 검증해야 하나: 공고 문서 AI Draft 자동화 사례
  2. AI가 만든 값을 바로 저장해도 될까? 공고 문서 자동 입력으로 보는 실무형 AI 백엔드 설계
  3. 챗봇 말고 업무 자동화: 공고 문서를 draft 데이터로 바꾸는 AI 파이프라인

  내 픽은 2번입니다. 비개발자도 이해하고, 개발자에게는 구조적으로 말할 거리가 있습니다.

  발표 흐름

  1. 요즘 AI 트렌드: Agentic AI, Structured Outputs, Observability
  2. 하지만 기업 AI 실패 원인은 모델보다 “업무 흐름에 못 붙는 것”
  3. 우리 문제: 공고 작성은 문서 기반 입력이 많고 step이 복잡하다
  4. 해결 방식: 문서 업로드 → AI preview → normalizer → Pydantic/enum 검증 → 저장 가능한 step만 draft 반영
  5. 핵심 정책: AI 출력은 정답이 아니라 후보값
  6. 결과 분류: APPLIED, REVIEW_REQUIRED, FAILED
  7. 운영 체크포인트: token/cost/latency/schema_valid/retry/error log
  8. 다음 단계: Structured Outputs 전환, eval set, MCP 기반 내부 도구 연결

  데모는 이렇게 작게 가면 됩니다

  - /v1/bidding/draft/ai/preview: DB 저장 없이 AI 후보 JSON 확인
  - /v1/bidding/draft/ai/apply: 저장 가능한 step만 반영
  - PROJECT_OVERVIEW는 필수값이 부족하면 REVIEW_REQUIRED
  - SUBMISSION_MATERIALS처럼 안전한 기본값은 APPLIED
  - 기존 draft 저장 정책을 우회하지 않는다는 점 강조

  한 줄로 정리하면:

  > 요즘 핫한 Agentic AI를 “AI가 다 해준다”로 말하지 말고, “AI가 업무 후보를 만들고 백엔드가 검증·분류·저장·감사한다”로 가져가면 실무 발표로 훨씬 강합니다.
