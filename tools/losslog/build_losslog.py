"""タワー敗戦ログ（静的HTML）を生成する。

50戦目以降の546型（種族・持ち物・技・素早さ）と自陣の構成（team.json）を template.html に埋め込み、
tower-losslog.html を書き出す。ページはこの1ファイルだけで動く（サーバー・外部通信なし）。

  cd battle-tower/tools/losslog && PYTHONHASHSEED=0 python3 build_losslog.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'setfinder'))
_out = sys.stdout
sys.stdout = open(os.devnull, 'w')          # evlib の読込メッセージを黙らせる
from build_setfinder import export          # noqa: E402
sys.stdout = _out


def data():
    """型サーチの書き出しを、ログに要る項目だけに削る。"""
    return [dict(i=s['i'], p=s['p'], it=s['it'], mv=s['mv'], s=s['st'][5]) for s in export()]


def main():
    sets = json.dumps(data(), ensure_ascii=False, separators=(',', ':'))
    team = json.dumps(json.load(open(os.path.join(HERE, 'team.json'), encoding='utf-8')),
                      ensure_ascii=False, separators=(',', ':'))
    tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    html = tpl.replace('__DATA__', sets).replace('__TEAM__', team)
    open(os.path.join(HERE, 'tower-losslog.html'), 'w', encoding='utf-8').write(html)
    print(f'tower-losslog.html: {len(html.encode())} bytes, {sets.count(chr(34)+"i"+chr(34))} sets')
    # スマホ等にファイルとして保存して直接開く版。claude.ai が公開時に足す外枠を自前で付け、Webフォントを使わない。
    lite = '\n'.join(l for l in html.split('\n') if 'fonts.googleapis.com' not in l and 'fonts.gstatic.com' not in l)
    standalone = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
                  '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                  '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
                  'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}'
                  '[hidden]{display:none!important}</style></head><body>' + lite + '</body></html>')
    open(os.path.join(HERE, 'tower-losslog-standalone.html'), 'w', encoding='utf-8').write(standalone)
    print(f'tower-losslog-standalone.html: {len(standalone.encode())} bytes')


if __name__ == '__main__':
    main()
