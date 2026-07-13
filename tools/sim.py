# -*- coding: utf-8 -*-
# Gen3 Emerald Battle Tower (Doubles, Open Level, battles 50+) full-battle simulator v0
# Built on calc_matchups.py (damage engine + enemy pool). Approximations tagged APPROX.
import random, collections, csv as _csv, json, sys

exec(open('calc_matchups.py').read().split("# ---------- Analysis 1")[0])

# ---------------- constants ----------------
FIRE_RETREAT = {"Charizard","Typhlosion","Ninetales","Entei","Houndoom","Arcanine","Rapidash","Magmar","Moltres","Blaziken"}
GHOST_SP = {"Gengar","Misdreavus","Dusclops","Shedinja","Banette","Sableye"}
DAMP_SP  = {"Golduck","Quagsire"}
REGI_SP  = {"Regirock","Regice","Registeel"}
OHKO_EFF = "EFFECT_OHKO"
# species-level physical ban (counter reflect kill range) per 01
CTR_BAN_SP = {"Snorlax","Regirock","Registeel","Tyrannitar","Tyranitar","Wobbuffet","Quagsire"}
FP_BREAK = True
SLEEP_EFFECTS = {"EFFECT_SLEEP"}
SECONDARY = {  # move -> (kind, chance%)  APPROX: common ones only
 "MOVE_THUNDERBOLT":("PAR",10),"MOVE_THUNDER":("PAR",30),"MOVE_BODY_SLAM":("PAR",30),
 "MOVE_ICE_BEAM":("FRZ",10),"MOVE_BLIZZARD":("FRZ",10),"MOVE_ICE_PUNCH":("FRZ",10),
 "MOVE_FLAMETHROWER":("BRN",10),"MOVE_FIRE_BLAST":("BRN",10),"MOVE_FIRE_PUNCH":("BRN",10),
 "MOVE_OVERHEAT":("SPA2DOWN_SELF",100),"MOVE_PSYCHIC":("SPDDOWN",10),
 "MOVE_SLUDGE_BOMB":("PSN",30),"MOVE_POISON_JAB":("PSN",30),"MOVE_CRUNCH":("SPDDOWN",20),
 "MOVE_SHADOW_BALL":("SPDDOWN",20),"MOVE_ROCK_SLIDE":("FLINCH",30),"MOVE_IRON_TAIL":("DFDOWN",30),
 "MOVE_HEADBUTT":("FLINCH",30),"MOVE_BITE":("FLINCH",30),"MOVE_ASTONISH":("FLINCH",30),
 "MOVE_DYNAMIC_PUNCH":("CNF",100),"MOVE_ICY_WIND":("SPEDOWN",100),"MOVE_MUD_SHOT":("SPEDOWN",100),
 "MOVE_METEOR_MASH":("ATKUP_SELF",20),
}
RECOIL = {"MOVE_DOUBLE_EDGE":3,"MOVE_VOLT_TACKLE":3,"MOVE_TAKE_DOWN":4,"MOVE_SUBMISSION":4}  # 1/n
GENDERLESS = {"Metagross","Regirock","Regice","Registeel","Magneton","Electrode","Claydol","Starmie","Porygon2","Shedinja","Lunatone","Solrock","Baltoy","Beldum","Metang","Voltorb","Staryu","Porygon","Ditto"}

STAGE_KEYS = ("atk","df","spa","spd","spe")
def stage_mult(n):
    return (2+n)/2 if n>=0 else 2/(2-n)
def acc_mult(n):
    return (3+n)/3 if n>=0 else 3/(3-n)

