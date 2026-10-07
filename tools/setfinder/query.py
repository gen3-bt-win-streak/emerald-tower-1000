"""タワー型サーチの端末版。ページ（template.html）と同じ規則で、見えた情報から敵の型を絞り込む。

  cd battle-tower/tools/setfinder
  python3 query.py "カビゴン メガトンキック かわらわり" "サイドン >150"
  python3 query.py "かびごん つめ / さいどん"          # 1つの引数に / 区切りで複数の枠を書いてもよい

1つの引数（または / で区切った1区間）が敵1体の枠。枠の中は空白区切りで、順不同に
  種族名（前方一致で1つに決まればよい）・技名・持ち物・特性（いずれも完全一致）、
  素早さ「>N」（この敵が自分の実数値Nより速い）「<N」（遅い）「=N」（同速）。先頭の S は付けても付けなくてもよい。
ひらがな・カタカナ・全角半角の違いは無視する。持ち物は「つめ」「ツメ」でせんせいのツメ、「のこし」でたべのこしなど、
部分一致で1つに決まれば受け付ける。

規則はページと同じ：
  ・素早さは個体値31と21の両方で判定し、同速は「速い」「遅い」の両方に含める。
  ・せんせいのツメ持ちは「速い」で素早さが足りなくても残す（注意を付ける）。
  ・敵チームは種族・持ち物が重複しないので、入力済みの枠どうしで持ち物が重ならない組み合わせを総当たりし、
    1つでも組み合わせを作れる型だけを残す。作れなければ「矛盾」を出す。
"""
import os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_out = sys.stdout
sys.stdout = open(os.devnull, 'w')          # evlib の読込メッセージを黙らせる
from build_setfinder import export          # noqa: E402
SETS = export()
sys.stdout = _out


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
    return ''.join(s.split())


SPECIES = sorted({s['p'] for s in SETS})
MOVES = sorted({m for s in SETS for m in s['mv']})
ITEMS = sorted({s['it'] for s in SETS})
ABILS = sorted({a for s in SETS for a in s['a']})
N = {k: norm(k) for k in SPECIES + MOVES + ITEMS + ABILS}


def pick(tok, names, partial):
    t = norm(tok)
    exact = [n for n in names if N[n] == t]
    if exact:
        return exact[0], None
    if not partial:
        return None, None
    hits = [n for n in names if (N[n].startswith(t) if partial == 'prefix' else t in N[n])]
    if len(hits) == 1:
        return hits[0], None
    return None, hits


def parse(text):
    slot = dict(sp='', moves=[], item='', ab='', spd=[], warn=[])
    for tok in text.split():
        t = unicodedata.normalize('NFKC', tok).lstrip('Ss')
        if t[:1] in '<>=' and t[1:].isdigit():
            slot['spd'].append(({'>': 'fast', '<': 'slow', '=': 'tie'}[t[0]], int(t[1:])))
            continue
        for kind, names, partial in (('moves', MOVES, None), ('ab', ABILS, None), ('sp', SPECIES, 'prefix'),
                                     ('item', ITEMS, 'sub')):
            hit, amb = pick(tok, names, partial)
            if hit:
                if kind == 'moves':
                    slot['moves'].append(hit)
                elif slot[kind] and slot[kind] != hit:
                    slot['warn'].append(f'「{tok}」: {slot[kind]} と重複したので無視')
                else:
                    slot[kind] = hit
                break
            if amb:
                slot['warn'].append(f'「{tok}」は候補が複数: {"・".join(amb[:8])}{" …" if len(amb) > 8 else ""}')
                break
        else:
            slot['warn'].append(f'「{tok}」は種族・技・持ち物・特性のどれにも当たらない')
    return slot


def own(slot):
    if not slot['sp']:
        return None
    out = []
    for s in SETS:
        if s['p'] != slot['sp']:
            continue
        if any(m not in s['mv'] for m in slot['moves']):
            continue
        if slot['item'] and s['it'] != slot['item']:
            continue
        if slot['ab'] and slot['ab'] not in s['a']:
            continue
        hi, lo = max(s['st'][5], s['s21']), min(s['st'][5], s['s21'])
        ok = True
        for rel, v in slot['spd']:
            if rel == 'fast' and not (s['qc'] or hi >= v):
                ok = False
            if rel == 'slow' and not lo <= v:
                ok = False
            if rel == 'tie' and not (s['st'][5] == v or s['s21'] == v):
                ok = False
        if ok:
            out.append(s)
    return out


