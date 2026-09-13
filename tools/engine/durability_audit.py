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

CANDS = {'サンダー': ZAP, 'ラティオス': LATIOS, 'ラティアス': LATIAS}

# type -> Japanese label
TJP = {'TYPE_ICE':'氷','TYPE_ROCK':'岩','TYPE_DARK':'悪','TYPE_GHOST':'ゴースト','TYPE_BUG':'むし',
       'TYPE_DRAGON':'竜','TYPE_NORMAL':'ノーマル','TYPE_ELECTRIC':'電気','TYPE_FIRE':'炎','TYPE_WATER':'水',
       'TYPE_GRASS':'草','TYPE_GROUND':'地面','TYPE_FIGHTING':'格闘','TYPE_FLYING':'飛行','TYPE_PSYCHIC':'エスパー',
       'TYPE_POISON':'毒','TYPE_STEEL':'鋼','TYPE_STELLAR':'?'}

def worst_hit(e, dfd, mk, iv=31):
    """max hi damage over ability branches (worst-case for defender)."""
    best=(0,0)
    for ab in set(a for a in e['abilities'] if a != 'ABILITY_NONE'):
        atk=dict(species=e['species'],stats=e[f'stats{iv}'],types=e['types'],ability=ab,item=e['item'],level=100)
        lo,hi=damage_range(atk,dfd,mk)
        if hi>best[1]: best=(lo,hi)
    return best

def best_incoming(e, dfd, iv=31):
    """best single move (max hi) vs defender; returns (lo,hi,mk)."""
    best=(0,0,'')
    for mk in e['moves']:
        if MOVES[mk]['power']<2: continue
        lo,hi=worst_hit(e,dfd,mk,iv)
        if hi>best[1]: best=(lo,hi,mk)
    return best

def analyze(name, dfd):
    hp=dfd['stats']['hp']; spe=dfd['stats']['spe']
    n_sure=n_rand=0            # 確定OHKO / 乱1
    n_first_ohko=0             # OHKO かつ 先手(spe>候補)
    type_sure=dict(); type_rand=dict()  # OHKO move type breakdown (by best OHKO move type)
    ohko_list=[]
    for e in pool:
        lo,hi,mk=best_incoming(e,dfd)
        if hi<hp:  # not OHKO
            continue
        mtype=MOVES[mk]['type']
        sure = lo>=hp
        if sure: n_sure+=1
        else:     n_rand+=1
        faster = e['stats31']['spe']>spe
        if faster: n_first_ohko+=1
        d = type_sure if sure else type_rand
        d[mtype]=d.get(mtype,0)+1
        ohko_list.append((e['set_id'],e['species'],mk.replace('MOVE_',''),
                          '確定' if sure else '乱1', lo,hi,hp, faster, e['stats31']['spe']))
    n_ohko=n_sure+n_rand
    n_safe=len(pool)-n_ohko    # OHKOされないセット数
    return dict(name=name,hp=hp,spe=spe,n_sure=n_sure,n_rand=n_rand,n_ohko=n_ohko,
                n_first=n_first_ohko,n_safe=n_safe,type_sure=type_sure,type_rand=type_rand,
                ohko_list=ohko_list)

reps={name:analyze(name,dfd) for name,dfd in CANDS.items()}

print('='*70)
print('1) OHKO被弾セット数 と 先手OHKO (546セット・敵IV31・特性最悪分岐)')
print('='*70)
for name in CANDS:
    r=reps[name]
    print(f"{name}(HP{r['hp']}/速{r['spe']}): OHKO計={r['n_ohko']} (確定{r['n_sure']}/乱1{r['n_rand']}) "
          f"先手OHKO={r['n_first']} 安全(非OHKO)={r['n_safe']}")

