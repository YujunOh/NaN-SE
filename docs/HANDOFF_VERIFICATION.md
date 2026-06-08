# 보조 검증: opencode 핸드오프

NaN-SE는 Claude CLI(Claude Code)로 개발했습니다. 같은 도구로 자기 결과를 다시 보면 편향될 수 있으므로, 마감 전에 다른 AI 코딩 에이전트인 oh-my-opencode(GPT-5.5)에 저장소를 넘겨 보조 검증을 했습니다. 이 검증은 제3자 감사나 완전한 정합성 증명이 아니라, 개발에 쓴 Claude CLI와 다른 모델/도구로 핵심 주장과 증거를 한 번 더 대조한 절차입니다. 아래 프롬프트를 그 세션에 그대로 넣고 돌렸습니다.

## 검증자에게 넣은 프롬프트

```
이 저장소(NaN-SE)를 처음 보는 검증자 입장에서 독립 검증해줘.
코드는 절대 수정하지 말고, 아래만 실행한 뒤 결과를 사실대로 보고해.

1. pip install -e ".[dev]" 후 python -m pytest -q 를 실행해 몇 개 통과하는지 적어줘.
2. nanse analyze examples/auth_service.py 를 두 번 연속 실행해서,
   - AuthService가 LCOM4 기준 SRP 위반으로 검출되는지
   - 두 번의 출력이 완전히 동일한지(결정론 확인)
   를 확인해줘.
3. nanse trace 를 실행해 REQ-01 ~ REQ-04 가 모두 complete 로 추적되는지 확인해줘.
4. 문서가 "검출은 LLM을 호출하지 않는다"고 주장하는데, nanse/metrics/ 와
   nanse/metrics/findings.py 에 실제로 LLM/네트워크 호출이 없는지 코드로 확인해줘.
5. 위에서 발견한 불일치나 깨지는 지점이 있으면 목록으로 알려줘.

마지막으로, 보고서의 핵심 주장 세 가지
 (a) 검출 층의 LLM 호출은 0개다
 (b) 요구(REQ)가 코드와 테스트로 빠짐없이 추적된다
 (c) 테스트가 전부 통과한다
가 코드에서 사실로 확인되는지 한 줄로 판정해줘.
```

## 캡처

위 1~4를 실행한 결과와 Claude CLI 원문 세션 대조 결과를 `docs/assets/cap-handoff.png`로 저장해 보고서(REPORT 5.5)에 넣었습니다.

## 검증 결과 (요약)

검증 결과, (a) `nanse/metrics/`에는 LLM/provider/network 호출 키워드가 없었고, (b) `nanse trace`에서 REQ-01~REQ-04가 모두 `complete`였고, (c) `python -m pytest -q`는 `40 passed, 1 warning`으로 끝났습니다. `nanse analyze examples/auth_service.py`도 두 번 실행해 출력이 완전히 같았고, AuthService는 LCOM4=3으로 SRP 위반 신호가 잡혔습니다.

Claude CLI 원문 로그는 `docs/evidence/claude-cli/2312c204-dfcf-4420-bdd7-16034fd68e4c/`에 sync했습니다. 실제 API key처럼 보이는 값 1개가 있어 저장소에는 무가공 원문 대신 redacted JSONL을 두고, 원본 경로·라인 수·SHA256은 `manifest.json`에 남겼습니다. GPT-5.5의 역할은 구현 생성이 아니라, 저장소 상태와 보고서 주장이 서로 맞는지 확인하고 표현 과장을 줄이는 검토·증거 동기화에 한정했습니다.