def compute(slots):
    base = [own(sl) for sl in slots]
    dup = [bool(sl['sp']) and any(j != i and o['sp'] == sl['sp'] for j, o in enumerate(slots)) for i, sl in enumerate(slots)]
    cand = [list(b) if b is not None else None for b in base]
    removed = [set() for _ in slots]
    conflict = [[] for _ in slots]
    filled = [i for i, b in enumerate(base) if b and not dup[i]]
    if len(filled) >= 2:
        keep = [set() for _ in filled]
        chosen, used, found = [None] * len(filled), set(), [False]

        def rec(k):
            if k == len(filled):
                found[0] = True
                for x, s in enumerate(chosen):
                    keep[x].add(s['i'])
                return
            for s in base[filled[k]]:
                if s['it'] in used:
                    continue
                chosen[k] = s
                used.add(s['it'])
                rec(k + 1)
                used.discard(s['it'])
        rec(0)
        if found[0]:
            for x, i in enumerate(filled):
                cand[i] = [s for s in base[i] if s['i'] in keep[x]]
                removed[i] = {s['it'] for s in base[i] if s['i'] not in keep[x]}
        else:
            for a in range(len(filled)):
                for b in range(a + 1, len(filled)):
                    A, B = base[filled[a]], base[filled[b]]
                    if not any(u['it'] != s['it'] for s in A for u in B):
                        conflict[filled[a]].append(filled[b])
                        conflict[filled[b]].append(filled[a])
            if not any(conflict):
                for i in filled:
                    conflict[i] = [j for j in filled if j != i]
    return cand, removed, dup, conflict


def show(slots):
    cand, removed, dup, conflict = compute(slots)
    for i, sl in enumerate(slots):
        cond = [sl['sp'] or '（種族未入力）'] + sl['moves'] + ([sl['item']] if sl['item'] else []) + \
               ([sl['ab']] if sl['ab'] else []) + [f"{ {'fast': '速い', 'slow': '遅い', 'tie': '同速'}[r]}（{v}）" for r, v in sl['spd']]
        print(f'■ 敵{i + 1}：' + '／'.join(cond))
        for w in sl['warn']:
            print(f'  ⚠ {w}')
        if dup[i]:
            print('  ⚠ 他の枠と同じ種族（同じチームに同種族は出ない）')
        if conflict[i]:
            print(f"  ⛔ 矛盾：敵{'・敵'.join(str(j + 1) for j in conflict[i])} と持ち物が必ず重なる組み合わせしかない")
        lst = cand[i]
        if lst is None:
            continue
        if not lst:
            print('  候補なし（条件を見直す）')
            continue
        items = {s['it'] for s in lst}
        head = f'  候補 {len(lst)}型'
        if len(items) == 1:
            head += f'（持ち物は {next(iter(items))} で確定）'
        if removed[i]:
            head += f"　他の枠との組み合わせで除外した持ち物：{'・'.join(sorted(removed[i]))}"
        print(head)
        lo31, hi31 = min(s['st'][5] for s in lst), max(s['st'][5] for s in lst)
        lo21, hi21 = min(s['s21'] for s in lst), max(s['s21'] for s in lst)
        print(f'  素早さ：個体値31 {lo31}〜{hi31}／個体値21 {lo21}〜{hi21}')
        for s in sorted(lst, key=lambda s: s['i']):
            st = '-'.join(map(str, s['st']))
            print(f"  #{s['i']} @{s['it']}{' ⚡ツメ' if s['qc'] else ''}｜{s['n']}（{s['nl']}）{s['ev']}｜{st}（S21={s['s21']}）"
                  f"｜{'／'.join(s['mv'])}｜{'・'.join(s['a'])}")
        fast_rows = [v for r, v in sl['spd'] if r == 'fast']
        qc_kept = [s for s in lst if s['qc'] and any(max(s['st'][5], s['s21']) < v for v in fast_rows)]
        if qc_kept:
            print(f"  ※ #{'・#'.join(str(s['i']) for s in qc_kept)} は素早さでは届かないが、せんせいのツメで先に動いた可能性があるので残している")
        print()


def main(argv):
    parts = [p for a in argv for p in a.split('/') if p.strip()]
    if not parts:
        print(__doc__)
        return 1
    if len(parts) > 4:
        print('枠は最大4つ（敵は4体）')
        return 1
    show([parse(p) for p in parts])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
