## v3統合ボット = sticky(安全不変条件) + 採用条項3 + 爆発釣りv2(暫定) + めざ氷4枠 + 攻IV最適化
## 条項優先順位: sticky不変 > エンテイ×ラティ開幕 > 炎×氷ピンサー > 麻痺爆発 > 爆発釣りv2
## 各実装は検証済みファイル(sim_userline_exp/sim_fireice_exp/sim_parboom_exp/sim_dp2_val)から字面移植
import sys, collections, random, copy, json, os, time
_z=open('sim_z11.py').read()
exec(_z[:_z.index("\nCASES=")])
G["SMART_SENDIN"]=0; RETREAT=True
NS["TH_GDANGER"]=1.3

# めざ氷70注入(特殊・こおり・命中/対象は冷凍ビーム準拠・追加効果なし)
MOVES["MOVE_HP_ICE"]=dict(MOVES["MOVE_ICE_BEAM"], power=70, effect="EFFECT_HIT")

def spec_v3():
    # v4確定ビルド: ラグ=たべのこし / グロス=せんせいのツメ+A164(H252/A164/B44/D44/S4)
    s=WRspec("Leftovers")                                        # ラグラージ持ち物=たべのこし
    z=list(s[0]); z[3]="Lum Berry"
    mv=list(z[4]); mv[1]="MOVE_HP_ICE"; z[4]=mv; s[0]=tuple(z)   # ドリルくちばし→めざ氷
    g=list(s[1]); g[3]="Quick Claw"                             # グロス持ち物=せんせいのツメ
    g[2]={"hp":252,"atk":164,"df":44,"spd":44,"spe":4}          # A252→A164, 余剰をB44/D44/S4へ(補遺20)
    s[1]=tuple(g)
    return s

rule_choose=z5_choose
max_hit=fair_maxhit
ai_choose=G["ai_choose"]; STAGE_KEYS=G["STAGE_KEYS"]

_bld0=team_builder(spec_v3())
def bld():
    t=_bld0()
    for m in t:
        # 攻IV最適化(混乱自傷の最小化): サンダー=IV2(めざ氷の奇偶条件内で最小) ラティ=IV0(物理技なし)
        if m.species=="Zapdos": m.stats["atk"]=168
        if m.species=="Latios": m.stats["atk"]=166
    return t

_s=open('sim_zsearch.py').read()
_mid=_s[_s.index("S=3; R=3"):_s.index("BASE=int")]
_mid=_mid.replace("S=3; R=3","S=5; R=5",1)
exec(_mid)
G["our_team"]=bld
G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
FIDELITY2=G.get("FIDELITY2", __import__('os').environ.get('FIDELITY2','1')=='1')

FIRE={'Charizard','Typhlosion','Ninetales','Entei','Houndoom','Arcanine','Rapidash','Magmar','Moltres','Blaziken'}
ICE={'Regice','Lapras','Cloyster','Walrein','Glalie','Articuno','Dewgong','Jynx','Starmie'}
GRASS={'Sceptile','Venusaur','Meganium','Ludicolo','Shiftry','Exeggutor','Victreebel','Vileplume','Tangela'}

def fair_maxhit_noboom(b,f,m):
    # 敵AIはHP50%超で爆発しないため、高HPの敵の爆発打点は脅威から除外(z_safe精密化・検証済み)
    best=0
    for fm in cand_moves(f):
        if fm not in MOVES or MOVES[fm]["power"]<2: continue
        if MOVES[fm].get("effect")=="EFFECT_EXPLOSION" and f.hp*2>f.max_hp: continue
        _,hi=b.pminmax(f,m,fm)
        best=max(best,hi)
    return best

