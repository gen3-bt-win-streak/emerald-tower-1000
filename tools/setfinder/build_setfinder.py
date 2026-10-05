"""タワー型サーチ（静的HTML）を生成する。

50戦目以降の定常プール546型を日本語のJSONにして template.html の __DATA__ に埋め込み、
tower-setfinder.html を書き出す。ページはこの1ファイルだけで動く（サーバー・外部通信なし）。

  cd battle-tower/tools/setfinder && PYTHONHASHSEED=0 python3 build_setfinder.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, '..', 'engine')
sys.path.insert(0, ENGINE)
_cwd = os.getcwd()
from evlib import pool, JPS, JPM  # noqa: E402  evlib は読込中だけ engine に cd する
import evlib                        # noqa: E402
from jpnames import JPI             # noqa: E402
os.chdir(_cwd)

NATURE = evlib._G['NATURE']
ITEM_FIX = {'Never Melt Ice': 'とけないこおり', 'Kings Rock': 'おうじゃのしるし'}
ABILITY = {
    'PRESSURE': 'プレッシャー', 'LEVITATE': 'ふゆう', 'CLEAR_BODY': 'クリアボディ', 'INTIMIDATE': 'いかく',
    'STURDY': 'がんじょう', 'ROCK_HEAD': 'いしあたま', 'SYNCHRONIZE': 'シンクロ', 'THICK_FAT': 'あついしぼう',
    'GUTS': 'こんじょう', 'INNER_FOCUS': 'せいしんりょく', 'CHLOROPHYLL': 'ようりょくそ', 'OBLIVIOUS': 'どんかん',
    'EARLY_BIRD': 'はやおき', 'STATIC': 'せいでんき', 'FLASH_FIRE': 'もらいび', 'NATURAL_CURE': 'しぜんかいふく',
    'WATER_ABSORB': 'ちょすい', 'TRACE': 'トレース', 'SWIFT_SWIM': 'すいすい', 'SOUNDPROOF': 'ぼうおん',
    'ILLUMINATE': 'はっこう', 'LIGHTNING_ROD': 'ひらいしん', 'OVERGROW': 'しんりょく', 'TORRENT': 'げきりゅう',
    'BLAZE': 'もうか', 'SHELL_ARMOR': 'シェルアーマー', 'KEEN_EYE': 'するどいめ', 'SAND_STREAM': 'すなおこし',
    'RUN_AWAY': 'にげあし', 'IMMUNITY': 'めんえき', 'SWARM': 'むしのしらせ', 'VOLT_ABSORB': 'ちくでん',
    'DAMP': 'しめりけ', 'OWN_TEMPO': 'マイペース', 'POISON_POINT': 'どくのトゲ', 'CUTE_CHARM': 'メロメロボディ',
    'SERENE_GRACE': 'てんのめぐみ', 'EFFECT_SPORE': 'ほうし', 'WATER_VEIL': 'みずのベール', 'SAND_VEIL': 'すながくれ',
    'SUCTION_CUPS': 'きゅうばん', 'ARENA_TRAP': 'ありじごく', 'PURE_POWER': 'ヨガパワー', 'RAIN_DISH': 'あめうけざら',
    'INSOMNIA': 'ふみん', 'FLAME_BODY': 'ほのおのからだ', 'BATTLE_ARMOR': 'カブトアーマー', 'CLOUD_NINE': 'ノーてんき',
    'STENCH': 'あくしゅう', 'STICKY_HOLD': 'ねんちゃく', 'LIQUID_OOZE': 'ヘドロえき', 'MARVEL_SCALE': 'ふしぎなうろこ',
    'TRUANT': 'なまけ', 'HYPER_CUTTER': 'かいりきバサミ', 'SHADOW_TAG': 'かげふみ', 'SPEED_BOOST': 'かそく',
    'WONDER_GUARD': 'ふしぎなまもり', 'COLOR_CHANGE': 'へんしょく', 'SHIELD_DUST': 'りんぷん', 'SHED_SKIN': 'だっぴ',
    'ROUGH_SKIN': 'さめはだ'}
NATURE_JP = {
    'Hardy': 'がんばりや', 'Lonely': 'さみしがり', 'Brave': 'ゆうかん', 'Adamant': 'いじっぱり', 'Naughty': 'やんちゃ',
    'Bold': 'ずぶとい', 'Docile': 'すなお', 'Relaxed': 'のんき', 'Impish': 'わんぱく', 'Lax': 'のうてんき',
    'Timid': 'おくびょう', 'Hasty': 'せっかち', 'Serious': 'まじめ', 'Jolly': 'ようき', 'Naive': 'むじゃき',
    'Modest': 'ひかえめ', 'Mild': 'おっとり', 'Quiet': 'れいせい', 'Bashful': 'てれや', 'Rash': 'うっかりや',
    'Calm': 'おだやか', 'Gentle': 'おとなしい', 'Sassy': 'なまいき', 'Careful': 'しんちょう', 'Quirky': 'きまぐれ'}
LETTER = {'hp': 'H', 'atk': 'A', 'df': 'B', 'spa': 'C', 'spd': 'D', 'spe': 'S'}
ORDER = 'H A B C D S'.split()


def export():
    missing, out = set(), []
    for e in pool:
        sp = JPS.get(e['species'])
        it = ITEM_FIX.get(e['item']) or JPI.get(e['item'])
        mv = [JPM.get(m.replace('MOVE_', '')) for m in e['moves']]
        ab = [ABILITY.get(a.replace('ABILITY_', '')) for a in e['abilities'] if a != 'ABILITY_NONE']
        for kind, v, raw in [('species', sp, e['species']), ('item', it, e['item'])] + \
                [('move', j, m) for j, m in zip(mv, e['moves'])] + \
                [('ability', j, a) for j, a in zip(ab, [a for a in e['abilities'] if a != 'ABILITY_NONE'])]:
            if not v:
                missing.add((kind, raw))
        nu = NATURE.get(e['nature'])
        s = e['stats31']
        out.append(dict(
            i=e['set_id'], p=sp, a=ab, it=it, n=NATURE_JP[e['nature']],
            nl=f"{LETTER[nu[0]]}↑{LETTER[nu[1]]}↓" if nu else '補正なし',
            ev=' '.join(f"{LETTER[k]}{v}" for k, v in sorted(e['evs'].items(), key=lambda kv: ORDER.index(LETTER[kv[0]]))),
            st=[s['hp'], s['atk'], s['df'], s['spa'], s['spd'], s['spe']],
            s21=e['stats21']['spe'], mv=mv, qc=e['item'] == 'Quick Claw'))
    if missing:
        sys.exit(f'日本語名が無い項目: {sorted(missing)}')
    return out


def main():
    data = json.dumps(export(), ensure_ascii=False, separators=(',', ':'))
    tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    html = tpl.replace('__DATA__', data)
    open(os.path.join(HERE, 'tower-setfinder.html'), 'w', encoding='utf-8').write(html)
    print(f'tower-setfinder.html: {len(html.encode())} bytes, {data.count(chr(34)+"i"+chr(34))} sets')
    # スマホ等にファイルとして保存して直接開く版。claude.ai が公開時に足す外枠を自前で付ける。
    standalone = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
                  '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                  '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
                  'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}'
                  '[hidden]{display:none!important}</style></head><body>' + html + '</body></html>')
    open(os.path.join(HERE, 'tower-setfinder-standalone.html'), 'w', encoding='utf-8').write(standalone)
    print(f'tower-setfinder-standalone.html: {len(standalone.encode())} bytes')


if __name__ == '__main__':
    main()
