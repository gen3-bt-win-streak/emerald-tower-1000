## ①爆発価値項の実験ボット: search_choose のスコアに「岩鋼壁stuck時の爆発加点」を追加
## BOOM_BONUS=0 → 現行v4と完全同一(対照)。 BOOM_BONUS=B → stuck-vs-wall時のみ爆発候補に+B
## 使い方: BOOM_BONUS=5 python3 sim_boomvalue.py <BASE> <N>
import sys, os, collections, json, time
src=open('sim_v4marathon.py').read()
pre=src[:src.index('if __name__')]
ns={'__name__':'drv','__file__':'sim_v4marathon.py'}
exec(pre, ns)
G=ns['G']; MOVES=ns['MOVES']
gen_candidates=ns['gen_candidates']; should_search=ns['should_search']; rule_choose=ns['rule_choose']
rollout=ns['rollout']; apply_desc=ns['apply_desc']; _battle_no=ns['_battle_no']; max_hit=ns['max_hit']
S=ns['S']; R=ns['R']; MARGIN=ns['MARGIN']

BOOM_BONUS=float(os.environ.get('BOOM_BONUS','0'))

def _cand_has_boom(d):
    for a in d:
        if a and a[0]=='move' and MOVES.get(a[1],{}).get('effect')=='EFFECT_EXPLOSION':
            return True
    return False

def _gross_stuck_vs_wall(b):
    # グロスが手詰まり(どの敵も確定OHKO不能) かつ 爆発半減の岩/鋼が場に居る
    gross=next((m for m in b.active['us'] if m and m.alive() and m.species=='Metagross'),None)
    if gross is None: return False
    foes=[f for f in b.active['foe'] if f and f.alive()]
    if not foes: return False
    if any(max_hit(b,gross,f)>=f.hp for f in foes): return False        # どれか確定OHKOできるなら手詰まりでない
    if not any(('TYPE_ROCK' in f.types or 'TYPE_STEEL' in f.types) for f in foes): return False
    return True

def search_choose_bv(b):
    rule=rule_choose(b)
    if not should_search(b): return rule
    cands=gen_candidates(b,rule)
    if len(cands)<=1: return rule
    bno=_battle_no[0]
    scores=[]
    for ci,d in enumerate(cands):
        tot=0.0
        for s in range(S):
            wseed=(bno*7919+b.turn*131+s*17)&0x7FFFFFFF
            for k in range(R):
                rseed=(bno*104729+b.turn*257+ci*31+s*7+k)&0x7FFFFFFF
                tot+=rollout(b,d,wseed,rseed)
        scores.append(tot/(S*R))
    if BOOM_BONUS and _gross_stuck_vs_wall(b):
        for ci,d in enumerate(cands):
            if _cand_has_boom(d): scores[ci]+=BOOM_BONUS
    bi=max(range(len(cands)),key=lambda i:scores[i])
    if bi==0 or scores[bi]<scores[0]+MARGIN: return rule
    return apply_desc(b,cands[bi])

ns['search_choose']=search_choose_bv   # v3_choose が動的参照するので差し替わる

if __name__=='__main__':
    BASE=int(sys.argv[1]); N=int(sys.argv[2])
    play=G['play_battle']
    losses=[]; t0=time.time()
    for i in range(N):
        _battle_no[0]+=1
        _,r=play(seed=BASE+i)
        if r!='win': losses.append(BASE+i)
    tag=('bonus%g'%BOOM_BONUS).replace('.','_')
    out='boomval_losses_%d_%s.json'%(BASE,tag)
    json.dump({'BASE':BASE,'N':N,'BOOM_BONUS':BOOM_BONUS,'losses':losses}, open(out,'w'))
    print('[boomval BOOM_BONUS=%g] %d戦 負け%d (%.4f%%) %.0f戦/分 → %s'%(
        BOOM_BONUS,N,len(losses),100*len(losses)/N,N/(time.time()-t0)*60,out),flush=True)