def v3_trapped(b,m):
    # 実機仕様: ありじごく(飛行/ふゆう免除)・かげふみ・じりょく(鋼)。メニューで交代不可は判明する=情報公平
    if not FIDELITY2: return False
    foes=[f for f in b.active["foe"] if f is not None and f.alive()]
    return any(f.ability=="ABILITY_SHADOW_TAG" or
               (f.ability=="ABILITY_ARENA_TRAP" and "TYPE_FLYING" not in m.types and m.ability!="ABILITY_LEVITATE") or
               (f.ability=="ABILITY_MAGNET_PULL" and "TYPE_STEEL" in m.types) for f in foes)

def v3_choose(b):
    acts=search_choose(b)
    ours=[m for m in b.active["us"] if m and m.alive()]
    # ---- sticky不変条件(1): 爆発するなら相方は必ずまもる。まもれないなら爆発中止 ----
    boomer=None
    for m in ours:
        a=acts.get(m)
        if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION":
            boomer=m; break
    if boomer is not None:
        ally=next((x for x in ours if x is not boomer),None)
        if ally is not None and "TYPE_GHOST" not in ally.types:
            aa=acts.get(ally)
            protecting = aa and aa[0]=="move" and MOVES.get(aa[1],{}).get("effect")=="EFFECT_PROTECT"
            if not protecting:
                if "MOVE_PROTECT" in ally.moves and ally.protect_streak<1:
                    acts[ally]=("move","MOVE_PROTECT",ally)
                else:
                    rule=rule_choose(b); ra=rule.get(boomer)
                    rb = ra and ra[0]=="move" and MOVES.get(ra[1],{}).get("effect")=="EFFECT_EXPLOSION"
                    if ra is not None and not rb: acts[boomer]=ra
    # ---- sticky不変条件(2): ルールのグロス退避指示は保持(罠特性で交代不能なら強制しない) ----
    rule=rule_choose(b)
    gross=next((m for m in ours if m.species=="Metagross"),None)
    if gross is not None:
        ra=rule.get(gross)
        if ra is not None and ra[0]=="switch" and not v3_trapped(b,gross):
            acts[gross]=ra
    # ---- 種別条項(優先度順・1ターン1条項) ----
    foes=[f for f in b.active["foe"] if f and f.alive()]
    fsp={f.species for f in foes}
    z=next((m for m in ours if m.species=="Zapdos"),None)
    g2=next((m for m in ours if m.species=="Metagross"),None)
    clause=False
    # A) エンテイ×ラティ: 麻痺爆発ライン(ユーザー新案が旧・引きラインを置換。救済100%/回帰92.0→97.5)
    #    根拠: ラティはグロスを確1不能(最大44%)→T1まもる+電磁波→麻痺エンテイの上から爆発が構造保証
    if "Entei" in fsp and ("Latios" in fsp or "Latias" in fsp) and z is not None and g2 is not None:
        ent=next((f for f in foes if f.species=="Entei"),None)
        if ent is not None:
            if b.turn==1 and ent.status is None:
                acts[z]=("move","MOVE_THUNDER_WAVE",ent)
                if "MOVE_PROTECT" in g2.moves and g2.protect_streak<1:
                    acts[g2]=("move","MOVE_PROTECT",g2)
                clause=True
            elif ent.status=="PAR" and "MOVE_EXPLOSION" in g2.moves:
                acts[g2]=("move","MOVE_EXPLOSION",ent)
                if "MOVE_PROTECT" in z.moves and z.protect_streak<1:
                    acts[z]=("move","MOVE_PROTECT",z)
                clause=True
    # B) 炎×氷ピンサー条項
    if not clause and b.turn<=2:
        fire=next((f for f in foes if f.species in FIRE),None)
        icem=next((f for f in foes if f.species in ICE),None)
        grass=any(f.species in GRASS for f in foes)
        if fire is not None and icem is not None and not grass and z is not None and g2 is not None:
            if fair_maxhit(b,fire,g2)>=g2.hp and fair_maxhit(b,icem,z)>=z.hp:
                if b.turn==1:
                    recv=next((x for x in b.bench["us"] if x.alive() and x.species=="Swampert"),None)
                    if recv is not None and not v3_trapped(b,g2): acts[g2]=("switch",g2,recv)
                    if "MOVE_PROTECT" in z.moves and z.protect_streak<1:
                        acts[z]=("move","MOVE_PROTECT",z)
                    clause=True
                else:
                    swp=next((m for m in ours if m.species=="Swampert"),None)
                    if swp is not None and acts.get(swp,("x",))[0]!="switch":
                        acts[swp]=("move","MOVE_EARTHQUAKE",fire)
                        clause=True
    # C') 炎×2拡張(暫定): でんじは対象=グロス確1で先手の炎のうち最速
    if not clause:
        fires2=[f for f in foes if f.species in FIRE]
        if z is not None and g2 is not None and len(fires2)==2:
            gspe=g2.eff()["spe"]
            dang=[f for f in fires2 if fair_maxhit(b,f,g2)>=g2.hp and cand_max_spe(f)>gspe]
            if dang:
                tgt=max(dang,key=lambda f:cand_max_spe(f))
                if b.turn==1 and tgt.status is None:
                    acts[z]=("move","MOVE_THUNDER_WAVE",tgt)
                    if "MOVE_PROTECT" in g2.moves and g2.protect_streak<1:
                        acts[g2]=("move","MOVE_PROTECT",g2)
                    clause=True
                elif tgt.status=="PAR" and "MOVE_EXPLOSION" in g2.moves:
                    acts[g2]=("move","MOVE_EXPLOSION",tgt)
                    if "MOVE_PROTECT" in z.moves and z.protect_streak<1:
                        acts[z]=("move","MOVE_PROTECT",z)
                    clause=True
    # C) 麻痺爆発プラン
    if not clause:
        fires=[f for f in foes if f.species in FIRE]
        if z is not None and g2 is not None and len(fires)==1:
            fire=fires[0]
            others=[f for f in foes if f is not fire]
            danger = fair_maxhit(b,fire,g2)>=g2.hp and cand_max_spe(fire)>g2.eff()["spe"]
            z_safe = all(fair_maxhit_noboom(b,o,z)<z.hp for o in others)
            if danger and z_safe:
                if b.turn==1 and fire.status is None:
                    acts[z]=("move","MOVE_THUNDER_WAVE",fire)
                    if "MOVE_PROTECT" in g2.moves and g2.protect_streak<1:
                        acts[g2]=("move","MOVE_PROTECT",g2)
                    clause=True
                elif fire.status=="PAR" and "MOVE_EXPLOSION" in g2.moves:
                    acts[g2]=("move","MOVE_EXPLOSION",fire)
                    if "MOVE_PROTECT" in z.moves and z.protect_streak<1:
                        acts[z]=("move","MOVE_PROTECT",z)
                    clause=True
    # D) 爆発釣りv2(暫定): 敵爆発圏でこちら2枚まもる
    if not clause and len(ours)==2:
        boom_now=any(a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION"
                     for a in (acts.get(m) for m in ours))
        if not boom_now:
            threat=None
            for f in foes:
                if f.hp*2<=f.max_hp and any(MOVES.get(mv,{}).get("effect")=="EFFECT_EXPLOSION" for mv in cand_moves(f)):
                    threat=f; break
            if threat is not None:
                for m in ours:
                    if acts.get(m,("x",))[0]=="switch": continue
                    if "MOVE_PROTECT" in m.moves and m.protect_streak<1:
                        acts[m]=("move","MOVE_PROTECT",m)
                    else:
                        ba=best_attack(b,m,[threat],relax=True)
                        if ba: acts[m]=("move",ba[0],ba[1])
    # ---- 安全不変条件(3): ラス1自壊禁止 ----
    # 控えゼロ時、相方の生存が保証されない爆発は禁止(相打ちドロー=負け扱いのため支配的ルール)
    # 保証 = ゴースト / まもる計画かつ行動阻害(麻痺/眠り/氷/メロメロ/混乱)なし / 爆発最大ロールでも耐える
    boomer3=None
    for m in ours:
        a=acts.get(m)
        if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION":
            boomer3=m; break
    if boomer3 is not None and not any(x.alive() for x in b.bench["us"]):
        ally=next((x for x in ours if x is not boomer3),None)
        ok=False
        if ally is not None and ally.alive():
            aa=acts.get(ally)
            blocked = ally.status in ("PAR","SLP","FRZ") or ally.attract or ally.cnf>0
            prot = aa and aa[0]=="move" and MOVES.get(aa[1],{}).get("effect")=="EFFECT_PROTECT" and ally.protect_streak<1
            if "TYPE_GHOST" in ally.types or (prot and not blocked): ok=True
            else:
                try:
                    a_=dict(species=boomer3.species,stats=boomer3.eff(),types=boomer3.types,ability=boomer3.ability,item=boomer3.item,level=100)
                    d_=dict(species=ally.species,stats=ally.eff(),types=ally.types,ability=ally.ability,item=None,level=100)
                    _,hi=damage_range(a_,d_,acts[boomer3][1])
                    if hi<ally.hp: ok=True
                except Exception: pass
        if not ok:
            rule3=rule_choose(b); ra=rule3.get(boomer3)
            rb = ra and ra[0]=="move" and MOVES.get(ra[1],{}).get("effect")=="EFFECT_EXPLOSION"
            if ra is not None and not rb:
                acts[boomer3]=ra
            else:
                foes3=[f for f in b.active["foe"] if f and f.alive()]
                ba=best_attack(b,boomer3,foes3,relax=True)
                if ba: acts[boomer3]=("move",ba[0],ba[1])
    return acts
