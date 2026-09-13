## Z 第5波アーム: S=賢い交代出し(公平版) / R=グロス即死圏退避
import collections
_src=open('sim_z4.py').read()
exec(_src[:_src.index("N=20000")])
ARM["fire"]=False; ARM["focus"]=True; ARM["pair"]=True
cand_entries=G["cand_entries"]; cand_moves=G["cand_moves"]
def spec_v04():
    s=WRspec("Quick Claw")
    z=list(s[0]); z[3]="Lum Berry"; s[0]=tuple(z)
    g=list(s[1]); g[3]="Leftovers"; g[2]={"hp":252,"atk":164,"df":46,"spd":46}; s[1]=tuple(g)
    return s
def fair_maxhit(b,f,m):
    best=0
    for fm in cand_moves(f):
        if fm not in MOVES or MOVES[fm]["power"]<2: continue
        _,hi=b.pminmax(f,m,fm)
        best=max(best,hi)
    return best
def cand_max_spe(f):
    es=cand_entries(f)
    return max((e["stats31"]["spe"] for e in es),default=0)
RETREAT=False
def z5_choose(b):
    acts=z_choose(b)
    if not RETREAT: return acts
    ours=[m for m in b.active["us"] if m and m.alive()]
    foes=[f for f in b.active["foe"] if f and f.alive()]
    gross=next((m for m in ours if m.species=="Metagross"),None)
    if gross is None or not foes: return acts
    a=acts.get(gross)
    if a is None or a[0]=="switch": return acts
    booming = a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION"
    gspe=gross.eff()["spe"]
    # 即死圏×先手を取られる敵がいる場合のみ。爆発プランでも相手が先なら無意味なので退避
    lethal=[f for f in foes if fair_maxhit(b,f,gross)>=gross.hp and cand_max_spe(f)>gspe]
    if not lethal: return acts
    if booming and all(cand_max_spe(f)<=gspe for f in foes): return acts
    bench=[x for x in b.bench["us"] if x.alive()]
    if not bench: return acts
    recv=min(bench,key=lambda c: sum(fair_maxhit(b,f,c) for f in foes)/max(1,c.max_hp))
    # 受け先も即死圏なら退避の意味なし
    if sum(fair_maxhit(b,f,recv) for f in foes)>=recv.max_hp*2: return acts
    acts[gross]=("switch",gross,recv)
    return acts
N=20000
CASES=[("v0.4基準",0,False),("S賢い交代出し",1,False),("Rグロス退避",0,True),("S+R",1,True)]
for label,ss,rt in CASES:
    G["SMART_SENDIN"]=ss
    globals()["RETREAT"]=rt
    G["our_team"]=team_builder(spec_v04()); G["our_choose"]=z5_choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    res=collections.Counter()
    for i in range(N):
        b,r=G["play_battle"](seed=100000+i)
        res[r]+=1
    print("%-14s %.3f%%"%(label,100*res["loss"]/N),flush=True)
