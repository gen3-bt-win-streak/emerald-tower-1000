from os.path import abspath
cs=open('calc_matchups.py').read()
ns={'__file__':abspath('calc_matchups.py')}
exec(cs[:cs.index('CANDS = {')], ns)
damage_range=ns['damage_range']; MOVES=ns['MOVES']; pool=ns['pool']; PHYSICAL=ns['PHYSICAL']; tchart=ns['tchart']
GROSS={'stats':{'hp':364,'atk':381,'df':307,'spd':227,'spe':177},'types':('TYPE_STEEL','TYPE_PSYCHIC'),'ability':'ABILITY_CLEAR_BODY','item':'Quick Claw','species':'Metagross','level':100}
ZAP={'stats':{'hp':322,'atk':168,'spa':383,'df':206,'spd':216,'spe':299},'types':('TYPE_ELECTRIC','TYPE_FLYING'),'ability':'ABILITY_PRESSURE','item':'Lum Berry','species':'Zapdos','level':100}
LATIOS={'stats':{'hp':302,'atk':166,'spa':359,'df':196,'spd':256,'spe':350},'types':('TYPE_DRAGON','TYPE_PSYCHIC'),'ability':'ABILITY_LEVITATE','item':'Lum Berry','species':'Latios','level':100}
LATIAS={'stats':{'hp':302,'atk':166,'spa':319,'df':216,'spd':296,'spe':350},'types':('TYPE_DRAGON','TYPE_PSYCHIC'),'ability':'ABILITY_LEVITATE','item':'Lum Berry','species':'Latias','level':100}
_mol=[e for e in pool if e['set_id']==791][0]
_a=dict(species='Moltres',stats=_mol['stats31'],types=_mol['types'],ability='ABILITY_PRESSURE',item=_mol['item'],level=100)
assert damage_range(_a,GROSS,'MOVE_OVERHEAT')[0]>=364, 'TYPE BUG'
# --- end preamble ---

# custom moves needed for our candidates
MOVES['MOVE_HP_ICE']=dict(effect='EFFECT_HIT',power=70,type='TYPE_ICE',accuracy=100,target='MOVE_TARGET_SELECTED',priority=0)
# GROSS only attacks physically (steel/ground/normal); damage_range reads spa upfront, so supply it (unused for physical).
GROSS['stats'].setdefault('spa',196)

# candidate attacking moves (Thunder Wave excluded)
ZAP_MOVES=['MOVE_THUNDERBOLT','MOVE_HP_ICE']            # 10まん(電気STAB) / めざ氷(氷70)
LATI_MOVES=['MOVE_PSYCHIC','MOVE_ICE_BEAM','MOVE_THUNDERBOLT']  # サイキネ(エスパーSTAB)/れいB(氷95)/10まん(電気95)
CANDS={'サンダー':(ZAP,ZAP_MOVES),'ラティオス':(LATIOS,LATI_MOVES),'ラティアス':(LATIAS,LATI_MOVES)}

MVJP={'MOVE_THUNDERBOLT':'10まん','MOVE_HP_ICE':'めざ氷','MOVE_PSYCHIC':'サイキネ',
      'MOVE_ICE_BEAM':'れいB','MOVE_METEOR_MASH':'コメパン','MOVE_EARTHQUAKE':'じしん','MOVE_EXPLOSION':'だいばくはつ'}
TJP={'TYPE_ICE':'氷','TYPE_ROCK':'岩','TYPE_DARK':'悪','TYPE_GHOST':'ゴースト','TYPE_BUG':'むし',
     'TYPE_DRAGON':'竜','TYPE_NORMAL':'ノーマル','TYPE_ELECTRIC':'電気','TYPE_FIRE':'炎','TYPE_WATER':'水',
     'TYPE_GRASS':'草','TYPE_GROUND':'地面','TYPE_FIGHTING':'格闘','TYPE_FLYING':'飛行','TYPE_PSYCHIC':'エスパー',
     'TYPE_POISON':'毒','TYPE_STEEL':'鋼'}
