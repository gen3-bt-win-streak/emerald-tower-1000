## 人間政策 実験ボット(プレイブック§4.5の再現コード・統合版)
## 使い方: HPOLICY=v1|v2a|v2b|v2c|v2d PYTHONHASHSEED=0 FIDELITY2=1 python3 sim_humanpolicy.py <off> <N>
##   seeds = 25,000,000+off .. +N。v4公式ベースライン(v4m_ckpt_*)と同一シードでペア比較する。
## モード(§4.5の実験系列):
##   v1  = 反射規則のみ(探索OFF)                        → 0.85% (1万戦)
##   v2a = v1 + 汎用「危険→まもる」全廃(TH_GDANGER=999) → 1.14% (悪化)
##   v2b = v1 + まもる中に合算確1があれば2枚がけ優先     → 0.99% (悪化)
##   v2c = T1-T2のみ探索 / T3+は反射                    → 0.60% (2千戦・不足)
##   v2d = 敵が2体立っている間は探索 / ラス1体で反射     → 0.10% = 公式と完全一致(不一致0/2000)
import json,sys,os
MODE=os.environ.get("HPOLICY","v1")
off=int(sys.argv[1]); N=int(sys.argv[2]); BASE=25000000
src=open('sim_v4marathon.py').read(); ns={'__name__':'drv','__file__':'sim_v4marathon.py'}
exec(src[:src.index('if __name__')], ns)
search=ns['search_choose']; rule=ns['rule_choose']
MOVES=ns['MOVES']; best_attack=ns['best_attack']

if MODE=="v1":
    ns['search_choose']=rule
elif MODE=="v2a":
    ns['NS']['TH_GDANGER']=999.0
    ns['search_choose']=rule
elif MODE=="v2b":
    def h2(b):
        acts=rule(b)
        ours=[m for m in b.active["us"] if m and m.alive()]
        foes=[f for f in b.active["foe"] if f and f.alive()]
        if len(ours)==2 and foes:
            prot=any(acts.get(m) and acts[m][0]=="move" and MOVES.get(acts[m][1],{}).get("effect")=="EFFECT_PROTECT" for m in ours)
            boom=any(acts.get(m) and acts[m][0]=="move" and MOVES.get(acts[m][1],{}).get("effect")=="EFFECT_EXPLOSION" for m in ours)
            sw=any(acts.get(m) and acts[m][0]=="switch" for m in ours)
            if prot and not boom and not sw:
                for f in foes:
                    parts=[]
                    for m in ours:
                        ba=best_attack(b,m,[f],relax=True)
                        if not ba: parts=None; break
                        parts.append((m,ba))
                    if parts and sum(ba[2] for _,ba in parts)>=1.0:
                        for m,ba in parts: acts[m]=("move",ba[0],f)
                        break
        return acts
    ns['search_choose']=h2
elif MODE=="v2c":
    def h4(b): return search(b) if b.turn<=2 else rule(b)
    ns['search_choose']=h4
elif MODE=="v2d":
    def h5(b):
        foes=[f for f in b.active["foe"] if f and f.alive()]
        bench=[x for x in b.bench["foe"] if x.alive()]
        return search(b) if (len(foes)+len(bench))>=3 or len(foes)==2 else rule(b)
    ns['search_choose']=h5
else:
    raise SystemExit("HPOLICY must be v1|v2a|v2b|v2c|v2d")

G=ns['G']; play=G['play_battle']; _bn=ns['_battle_no']
losses=[]
for i in range(off,off+N):
    _bn[0]=i+1
    b,r=play(seed=BASE+i)
    if r!='win': losses.append(BASE+i)
out="hpol_%s_%d.json"%(MODE,off)
json.dump(dict(mode=MODE,losses=losses,start=off,N=N),open(out,"w"))
print("[%s] done off=%d N=%d losses=%d (%.2f%%) -> %s"%(MODE,off,N,len(losses),100*len(losses)/N,out))
