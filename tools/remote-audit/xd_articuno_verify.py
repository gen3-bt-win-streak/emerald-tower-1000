#!/usr/bin/env python3
"""XD (Gale of Darkness) Shadow Articuno provenance verifier.

Independent of PKHeX: implements the XDRNG (LCG mult 0x343FD / add 0x269EC3) and
PokeFinder's non-lock XD generation order (IV1, IV2, ability, PID-hi, PID-lo, anti-shiny
reroll), validates against PokeFinder's own test vectors (Test/Gen3/gamecube.json,
generateNonLock, profile TID 12345 / SID 54321), derives the target individual from its
origin seed, runs a port of PKHeX's reverse check (MethodFinder.GetXDRNGMatch) and of
PKHeX's NPC lock-chain check (TeamLockResult) for the 5 Articuno party variants, and
exhaustively enumerates the direct-path spreads.

Usage: python3 xd_articuno_verify.py [--vectors pf_nonlock_vectors.json]
"""
import sys, json, os, argparse
M=0x343FD; A=0x269EC3; rM=0xB9B33155; rA=0xA170F641; MASK=0xFFFFFFFF
nxt=lambda s:(s*M+A)&MASK
prv=lambda s:(s*rM+rA)&MASK
NAT=['Hardy','Lonely','Brave','Adamant','Naughty','Bold','Docile','Relaxed','Impish','Lax','Timid','Hasty','Serious','Jolly','Naive','Modest','Mild','Quiet','Bashful','Rash','Calm','Gentle','Sassy','Careful','Quirky']
TWO_ABILITY=set()  # Gen 3 species with 2 abilities among those handled here: none (Eevee/Espeon/Umbreon/Celebi/Chikorita/Articuno are single-ability)
TARGET=dict(origin=0xECFE3E26, pid=0x2F3C902C, ivs=(31,0,31,29,31,31), nature='Calm')  # H/A/B/C/D/S
ok=[]
def check(name, cond, detail=''):
    ok.append((name,bool(cond),detail)); print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ---------- PokeFinder non-lock XD generation (GameCubeGenerator::generateNonLock) ----------
def gen_nonlock(seed, tsv, species=None, shiny_never=True, ability_mode='and1'):
    """Returns (pid, ivs(H,A,B,C,D,S), ability) for the state `seed` (= state before IV1)."""
    s=seed
    def u16():
        nonlocal s; s=nxt(s); return s>>16
    actual=tsv
    if species==133:              # Gales Eevee: own TID/SID first
        actual=u16()^u16(); s=nxt(nxt(s))
    if species in (196,197):      # Colo starters
        actual=u16()^u16(); rounds=2 if species==196 else 1
        for _ in range(rounds):
            s=nxt(nxt(s)); iv1=u16(); iv2=u16(); ab=u16(); hi=u16(); lo=u16()
            while ((hi^lo^actual)<8) or ((lo&255)<31):   # gender ratio 31 (12.5% F) male-locked
                hi=u16(); lo=u16()
    else:
        iv1=u16(); iv2=u16(); ab=u16(); hi=u16(); lo=u16()
        if shiny_never:
            while (hi^lo^actual)<8: hi=u16(); lo=u16()
    pid=(hi<<16)|lo
    ivs=(iv1&31,(iv1>>5)&31,(iv1>>10)&31,(iv2>>5)&31,(iv2>>10)&31,iv2&31)
    # PokeFinder: ability = nextUShort(2) & (species has two abilities); all species here (and Articuno) have one ability -> 0
    two = species in TWO_ABILITY
    ability = ((ab&1) if ability_mode=='and1' else (ab>>15)) if two else 0
    return pid, ivs, ability

def run_vectors(path):
    vec=json.load(open(path)); tsv=12345^54321
    for v in vec:
        sp={'Colo Umbreon':197,'Colo Espeon':196,'Ageto Celebi':251,'Gales Eevee':133,'Gales Chikorita':152}[v['name']]
        t = 31121 if sp in (25,251) else tsv
        for mode in ('and1','top'):
            good=0
            for r in v['results']:
                seed=v['seed']
                for _ in range(r['advances']): seed=nxt(seed)
                pid,ivs,ab=gen_nonlock(seed,t,sp,True,mode)
                if pid==r['pid'] and list(ivs)==r['ivs'] and pid%25==r['nature'] and ab==r['ability']: good+=1
            if good==len(v['results']): break
        check(f"PokeFinder vector {v['name']}", good==len(v['results']), f"{good}/{len(v['results'])} states match (ability={mode})")