G["our_choose"]=v3_choose
G["PIVOT_AI"]=True  # 関所3: 敵AIの不利対面ピボット交代(#5/#6)を有効化してPIVOT_ONマラソンを回す


if __name__=="__main__":
    BASE=int(sys.argv[1]); START=int(sys.argv[2]); N=int(sys.argv[3])
    # seed範囲 [BASE+START, BASE+START+N)。連勝統計は集計時に負けシード列から各250kブロック単位で再計算する
    CKPT="pivotm_ckpt_%d_%d.json"%(BASE,START)
    st=dict(i=0,losses=[],streak=0,best=0,run_start=BASE+START,s250=0,s500=0,s750=0,s1000=0,base=BASE,start=START,count=N)
    if os.path.exists(CKPT): st.update(json.load(open(CKPT)))
    t0=time.time(); i0=st["i"]
    def event(kind,seed,streak):
        open("milestones_pivot.jsonl","a").write(json.dumps(dict(w=BASE,start=START,kind=kind,run_start=st["run_start"],hit=seed,streak=streak))+"\n")
    while st["i"]<N:
        seed=BASE+START+st["i"]
        _battle_no[0]=(START+st["i"])+1
        _,r=G["play_battle"](seed=seed)
        if r=="win":
            st["streak"]+=1
            s=st["streak"]
            if s in (250,500,750,1000):
                st["s%d"%s]+=1
                if s==1000: event("S1000",seed,s)
            if s>st["best"]:
                st["best"]=s
                if s==1458 or (s>1458 and s%100==0): event("NEWBEST",seed,s)  # プロジェクト歴代最長1458の更新のみ即時
        else:
            st["losses"].append(seed)
            st["streak"]=0; st["run_start"]=seed+1
        st["i"]+=1
        if st["i"]%1000==0:
            json.dump(st,open(CKPT,"w"))
            print("[W%d+%d] %d/%d 負け%d(%.3f%%) 連勝中%d 最長%d(chunk内) %d戦/分"%(
                BASE,START,st["i"],N,len(st["losses"]),100*len(st["losses"])/st["i"],st["streak"],st["best"],
                (st["i"]-i0)/max(1,(time.time()-t0)/60)),flush=True)
    json.dump(st,open(CKPT,"w"))
    print("[W%d+%d] 完走 %d戦 負け%d(%.3f%%)"%(BASE,START,N,len(st["losses"]),100*len(st["losses"])/N),flush=True)
