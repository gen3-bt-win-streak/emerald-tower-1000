## ①爆発価値項が「発火(stuck-vs-wall)」し「決定を変える(flip)」頻度を計測。不発 vs 無効の切り分け用。
import sys, os
src=open('sim_v4marathon.py').read()
pre=src[:src.index('if __name__')]
ns={'__name__':'drv','__file__':'sim_v4marathon.py'}
exec(pre, ns)
G=ns['G']; MOVES=ns['MOVES']
gen_candidates=ns['gen_candidates']; should_search=ns['should_search']; rule_choose=ns['rule_choose']
rollout=ns['rollout']; apply_desc=ns['apply_desc']; _battle_no=ns['_battle_no']; max_hit=ns['max_hit']
S=ns['S']; R=ns['R']; MARGIN=ns['MARGIN']
BOOM_BONUS=5.0
CNT={'decisions':0,'stuck_fire':0,'flip':0}
def _cand_has_boom(d):
    return any(a and a[0]=='move' and MOVES.get(a[1],{}).get('effect')=='EFFECT_EXPLOSION' for a in d)
def _stuck(b):
    g=next((m for m in b.active['us'] if m and m.alive() and m.species=='Metagross'),None)
    if g is None: return False
    foes=[f for f in b.active['foe'] if f and f.alive()]
    if not foes or any(max_hit(b,g,f)>=f.hp for f in foes): return False
    return any(('TYPE_ROCK' in f.types or 'TYPE_STEEL' in f.types) for f in foes)
def sc(b):
    rule=rule_choose(b)
    if not should_search(b): return rule
    cands=gen_candidates(b,rule)
    if len(cands)<=1: return rule
    CNT['decisions']+=1
    bno=_battle_no[0]; scores=[]
    for ci,d in enumerate(cands):
        tot=0.0
        for s in range(S):
            wseed=(bno*7919+b.turn*131+s*17)&0x7FFFFFFF
            for k in range(R):
                rseed=(bno*104729+b.turn*257+ci*31+s*7+k)&0x7FFFFFFF
                tot+=rollout(b,d,wseed,rseed)
        scores.append(tot/(S*R))
    base_bi=max(range(len(cands)),key=lambda i:scores[i])
    if _stuck(b):
        CNT['stuck_fire']+=1
        sc2=list(scores)
        for ci,d in enumerate(cands):
            if _cand_has_boom(d): sc2[ci]+=BOOM_BONUS
        new_bi=max(range(len(cands)),key=lambda i:sc2[i])
        if new_bi!=base_bi: CNT['flip']+=1
    bi=base_bi
    if bi==0 or scores[bi]<scores[0]+MARGIN: return rule
    return apply_desc(b,cands[bi])
ns['search_choose']=sc
if __name__=='__main__':
    BASE=int(sys.argv[1]); N=int(sys.argv[2]); play=G['play_battle']
    for i in range(N):
        _battle_no[0]+=1; play(seed=BASE+i)
    print('[firecount base=%d N=%d] 探索決定=%d / stuck-vs-wall発火=%d / 決定変更flip=%d'%(
        BASE,N,CNT['decisions'],CNT['stuck_fire'],CNT['flip']))
