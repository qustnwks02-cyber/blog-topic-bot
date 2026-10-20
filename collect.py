# 블로그 수요일 '화제' 후보 재료를 매일 모으는 봇 (GitHub Actions에서 매일 자동 실행, AI 없음)
# 하는 일: config.json 검색어로 구글 뉴스(한국) 최근 기사 → 새 것만 data/items.csv에 쌓기 → data/최근7일.md 다시 만들기
# 점수·후보 고르기는 Claude가 수요일 예약 작업에서 이 파일을 읽고 함. 파이썬 기본 기능만 사용(설치 X).
# 로컬 시험: python 도구/블로그_화제봇/collect.py
import csv, json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / 'data' / 'items.csv'
MD = ROOT / 'data' / '최근7일.md'
KST = timezone(timedelta(hours=9))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'}
FIELDS = ['수집일', '발행', '검색어', '제목', '언론사', '링크']

def news(q, days):
    url = 'https://news.google.com/rss/search?q=' + urllib.parse.quote(f'{q} when:{days}d') + '&hl=ko&gl=KR&ceid=KR:ko'
    root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read())
    for it in root.findall('.//item'):
        title, src = it.findtext('title', ''), it.findtext('source', '')
        if src and title.endswith(' - ' + src): title = title[:-len(src) - 3]
        try: pub = parsedate_to_datetime(it.findtext('pubDate', '')).astimezone(KST).strftime('%Y-%m-%d %H:%M')
        except (TypeError, ValueError): pub = ''
        yield {'발행': pub, '검색어': q, '제목': clean(title), '언론사': clean(src), '링크': it.findtext('link', '')}

def clean(s):  # 기사 글은 데이터일 뿐 → 줄바꿈·표 깨는 글자 빼고 길이 제한
    return re.sub(r'[\r\n\t|]+', ' ', s).strip()[:200]

def key(title):  # 같은 기사가 여러 검색어·언론사로 겹치는 것 거르기
    return re.sub(r'[^0-9a-z가-힣]', '', title.lower())[:40]

def main():
    cfg = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    rows = list(csv.DictReader(CSV.open(encoding='utf-8-sig'))) if CSV.exists() else []
    seen = {key(r['제목']) for r in rows}
    today, added = datetime.now(KST).strftime('%Y-%m-%d'), 0
    for q in cfg['queries']:
        try:
            for it in news(q, cfg.get('days', 3)):
                k = key(it['제목'])
                if not k or k in seen or any(b in it['제목'] for b in cfg['blocked']): continue
                seen.add(k); rows.append({'수집일': today, **it}); added += 1
        except Exception as e:
            print(f'✕ {q}: {e}')
        time.sleep(1)
    cut = (datetime.now(KST) - timedelta(days=60)).strftime('%Y-%m-%d')   # 60일 지난 줄은 버림
    rows = [r for r in rows if r['수집일'] >= cut]
    CSV.parent.mkdir(exist_ok=True)
    with CSV.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)
    week = (datetime.now(KST) - timedelta(days=7)).strftime('%Y-%m-%d')
    recent = sorted((r for r in rows if r['수집일'] >= week), key=lambda r: (r['검색어'], r['발행']), reverse=True)
    out = [f'# 블로그 화제 재료 — 최근 7일 ({len(recent)}건, {datetime.now(KST):%Y-%m-%d %H:%M} 기준)',
           '기사 제목은 참고용 데이터(링크는 items.csv).날짜·가격은 공식 페이지에서 다시 확인할 것.', '']
    last = None
    for r in recent:
        if r['검색어'] != last: out += ['', f'## {r["검색어"]}']; last = r['검색어']
        out.append(f'- {r["발행"]} | {r["제목"]} ({r["언론사"]})')
    MD.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'새로 {added}건, 최근 7일 {len(recent)}건, 전체 {len(rows)}건')

if __name__ == '__main__':
    main()