# Japanese species names (tower-relevant)
SPJP={'Suicune':'スイクン','Lapras':'ラプラス','Gyarados':'ギャラドス','Starmie':'スターミー','Vaporeon':'シャワーズ',
      'Milotic':'ミロカロス','Blastoise':'カメックス','Kingdra':'キングドラ','Slowbro':'ヤドラン','Slowking':'ヤドキング',
      'Walrein':'トドゼルガ','Cloyster':'パルシェン','Dewgong':'ジュゴン','Tentacruel':'ドククラゲ','Ludicolo':'ルンパッパ',
      'Whiscash':'ナマズン','Quagsire':'ヌオー','Sharpedo':'サメハダー','Feraligatr':'オーダイル','Politoed':'ニョロトノ',
      'Golduck':'ゴルダック','Pelipper':'ペリッパー','Wailord':'ホエルオー','Relicanth':'ジーランス','Crawdaunt':'ヘイガニ',
      'Articuno':'フリーザー','Zapdos':'サンダー','Moltres':'ファイヤー','Dragonite':'カイリュー','Salamence':'ボーマンダ',
      'Flygon':'フライゴン','Altaria':'チルタリス','Aerodactyl':'プテラ','Skarmory':'エアームド','Charizard':'リザードン',
      'Fearow':'オニドリル','Pidgeot':'ピジョット','Crobat':'クロバット','Xatu':'ネイティオ','Noctowl':'ヨルノズク',
      'Houndoom':'ヘルガー','Tyranitar':'バンギラス','Gengar':'ゲンガー','Snorlax':'カビゴン','Blissey':'ハピナス',
      'Metagross':'メタグロス','Regice':'レジアイス','Regirock':'レジロック','Registeel':'レジスチル','Claydol':'ネンドール',
      'Golem':'ゴローニャ','Rhydon':'サイドン','Steelix':'ハガネール','Aggron':'ボスゴドラ','Donphan':'ドンファン',
      'Marowak':'ガラガラ','Nidoking':'ニドキング','Nidoqueen':'ニドクイン','Weezing':'マタドガス','Muk':'ベトベトン',
      'Gardevoir':'サーナイト','Alakazam':'フーディン','Hypno':'スリーパー','Exeggutor':'ナッシー','Vileplume':'ラフレシア',
      'Victreebel':'ウツボット','Venusaur':'フシギバナ','Meganium':'メガニウム','Sceptile':'ジュカイン','Breloom':'キノガッサ',
      'Shiftry':'ダーテング','Cradily':'リリーラ->ユレイドル','Cacturne':'ノクタス','Cradily ':'ユレイドル','Heracross':'ヘラクロス',
      'Machamp':'カイリキー','Hariyama':'ハリテヤマ','Medicham':'チャーレム','Hitmonlee':'サワムラー','Hitmonchan':'エビワラー',
      'Poliwrath':'ニョロボン','Ampharos':'デンリュウ','Manectric':'ライボルト','Raikou':'ライコウ','Electrode':'マルマイン',
      'Jolteon':'サンダース','Magneton':'レアコイル','Lanturn':'ランターン','Camerupt':'バクーダ','Magcargo':'マグカルゴ',
      'Ninetales':'キュウコン','Arcanine':'ウインディ','Rapidash':'ギャロップ','Entei':'エンテイ','Typhlosion':'バクフーン',
      'Blaziken':'バシャーモ','Torkoal':'コータス','Flareon':'ブースター','Espeon':'エーフィ','Umbreon':'ブラッキー',
      'Absol':'アブソル','Mightyena':'グラエナ','Sableye':'ヤミラミ','Banette':'ジュペッタ','Dusclops':'サマヨール',
      'Misdreavus':'ムウマ','Sudowoodo':'ウソッキー','Forretress':'フォレトス','Scizor':'ハッサム','Ariados':'アリアドス',
      'Shuckle':'ツボツボ','Ledian':'レディアン','Kabutops':'カブトプス','Omastar':'オムスター','Armaldo':'アーマルド',
      'Lunatone':'ルナトーン','Solrock':'ソルロック','Girafarig':'キリンリキ','Wobbuffet':'ソーナンス','Grumpig':'ブーピッグ',
      'Lickitung':'ベロリンガ','Kangaskhan':'ガルーラ','Tauros':'ケンタロス','Miltank':'ミルタンク','Porygon2':'ポリゴン2',
      'Ursaring':'リングマ','Granbull':'グランブル','Pinsir':'カイロス','Vibrava':'ビブラーバ','Swampert':'ラグラージ',
      'Ludicolo ':'ルンパッパ','Sunflora':'キマワリ','Bellossom':'キレイハナ','Jumpluff':'ワタッコ','Cacnea':'サボネア',
      'Glalie':'オニゴーリ','Sealeo':'トドグラー','Delibird':'デリバード','Piloswine':'イノムー','Mamoswine':'マンムー',
      'Weezing ':'マタドガス','Qwilfish':'ハリーセン','Seaking':'アズマオウ','Octillery':'オクタン','Mantine':'マンタイン',
      'Huntail':'ハンテール','Gorebyss':'サクラビス','Luvdisc':'ラブカス','Corsola':'サニーゴ','Chinchou':'チョンチー',
      'Lombre':'ハスブレロ','Masquerain':'アメモース','Ninjask':'テッカニン','Volbeat':'バルビート','Illumise':'イルミーゼ',
      'Beautifly':'アゲハント','Dustox':'ドクケイル','Swellow':'オオスバメ','Taillow':'スバメ','Wingull':'キャモメ',
      'Tropius':'トロピウス','Zangoose':'ザングース','Seviper':'ハブネーク','Kecleon':'カクレオン','Spinda':'パッチール',
      'Slaking':'ケッキング','Vigoroth':'ヤルキモノ','Exploud':'バクオング','Loudred':'ドゴーム','Linoone':'マッスグマ',
      'Swalot':'マルノーム','Grumpig ':'ブーピッグ','Spoink':'バネブー','Numel':'ドンメル','Trapinch':'ナックラー',
      'Baltoy':'ヤジロン','Nosepass':'ノズパス','Lairon':'コドラ','Aron':'ココドラ','Beldum':'ダンバル',
      'Metang':'メタング','Bagon':'タツベイ','Shelgon':'コモルー','Whismur':'ゴニョニョ','Azumarill':'マリルリ',
      'Wigglytuff':'プクリン','Clefable':'ピクシー','Chansey':'ラッキー','Aromatisse':'','Togetic':'トゲチック',
      'Dodrio':'ドードリオ','Farfetchd':'カモネギ',"Farfetch'd":'カモネギ','Mr. Mime':'バリヤード','Mr Mime':'バリヤード',
      'Jynx':'ルージュラ','Electabuzz':'エレブー','Magmar':'ブーバー','Pinsir ':'カイロス','Scyther':'ストライク',
      'Sandslash':'サンドパン','Nidorina':'ニドリーナ','Dugtrio':'ダグトリオ','Golbat':'ゴルバット','Venomoth':'モルフォン',
      'Parasect':'パラセクト','Primeape':'オコリザル','Persian':'ペルシアン','Arbok':'アーボック','Raichu':'ライチュウ'}