# ---------------- Mon ----------------
class Mon:
    def __init__(self, species, types, ability, item, stats, moves, side, set_id=None, gender=None):
        self.species=species; self.types=list(types); self.ability=ability; self.item=item
        self.stats=dict(stats); self.max_hp=stats["hp"]; self.hp=stats["hp"]
        self.moves=list(moves); self.side=side; self.set_id=set_id
        # foe genders are re-drawn seed-deterministically in Battle.__init__
        # (a bare random.choice here leaked module-RNG state across battles
        #  and broke (seed,event_seed) reproducibility)
        self.gender = gender if gender is not None else (None if species in GENDERLESS else "M")
        self.status=None; self.slp=0; self.toxn=0
        self.stages={k:0 for k in STAGE_KEYS}; self.acc_st=0; self.eva_st=0
        self.sub=0; self.cnf=0; self.attract=False
        self.protect_streak=0; self.protected=False
        self.choice=None; self.perish=None
        self.charging=None  # (move, target) for solarbeam; 'FP' focus punch pending
        self.truant=False; self.flinch=False
        self.dmg_phys=(0,None); self.dmg_spec=(0,None)  # (amount, attacker) this turn
        self.took_dmg=False; self.destiny=False
        self.item_used=False  # berries/focus band one-shot flags handled ad hoc
        self.observed=set()   # moves this mon has revealed (set-elimination basis)
        self.endure=False; self.endure_streak=0; self.recharge=False
        self.drowsy=0; self.trapped=False; self.invuln=False; self.first_turn=True
        self.tormented=False; self.last_move=None
    def alive(self): return self.hp>0
    def eff(self, crit_att=False, crit_def=False):
        s=dict(self.stats)
        for k in STAGE_KEYS:
            st=self.stages[k]
            if crit_att and k in ("atk","spa") and st<0: st=0
            if crit_def and k in ("df","spd") and st>0: st=0
            s[k]=max(1,int(s[k]*stage_mult(st)))
        if self.status=="BRN": s["atk"]=max(1,s["atk"]//2)
        if self.status=="PAR": s["spe"]=max(1,s["spe"]//4)
        return s

def our_team():
    if GENGAR_BUILD=="attacker":
        g = make("Gengar","Timid",{"spa":252,"spe":252,"hp":4},"Lum Berry",
              ["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_THUNDERBOLT","MOVE_GIGA_DRAIN"])
    else:
        g = make("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",
              ["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_SUBSTITUTE","MOVE_GIGA_DRAIN"])
    m  = make("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",
              ["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"])
    k  = make("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",
              ["MOVE_SELF_DESTRUCT","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_PROTECT"])
    l  = make("Latios","Timid",{"spa":252,"spe":252,"hp":4},"Bright Powder",
              ["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"])
    team=[]
    for d,ab,gen in ((g,"ABILITY_LEVITATE","M"),(m,"ABILITY_CLEAR_BODY",None),(k,"ABILITY_THICK_FAT","M"),(l,"ABILITY_LEVITATE","M")):
        team.append(Mon(d["species"],d["types"],ab,d["item"],d["stats"],d["moves"],"us",gender=gen))
    return team  # [Gengar, Metagross, Snorlax, Latios]

# trainer table
TRAINERS=[]
for r in _csv.DictReader(open(f"{DATA}/trainers.csv")):
    tid=int(r["trainer_id"])
    if 200<=tid<=299:
        TRAINERS.append((tid,int(r["fixed_iv"]),[int(x) for x in r["set_ids"].split("|") if x]))
BYID={e["set_id"]:e for e in pool}

def enemy_team(rng):
    tid,iv,ids=rng.choice(TRAINERS)
    team=[]; sp=set(); it=set()
    cand=ids[:]; rng.shuffle(cand)
    for i in cand:
        e=BYID.get(i)
        if e is None: continue
        if e["species"] in sp or (e["item"] and e["item"] in it): continue
        abil=[a for a in e["abilities"] if a!="ABILITY_NONE"]
        ab=rng.choice(abil) if abil else "ABILITY_NONE"
        st=e["stats31"] if iv>=31 else e["stats21"]
        team.append(Mon(e["species"],e["types"],ab,e["item"],st,e["moves"],"foe",set_id=e["set_id"]))
        sp.add(e["species"]); it.add(e["item"])
        if len(team)==4: break
    return tid,team

# ---------------- battle state ----------------
class Battle:
    def __init__(self, seed=None, event_seed=None):
        rngd=random.Random(seed)
        self.rng=random.Random(event_seed) if event_seed is not None else rngd
        self.us=our_team()
        self.tid,self.foe=enemy_team(rngd)
        grng=random.Random((0 if seed is None else seed)^0xA5F00D)
        for _m in self.foe:
            if _m.gender is not None: _m.gender=grng.choice("MF")
        self.enemy_iv=next((iv for t,iv,_ in TRAINERS if t==self.tid),31)
        self.active={"us":[self.us[0],self.us[1]],"foe":[self.foe[0],self.foe[1]]}
        self.bench={"us":[self.us[2],self.us[3]],"foe":self.foe[2:]}
        self.weather=None; self.wturns=0
        self.screens={"foe_reflect":0,"foe_light":0}
        self.turn=0; self.log=[]; self.flags=collections.Counter()
        self.boom_plan=True
        for mon in self.active["foe"]:
            if mon.ability=="ABILITY_INTIMIDATE": pass  # applied on send-in below
        for side in ("us","foe"):
            for mon in self.active[side]: self.on_entry(mon)
        if any(m.ability=="ABILITY_SAND_STREAM" for m in self.active["foe"]):
            self.weather="sand"; self.wturns=9999
    def lg(self,s):
        if VERBOSE: self.log.append("T%d %s"%(self.turn,s))
    def foes_of(self,mon): return [m for m in self.active["foe" if mon.side=="us" else "us"] if m and m.alive()]
    def ally_of(self,mon):
        pair=self.active[mon.side]
        for m in pair:
            if m is not mon and m and m.alive(): return m
        return None
    def on_entry(self,mon):
        if mon.ability=="ABILITY_INTIMIDATE":
            for f in self.foes_of(mon):
                if f.ability not in ("ABILITY_CLEAR_BODY","ABILITY_HYPER_CUTTER","ABILITY_WHITE_SMOKE"):
                    f.stages["atk"]=max(-6,f.stages["atk"]-1)
        if mon.ability=="ABILITY_DROUGHT": self.weather="sun"; self.wturns=9999
        if mon.ability=="ABILITY_DRIZZLE": self.weather="rain"; self.wturns=9999
        if mon.ability=="ABILITY_SAND_STREAM": self.weather="sand"; self.wturns=9999

    # ---------- damage ----------
    def calc(self, att, dfd, move, crit=False, spread=False):
        eff=MOVES[move]["effect"]
        if eff=="EFFECT_FLAIL":
            frac=att.hp/att.max_hp
            pw=20 if frac>0.6874 else 40 if frac>0.3542 else 80 if frac>0.2083 else 100 if frac>0.1042 else 150 if frac>0.0417 else 200
            MOVES["__TMP__"]=dict(MOVES[move],power=pw); move="__TMP__"
        elif eff=="EFFECT_FACADE" and att.status in ("BRN","PSN","TOX","PAR"):
            MOVES["__TMP__"]=dict(MOVES[move],power=MOVES[move]["power"]*2); move="__TMP__"
        a=dict(species=att.species,stats=att.eff(crit_att=crit),types=att.types,ability=att.ability,item=att.item,level=100)
        d=dict(species=dfd.species,stats=dfd.eff(crit_def=crit),types=dfd.types,ability=dfd.ability,item=None,level=100)
        lo,hi=damage_range(a,d,move,crit=crit)
        if hi==0: return 0
        dmg=self.rng.randint(lo,hi)
        mt=MOVES[move]["type"]
        if self.weather=="sun":
            if mt=="TYPE_FIRE": dmg=int(dmg*1.5)
            if mt=="TYPE_WATER": dmg//=2
        elif self.weather=="rain":
            if mt=="TYPE_WATER": dmg=int(dmg*1.5)
            if mt=="TYPE_FIRE": dmg//=2
        if spread: dmg//=2
        if dfd.side=="us" and False: pass
        if att.side=="us":
            if self.screens["foe_reflect"]>0 and mt in PHYSICAL and not crit: dmg//=2
            if self.screens["foe_light"]>0 and mt not in PHYSICAL and not crit: dmg//=2
        return max(1,dmg)

    def pminmax(self, att, dfd, move, spread=False):
        """info-fair damage estimate: worst case over the defender's / attacker's candidate sets"""
        iv=getattr(self,"enemy_iv",31)
        if dfd.side=="foe" and att.side=="us":
            key=("out",att.species,tuple(sorted(att.stages.items())),att.status,att.item,dfd.species,frozenset(dfd.observed),move,iv,spread)
            fr=_PM_CACHE.get(key)
            if fr is None:
                lo_f=None; hi_f=None
                a=dict(species=att.species,stats=att.eff(),types=att.types,ability=att.ability,item=att.item,level=100)
                for e in cand_entries(dfd):
                    st=e["stats31"] if iv>=31 else e["stats21"]
                    for ab in set(x for x in e["abilities"] if x!="ABILITY_NONE") or {"ABILITY_NONE"}:
                        d=dict(species=dfd.species,stats=st,types=e["types"],ability=ab,item=None,level=100)
                        lo,hi=damage_range(a,d,move)
                        lof,hif=lo/st["hp"],hi/st["hp"]
                        lo_f=lof if lo_f is None or lof<lo_f else lo_f
                        hi_f=hif if hi_f is None or hif<hi_f else hi_f
                if lo_f is None: lo_f=hi_f=0.0
                fr=(lo_f,hi_f); _PM_CACHE[key]=fr
            lo=int(fr[0]*dfd.max_hp); hi=int(fr[1]*dfd.max_hp)
            if spread: lo//=2; hi//=2
            return lo,hi
        if att.side=="foe" and dfd.side=="us":
            if move not in cand_moves(att): return (0,0)
            key=("in",att.species,frozenset(att.observed),att.status,dfd.species,tuple(sorted(dfd.stages.items())),move,iv,spread)
            v=_PM_CACHE.get(key)
            if v is None:
                hi_m=0; lo_m=None
                d=dict(species=dfd.species,stats=dfd.eff(),types=dfd.types,ability=dfd.ability,item=None,level=100)
                for e in cand_entries(att):
                    if move not in e["moves"]: continue
                    st=e["stats31"] if iv>=31 else e["stats21"]
                    st=dict(st)
                    if att.status=="BRN": st["atk"]=max(1,st["atk"]//2)
                    a=dict(species=att.species,stats=st,types=e["types"],ability=e["abilities"][0],item=e["item"],level=100)
                    lo,hi=damage_range(a,d,move)
                    hi_m=max(hi_m,hi); lo_m=lo if lo_m is None or lo<lo_m else lo_m
                v=(lo_m or 0,hi_m); _PM_CACHE[key]=v
            lo,hi=v
            if spread: lo//=2; hi//=2
            return lo,hi
        return self.minmax(att,dfd,move,spread=spread)

    def minmax(self, att, dfd, move, spread=False):
        a=dict(species=att.species,stats=att.eff(),types=att.types,ability=att.ability,item=att.item,level=100)
        d=dict(species=dfd.species,stats=dfd.eff(),types=dfd.types,ability=dfd.ability,item=None,level=100)
        lo,hi=damage_range(a,d,move)
        if spread: lo//=2; hi//=2
        return lo,hi

    # ---------- apply hit ----------
    def deal(self, att, dfd, move, dmg):
        mt=MOVES[move]["type"]
        if dfd.sub>0 and move!="MOVE_ATTRACT":
            dfd.sub-=dmg
            self.lg("%s sub took %d (%s)"%(dfd.species,dmg,move))
            if dfd.sub<=0: dfd.sub=0; self.lg("%s sub broke"%dfd.species)
            return 0
        real=min(dfd.hp,dmg)
        if dfd.endure and real>=dfd.hp:
            real=dfd.hp-1; self.flags["endure"]+=1
        elif dfd.item=="Focus Band" and real>=dfd.hp and self.rng.random()<0.10:
            real=dfd.hp-1; self.flags["focus_band"]+=1
        dfd.hp-=real; dfd.took_dmg=True
        if mt in PHYSICAL: dfd.dmg_phys=(real,att)
        else: dfd.dmg_spec=(real,att)
        if dfd.item in ("Lum Berry","Chesto Berry","Sitrus Berry") and not dfd.item_used:
            pass  # handled at status/hp check points
        if att.item=="Shell Bell":
            att.hp=min(att.max_hp,att.hp+max(1,real//8))
        self.lg("%s -> %s %s %d dmg (hp %d/%d)"%(att.species,dfd.species,move,real,max(0,dfd.hp),dfd.max_hp))
        if dfd.hp<=0:
            self.lg("%s fainted"%dfd.species)
            if dfd.destiny and att.alive() and att is not dfd:
                att.hp=0; self.lg("destiny bond killed %s"%att.species); self.flags["destiny"]+=1
        else:
            if dfd.item=="Sitrus Berry" and not dfd.item_used and dfd.hp<=dfd.max_hp//2:
                dfd.hp=min(dfd.max_hp,dfd.hp+30); dfd.item_used=True
        return real

    def try_status(self, dfd, st):
        if not dfd.alive(): return False
        if dfd.sub>0 and st!="ATT": return False
        if st=="SLP":
            if dfd.status: return False
            if dfd.ability in ("ABILITY_INSOMNIA","ABILITY_VITAL_SPIRIT"): return False
            if any(m.ability=="ABILITY_SOUNDPROOF" for m in [dfd]) : pass
            dfd.status="SLP"; dfd.slp=self.rng.randint(1,4)
        elif st=="PAR":
            if dfd.status or dfd.ability=="ABILITY_LIMBER" or "TYPE_GROUND" in dfd.types and False: return False
            dfd.status="PAR"
        elif st=="BRN":
            if dfd.status or "TYPE_FIRE" in dfd.types or dfd.ability=="ABILITY_WATER_VEIL": return False
            dfd.status="BRN"
        elif st=="FRZ":
            if dfd.status or "TYPE_ICE" in dfd.types: return False
            dfd.status="FRZ"
        elif st in ("PSN","TOX"):
            if dfd.status or "TYPE_POISON" in dfd.types or "TYPE_STEEL" in dfd.types or dfd.ability=="ABILITY_IMMUNITY": return False
            dfd.status=st; dfd.toxn=1
        elif st=="CNF":
            if dfd.cnf>0 or dfd.ability=="ABILITY_OWN_TEMPO": return False
            dfd.cnf=self.rng.randint(2,5)
        # Lum
        if dfd.item=="Lum Berry" and not dfd.item_used and dfd.status:
            dfd.status=None; dfd.slp=0; dfd.item_used=True; self.lg("%s Lum cured"%dfd.species); return True
        if dfd.item=="Chesto Berry" and not dfd.item_used and dfd.status=="SLP":
            dfd.status=None; dfd.slp=0; dfd.item_used=True; return True
        self.lg("%s got %s"%(dfd.species,st))
        return True

    # ---------- move execution ----------
    def accuracy_ok(self, att, dfd, move):
        if dfd.invuln: return False
        acc=MOVES[move]["accuracy"]
        if MOVES[move]["effect"]==OHKO_EFF:
            return self.rng.random()<0.30
        if acc==0: return True
        mult=acc_mult(att.acc_st)/acc_mult(dfd.eva_st)
        if dfd.item=="Bright Powder": mult*=0.9
        if dfd.item=="Lax Incense": mult*=0.95
        if self.weather=="sun" and move=="MOVE_THUNDER": acc=50
        if self.weather=="rain" and move=="MOVE_THUNDER": return True
        return self.rng.random() < (acc/100.0)*mult

    def execute(self, att, action):
        kind=action[0]
        if kind!="move": return
        move,target=action[1],action[2]
        if not att.alive(): return
        if att.flinch: att.flinch=False; self.lg("%s flinched"%att.species); return
        if att.truant: att.truant=False; self.lg("%s loafing"%att.species); return
        if att.ability=="ABILITY_TRUANT": att.truant=True
        # status checks
        if att.recharge:
            att.recharge=False; self.lg("%s recharging"%att.species); return
        if att.status=="SLP":
            att.slp-=1
            if att.slp<=0: att.status=None; self.lg("%s woke"%att.species)
            else:
                if "MOVE_SLEEP_TALK" in att.moves:
                    alts=[x for x in att.moves if x!="MOVE_SLEEP_TALK" and x in MOVES and MOVES[x]["power"]>=2]
                    if alts:
                        move=self.rng.choice(alts); mvst=MOVES[move]
                        self.lg("%s sleep-talks %s"%(att.species,move))
                        target=action[2]
                    else:
                        self.lg("%s sleeping"%att.species); return
                else:
                    self.lg("%s sleeping"%att.species); return
        if att.status=="FRZ":
            if self.rng.random()<0.20: att.status=None
            else: self.lg("%s frozen"%att.species); return
        if att.cnf>0:
            att.cnf-=1
            if self.rng.random()<0.5:
                s=att.eff(); dmg=max(1,s["atk"]*40*42//s["df"]//50+2); dmg=self.rng.randint(dmg*85//100,dmg)
                att.hp-=min(att.hp,dmg); self.lg("%s hit self in confusion %d"%(att.species,dmg))
                self.flags["confusion_self"]+=1
                return
        if att.attract and self.rng.random()<0.5:
            self.lg("%s immobilized by love"%att.species); return
        if att.status=="PAR" and self.rng.random()<0.25:
            self.lg("%s fully paralyzed"%att.species); self.flags["full_para_"+att.side]+=1; return

        att.observed.add(move)
        mv=MOVES[move]; eff=mv["effect"]
        # choice lock
        if att.item=="Choice Band": att.choice=move
        # protect
        if eff=="EFFECT_PROTECT":
            if att.side=="us" and att.protect_streak>=1: self.flags["protect2_try_us"]+=1
            rate=1.0/(2**att.protect_streak)
            if self.rng.random()<rate:
                att.protected=True; att.protect_streak+=1; self.lg("%s protected"%att.species)
            else:
                att.protect_streak=0; self.lg("%s protect FAILED"%att.species); self.flags["protect_fail_"+att.side]+=1
            return
        att.protect_streak=0
        if eff=="EFFECT_SUBSTITUTE":
            cost=att.max_hp//4
            if att.hp>cost and att.sub==0:
                att.hp-=cost; att.sub=cost; self.lg("%s made sub"%att.species)
            return
        if eff=="EFFECT_PERISH_SONG":
            for m in self.active["us"]+self.active["foe"]:
                if m and m.alive() and m.ability!="ABILITY_SOUNDPROOF" and m.perish is None:
                    m.perish=3
            self.lg("%s perish song"%att.species); return
        if eff=="EFFECT_DESTINY_BOND":
            att.destiny=True; return
        if eff in ("EFFECT_RAIN_DANCE","EFFECT_SUNNY_DAY","EFFECT_SANDSTORM","EFFECT_HAIL"):
            self.weather={"EFFECT_RAIN_DANCE":"rain","EFFECT_SUNNY_DAY":"sun","EFFECT_SANDSTORM":"sand","EFFECT_HAIL":"hail"}[eff]
            self.wturns=5; return
        if eff=="EFFECT_REFLECT" and att.side=="foe": self.screens["foe_reflect"]=5; return
        if eff=="EFFECT_LIGHT_SCREEN" and att.side=="foe": self.screens["foe_light"]=5; return
        if eff=="EFFECT_REST":
            if att.hp<att.max_hp:
                att.hp=att.max_hp; att.status="SLP"; att.slp=2; att.toxn=0
                if att.item=="Chesto Berry" and not att.item_used: att.status=None; att.slp=0; att.item_used=True
            return
        if eff in ("EFFECT_RESTORE_HP","EFFECT_SOFTBOILED","EFFECT_MOONLIGHT","EFFECT_MORNING_SUN","EFFECT_SYNTHESIS"):
            att.hp=min(att.max_hp,att.hp+att.max_hp//2); return
        # single-target resolution below
        tgt=target
        onfield=self.active["us"]+self.active["foe"]
        if tgt is not None and (not tgt.alive() or tgt not in onfield):
            foes=self.foes_of(att)
            tgt=self.rng.choice(foes) if foes else None
        if mv["power"]>=2 or eff==OHKO_EFF or eff=="EFFECT_COUNTER" or eff=="EFFECT_MIRROR_COAT":
            # damaging moves
            if eff=="EFFECT_COUNTER":
                amt,src=att.dmg_phys
                if amt>0 and src is not None and src.alive():
                    self.deal(att,src,move,amt*2); self.flags["counter_hit_"+att.side]+=1
                return
            if eff=="EFFECT_MIRROR_COAT":
                amt,src=att.dmg_spec
                if amt>0 and src is not None and src.alive():
                    self.deal(att,src,move,amt*2)
                return
            if eff=="EFFECT_EXPLOSION":
                allmons=[m for m in self.active["us"]+self.active["foe"] if m and m.alive()]
                if any(m.ability=="ABILITY_DAMP" for m in allmons):
                    self.lg("%s explosion blocked by damp"%att.species); return
                targets=[m for m in allmons if m is not att and m is not self.ally_of(att)] if MOVES[move]["target"]=="MOVE_TARGET_FOES_AND_ALLY" else []
                # gen3 explosion hits both foes AND ally, full damage
                targets=[m for m in allmons if m is not att]
                att.hp=0; self.lg("%s exploded"%att.species)
                for t in targets:
                    if t.protected: self.lg("%s protected from boom"%t.species); continue
                    dmg=self.calc(att,t,move)
                    if dmg>0: self.deal(att,t,move,dmg)
                    else: self.lg("%s immune to boom"%t.species)
                self.flags["boom_"+att.side]+=1
                return
            if eff=="EFFECT_SOLAR_BEAM" and att.charging is None and self.weather!="sun":
                att.charging=("MOVE_SOLAR_BEAM",tgt); self.lg("%s charging solarbeam"%att.species); return
            if eff=="EFFECT_SEMI_INVULNERABLE" and att.charging is None:
                att.charging=(move,tgt); att.invuln=True; self.lg("%s went up/under (%s)"%(att.species,move)); return
            if att.charging is not None and att.invuln:
                att.invuln=False
            if eff=="EFFECT_DREAM_EATER" and (tgt is None or tgt.status!="SLP"):
                self.lg("%s dream eater failed"%att.species); att.charging=None; return
            if eff=="EFFECT_FAKE_OUT" and not att.first_turn:
                self.lg("%s fake out failed"%att.species); return
            if eff=="EFFECT_FOCUS_PUNCH" and att.took_dmg:
                self.lg("%s focus punch broken"%att.species); self.flags["fp_broken"]+=1; return
            if att.tormented and move==att.last_move:
                self.lg("%s torment blocked %s"%(att.species,move)); return
            att.last_move=move
            att.charging=None
            if tgt is None: return
            if eff=="EFFECT_LEVEL_DAMAGE":
                if tgt.protected or not self.accuracy_ok(att,tgt,move):
                    self.lg("%s level-damage missed/blocked"%att.species); return
                if damage_range(dict(species=att.species,stats=att.eff(),types=att.types,ability=att.ability,item=None,level=100),
                                dict(species=tgt.species,stats=tgt.eff(),types=tgt.types,ability=tgt.ability,item=None,level=100),
                                "MOVE_TACKLE")[1]==0 and MOVES[move]["type"] in ("TYPE_NORMAL","TYPE_FIGHTING") and "TYPE_GHOST" in tgt.types:
                    return
                self.deal(att,tgt,move,100); return
            if tgt.protected:
                self.lg("%s protected from %s"%(tgt.species,move)); return
            if eff==OHKO_EFF:
                if tgt.sub>0: tgt.sub=0; self.lg("ohko broke sub"); return
                if self.accuracy_ok(att,tgt,move):
                    self.deal(att,tgt,move,tgt.hp); self.flags["ohko_hit_"+tgt.side]+=1
                else: self.lg("%s ohko missed"%att.species)
                return
            spread = MOVES[move]["target"]=="MOVE_TARGET_BOTH" and len(self.foes_of(att))==2
            hit_targets=[m for m in self.foes_of(att)] if MOVES[move]["target"]=="MOVE_TARGET_BOTH" else [tgt]
            if MOVES[move]["target"]=="MOVE_TARGET_FOES_AND_ALLY":
                hit_targets=[m for m in self.foes_of(att)]
                al=self.ally_of(att)
                if al is not None: hit_targets.append(al)
            for t in hit_targets:
                if not t.alive(): continue
                if t.protected: self.lg("%s protected"%t.species); continue
                if not self.accuracy_ok(att,t,move):
                    self.lg("%s missed %s on %s"%(att.species,move,t.species)); self.flags["miss_"+att.side]+=1; continue
                crit_chance=1/16
                if MOVES[move]["effect"]=="EFFECT_HIGH_CRITICAL": crit_chance=1/4
                if att.item=="Scope Lens": crit_chance=1/3 if crit_chance==1/4 else 1/8
                crit=self.rng.random()<crit_chance
                if crit: self.flags["crit_"+t.side]+=1
                dmg=self.calc(att,t,move,crit=crit,spread=(spread and t.side!=att.side))
                if dmg==0:
                    self.lg("%s no effect on %s"%(move,t.species)); continue
                real=self.deal(att,t,move,dmg)
                if move in RECOIL and real>0:
                    att.hp-=min(att.hp,max(1,real//RECOIL[move])); self.lg("%s recoil"%att.species)
                if eff in ("EFFECT_ABSORB","EFFECT_DREAM_EATER") and real>0:
                    att.hp=min(att.max_hp,att.hp+max(1,real//2))
                if MOVES[move]["effect"]=="EFFECT_RECHARGE": att.recharge=True
                if MOVES[move]["effect"]=="EFFECT_FAKE_OUT" and t.alive(): t.flinch=True
                if MOVES[move]["effect"]=="EFFECT_TRI_ATTACK" and t.alive() and self.rng.random()<0.20:
                    self.try_status(t,self.rng.choice(["PAR","BRN","FRZ"]))
                if MOVES[move]["effect"]=="EFFECT_DREAM_EATER":
                    att.hp=min(att.max_hp,att.hp+max(1,real//2))
                sec=SECONDARY.get(move)
                if sec and t.alive():
                    kindx,ch=sec
                    if self.rng.random()<ch/100.0:
                        if kindx in ("PAR","BRN","FRZ","PSN","CNF"): self.try_status(t,kindx)
                        elif kindx=="FLINCH" or (att.item=="Kings Rock" and self.rng.random()<0.10): t.flinch=True
                        elif kindx=="SPDDOWN": t.stages["spd"]=max(-6,t.stages["spd"]-1)
                        elif kindx=="SPEDOWN": t.stages["spe"]=max(-6,t.stages["spe"]-1)
                        elif kindx=="DFDOWN": t.stages["df"]=max(-6,t.stages["df"]-1)
                        elif kindx=="ATKUP_SELF": att.stages["atk"]=min(6,att.stages["atk"]+1)
                        elif kindx=="SPA2DOWN_SELF": att.stages["spa"]=max(-6,att.stages["spa"]-2)
                elif att.item=="Kings Rock" and t.alive() and self.rng.random()<0.10:
                    t.flinch=True
            return
        # non-damaging status moves
        if tgt is None: tgt=att
        if tgt.protected and MOVES[move]["target"] not in ("MOVE_TARGET_USER",):
            self.lg("%s protected from %s"%(tgt.species,move)); return
        if not self.accuracy_ok(att,tgt,move):
            self.lg("%s missed %s"%(att.species,move)); return
        if eff=="EFFECT_ENDURE":
            rate=1.0/(2**att.endure_streak)
            if self.rng.random()<rate: att.endure=True; att.endure_streak+=1
            else: att.endure_streak=0
            return
        if eff=="EFFECT_YAWN":
            if tgt.status is None and tgt.drowsy==0 and tgt.sub==0: tgt.drowsy=2
            return
        if eff=="EFFECT_MEAN_LOOK":
            tgt.trapped=True; self.lg("%s trapped %s"%(att.species,tgt.species)); return
        if eff=="EFFECT_TRICK":
            if tgt.sub==0:
                att.item,tgt.item=tgt.item,att.item
                att.choice=None; tgt.choice=None
                self.lg("%s tricked items with %s"%(att.species,tgt.species)); self.flags["trick"]+=1
            return
        if eff=="EFFECT_SKILL_SWAP":
            att.ability,tgt.ability=tgt.ability,att.ability
            self.lg("skill swap %s<->%s"%(att.species,tgt.species)); return
        if eff=="EFFECT_BATON_PASS":
            bench=[x for x in self.bench[att.side] if x.alive()]
            if bench:
                nxt=bench[0]; self.bench[att.side].remove(nxt)
                idx=self.active[att.side].index(att)
                self.bench[att.side].append(att)
                nxt.stages=dict(att.stages); nxt.sub=att.sub
                att.stages={k:0 for k in STAGE_KEYS}; att.sub=0; att.perish=None
                self.active[att.side][idx]=nxt; self.on_entry(nxt); nxt.first_turn=True
                self.lg("%s baton passed to %s"%(att.species,nxt.species))
            return
        if eff=="EFFECT_ROAR":
            side=tgt.side
            bench=[x for x in self.bench[side] if x.alive()]
            if bench and tgt in self.active[side]:
                nxt=self.rng.choice(bench)
                self.bench[side].remove(nxt); self.bench[side].append(tgt)
                idx=self.active[side].index(tgt)
                tgt.stages={k:0 for k in STAGE_KEYS}; tgt.sub=0; tgt.perish=None; tgt.choice=None; tgt.tormented=False; tgt.last_move=None
                self.active[side][idx]=nxt; self.on_entry(nxt); nxt.first_turn=True
                self.lg("%s roared %s away -> %s"%(att.species,tgt.species,nxt.species))
                self.flags["phazed_"+side]+=1
            return
        if eff=="EFFECT_PSYCH_UP":
            att.stages=dict(tgt.stages); self.lg("%s psych up"%att.species); return
        if eff in ("EFFECT_SLEEP",): self.try_status(tgt,"SLP"); self.flags["sleep_try"]+=1
        elif eff=="EFFECT_TOXIC": self.try_status(tgt,"TOX")
        elif eff=="EFFECT_POISON": self.try_status(tgt,"PSN")
        elif eff in ("EFFECT_PARALYZE","EFFECT_THUNDER_WAVE"):
            if "TYPE_GROUND" in tgt.types and move=="MOVE_THUNDER_WAVE": return
            self.try_status(tgt,"PAR"); self.flags["twave_"+tgt.side]+=1
        elif eff=="EFFECT_WILL_O_WISP": self.try_status(tgt,"BRN")
        elif eff=="EFFECT_TORMENT":
            if tgt.sub==0 and not tgt.tormented:
                tgt.tormented=True; self.lg("%s tormented %s"%(att.species,tgt.species))
        elif eff=="EFFECT_CONFUSE": self.try_status(tgt,"CNF")
        elif eff=="EFFECT_SWAGGER":
            tgt.stages["atk"]=min(6,tgt.stages["atk"]+2); self.try_status(tgt,"CNF")
        elif eff=="EFFECT_FLATTER":
            tgt.stages["spa"]=min(6,tgt.stages["spa"]+1); self.try_status(tgt,"CNF")
        elif eff=="EFFECT_ATTRACT":
            if att.gender and tgt.gender and att.gender!=tgt.gender:
                tgt.attract=True; self.lg("%s attracted"%tgt.species); self.flags["attract_"+tgt.side]+=1
        elif eff=="EFFECT_LEECH_SEED":
            if "TYPE_GRASS" not in tgt.types: tgt.leech=True
        elif "EFFECT_EVASION_UP" in eff: att.eva_st=min(6,att.eva_st+1); self.flags["dt_used"]+=1
        elif eff=="EFFECT_MINIMIZE": att.eva_st=min(6,att.eva_st+2)
        elif eff=="EFFECT_CURSE":
            if "TYPE_GHOST" in att.types:
                att.hp-=att.max_hp//2  # APPROX curse ghost, target curse skipped
            else:
                att.stages["atk"]=min(6,att.stages["atk"]+1); att.stages["df"]=min(6,att.stages["df"]+1)
                att.stages["spe"]=max(-6,att.stages["spe"]-1)
        elif eff=="EFFECT_CALM_MIND":
            att.stages["spa"]=min(6,att.stages["spa"]+1); att.stages["spd"]=min(6,att.stages["spd"]+1)
        elif eff=="EFFECT_DRAGON_DANCE":
            att.stages["atk"]=min(6,att.stages["atk"]+1); att.stages["spe"]=min(6,att.stages["spe"]+1)
        elif eff=="EFFECT_BULK_UP":
            att.stages["atk"]=min(6,att.stages["atk"]+1); att.stages["df"]=min(6,att.stages["df"]+1)
        else:
            # generic stat up/down parsing
            up = [k for k in ("ATTACK","DEFENSE","SP_ATK","SP_DEF","SPEED") if k in eff]
            key={"ATTACK":"atk","DEFENSE":"df","SP_ATK":"spa","SP_DEF":"spd","SPEED":"spe"}
            n = 2 if eff.endswith("_2") else 1
            if up:
                k=key[up[0]]
                if "_UP" in eff:
                    att.stages[k]=min(6,att.stages[k]+n); self.lg("%s %s +%d"%(att.species,k,n))
                elif "_DOWN" in eff and tgt.sub==0:
                    tgt.stages[k]=max(-6,tgt.stages[k]-n); self.lg("%s %s -%d"%(tgt.species,k,n))
            # everything else: no-op (APPROX)

    # ---------- end of turn ----------
    def end_turn(self):
        for m in self.active["us"]+self.active["foe"]:
            if m is None or not m.alive(): continue
            if self.weather in ("sand","hail"):
                immune = ("TYPE_ROCK" in m.types or "TYPE_GROUND" in m.types or "TYPE_STEEL" in m.types) if self.weather=="sand" else ("TYPE_ICE" in m.types)
                if not immune and m.ability not in ("ABILITY_SAND_VEIL",):
                    m.hp-=min(m.hp,m.max_hp//16)
            if m.item=="Leftovers": m.hp=min(m.max_hp,m.hp+m.max_hp//16)
            if m.status=="BRN" or m.status=="PSN": m.hp-=min(m.hp,m.max_hp//8)
            if m.status=="TOX":
                m.hp-=min(m.hp,m.max_hp*m.toxn//16); m.toxn=min(15,m.toxn+1)
            if getattr(m,"leech",False):
                d=min(m.hp,m.max_hp//8); m.hp-=d
        if self.wturns>0:
            self.wturns-=1
            if self.wturns==0: self.weather=None
        for k in ("foe_reflect","foe_light"):
            if self.screens[k]>0: self.screens[k]-=1
        for m in self.active["us"]+self.active["foe"]:
            if m is None or not m.alive(): continue
            m.first_turn=False
            if m.drowsy>0:
                m.drowsy-=1
                if m.drowsy==0 and m.status is None:
                    self.try_status(m,"SLP")
        # perish
        for m in self.active["us"]+self.active["foe"]:
            if m is None or not m.alive() or m.perish is None: continue
            m.perish-=1
            if m.perish<=0:
                m.hp=0; self.lg("%s perished"%m.species); self.flags["perish_kill_"+m.side]+=1

    def replace_fainted(self):
        for side in ("us","foe"):
            for i,m in enumerate(self.active[side]):
                if m is not None and not m.alive():
                    self.active[side][i]=None
            for i,m in enumerate(self.active[side]):
                if m is None:
                    nxt=None
                    alive_bench=[b for b in self.bench[side] if b.alive()]
                    if side=="us" and SMART_SENDIN and len(alive_bench)>1:
                        foes_now=[f for f in self.active["foe"] if f and f.alive()]
                        def threat(cand):
                            # fair-info: candidate-move union + pminmax worst case
                            tot=0
                            for f in foes_now:
                                best=0
                                for fm in cand_moves(f):
                                    if fm not in MOVES or MOVES[fm]["power"]<2: continue
                                    _,hi=self.pminmax(f,cand,fm)
                                    best=max(best,hi)
                                tot+=best/max(1,cand.max_hp)
                            return tot
                        nxt=min(alive_bench,key=threat)
                    elif alive_bench:
                        nxt=alive_bench[0]
                    if nxt:
                        self.bench[side].remove(nxt)
                        self.active[side][i]=nxt; self.on_entry(nxt)
                        nxt.choice=None; nxt.first_turn=True
                        self.lg("%s sent out %s"%(side,nxt.species))

    def result(self):
        us_alive=any(m.alive() for m in self.us)
        foe_alive=any(m.alive() for m in self.foe)
        if not us_alive: return "loss"     # includes draw=loss
        if not foe_alive: return "win"
        return None

# ---------------- enemy AI (model of CHECK_BAD_MOVE|TRY_TO_FAINT|CHECK_VIABILITY) ----------------
def ai_choose(b, mon):
    """returns ('move', move, target). AI cheats: real stats, max-roll dmg, no acc/crit."""
    foes=b.foes_of(mon)
    if not foes: return ("move",mon.moves[0],None)
    cands=[]
    moves = [mon.choice] if (mon.item=="Choice Band" and mon.choice) else mon.moves
    for mv in moves:
        if mv not in MOVES: continue
        if mon.tormented and mv==mon.last_move: continue  # torment: same move twice is illegal
        m=MOVES[mv]; eff=m["effect"]
        if m["power"]>=2 or eff==OHKO_EFF:
            if eff=="EFFECT_EXPLOSION":
                allm=[x for x in b.active["us"]+b.active["foe"] if x and x.alive()]
                if any(x.ability=="ABILITY_DAMP" for x in allm): continue
                if mon.hp*2>mon.max_hp: continue          # never above 50%
                base=99 if mon.hp*10<=mon.max_hp*3 else 96 # near-certain <=30%
                best=None
                for t in foes:
                    _,hi=b.minmax(mon,t,mv)
                    sc=base+(4 if hi>=t.hp else 0)
                    if best is None or sc>best[0]: best=(sc,t)
                cands.append((best[0]+b.rng.uniform(-AI_JITTER,AI_JITTER),mv,best[1]))
                continue
            if eff==OHKO_EFF:
                for t in foes:
                    if t.sub>0: continue
                    cands.append((97+b.rng.uniform(-0.5,0.5),mv,t))
                continue
            if eff=="EFFECT_COUNTER":
                cands.append((97+b.rng.uniform(-1,1),mv,foes[0])); continue
            if eff=="EFFECT_MIRROR_COAT":
                cands.append((97+b.rng.uniform(-1,1),mv,foes[0])); continue
            if eff=="EFFECT_FOCUS_PUNCH":
                for t in foes:
                    _,hi=b.minmax(mon,t,mv)
                    if hi==0: continue
                    cands.append((98+(4 if hi>=t.hp else 0)+b.rng.uniform(-0.5,0.5),mv,t))
                continue
            if eff=="EFFECT_DREAM_EATER":
                for t in foes:
                    if t.status=="SLP":
                        _,hi=b.minmax(mon,t,mv)
                        cands.append((98+(4 if hi>=t.hp else 0)+b.rng.uniform(-AI_JITTER,AI_JITTER),mv,t))
                continue
            spread = m["target"]=="MOVE_TARGET_BOTH" and len(foes)==2
            for t in foes:
                lo,hi=b.minmax(mon,t,mv,spread=spread)
                if hi==0: continue   # CHECK_BAD_MOVE: no-effect skipped
                if t.sub>0 and hi<t.sub: sc=95
                else:
                    sc=98 + (AI_KILL_BONUS if hi>=t.hp else 0)
                    sc += min(2, 2*hi/max(1,t.max_hp))   # prefer stronger move (approx viability)
                cands.append((sc+b.rng.uniform(-AI_JITTER,AI_JITTER),mv,t))
        else:
            if eff in ("EFFECT_PARALYZE","EFFECT_THUNDER_WAVE"):
                for t in foes:
                    if t.status or "TYPE_GROUND" in t.types or t.sub>0: continue
                    bonus=3 if (t.eff()["spe"]>mon.eff()["spe"] and b.rng.random()<0.92) else 0
                    cands.append((97+bonus+AI_STATUS_BONUS+b.rng.uniform(-AI_JITTER,AI_JITTER),mv,t))
            elif eff=="EFFECT_SLEEP":
                for t in foes:
                    if t.status or t.sub>0: continue
                    cands.append((98+AI_STATUS_BONUS+b.rng.uniform(-1,1),mv,t))  # bugged bonus -> flat
            elif eff=="EFFECT_PROTECT":
                sc=100 - 3*mon.protect_streak
                cands.append((sc+b.rng.uniform(-AI_JITTER,AI_JITTER),mv,mon))
            elif eff=="EFFECT_ROAR":
                for t in foes:
                    boost=sum(max(0,v) for v in t.stages.values())
                    sc=99.5 if boost>=3 else 90.0
                    cands.append((sc+b.rng.uniform(-0.5,0.5),mv,t))
            elif eff=="EFFECT_ATTRACT":
                for t in foes:
                    if t.attract or not t.gender or t.gender==mon.gender: continue
                    cands.append((98+b.rng.uniform(-1,1),mv,t))
            elif eff in ("EFFECT_SLEEP",): pass
            elif eff=="EFFECT_DESTINY_BOND":
                cands.append((96+b.rng.uniform(-1,1),mv,mon))
            elif eff=="EFFECT_PSYCH_UP":
                for t in foes:
                    boost=sum(max(0,v) for v in t.stages.values())
                    if boost>=2: cands.append((99+b.rng.uniform(-0.5,0.5),mv,t))
            elif eff=="EFFECT_REST":
                sc=101 if mon.hp*2<mon.max_hp else 90
                cands.append((sc,mv,mon))
            else:
                cands.append((97+b.rng.uniform(-1,1),mv,mon if m["target"]=="MOVE_TARGET_USER" else b.rng.choice(foes)))
    if not cands:
        return ("move",moves[0],foes[0])
    cands.sort(key=lambda x:-x[0])
    _,mv,t=cands[0]
    return ("move",mv,t)

# ---------------- our policy bot (playbook encoding) ----------------
FORTRESS_THRESH=0.50
TH_LAX_ATK=0.25
TH_DANGER=1.0
TH_SOLO=1.0
STALL_MOVES={"MOVE_DOUBLE_TEAM","MOVE_MINIMIZE","MOVE_PROTECT","MOVE_DETECT","MOVE_REST",
             "MOVE_RECOVER","MOVE_SOFTBOILED","MOVE_MILK_DRINK","MOVE_MOONLIGHT","MOVE_MORNING_SUN","MOVE_SYNTHESIS"}
SPECIES_SETS={}
SPECIES_ENTRIES={}
for _e in pool:
    SPECIES_SETS.setdefault(_e["species"],[]).append(frozenset(_e["moves"]))
    SPECIES_ENTRIES.setdefault(_e["species"],[]).append(_e)
def candidates(mon):
    ms=SPECIES_SETS.get(mon.species)
    if not ms: return []
    c=[s for s in ms if mon.observed<=s]
    return c if c else ms
def cand_entries(mon):
    es=SPECIES_ENTRIES.get(mon.species)
    if not es: return []
    c=[e for e in es if mon.observed<=frozenset(e["moves"])]
    return c if c else es
def cand_moves(mon):
    u=set()
    for e in cand_entries(mon): u|=set(e["moves"])
    return u
_PM_CACHE={}
def cand_has_counter(mon):
    return any("MOVE_COUNTER" in s for s in candidates(mon))
def cand_has_boom(mon):
    return any(("MOVE_EXPLOSION" in s or "MOVE_SELF_DESTRUCT" in s) for s in candidates(mon))
def cand_has_ohko(mon):
    O={"MOVE_HORN_DRILL","MOVE_FISSURE","MOVE_SHEER_COLD","MOVE_GUILLOTINE"}
    return any(s & O for s in candidates(mon))
def is_staller(mon):
    return bool(mon.observed & STALL_MOVES)
POLICY_VARIANT="A"
PROTECT_CAP=2
GENGAR_BUILD="support"
FIRE_T1_MODE="default"
AI_JITTER=0.5
AI_KILL_BONUS=4
AI_STATUS_BONUS=0.0
GENGAR_OVERLAY="ohko"
STEEL_LEAD_EQ=1
SMART_SENDIN=0
FOCUS_FIRE=0
JIBAKU_RELAX=0  # A=baseline / B=T1 sub / C=sub-first doctrine
def best_attack(b, mon, foes, only=None, relax=False):
    """(move,target,minfrac,maxfrac) best by min-roll fraction; avoids feeding enemy boom zone.
    relax=True: ignore counter/boom-zone guards (deadlock breaker — timeout loss is worse)"""
    best=None
    moves=[mon.choice] if (mon.item=="Choice Band" and mon.choice) else mon.moves
    our_boomable=any(x is not None and x.alive() and x.species!="Gengar" for x in b.active["us"]) or any(x.alive() for x in b.bench["us"])
    for mv in moves:
        if only and mv not in only: continue
        if mv not in MOVES or MOVES[mv]["power"]<2: continue
        if MOVES[mv]["effect"]=="EFFECT_EXPLOSION": continue
        for t in foes:
            spread=MOVES[mv]["target"]=="MOVE_TARGET_BOTH" and len(foes)==2
            lo,hi=b.pminmax(mon,t,mv,spread=spread)
            if hi==0: continue
            if not relax and MOVES[mv]["type"] in PHYSICAL and cand_has_counter(t) and 2*hi>=mon.hp: continue
            # boom-zone guard: never chip an explosion-carrier into <=50% unless the hit kills
            has_boom=cand_has_boom(t)
            if not relax and has_boom and our_boomable and lo<t.hp and (t.hp-hi)*2<=t.max_hp and t.hp*2>t.max_hp:
                continue
            key=(lo/max(1,t.hp), hi/max(1,t.hp))
            if best is None or key>best[3]:
                best=(mv,t,lo/max(1,t.hp),key)
    return best

def boom_kills_all(b, mon, foes, move):
    for t in foes:
        lo,_=b.pminmax(mon,t,move)
        if lo<t.hp: return False
    return True and len(foes)>0

def our_choose(b):
    """actions for our two active slots; may return ('switch',mon,replacement)"""
    acts={}
    foes=[m for m in b.active["foe"] if m and m.alive()]
    gengar=next((m for m in b.active["us"] if m and m.alive() and m.species=="Gengar"),None)
    gross=next((m for m in b.active["us"] if m and m.alive() and m.species=="Metagross"),None)
    lax=next((m for m in b.active["us"] if m and m.alive() and m.species=="Snorlax"),None)
    lati=next((m for m in b.active["us"] if m and m.alive() and m.species=="Latios"),None)
    fsp={f.species for f in foes}
    fire=[f for f in foes if f.species in FIRE_RETREAT]
    damp_present=any(f.species in DAMP_SP for f in foes)
    wobb=any(f.species=="Wobbuffet" for f in foes)
    boom_ok = not damp_present

    # ---- turn 1 tree (gross+gengar out) ----
    if gross is not None and gengar is not None and b.turn==1:
        if fire and not wobb:
            fp_holder=next((f for f in foes if "MOVE_FOCUS_PUNCH" in f.moves and f.species not in FIRE_RETREAT),None)
            cc = next((f for f in foes if f.species in ("Machamp","Hariyama","Medicham")),None)
            bench_lax=next((m for m in b.bench["us"] if m.species=="Snorlax" and m.alive()),None)
            bench_lati=next((m for m in b.bench["us"] if m.species=="Latios" and m.alive()),None)
            if FIRE_T1_MODE=="stay":
                gb=best_attack(b,gross,foes)
                acts[gross]=("move",gb[0],gb[1]) if gb else ("move","MOVE_METEOR_MASH",foes[0])
            elif cc and not any(f.species=="Houndoom" for f in fire) and bench_lati:
                acts[gross]=("switch",gross,bench_lati)
            elif bench_lax:
                acts[gross]=("switch",gross,bench_lax)
            if fp_holder is not None:
                acts[gengar]=("move","MOVE_GIGA_DRAIN",fp_holder)
            elif FIRE_T1_MODE=="sub":
                acts[gengar]=("move","MOVE_SUBSTITUTE",gengar)
            elif FIRE_T1_MODE=="giga":
                gg=best_attack(b,gengar,foes)
                acts[gengar]=("move",gg[0],gg[1]) if gg else ("move","MOVE_PROTECT",gengar)
            else:
                acts[gengar]=("move","MOVE_PROTECT",gengar)
            b.flags["branch_fire"]+=1
            return acts
        if fire and wobb:
            acts[gross]=("move","MOVE_EXPLOSION",None); acts[gengar]=("move","MOVE_SUBSTITUTE",gengar)
            b.flags["branch_firewobb"]+=1; return acts
        regirock=next((f for f in foes if f.species=="Regirock"),None)
        regice=next((f for f in foes if f.species=="Regice"),None)
        if regirock is not None:
            acts[gross]=("move","MOVE_METEOR_MASH",regirock)
            acts[gengar]=("move","MOVE_GIGA_DRAIN",regirock)
            b.flags["branch_regirock"]+=1; return acts
        if regice is not None:
            acts[gross]=("move","MOVE_METEOR_MASH",regice)
            other=[f for f in foes if f is not regice]
            acts[gengar]=("move","MOVE_GIGA_DRAIN",other[0]) if other and b.pminmax(gengar,other[0],"MOVE_GIGA_DRAIN")[1]>0 else ("move","MOVE_PROTECT",gengar)
            b.flags["branch_regice"]+=1; return acts
        STEELS={"Aggron","Steelix","Registeel","Metagross","Scizor","Forretress"}
        steel_t=next((f for f in foes if f.species in STEELS and b.pminmax(gross,f,"MOVE_EXPLOSION")[0]<f.hp and b.pminmax(gross,f,"MOVE_EARTHQUAKE")[1]>0),None)
        if STEEL_LEAD_EQ and steel_t is not None:
            acts[gross]=("move","MOVE_EARTHQUAKE",steel_t)
            other=[f for f in foes if f is not steel_t]
            gb=best_attack(b,gengar,other) if other else None
            acts[gengar]=("move",gb[0],gb[1]) if (gb and gb[3][1]>=0.5) else ("move","MOVE_PROTECT",gengar)
            b.flags["branch_steel_eq"]+=1; return acts
        aggron=next((f for f in foes if f.species=="Aggron"),None)
        if aggron is not None:
            acts[gross]=("move","MOVE_EARTHQUAKE",aggron)
            other=[f for f in foes if f is not aggron]
            gb=best_attack(b,gengar,other) if other else None
            acts[gengar]=("move",gb[0],gb[1]) if (gb and gb[3][1]>=0.5) else ("move","MOVE_PROTECT",gengar)
            b.flags["branch_aggron"]+=1; return acts
        ghosts=[f for f in foes if f.species in GHOST_SP]
        if len(ghosts)==len(foes) and foes:
            ba=best_attack(b,gross,foes)
            acts[gross]=("move",ba[0],ba[1]) if ba else ("move","MOVE_SHADOW_BALL",foes[0])
            gb=best_attack(b,gengar,foes)
            acts[gengar]=("move","MOVE_GIGA_DRAIN",gb[1]) if gb else ("move","MOVE_PROTECT",gengar)
            b.flags["branch_ghost2"]+=1; return acts
        if damp_present:
            dampmon=next(f for f in foes if f.species in DAMP_SP)
            if dampmon.species=="Quagsire" and cand_has_counter(dampmon):
                acts[gross]=("move","MOVE_SHADOW_BALL",next((f for f in foes if f is not dampmon),dampmon))
            else:
                acts[gross]=("move","MOVE_EARTHQUAKE",dampmon)
            acts[gengar]=("move","MOVE_GIGA_DRAIN",dampmon)
            b.flags["branch_damp"]+=1; return acts
        # default: boom (+ giga overlay on Rhydon etc.) — but only if it guarantees >=1 kill
        kills_boom=sum(1 for f in foes if b.pminmax(gross,f,"MOVE_EXPLOSION")[0]>=f.hp)
        if kills_boom==0:
            gb2=best_attack(b,gross,foes)
            acts[gross]=("move",gb2[0],gb2[1]) if gb2 else ("move","MOVE_METEOR_MASH",foes[0])
            gg=best_attack(b,gengar,foes)
            acts[gengar]=("move",gg[0],gg[1]) if (gg and gg[3][1]>=0.4) else ("move","MOVE_PROTECT",gengar)
            b.flags["branch_noboom_wall"]+=1
            return acts
        acts[gross]=("move","MOVE_EXPLOSION",None)
        ohko_t=next((f for f in foes if cand_has_ohko(f)),None)
        if ohko_t is not None and b.pminmax(gengar,ohko_t,"MOVE_GIGA_DRAIN")[1]>0:
            acts[gengar]=("move","MOVE_GIGA_DRAIN",ohko_t)
        elif POLICY_VARIANT in ("B","C","DB","EB","FB","GB"):
            acts[gengar]=("move","MOVE_SUBSTITUTE",gengar)
        else:
            acts[gengar]=("move","MOVE_PROTECT",gengar)
        b.flags["branch_boom"]+=1
        return acts

    # ---- generic mid/endgame ----
    ours=[m for m in b.active["us"] if m and m.alive()]
    # perish rotation: switch out our mons at perish 1
    shadow_tag=any(f.alive() and f.ability=="ABILITY_SHADOW_TAG" for f in b.active["foe"] if f)
    used_bench=[]
    rotating={}
    for m in ours:
        if m.trapped or shadow_tag: continue
        if m.perish==1:
            bench=[x for x in b.bench["us"] if x.alive() and x not in used_bench]
            if bench:
                used_bench.append(bench[0])
                acts[m]=("switch",m,bench[0]); rotating[m]=bench[0]

    def eff_ally(m):
        """ally on field after this turn's switches resolve"""
        pair=[x for x in b.active["us"] if x is not None and x is not m]
        if not pair: return None, False
        a=pair[0]
        if a in rotating: return rotating[a], True   # (mon, just_switched_in)
        return (a if a.alive() else None), False

    def incoming_max(m):
        """top-2 sum of max single-hit rolls vs m from current foes"""
        hits=[]
        for f in foes:
            bestf=0
            for fm in cand_moves(f):
                if fm not in MOVES or MOVES[fm]["power"]<2: continue
                if MOVES[fm]["effect"]=="EFFECT_EXPLOSION" and f.hp*2>f.max_hp: continue
                sp=MOVES[fm]["target"]=="MOVE_TARGET_BOTH" and len([x for x in b.active["us"] if x and x.alive()])==2
                _,hi=b.pminmax(f,m,fm,spread=sp)
                bestf=max(bestf,hi)
            hits.append(bestf)
        hits.sort(reverse=True)
        return hits[0] if hits else 0, sum(hits[:2])

    order={"Metagross":0,"Snorlax":1,"Gengar":2,"Latios":3}
    for m in sorted(ours,key=lambda x:order.get(x.species,9)):
        if m in acts: continue
        if not foes: acts[m]=("move",m.moves[0],None); continue
        ally,ally_fresh=eff_ally(m)
        ally_safe = (ally is None) or (ally.species=="Gengar") or (not ally_fresh and "MOVE_PROTECT" in ally.moves)
        foes_sung = any(f.perish is not None for f in foes)
        if m.species=="Metagross":
            can_boom = boom_ok and (m.choice is None or m.choice=="MOVE_EXPLOSION") and ally_safe
            kills=sum(1 for t in foes if b.pminmax(m,t,"MOVE_EXPLOSION")[0]>=t.hp)
            others=[x for x in ours if x is not m]+[x for x in b.bench["us"] if x.alive()]
            stallers_g=[f for f in foes if is_staller(f)]
            stall_die_g = bool(stallers_g) and all(b.pminmax(m,f,"MOVE_EXPLOSION")[0]>=f.hp for f in stallers_g)
            if can_boom and others and (kills==len(foes) or (kills>=1 and len(foes)==1) or (stall_die_g and len(others)>=2)):
                acts[m]=("move","MOVE_EXPLOSION",None); continue
            ba=best_attack(b,m,foes)
            acts[m]=("move",ba[0],ba[1]) if ba else ("move","MOVE_METEOR_MASH",foes[0])
        elif m.species=="Snorlax" and "MOVE_SELF_DESTRUCT" in m.moves:
            ally_booming = ally is not None and acts.get(ally,("",))[0]=="move" and acts.get(ally,("",""))[1]=="MOVE_EXPLOSION"
            if ally_booming:
                acts[m]=("move","MOVE_PROTECT",m); continue
            kills=sum(1 for t in foes if b.pminmax(m,t,"MOVE_SELF_DESTRUCT")[0]>=t.hp)
            others=[x for x in ours if x is not m]+[x for x in b.bench["us"] if x.alive()]
            fire_all_die = fire and all(b.pminmax(m,f,"MOVE_SELF_DESTRUCT")[0]>=f.hp for f in fire)
            stallers=[f for f in foes if is_staller(f)]
            stall_all_die = bool(stallers) and all(b.pminmax(m,f,"MOVE_SELF_DESTRUCT")[0]>=f.hp for f in stallers)
            relax_ok=False
            if JIBAKU_RELAX and kills>=1 and len(others)>=2:
                surv=[t for t in foes if b.pminmax(m,t,"MOVE_SELF_DESTRUCT")[0]<t.hp]
                def harmless(t):
                    if cand_has_ohko(t): return False
                    for x in ours:
                        if x is m: continue
                        worst=0
                        for fm in t.moves:
                            if fm not in MOVES or MOVES[fm]["power"]<2: continue
                            _,hi=b.pminmax(t,x,fm)
                            worst=max(worst,hi/max(1,x.max_hp))
                        if worst>=0.35: return False
                    return True
                relax_ok=all(harmless(t) for t in surv)
            if not damp_present and ally_safe and others and (kills==len(foes) or relax_ok or ((fire_all_die or stall_all_die) and len(others)>=2)):
                acts[m]=("move","MOVE_SELF_DESTRUCT",None); continue
            ba=best_attack(b,m,foes)
            solo,duo=incoming_max(m)
            last_mon = len(ours)==1 and not any(x.alive() for x in b.bench["us"])
            crunch_time = foes_sung and min((f.perish for f in foes if f.perish is not None),default=9)<=1
            if crunch_time and ba and m.perish is not None and m.perish<=1:
                acts[m]=("move",ba[0],ba[1])
            elif ba and (ba[2]>=1.0 or (duo<m.hp*TH_DANGER and (ba[3][1]>=TH_LAX_ATK or last_mon))):
                acts[m]=("move",ba[0],ba[1])
            elif duo>=m.hp*TH_DANGER and m.protect_streak<PROTECT_CAP and not last_mon:
                acts[m]=("move","MOVE_PROTECT",m)
            elif ba: acts[m]=("move",ba[0],ba[1])
            else:
                ba2=best_attack(b,m,foes,relax=True)
                acts[m]=("move",ba2[0],ba2[1]) if ba2 else ("move","MOVE_PROTECT",m)
        elif m.species=="Gengar":
            team_atk=[x for x in ours]+[y for y in b.bench["us"] if y.alive()]
            lax_any=next((x for x in team_atk if x.species=="Snorlax"),None)
            gross_any=next((x for x in team_atk if x.species=="Metagross"),None)
            def fortress(t):
                best=0
                for a in team_atk:
                    ba=best_attack(b,a,[t])
                    if ba: best=max(best,ba[3][1])
                if lax_any is not None and not damp_present:
                    best=max(best,b.pminmax(lax_any,t,"MOVE_SELF_DESTRUCT")[0]/max(1,t.hp))
                if gross_any is not None and not damp_present and (gross_any.choice in (None,"MOVE_EXPLOSION")):
                    best=max(best,b.pminmax(gross_any,t,"MOVE_EXPLOSION")[0]/max(1,t.hp))
                return best<FORTRESS_THRESH
            sung=any(f.perish is not None for f in foes)
            solo,duo=incoming_max(m)
            bench_alive=any(x.alive() for x in b.bench["us"])
            sing_ok = bench_alive and not sung and not any(f.species in ("Mr Mime","Electrode","Exploud","Whismur","Loudred") for f in foes)
            if POLICY_VARIANT=="H" and foes and sing_ok:
                foe_bench_h = any(x.alive() for x in b.bench["foe"])
                no_fire_h = not any(f.species in FIRE_RETREAT for f in foes)
                if all(fortress(t) for t in foes) and not foe_bench_h and no_fire_h:
                    acts[m]=("move","MOVE_PERISH_SONG",m); b.flags["perish_used"]+=1; continue
            if POLICY_VARIANT in ("D","DB","E","EB","F","FB","G","GB") and foes and sing_ok:
                jib_ok = lax_any is not None and not damp_present
                sweep = jib_ok and all(b.pminmax(lax_any,t,"MOVE_SELF_DESTRUCT")[0]>=t.hp for t in foes)
                foe_bench = any(x.alive() for x in b.bench["foe"])
                need_no_bench = POLICY_VARIANT in ("E","EB","F","FB","G","GB")
                need_slow = POLICY_VARIANT in ("F","FB")
                slow_exists = any(fortress(t) for t in foes)
                fires_f=[f for f in foes if f.species in FIRE_RETREAT]
                entei_only = bool(fires_f) and all(f.species=="Entei" for f in fires_f)
                fire_veto = POLICY_VARIANT in ("G","GB") and bool(fires_f) and not (entei_only and m.hp*3>=m.max_hp*2)
                if not sweep and (not need_no_bench or not foe_bench) and (not need_slow or slow_exists) and not fire_veto:
                    acts[m]=("move","MOVE_PERISH_SONG",m); b.flags["perish_used"]+=1; continue
            if foes and all(fortress(t) for t in foes) and not sung and bench_alive and not any(f.species in ("Mr Mime","Electrode","Exploud","Whismur","Loudred") for f in foes):
                acts[m]=("move","MOVE_PERISH_SONG",m); b.flags["perish_used"]+=1; continue
            if sung:
                if m.protect_streak<PROTECT_CAP: acts[m]=("move","MOVE_PROTECT",m)
                elif m.hp>m.max_hp//4 and "MOVE_SUBSTITUTE" in m.moves: acts[m]=("move","MOVE_SUBSTITUTE",m)
                else: acts[m]=("move","MOVE_PROTECT",m)
                continue
            ba=best_attack(b,m,foes)
            kill_now = ba and ba[2]>=1.0
            danger = (duo>=m.hp*TH_DANGER) or (solo>=m.hp*TH_SOLO)
            if POLICY_VARIANT=="C" and not kill_now:
                if m.sub==0 and m.hp>m.max_hp//4:
                    acts[m]=("move","MOVE_SUBSTITUTE",m); continue
                if m.sub>0 and ba:
                    acts[m]=("move","MOVE_GIGA_DRAIN",ba[1]); continue
            if kill_now:
                acts[m]=("move","MOVE_GIGA_DRAIN",ba[1])
            elif danger and m.protect_streak==0 and m.sub==0:
                acts[m]=("move","MOVE_PROTECT",m)
            elif danger and m.sub==0 and m.hp>m.max_hp//4 and "MOVE_SUBSTITUTE" in m.moves:
                acts[m]=("move","MOVE_SUBSTITUTE",m)
            elif danger and m.protect_streak<PROTECT_CAP:
                acts[m]=("move","MOVE_PROTECT",m)
            elif ba and ba[3][1]>=0.4:
                acts[m]=("move","MOVE_GIGA_DRAIN",ba[1])
            elif m.sub==0 and m.hp>m.max_hp//4 and len(foes)>1 and "MOVE_SUBSTITUTE" in m.moves:
                acts[m]=("move","MOVE_SUBSTITUTE",m)
            elif ba: acts[m]=("move","MOVE_GIGA_DRAIN",ba[1])
            else: acts[m]=("move","MOVE_PROTECT",m)
        elif m.species=="Latios":
            ally_booming = ally is not None and acts.get(ally,("",))[0]=="move" and acts.get(ally,("",""))[1] in ("MOVE_EXPLOSION","MOVE_SELF_DESTRUCT")
            if ally_booming:
                acts[m]=("move","MOVE_PROTECT",m); continue
            ba=best_attack(b,m,foes)
            solo,duo=incoming_max(m)
            kill_now = ba and ba[2]>=1.0
            ally_alive = ally is not None
            crunch_time = foes_sung and min((f.perish for f in foes if f.perish is not None),default=9)<=1
            if crunch_time and ba and m.perish is not None and m.perish<=1:
                acts[m]=("move",ba[0],ba[1])
            elif kill_now:
                acts[m]=("move",ba[0],ba[1])
            elif solo>=m.hp*TH_SOLO and m.protect_streak<PROTECT_CAP and ally_alive:
                acts[m]=("move","MOVE_PROTECT",m)
            elif ba:
                acts[m]=("move",ba[0],ba[1])
            else:
                acts[m]=("move","MOVE_PROTECT",m)
    if FOCUS_FIRE and foes:
        attackers=[(m,a) for m,a in acts.items() if a[0]=="move" and a[1] in MOVES and MOVES[a[1]]["power"]>=2
                   and MOVES[a[1]]["effect"] not in ("EFFECT_EXPLOSION",) and a[2] is not None and a[2].side=="foe"]
        if len(attackers)==2:
            (m1,a1),(m2,a2)=attackers
            if a1[2] is not a2[2]:
                def mindmg(m,a,t):
                    lo,_=b.pminmax(m,t,a[1]); return lo
                for t in sorted(foes,key=lambda f:-max(
                        (b.pminmax(f,x,fm)[1]/max(1,x.max_hp) for x in (m1,m2) for fm in f.moves
                         if fm in MOVES and MOVES[fm]["power"]>=2),default=0)):
                    solo1=mindmg(m1,a1,t)>=t.hp; solo2=mindmg(m2,a2,t)>=t.hp
                    if not solo1 and not solo2 and mindmg(m1,a1,t)+mindmg(m2,a2,t)>=t.hp:
                        ba1=best_attack(b,m1,[t]); ba2=best_attack(b,m2,[t])
                        if ba1 and ba2 and ba1[3][0]*t.hp+ba2[3][0]*t.hp>=t.hp:
                            acts[m1]=("move",ba1[0],t); acts[m2]=("move",ba2[0],t)
                            b.flags["focus_fire"]+=1
                        break
    return acts

# ---------------- turn loop ----------------
def play_battle(seed=None, verbose=False, event_seed=None):
    global VERBOSE
    VERBOSE=verbose
    b=Battle(seed, event_seed=event_seed)
    while True:
        b.turn+=1
        if b.turn>120:
            b.flags["timeout"]+=1
            return b,"loss"
        for m in b.active["us"]+b.active["foe"]:
            if m: m.protected=False; m.endure=False; m.flinch=False; m.dmg_phys=(0,None); m.dmg_spec=(0,None); m.took_dmg=False; m.destiny=False
        acts=our_choose(b)
        foe_acts={}
        for m in b.active["foe"]:
            if m and m.alive():
                # perish final-turn switch (the only reliable AI switch trigger)
                if m.perish==1 and not m.trapped and not any(x is not None and x.alive() and x.ability=="ABILITY_SHADOW_TAG" for x in b.active["us"]):
                    bench=[x for x in b.bench["foe"] if x.alive()]
                    if bench:
                        foe_acts[m]=("switch",m,bench[0]); continue
                foe_acts[m]=ai_choose(b,m)
        # resolve switches first
        allacts=[]; swapped={}
        for m,a in list(acts.items())+list(foe_acts.items()):
            if a[0]=="switch":
                side=m.side
                if a[2] not in b.bench[side] or not a[2].alive() or m not in b.active[side]:
                    continue
                idx=b.active[side].index(m)
                b.bench[side].append(m)
                b.bench[side].remove(a[2])
                b.active[side][idx]=a[2]
                a[2].choice=None
                m.perish=None; m.stages={k:0 for k in STAGE_KEYS}; m.acc_st=0; m.eva_st=0; m.sub=0; m.attract=False; m.cnf=0
                m.tormented=False; m.last_move=None
                swapped[m]=a[2]
                b.on_entry(a[2])
                b.lg("%s switched %s -> %s"%(side,m.species,a[2].species))
            else:
                allacts.append((m,a))
        if swapped:
            allacts=[(m,(a[0],a[1],swapped.get(a[2],a[2]))) for m,a in allacts]
        # order: priority > QC(shared roll) > speed
        qc_proc = b.rng.random()<0.20
        if qc_proc: b.flags["qc_roll"]+=1
        def order_key(item):
            m,a=item
            mv=a[1]
            pri=MOVES[mv]["priority"] if mv in MOVES else 0
            qc = 1 if (qc_proc and m.item=="Quick Claw") else 0
            return (-pri,-qc,-m.eff()["spe"],b.rng.random())
        allacts.sort(key=order_key)
        for m,a in allacts:
            if not m.alive(): continue
            if m not in b.active["us"]+b.active["foe"]: continue
            b.execute(m,a)
            r=b.result()
            if r: return b,r
        b.end_turn()
        r=b.result()
        if r: return b,r
        b.replace_fainted()
        r=b.result()
        if r: return b,r