# ---------- derivation ----------
def derive(origin):
    s=origin; fr=[]
    for _ in range(5): s=nxt(s); fr.append(s)
    iv1=(fr[0]>>16)&0x7FFF; iv2=(fr[1]>>16)&0x7FFF
    pid=((fr[3]>>16)<<16)|(fr[4]>>16)
    ivs=(iv1&31,(iv1>>5)&31,(iv1>>10)&31,(iv2>>5)&31,(iv2>>10)&31,iv2&31)
    return fr,pid,ivs,(fr[2]>>16)&1

# ---------- PKHeX reverse check (MethodFinder.GetXDRNGMatch, GetSeeds by brute force) ----------
def reverse(pid, ivs):
    hp,at,df,spa,spd,spe=ivs; iv1=hp|(at<<5)|(df<<10); iv2=spe|(spa<<5)|(spd<<10)
    first=pid&0xFFFF0000; second=(pid<<16)&MASK; hits=[]
    for low in range(0x10000):
        seed=prv(second|low)
        if (seed&0xFFFF0000)==first:
            s3=prv(seed); B=prv(s3); Aa=prv(B)
            if ((Aa>>16)&0x7FFF)==iv1 and ((B>>16)&0x7FFF)==iv2: hits.append(prv(Aa))
    return hits

# ---------- PKHeX TeamLockResult port (Articuno: 4 prior unlocked shadows) ----------
VARIANTS={'all unseen':[7,7,7,7],'Rhydon+Moltres seen':[5,5,7,7],'Rhydon+Moltres+Tauros seen':[5,5,7,5],
          'Rhydon+Moltres+Exeggutor seen':[5,5,5,7],'all seen':[5,5,5,5]}
