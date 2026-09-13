# 20k-battle stats run with loss categorization
exec(open('sim.py').read())
import collections, json

N=20000
res=collections.Counter()
loss_cat=collections.Counter(); loss_flags=collections.Counter()
loss_detail=[]
FORTRESS_LEADS={"Snorlax","Blissey","Chansey","Umbreon","Tyranitar","Metagross","Registeel","Regirock","Regice","Steelix","Shuckle","Porygon2","Miltank","Dusclops"}
turns_sum=0
for i in range(N):
    b,r=play_battle(seed=100000+i)
    res[r]+=1; turns_sum+=b.turn
    if r!="loss": continue
    leads={m.species for m in b.foe[:2]}
    if leads & {"Wobbuffet"}: cat="wobbuffet"
    elif leads & FIRE_RETREAT: cat="fire"
    elif leads & REGI_SP: cat="regi"
    elif leads & DAMP_SP: cat="damp"
    elif len(leads & GHOST_SP)>=1: cat="ghost"
    elif leads & FORTRESS_LEADS: cat="fortress_lead"
    else: cat="default_boom"
    loss_cat[cat]+=1
    for k in ("ohko_hit_us","crit_us","miss_us","protect_fail_us","perish_kill_us","full_para_us","attract_us","twave_us","confusion_self","sleep_try","counter_hit_foe","focus_band","destiny","timeout","fp_broken"):
        if b.flags.get(k): loss_flags[k]+=1
    loss_detail.append(dict(seed=100000+i,tid=b.tid,cat=cat,turns=b.turn,
        foe=[[m.species,m.set_id] for m in b.foe],
        foe_left=[m.species for m in b.foe if m.alive()],
        flags={k:v for k,v in b.flags.items() if v}))
out=dict(n=N,win=res["win"],loss=res["loss"],loss_rate=res["loss"]/N,
         avg_turns=turns_sum/N,loss_by_category=dict(loss_cat),
         loss_flag_incidence=dict(loss_flags))
json.dump(out,open("sim20k_summary.json","w"),indent=1,ensure_ascii=False)
json.dump(loss_detail,open("sim20k_losses.json","w"),ensure_ascii=False)
print(json.dumps(out,indent=1,ensure_ascii=False))
top=collections.Counter()
for d in loss_detail:
    top[tuple(sorted(x[0] for x in d["foe"][:2]))]+=1
print("top losing lead pairs:",top.most_common(15))
