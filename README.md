# 블로그 화제봇

블로그 수요일 '화제' 글 후보를 고를 재료를 매일 모으는 봇이에요. GitHub가 매일 한국 시간 06:00에 대신 돌려 줘서 컴퓨터를 꺼 둬도 돼요.

- 모으는 것: `config.json`에 적은 검색어(한정판·러닝화·팝업·티켓 오픈·마라톤 접수 등)로 찾은 구글 뉴스(한국) 기사 제목
- 버리는 것: 제목에 축제·열애·논란·도박 같은 단어가 있는 기사, 이미 모은 기사, 60일 지난 기사
- 결과: `data/items.csv`(전체, 링크 포함), `data/최근7일.md`(수요일에 Claude가 읽는 요약)
- AI·API 키 없음. 점수는 수요일 예약 작업(`blog-topic-memo`)에서 Claude가 블로그 규칙으로 매겨요.

## 결과 주소
GitHub에 올린 뒤 적기: `https://raw.githubusercontent.com/qustnwks02-cyber/blog-topic-bot/main/data/최근7일.md`

## 고치기
- 검색어 추가·삭제: `config.json`의 `queries`, 거를 단어는 `blocked`
- 로컬 시험: `python 도구/블로그_화제봇/collect.py`
- 드라이브에서 고친 뒤 GitHub 저장소에도 다시 올려야 봇에 반영돼요.