print()
print('='*70)
print('2) OHKOしてくる技のタイプ内訳 (確定 / 乱1)')
print('='*70)
for name in CANDS:
    r=reps[name]
    allt=sorted(set(list(r['type_sure'])+list(r['type_rand'])),
                key=lambda t:-(r['type_sure'].get(t,0)+r['type_rand'].get(t,0)))
    print(f"\n[{name}]")
    for t in allt:
        s=r['type_sure'].get(t,0); rd=r['type_rand'].get(t,0)
        print(f"  {TJP.get(t,t):6} 確定{s} 乱1{rd} (計{s+rd})")

print()
print('='*70)
print('3) ヘルガー かみくだく(悪=特殊,特防狙い) 全4セット vs 3候補')
print('='*70)
hd=[e for e in pool if e['species']=='Houndoom']
for e in hd:
    print(f"\n#{e['set_id']} ヘルガー {e['item']} {e['nature']} spa31={e['stats31']['spa']}")
    for name,dfd in CANDS.items():
        lo,hi=worst_hit(e,dfd,'MOVE_CRUNCH')
        hp=dfd['stats']['hp']; spd=dfd['stats']['spd']
        if hi>=hp and lo>=hp: verdict='確定OHKO'
        elif hi>=hp: verdict=f'乱1({(hi-hp+ (hi-lo))})'
        else:
            # hits to KO
            verdict=f'確2' if lo*2>=hp else f'{ -(-hp//hi) }発〜'
        pct=f"{lo*100//hp}-{hi*100//hp}%"
        note='OHKO' if lo>=hp else ('乱1' if hi>=hp else ('確2' if lo*2>=hp else f'{-(-hp//max(hi,1))}+発'))
        print(f"   {name:8}(特防{spd}/HP{hp}): {lo}-{hi} = {pct}  -> {note}")

print()
print('='*70)
print('3b) 悪/ゴースト/竜/むし/氷 の2倍技で ラティ を確定OHKOする敵 (全プール網羅)')
print('='*70)
SE_TYPES={'TYPE_DARK','TYPE_GHOST','TYPE_DRAGON','TYPE_BUG','TYPE_ICE'}
for name in ('ラティオス','ラティアス'):
    dfd=CANDS[name]; hp=dfd['stats']['hp']
    hits=[]
    for e in pool:
        for mk in e['moves']:
            mv=MOVES[mk]
            if mv['power']<2 or mv['type'] not in SE_TYPES: continue
            lo,hi=worst_hit(e,dfd,mk)
            if lo>=hp:  # guaranteed OHKO
                hits.append((e['set_id'],e['species'],mk.replace('MOVE_',''),TJP.get(mv['type']),lo,hi,
                             e['stats31']['spe']>dfd['stats']['spe']))
    print(f"\n[{name}] 確定OHKOしてくる2倍技: {len(hits)}件")
    for sid,sp,mk,tj,lo,hi,fast in sorted(hits,key=lambda x:-x[4]):
        print(f"  #{sid} {sp} {mk}({tj}) {lo}-{hi}/{hp} {'先手' if fast else '後手'}")

print()
print('='*70)
print('4) 確定耐え/確2圏 の比較 (OHKOされないセット数 と その内訳)')
print('='*70)
for name in CANDS:
    dfd=CANDS[name]; hp=dfd['stats']['hp']
    safe_full=0   # 最大打点でもHP半分未満(実質確定耐え余裕)
    safe_ch2=0    # 確2圏(hi>=HP//2 だが非OHKO)
    for e in pool:
        lo,hi,mk=best_incoming(e,dfd)
        if hi>=hp: continue
        if hi>=hp//2: safe_ch2+=1
        else: safe_full+=1
    print(f"{name}: 非OHKO={reps[name]['n_safe']} (うち確2圏[最大>=HP/2]={safe_ch2} / 余裕[最大<HP/2]={safe_full})")

# raw summary line for structured output
print()
print('RAW_SUMMARY')
for name in CANDS:
    r=reps[name]
    print(f"{name}\tOHKO={r['n_ohko']}(確{r['n_sure']}/乱{r['n_rand']})\t先手OHKO={r['n_first']}\t非OHKO={r['n_safe']}")