def spjp(name):
    return SPJP.get(name, name)

def worst_def(att, e, mk, iv=31):
    """our move vs enemy; enemy ability = worst (min damage) branch. returns (lo,hi)."""
    best=None
    for ab in set(a for a in e['abilities'] if a!='ABILITY_NONE'):
        d=dict(species=e['species'],stats=e[f'stats{iv}'],types=e['types'],ability=ab,item=e['item'],level=100)
        lohi=damage_range(att,d,mk)
        if best is None or lohi<best: best=lohi
    return best

def enemy_atk(e, iv=31):
    """iterator of enemy attacker dicts across worst ability branches"""
    for ab in set(a for a in e['abilities'] if a!='ABILITY_NONE'):
        yield dict(species=e['species'],stats=e[f'stats{iv}'],types=e['types'],ability=ab,item=e['item'],level=100)

def classify(lo,hi,hp,item):
    """確1 / 乱1 / 2発 / 3発+  (Focus Band downgrades 確1->乱1)"""
    if hi==0: return '無効'
    if lo>=hp: return '乱1' if item=='Focus Band' else '確1'
    if hi>=hp: return '乱1'
    if lo*2>=hp: return '確2'
    if hi*2>=hp: return '乱2'
    n=-(-hp//max(hi,1))
    return f'{n}発'

# ===================================================================
# STEP 1: グロスの穴 (Metagross can't guaranteed-OHKO; explosion immune/resist)
# ===================================================================
GROSS_ATK=['MOVE_METEOR_MASH','MOVE_EARTHQUAKE']   # 非自爆技
holes=[]        # A: MM/EQ どちらも確定OHKO不可 (=爆発せねば倒せない/倒せない)
for e in pool:
    hp=e['stats31']['hp']; fb=(e['item']=='Focus Band')
    best_reg=(0,0,'')
    for mk in GROSS_ATK:
        lo,hi=worst_def(GROSS,e,mk)
        if hi>best_reg[1]: best_reg=(lo,hi,mk)
    reg_ohko = best_reg[0]>=hp and not fb
    if reg_ohko:
        continue   # グロスが通常技で確定OHKO → 穴ではない
    # explosion analysis
    elo,ehi=worst_def(GROSS,e,'MOVE_EXPLOSION')
    expl_mult=ns['type_mult']('TYPE_NORMAL',e['types'],'ABILITY_NONE')  # x10 scale
    if expl_mult==0: expl_tag='無効'
    elif expl_mult<10: expl_tag='半減'
    else: expl_tag='等倍'
    expl_ohko = elo>=hp and not fb
    holes.append(dict(e=e,hp=hp,fb=fb,reg=best_reg,elo=elo,ehi=ehi,expl_tag=expl_tag,expl_ohko=expl_ohko,
                      reg_class=classify(best_reg[0],best_reg[1],hp,e['item'])))

# subsets
A=holes                                                     # 通常技で確定OHKO不可 (=爆発 or 先発2に依存)
expl_immune=[h for h in holes if h['expl_tag']=='無効']       # ゴースト(爆発無効)
expl_resist=[h for h in holes if h['expl_tag']=='半減']       # 岩/鋼(爆発半減)
expl_saves =[h for h in holes if h['expl_ohko']]             # 爆発なら確定OHKO(自滅で処理可)
hard_hole  =[h for h in holes if (not h['fb']) and not h['expl_ohko']]  # 構造的な穴: 非FB & 爆発でも確定OHKO不可
fb_hole    =[h for h in holes if h['fb']]                    # メンタルハーブ無 Focus Band(1/8生存, 確定OHKO不能)

print('='*72)
print('STEP1: グロスの穴 (A164=381 コメパン100/じしん100 で確定OHKO不可の敵)')
print('='*72)
print(f"通常技(コメパン/じしん)で確定OHKO不可 = {len(A)}セット / 546  ←爆発 or 先発2に依存")
print(f"  うち 爆発なら確定OHKO(自滅すれば処理可)  = {len(expl_saves)}")
print(f"  うち Focus Band(1/8生存で確定OHKO不能)   = {len(fb_hole)}")
print(f"  うち 構造的な穴(非FB&爆発でも確定OHKO不可)= {len(hard_hole)}")
print(f"    [参考] だいばくはつ無効(ゴースト)全体 = {len(expl_immune)} / 半減(岩鋼)全体 = {len(expl_resist)}")
print()
print('--- 構造的な穴(非FB, 爆発でも確定OHKOできない敵 = 先発2が本当に埋めるべき対象) ---')
for h in sorted(hard_hole,key=lambda h:h['e']['set_id']):
    e=h['e']
    print(f"  #{e['set_id']} {spjp(e['species'])}({e['species']}) HP{h['hp']} "
          f"通常最大={MVJP.get(h['reg'][2],h['reg'][2])} {h['reg'][0]}-{h['reg'][1]}({h['reg_class']}) "
          f"爆発={h['elo']}-{h['ehi']}[{h['expl_tag']}]")

# ===================================================================
# STEP 2: 各先発2の最大打点が グロスの穴 をどれだけ埋めるか
# ===================================================================
def best_move(att, moves, e):
    best=(0,0,'')
    for mk in moves:
        lo,hi=worst_def(att,e,mk)
        if hi>best[1]: best=(lo,hi,mk)
    return best

def count_over(att, moves, hlist):
    c1=c1r=c2=cx=0
    for h in hlist:
        e=h['e']; hp=h['hp']
        lo,hi,mk=best_move(att,moves,e)
        cl=classify(lo,hi,hp,e['item'])
        if cl=='確1': c1+=1
        elif cl=='乱1': c1r+=1
        elif cl in ('確2','乱2'): c2+=1
        else: cx+=1
    return c1,c1r,c2,cx

print()
print('='*72)
print('STEP2: 各先発2の攻撃技(でんじは以外)が「グロスの穴」を埋める数')
print('='*72)
step2={}
print(f"[A] 通常技で確定OHKO不可 = {len(A)}セット (先発2が確1すれば爆発温存/自滅回避)")
for name,(att,moves) in CANDS.items():
    c1,c1r,c2,cx=count_over(att,moves,A)
    step2[name]=dict(c1=c1,c1r=c1r,c2=c2,cx=cx)
    print(f"  {name}: 確1={c1} 乱1={c1r} 2発={c2} 3発+/無効={cx}  (確1+乱1={c1+c1r}/{len(A)})")
print(f"[H] 構造的な穴(非FB&爆発でも倒せない) = {len(hard_hole)}セット (ここを埋められるか＝真価)")
step2h={}
for name,(att,moves) in CANDS.items():
    c1,c1r,c2,cx=count_over(att,moves,hard_hole)
    step2h[name]=dict(c1=c1,c1r=c1r,c2=c2,cx=cx)
    print(f"  {name}: 確1={c1} 乱1={c1r} 2発={c2} 3発+/無効={cx}  (確1+乱1={c1+c1r}/{len(hard_hole)})")

# 構造的な穴を誰が埋めるか (個別)
print()
print('--- 構造的な穴(%d体)を各候補が確1で埋められるか ---' % len(hard_hole))
for h in sorted(hard_hole,key=lambda h:h['e']['set_id']):
    e=h['e']; hp=h['hp']
    row=[]
    for name,(att,moves) in CANDS.items():
        lo,hi,mk=best_move(att,moves,e)
        row.append(f"{name}={MVJP.get(mk,mk)}{lo}-{hi}({classify(lo,hi,hp,e['item'])})")
    print(f"  #{e['set_id']} {spjp(e['species'])} HP{hp}: "+' | '.join(row))

# ===================================================================
# STEP 3: 電気STAB(サンダー) vs エスパー/氷(ラティ) の刺さる範囲
#          - グロスの穴集合 A
#          - danger pool (先発2いずれかをOHKOしうる敵)
# ===================================================================
def cand_hp(att): return att['stats']['hp']

# danger pool: 3候補いずれかを確定or乱1でOHKOしうる敵セット
def can_ohko_cand(e, att):
    hp=att['stats']['hp']
    for mk in e['moves']:
        if MOVES[mk]['power']<2: continue
        for a in enemy_atk(e):
            lo,hi=damage_range(a,att,mk)
            if hi>=hp: return True
    return False

danger=[]
for e in pool:
    tgt=[nm for nm,(att,_) in CANDS.items() if can_ohko_cand(e,att)]
    if tgt: danger.append((e,tgt))
danger_set=[e for e,_ in danger]

def type_reach(att, moves, elist, move_subset=None):
    """count 確1 / 確1+乱1 over elist using best of move_subset (default all moves)."""
    mv = move_subset if move_subset else moves
    c1=cin=0
    for e in elist:
        hp=e['stats31']['hp']
        lo,hi,mk=best_move(att,mv,e)
        cl=classify(lo,hi,hp,e['item'])
        if cl=='確1': c1+=1; cin+=1
        elif cl=='乱1': cin+=1
    return c1,cin

print()
print('='*72)
print('STEP3: 電気STAB vs エスパー/氷 の刺さる範囲 (確1 / 確1+乱1)')
print('='*72)
print(f"[グロスの穴 A={len(A)}]")
poolA=[h['e'] for h in A]
z1,zin=type_reach(ZAP,ZAP_MOVES,poolA,['MOVE_THUNDERBOLT'])
zi1,ziin=type_reach(ZAP,ZAP_MOVES,poolA,['MOVE_HP_ICE'])
za1,zain=type_reach(ZAP,ZAP_MOVES,poolA)
print(f"  サンダー 10まん(電気STAB): 確1={z1} 確1+乱1={zin}")
print(f"  サンダー めざ氷(氷70):     確1={zi1} 確1+乱1={ziin}")
print(f"  サンダー 最大(電/氷):      確1={za1} 確1+乱1={zain}")
for nm in ('ラティオス','ラティアス'):
    att,_=CANDS[nm]
    p1,pin=type_reach(att,LATI_MOVES,poolA,['MOVE_PSYCHIC'])
    i1,iin=type_reach(att,LATI_MOVES,poolA,['MOVE_ICE_BEAM'])
    t1,tin=type_reach(att,LATI_MOVES,poolA,['MOVE_THUNDERBOLT'])
    a1,ain=type_reach(att,LATI_MOVES,poolA)
    print(f"  {nm} サイキネ(エスパーSTAB):確1={p1} +乱1={pin} | れいB(氷):確1={i1} +乱1={iin} | 10まん(電):確1={t1} +乱1={tin} | 最大:確1={a1} +乱1={ain}")

print()
print(f"[danger pool = 先発2いずれかをOHKOしうる敵 = {len(danger_set)}]")
za1,zain=type_reach(ZAP,ZAP_MOVES,danger_set)
z1,zin=type_reach(ZAP,ZAP_MOVES,danger_set,['MOVE_THUNDERBOLT'])
print(f"  サンダー 10まん(電気STAB): 確1={z1} +乱1={zin} | 最大(電/氷):確1={za1} +乱1={zain}")
for nm in ('ラティオス','ラティアス'):
    att,_=CANDS[nm]
    p1,pin=type_reach(att,LATI_MOVES,danger_set,['MOVE_PSYCHIC'])
    i1,iin=type_reach(att,LATI_MOVES,danger_set,['MOVE_ICE_BEAM'])
    a1,ain=type_reach(att,LATI_MOVES,danger_set)
    print(f"  {nm} サイキネ:確1={p1}+乱1={pin} | れいB:確1={i1}+乱1={iin} | 最大:確1={a1}+乱1={ain}")

# ===================================================================
# 水/飛行の代表先発 比較: スイクン/ラプラス/ギャラ/スターミー等
# ===================================================================
print()
print('='*72)
print('STEP2b: 水/飛行の代表先発への打点比較 (サンダー10まん vs ラティ サイキネ/れいB)')
print('='*72)
WF=['Suicune','Lapras','Gyarados','Starmie','Vaporeon','Milotic','Blastoise','Kingdra',
    'Slowbro','Slowking','Walrein','Cloyster','Tentacruel','Dewgong','Ludicolo','Politoed',
    'Golduck','Pelipper','Wailord','Sharpedo','Feraligatr','Articuno','Dragonite','Salamence',
    'Altaria','Charizard','Skarmory','Aerodactyl','Crobat','Fearow','Pidgeot','Azumarill']
for sp in WF:
    es=[e for e in pool if e['species']==sp]
    for e in es:
        hp=e['stats31']['hp']
        zl,zh=worst_def(ZAP,e,'MOVE_THUNDERBOLT')
        ol,oh,om=best_move(LATIOS,LATI_MOVES,e)
        al,ah,am=best_move(LATIAS,LATI_MOVES,e)
        # latios psychic & ice explicit
        opl,oph=worst_def(LATIOS,e,'MOVE_PSYCHIC'); oil,oih=worst_def(LATIOS,e,'MOVE_ICE_BEAM')
        print(f"#{e['set_id']} {spjp(sp)} HP{hp} [{TJP.get(e['types'][0],'')}/{TJP.get(e['types'][1],'') if e['types'][1]!=e['types'][0] else ''}]")
        print(f"    サンダー10まん: {zl}-{zh} ({classify(zl,zh,hp,e['item'])})")
        print(f"    ラティオス最大 {MVJP.get(om,om)}: {ol}-{oh} ({classify(ol,oh,hp,e['item'])}) [サイキネ{opl}-{oph}/れいB{oil}-{oih}]")
        print(f"    ラティアス最大 {MVJP.get(am,am)}: {al}-{ah} ({classify(al,ah,hp,e['item'])})")

# raw summary
print()
print('RAW')
print(f"HOLES_A={len(A)} HARD_HOLE={len(hard_hole)} FB_HOLE={len(fb_hole)} EXPL_SAVES={len(expl_saves)} EXPL_IMMUNE={len(expl_immune)} EXPL_RESIST={len(expl_resist)}")
for name in CANDS:
    s=step2[name]; sh=step2h[name]
    print(f"{name}\tA確1={s['c1']} A乱1={s['c1r']} A圏内={s['c1']+s['c1r']}/{len(A)}\tH確1={sh['c1']} H乱1={sh['c1r']} H圏内={sh['c1']+sh['c1r']}/{len(hard_hole)}")
print(f"DANGER_POOL={len(danger_set)}")