def lockchain(origin, tsv=None, bound=40):
    base=prv(prv(origin)); cache=[base]
    def C(i):
        while len(cache)<=i: cache.append(prv(cache[-1]))
        return cache[i]>>16
    out={}
    for name,fc in VARIANTS.items():
        order=list(reversed(fc)); names=list(reversed(['Rhydon','Moltres','Exeggutor','Tauros']))
        def dfs(frame,depth,team):
            if depth==len(order):
                TID=C(frame+1); SID=C(frame); cpusv=(TID^SID)>>3
                for (nm,pid),_ in team:
                    if (((pid&0xFFFF)^(pid>>16))>>3)==cpusv: return None
                return team+[(('CPU TID/SID',TID,SID),frame)]
            for start in [frame]+list(range(2,bound,2)):
                pid=(C(start+1)<<16)|C(start)
                r=dfs(start+order[depth],depth+1,team+[((names[depth],pid),start)])
                if r: return r
            return None
        out[name]=dfs(0,0,[])
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--vectors',default=os.path.join(os.path.dirname(__file__),'pf_nonlock_vectors.json')); a=ap.parse_args()
    print("== 1. PokeFinder test vectors (generateNonLock) ==")
    if os.path.exists(a.vectors): run_vectors(a.vectors)
    else: print("  (vectors file not found, skipped)")
    print("\n== 2. Derivation from origin seed ==")
    fr,pid,ivs,ab=derive(TARGET['origin'])
    for i,s in enumerate(fr,1): print(f"  s{i}={s:08X} out={s>>16:04X}")
    print(f"  IV H/A/B/C/D/S={ivs} ability_bit={ab} PID={pid:08X} nature={NAT[pid%25]} PSV={((pid>>16)^(pid&0xFFFF))>>3}")
    check("derived PID", pid==TARGET['pid'], f"{pid:08X}"); check("derived IVs", ivs==TARGET['ivs'], str(ivs)); check("derived nature", NAT[pid%25]==TARGET['nature'])
    print("\n== 3. Reverse check (PKHeX GetXDRNGMatch port) ==")
    hits=reverse(TARGET['pid'],TARGET['ivs']); print("  origins found:",[f"{h:08X}" for h in hits])
    check("reverse check returns origin", TARGET['origin'] in hits)
    print("\n== 4. Lock chain (PKHeX TeamLockResult port, 5 Articuno party variants) ==")
    lc=lockchain(TARGET['origin'])
    for name,res in lc.items():
        print(f"  {name:32s}: {'VALID' if res else 'invalid'}", "" if not res else " | ".join(f"{k[0]}@{f}:{k[1]:08X}" if len(k)==2 else f"{k[0]}@{f}:{k[1]:04X}/{k[2]:04X}" for k,f in res))
    check("lock chain valid for at least one variant", any(lc.values()))
    print("\n== 5. Direct-path enumeration (HP/Def/SpD/Spe=31) ==")
    from collections import defaultdict
    best=defaultdict(lambda:(-1,None)); calmA0=[]
    for atk in range(32):
        for b15 in (0,1):
            hiw=(31|(atk<<5)|(31<<10)|(b15<<15))<<16
            for low in range(0x10000):
                s1=hiw|low; s2=nxt(s1); iv2=(s2>>16)&0x7FFF
                if (iv2>>10)&31!=31 or iv2&31!=31: continue
                s3=nxt(s2); s4=nxt(s3); s5=nxt(s4); p=((s4>>16)<<16)|(s5>>16); n=NAT[p%25]; spa=(iv2>>5)&31
                if n=='Calm' and atk==0: calmA0.append((spa,p,prv(s1)))
                if n in ('Bold','Calm','Modest','Timid'):
                    key=(atk if n in ('Bold','Calm') else atk)  # A irrelevant for all four; rank by (A low, C high)
                    score=(-atk if n in ('Bold','Calm') else spa) ; 
                    cur=best[n]
                    cand=( (spa, -atk) if n in ('Modest','Timid') else (-atk, spa) )
                    if cur[1] is None or cand>cur[1]: best[n]=(p,cand,atk,spa,prv(s1))
    calmA0.sort(reverse=True)
    print("  Calm A0 spreads (C values):",[c for c,_,_ in calmA0])
    check("Calm 31/0/31/31/31/31 absent on direct path", all(c!=31 for c,_,_ in calmA0))
    check("Calm 31/0/31/29/31/31 present on direct path", any(c==29 and p==TARGET['pid'] for c,p,_ in calmA0))
    for n in ('Bold','Calm','Modest','Timid'):
        p,cand,atk,spa,o=best[n]; print(f"  best {n:6s}: 31/{atk}/31/{spa}/31/31  PID {p:08X} origin {o:08X}")

    print("\n== 6. Anti-shiny (CXDAnti) one-reroll path for Calm/Bold 31/0/31/31/31/31 ==")
    # frames: s1=IV1, s2=IV2, s3=ability, (s4,s5)=first PID (must be shiny vs player TSV -> rerolled), (s6,s7)=final PID
    want_iv1=31|(0<<5)|(31<<10); want_iv2=31|(31<<5)|(31<<10)
    anti={'Calm':[], 'Bold':[]}
    direct={'Calm':0,'Bold':0}
    for b15 in (0,1):
        hiw=(want_iv1|(b15<<15))<<16
        for low in range(0x10000):
            s1=hiw|low; s2=nxt(s1)
            if ((s2>>16)&0x7FFF)!=want_iv2: continue
            s3=nxt(s2); s4=nxt(s3); s5=nxt(s4); s6=nxt(s5); s7=nxt(s6)
            p1=((s4>>16)<<16)|(s5>>16); p2=((s6>>16)<<16)|(s7>>16)
            n1=NAT[p1%25]
            if n1 in direct: direct[n1]+=1
            psv1=((p1>>16)^(p1&0xFFFF))>>3; psv2=((p2>>16)^(p2&0xFFFF))>>3
            n2=NAT[p2%25]
            if n2 in anti and psv2!=psv1: anti[n2].append((p2,psv1,prv(s1)))
    for n in ('Calm','Bold'):
        print(f"  {n} 31/0/31/31/31/31: direct path = {direct[n]}  | one-reroll anti-shiny candidates = {len(anti[n])} (each REQUIRES player TSV=(TID^SID)>>3 shown)")
        for p2,tsv,o in anti[n][:3]: print(f"     PID {p2:08X} origin {o:08X} requires TSV {tsv}")
    check("Bold 31/0/31/31/31/31 absent on direct path", direct['Bold']==0)
    check("Calm 31/0/31/31/31/31 absent on direct path (recheck)", direct['Calm']==0)
    print("\n== SUMMARY ==")
    bad=[n for n,c,_ in ok if not c]; print("ALL PASS" if not bad else "FAILED: "+", ".join(bad))
    return 0 if not bad else 1
if __name__=='__main__': sys.exit(main())
