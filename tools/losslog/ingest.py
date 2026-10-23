"""敗戦ログの取り込み。ページ（template.html）の「書き出し」を貼ったテキストを受け取り、
logs/losses/<日付>-<連勝>.md に保存して、要約を表示する。

  cd battle-tower/tools/losslog && python3 ingest.py <貼り付けたテキストのファイル>
  python3 ingest.py -            # 標準入力から

末尾の ```json ブロック（v:1）を正とし、本文（人が読む用）はそのまま保存する。
同じ日付・連勝のファイルがあれば上書きせず -2, -3 … を付ける。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.normpath(os.path.join(HERE, '..', '..', 'logs', 'losses'))


def parse(text):
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S)
    if not m:
        sys.exit('json ブロックが見つからない（ページの「書き出し」を末尾まで貼る）')
    data = json.loads(m.group(1))
    if data.get('v') != 1:
        sys.exit(f'未知の形式 v={data.get("v")}')
    body = text[:m.start()].rstrip()
    return data, body


def filename(data):
    streak = re.sub(r'\D', '', str(data.get('streak') or '')) or 'x'
    base = f"{data['date']}-{streak}"
    path = os.path.join(LOGS, base + '.md')
    n = 2
    while os.path.exists(path):
        path = os.path.join(LOGS, f'{base}-{n}.md'); n += 1
    return path


def summary(data):
    en = '、'.join(f"{e['slot']} {e['species'] or '?'}{'#' + str(e['set']) if e.get('set') else ''}" for e in data['enemies'])
    out = [f"{data['date']} {data['build']} {data.get('streak') or '?'}連勝 {data['result']}　先発 {'／'.join(data['lead'])}", f"敵: {en}"]
    for i, t in enumerate(data['turns'], 1):
        acts = '／'.join(f"{a['who']} {a['act']}" + (f"→{a['target']}" if a.get('target') else '') + (f"（{'・'.join(a['tags'])}）" if a.get('tags') else '') for a in t['acts'])
        out.append(f"T{i}: {acts}" + (f"　※{t['note']}" if t.get('note') else ''))
    if data.get('left'):
        out.append(f"残り: {data['left']}")
    if data.get('note'):
        out.append(f"所感: {data['note']}")
    return '\n'.join(out)


def main(argv):
    if not argv:
        print(__doc__); return 1
    text = sys.stdin.read() if argv[0] == '-' else open(argv[0], encoding='utf-8').read()
    data, body = parse(text)
    os.makedirs(LOGS, exist_ok=True)
    path = filename(data)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body + '\n\n```json\n' + json.dumps(data, ensure_ascii=False) + '\n```\n')
    print('saved:', os.path.relpath(path, os.path.join(HERE, '..', '..', '..')))
    print(summary(data))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
