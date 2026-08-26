## 全mdの「| #id | 種族 | 持ち物 | 技... |」形式の表行を frontier_sets.csv と全項目(種族/持ち物/技)突合する。
## 技は「注目技」列である場合が多く部分列挙が正式仕様なので、リストされた技が"真の4技の部分集合"かのみ検証する
## （リストが4件かつ真データと一致数<4なら="非部分集合"として即フラグ）。種族/持ち物は完全一致必須。
import csv, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from jpnames import JPM, JPI, JPS

rows = list(csv.DictReader(open('../../data/frontier_sets.csv')))
BY_ID = {}
for r in rows:
    moves = set(JPM.get(r[f'move{i}'].upper().replace(' ', '_').replace("'", ''), r[f'move{i}']) for i in range(1, 5))
    item_jp = JPI.get(r['item'], r['item']) if r['item'] and r['item'] != 'None' else 'なし'
    BY_ID[r['set_id']] = dict(species=JPS.get(r['species'], r['species']), item=item_jp, moves=moves)

# 略記正規化（ドキュメント全体で確立された慣用表記）
ABBR = {
    'シャドボ': 'シャドーボール', 'ギガドレ': 'ギガドレイン', '10まん': '10まんボルト',
    'こんらん光線': 'あやしいひかり', '電磁波': 'でんじは', '炎P': 'ほのおのパンチ',
    '冷P': 'れいとうパンチ', '冷B': 'れいとうビーム', 'サイキネ': 'サイコキネシス',
    'すてみタックル': 'すてみタックル', 'こだわりハチマキ': 'こだわりハチマキ',
    'めざ氷': 'めざめるパワー', 'めざ岩': 'めざめるパワー', 'めざ': 'めざめるパワー',
    'オバヒ': 'オーバーヒート', 'コメパン': 'コメットパンチ', 'じわれ': 'じわれ',
    'ふぶき': 'ふぶき', 'カゴ': 'カゴのみ', 'ラム': 'ラムのみ', 'QC': 'せんせいのツメ',
    'たべのこし': 'たべのこし', 'ひかりのこな': 'ひかりのこな', 'きあいのハチマキ': 'きあいのハチマキ',
    'ヒメリ': 'ヒメリのみ', 'クラボ': 'クラボのみ', 'モモン': 'モモンのみ', 'キー': 'キーのみ',
    'チーゴ': 'チーゴのみ', 'ナナシ': 'ナナシのみ', 'カムラ': 'カムラのみ', 'オボン': 'オボンのみ',
    'おうじゃ': 'おうじゃのしるし', 'しろいハーブ': 'しろいハーブ', 'メンタル': 'メンタルハーブ',
}
AMBIGUOUS_TOKENS = {'パンチ系', '確1', '確定', 'まもる持ち', 'ふしぎなまもり'}

def norm_move(tok):
    tok = tok.strip('*＊ ')
    return ABBR.get(tok, tok)

PAT_ROW = re.compile(r'^\|\s*#([\d#/\-]+)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|')

def expand_ids(idstr):
    out = []
    for part in idstr.split('/'):
        part = part.strip('#')
        if '-' in part:
            lo, hi = part.split('-')
            if lo.isdigit() and hi.isdigit() and int(hi) - int(lo) <= 30:
                out += [str(n) for n in range(int(lo), int(hi) + 1)]
        elif part.isdigit():
            out.append(part)
    return out

HEADER_PAT = re.compile(r'^\|.*(持ち物|アイテム).*\|.*(技|注目技|move)', re.IGNORECASE)

md_files = sorted(f for f in os.listdir('../..') if f.endswith('.md'))
flags = []
checked_rows = 0
for fn in md_files:
    path = os.path.join('../..', fn)
    in_item_table = False
    for lineno, line in enumerate(open(path, encoding='utf-8'), 1):
        stripped = line.strip()
        if stripped.startswith('|') and ('持ち物' in stripped or 'アイテム' in stripped) and '種族' in stripped:
            in_item_table = True
            continue
        if not stripped.startswith('|'):
            in_item_table = False
            continue
        if re.match(r'^\|[\s:\-|]+\|$', stripped):  # 区切り行 |---|---|
            continue
        if not in_item_table:
            continue
        m = PAT_ROW.match(stripped)
        if not m:
            continue
        idstr, species_field, item_field, moves_field = m.groups()
        ids = expand_ids(idstr)
        ids = [i for i in ids if i in BY_ID]
        if not ids:
            continue
        checked_rows += 1
        species_claim = re.sub(r'[*＊]', '', species_field).strip()
        item_claim = norm_move(re.sub(r'[*＊]', '', item_field).strip())
        move_tokens = [norm_move(t) for t in re.split(r'[/／、,]', moves_field) if t.strip('* ')]
        move_tokens = [t for t in move_tokens if t not in AMBIGUOUS_TOKENS and not re.search(r'[（(]', t)]
        for sid in ids:
            truth = BY_ID[sid]
            if species_claim and species_claim not in ('種族',) and truth['species'] not in species_claim and species_claim not in truth['species']:
                flags.append((fn, lineno, sid, 'species', species_claim, truth['species'], line.strip()))
            if item_claim and item_claim not in ('持ち物', 'なし') and item_claim != truth['item'] and truth['item'] not in item_claim:
                flags.append((fn, lineno, sid, 'item', item_claim, truth['item'], line.strip()))
            bad_moves = [t for t in move_tokens if t not in truth['moves'] and t in set(JPM.values())]
            if bad_moves:
                flags.append((fn, lineno, sid, 'move', bad_moves, sorted(truth['moves']), line.strip()))

print(f"検査対象行(id有効な表行): {checked_rows}  フラグ数: {len(flags)}")
for fn, lineno, sid, kind, claim, truth, line in flags:
    print(f"\n[{fn}:{lineno}] #{sid} 真species={BY_ID[sid]['species']} kind={kind}")
    print(f"  記載: {claim}  正: {truth}")
    print(f"  > {line}")
