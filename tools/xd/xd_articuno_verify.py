#!/usr/bin/env python3
"""XD (Pokemon XD: Gale of Darkness) Shadow Articuno provenance verifier -- self-contained, no side files.

Target individual (ground truth): Shadow Articuno, Citadark Isle, Lv50, Calm, IVs H31/A0/B31/C29/D31/S31,
PID 0x2F3C902C, XDRNG origin seed 0xECFE3E26 (= RNG state immediately before the IV1 frame), PSV 6114.

What this script does (all independent of PKHeX binaries):
  0. XDRNG (MSVC LCG: mult 0x343FD, add 0x269EC3; reverse 0xB9B33155 / 0xA170F641) with a self-test.
  1. Re-runs PokeFinder's own GameCube test vectors (Test/Gen3/gamecube.json: generateNonLock x5, generateGalesShadow x6,
     profile TID 12345 / SID 54321) through a Python port of GameCubeGenerator::generateNonLock / generateGalesShadow.
     The vectors are embedded below verbatim (seed, advances, PID, IVs, ability bit, nature).
  2. Derives the target from the origin seed frame by frame and asserts PID / IVs / nature / PSV.
  3. Reverse check: port of PKHeX MethodFinder.GetXDRNGMatch (CXD + CXDAnti branches) with XDRNG.GetSeeds ported
     both as PKHeX's lag-based recovery and as a 65536-way brute force (asserted equal).
  4. Lock chain: port of PKHeX TeamLockResult / FrameCache / NPCLock for the five Articuno TeamLock variants in
     Encounters3XDShadow.cs (XArticuno, XArticunoRhydonMoltresSeen, XArticunoRhydonMoltresTaurosSeen,
     XArticunoRhydonMoltresExeggutorSeen, XArticunoRhydonMoltresExeggutorTaurosSeen); prints the frame / PID assigned
     to each prior NPC shadow, the CPU trainer TID/SID frame and the pre-team origin seed (Cache.GetSeed(OriginFrame)).
  5. Exhaustive direct-path enumeration (no anti-shiny reroll) of every XDRNG state giving HP=Def=SpD=Spe=31:
     full Atk x SpA table for Calm, best spreads per nature under several criteria, and the two Timid spreads used by the
     Smogon Gen III Battle Tower Doubles #1 streaks (31/6/31/30/31/31 and 31/26/31/30/31/31, both HP Grass 70).
  6. Anti-shiny (CXDAnti, k rerolls) enumeration for 31/0/31/31/31/31 and the player TSV each candidate would require.

Usage: python3 xd_articuno_verify.py          (exit code 0 == all PASS)
"""
import sys
from collections import defaultdict, Counter

MASK = 0xFFFFFFFF
M, A = 0x343FD, 0x269EC3            # XDRNG forward   (PKHeX XDRNG.Mult/Add; PokeFinder LCRNG<0x269EC3,0x343FD>)
rM, rA = 0xB9B33155, 0xA170F641     # XDRNG reverse   (PKHeX XDRNG.rMult/rAdd; PokeFinder XDRNGR)
nxt = lambda s: (s * M + A) & MASK
prv = lambda s: (s * rM + rA) & MASK
NAT = ['Hardy','Lonely','Brave','Adamant','Naughty','Bold','Docile','Relaxed','Impish','Lax','Timid','Hasty','Serious',
       'Jolly','Naive','Modest','Mild','Quiet','Bashful','Rash','Calm','Gentle','Sassy','Careful','Quirky']
TARGET = dict(origin=0xECFE3E26, pid=0x2F3C902C, ivs=(31, 0, 31, 29, 31, 31), nature='Calm', psv=6114)  # ivs = H/A/B/C/D/S

# Gen 3 species with two abilities (pokeemerald species_info.h): needed because PokeFinder masks the ability bit with
# (ability0 != ability1). Everything else used here (Spheal, Salamence, Eevee, Chikorita, Umbreon, Espeon, Celebi,
# Articuno=Pressure only) has a single ability -> bit forced to 0.
TWO_ABILITIES = {165, 58}  # Ledyba (Swarm/Early Bird), Growlithe (Intimidate/Flash Fire)

RESULTS = []
def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ''))
    return bool(cond)

def unpack(iv1, iv2):
    """PokeFinder / PKHeX bit layout: IV1 = HP | Atk<<5 | Def<<10 ; IV2 = Spe | SpA<<5 | SpD<<10. Returns H/A/B/C/D/S."""
    return (iv1 & 31, (iv1 >> 5) & 31, (iv1 >> 10) & 31, (iv2 >> 5) & 31, (iv2 >> 10) & 31, iv2 & 31)

def psv_of(pid):
    return ((pid >> 16) ^ (pid & 0xFFFF)) >> 3

def is_shiny(high, low, tsv):
    """PokeFinder GameCubeGenerator.cpp:32  static bool isShiny(u16 high, u16 low, u16 tsv){ return (high^low^tsv) < 8; }"""
    return ((high ^ low ^ tsv) & 0xFFFF) < 8

# ----------------------------------------------------------------------------------------------------------------------
# 0. RNG self-test
# ----------------------------------------------------------------------------------------------------------------------
def section0():
    print("== 0. XDRNG self-test ==")
    ok = all(prv(nxt(x)) == x and nxt(prv(x)) == x for x in (0, 1, 0xECFE3E26, 0x7C1FFC51, 0xFFFFFFFF, 0x12345678))
    check("reverse constants invert forward LCG", ok, f"mult={M:#X} add={A:#X} rmult={rM:#X} radd={rA:#X}")
    check("(M*rM) mod 2^32 == 1", (M * rM) & MASK == 1)
    check("Prev2/Next constants agree with PKHeX comments", ((M * M) & MASK) == 0xA9FC6809 and ((A * (M + 1)) & MASK) == 0x1E278E7A)

# ----------------------------------------------------------------------------------------------------------------------
# 1. PokeFinder test vectors
# ----------------------------------------------------------------------------------------------------------------------
class XDRNG:
    def __init__(self, seed): self.s = seed & MASK
    def next(self): self.s = nxt(self.s); return self.s
    def u16(self): return self.next() >> 16
    def advance(self, n):
        for _ in range(n): self.next()

def pf_generate_nonlock(seed, species, tsv, shiny_never, max_adv=9):
    """Port of GameCubeGenerator::generateNonLock (Core/Gen3/Generators/GameCubeGenerator.cpp:300-396)."""
    out = []
    actual = tsv
    if species in (25, 251): actual = 31121          # Ageto Pikachu / Celebi
    elif species == 250: actual = 10048              # Mattle Ho-Oh
    base = seed
    for cnt in range(max_adv + 1):
        go = XDRNG(base)
        if species == 133:                           # Gales Eevee: TSV from its own TID/SID, then 2 advances
            actual = go.u16() ^ go.u16(); go.advance(2)
        if species in (196, 197):                    # Colo Espeon/Umbreon
            actual = go.u16() ^ go.u16()
            for _ in range(2 if species == 196 else 1):
                go.advance(2); iv1 = go.u16(); iv2 = go.u16(); ab = go.u16() % 2; hi = go.u16(); lo = go.u16()
                while is_shiny(hi, lo, actual) or (lo & 255) < 31:   # shiny-locked & male-locked (gender ratio 31)
                    hi = go.u16(); lo = go.u16()
        else:
            iv1 = go.u16(); iv2 = go.u16(); ab = go.u16() % 2; hi = go.u16(); lo = go.u16()
            if shiny_never:
                while is_shiny(hi, lo, actual): hi = go.u16(); lo = go.u16()
        pid = (hi << 16) | lo
        ab &= 1 if species in TWO_ABILITIES else 0
        out.append((cnt, pid, list(unpack(iv1, iv2)), ab, pid % 25))
        base = nxt(base)
    return out

def pf_generate_gales_shadow(seed, species, locks, stype, unset, tsv, max_adv=9):
    """Port of GameCubeGenerator::generateGalesShadow (GameCubeGenerator.cpp:215-298)."""
    out = []
    base = seed
    for cnt in range(max_adv + 1):
        go = XDRNG(base)
        go.advance(2)                                # enemy trainer TID/SID
        for (nature, gender, ratio) in locks:
            go.advance(5)                            # temp PID (2) + IVs (2) + ability (1)
            ignore = (nature == 0 and gender == 0 and ratio == 0)   # LockInfo::ignore == the member is itself a shadow
            if not ignore:
                while True:
                    hi = go.u16(); lo = go.u16(); pid = (hi << 16) | lo
                    if is_shiny(hi, lo, tsv): continue
                    if gender != 2 and gender != (1 if (pid & 0xFF) < ratio else 0): continue
                    if pid % 25 == nature: break
        if stype in ('SecondShadow', 'Salamence') and unset:
            while is_shiny(go.u16(), go.u16(), tsv): pass
        go.advance(2)                                # fake PID
        iv1 = go.u16(); iv2 = go.u16(); ab = (go.u16() % 2) & (1 if species in TWO_ABILITIES else 0)
        hi = go.u16(); lo = go.u16()
        while is_shiny(hi, lo, tsv): hi = go.u16(); lo = go.u16()
        pid = (hi << 16) | lo
        out.append((cnt, pid, list(unpack(iv1, iv2)), ab, pid % 25))
        base = nxt(base)
    return out

# Embedded PokeFinder vectors (Test/Gen3/gamecube.json, "gamecubegenerator"); results rows = [advances, pid, ivs(H/A/B/C/D/S), ability, nature]
PF_VECTORS = [
    dict(kind='nonlock', name='Colo Umbreon', seed=0, species=197, shiny_never=True,
         results=[
            [0, 2115872978, [23, 20, 8, 16, 11, 21], 0, 3],
            [1, 2832365460, [21, 16, 11, 5, 8, 13], 0, 10],
            [2, 2006226653, [13, 5, 8, 16, 31, 29], 0, 3],
            [3, 2531126724, [29, 16, 31, 6, 10, 18], 0, 24],
            [4, 3989079158, [18, 6, 10, 28, 29, 20], 0, 8],
            [5, 1345928753, [20, 28, 29, 22, 5, 29], 0, 3],
            [6, 2165919801, [29, 22, 5, 14, 27, 4], 0, 1],
            [7, 1345928753, [4, 14, 27, 3, 1, 22], 0, 3],
            [8, 1043407601, [22, 3, 1, 8, 0, 25], 0, 1],
            [9, 586278573, [25, 8, 0, 1, 20, 25], 0, 23],
         ]),
    dict(kind='nonlock', name='Colo Espeon', seed=0, species=196, shiny_never=True,
         results=[
            [0, 1345928753, [4, 14, 27, 3, 1, 22], 0, 3],
            [1, 1043407601, [22, 3, 1, 8, 0, 25], 0, 1],
            [2, 586278573, [25, 8, 0, 1, 20, 25], 0, 23],
            [3, 3870133173, [25, 1, 20, 17, 15, 17], 0, 23],
            [4, 2343942488, [17, 17, 15, 23, 8, 17], 0, 13],
            [5, 2090062999, [21, 29, 2, 10, 14, 24], 0, 24],
            [6, 3522198675, [13, 21, 25, 29, 2, 21], 0, 0],
            [7, 2090062999, [21, 29, 2, 10, 14, 24], 0, 24],
            [8, 3566724402, [24, 10, 14, 15, 20, 16], 0, 2],
            [9, 2234249425, [16, 15, 20, 4, 31, 19], 0, 0],
         ]),
    dict(kind='nonlock', name='Ageto Celebi', seed=0, species=251, shiny_never=True,
         results=[
            [0, 159752855, [6, 1, 0, 17, 7, 7], 0, 5],
            [1, 2727816725, [7, 17, 7, 23, 20, 22], 0, 0],
            [2, 773136557, [22, 23, 20, 12, 2, 5], 0, 7],
            [3, 548240925, [5, 12, 2, 20, 8, 23], 0, 0],
            [4, 2115872978, [23, 20, 8, 16, 11, 21], 0, 3],
            [5, 2832365460, [21, 16, 11, 5, 8, 13], 0, 10],
            [6, 2006226653, [13, 5, 8, 16, 31, 29], 0, 3],
            [7, 2531126724, [29, 16, 31, 6, 10, 18], 0, 24],
            [8, 3989079158, [18, 6, 10, 28, 29, 20], 0, 8],
            [9, 2222358809, [20, 28, 29, 22, 5, 29], 0, 9],
         ]),
    dict(kind='nonlock', name='Gales Eevee', seed=0, species=133, shiny_never=False,
         results=[
            [0, 2115872978, [23, 20, 8, 16, 11, 21], 0, 3],
            [1, 2832365460, [21, 16, 11, 5, 8, 13], 0, 10],
            [2, 2006226653, [13, 5, 8, 16, 31, 29], 0, 3],
            [3, 2531126724, [29, 16, 31, 6, 10, 18], 0, 24],
            [4, 3989079158, [18, 6, 10, 28, 29, 20], 0, 8],
            [5, 2222358809, [20, 28, 29, 22, 5, 29], 0, 9],
            [6, 2165919801, [29, 22, 5, 14, 27, 4], 0, 1],
            [7, 1345928753, [4, 14, 27, 3, 1, 22], 0, 3],
            [8, 1043407601, [22, 3, 1, 8, 0, 25], 0, 1],
            [9, 586278573, [25, 8, 0, 1, 20, 25], 0, 23],
         ]),
    dict(kind='nonlock', name='Gales Chikorita', seed=0, species=152, shiny_never=False,
         results=[
            [0, 159752855, [6, 1, 0, 17, 7, 7], 0, 5],
            [1, 2727816725, [7, 17, 7, 23, 20, 22], 0, 0],
            [2, 773136557, [22, 23, 20, 12, 2, 5], 0, 7],
            [3, 548240925, [5, 12, 2, 20, 8, 23], 0, 0],
            [4, 2115872978, [23, 20, 8, 16, 11, 21], 0, 3],
            [5, 2832365460, [21, 16, 11, 5, 8, 13], 0, 10],
            [6, 2006226653, [13, 5, 8, 16, 31, 29], 0, 3],
            [7, 2531126724, [29, 16, 31, 6, 10, 18], 0, 24],
            [8, 3989079158, [18, 6, 10, 28, 29, 20], 0, 8],
            [9, 2222358809, [20, 28, 29, 22, 5, 29], 0, 9],
         ]),
    dict(kind='shadow', name='Ledyba (Single Lock)', seed=0, species=165, unset=False, type='SingleLock', locks=[[0, 1, 127]],
         results=[
            [0, 2569274063, [28, 12, 31, 14, 19, 7], 1, 13],
            [1, 2146605947, [30, 16, 13, 11, 21, 28], 0, 22],
            [2, 2569274063, [28, 12, 31, 14, 19, 7], 1, 13],
            [3, 2146605947, [30, 16, 13, 11, 21, 28], 0, 22],
            [4, 2569274063, [28, 12, 31, 14, 19, 7], 1, 13],
            [5, 2146605947, [30, 16, 13, 11, 21, 28], 0, 22],
            [6, 2569274063, [28, 12, 31, 14, 19, 7], 1, 13],
            [7, 2146605947, [30, 16, 13, 11, 21, 28], 0, 22],
            [8, 2569274063, [28, 12, 31, 14, 19, 7], 1, 13],
            [9, 2146605947, [30, 16, 13, 11, 21, 28], 0, 22],
         ]),
    dict(kind='shadow', name='Spheal (First Shadow)', seed=0, species=363, unset=False, type='FirstShadow', locks=[[24, 0, 63], [12, 1, 127]],
         results=[
            [0, 2974363816, [11, 16, 16, 23, 20, 21], 0, 16],
            [1, 180087535, [31, 9, 16, 28, 14, 28], 0, 10],
            [2, 2974363816, [11, 16, 16, 23, 20, 21], 0, 16],
            [3, 180087535, [31, 9, 16, 28, 14, 28], 0, 10],
            [4, 2974363816, [11, 16, 16, 23, 20, 21], 0, 16],
            [5, 2807165562, [27, 2, 18, 29, 8, 12], 0, 12],
            [6, 2974363816, [11, 16, 16, 23, 20, 21], 0, 16],
            [7, 2807165562, [27, 2, 18, 29, 8, 12], 0, 12],
            [8, 2974363816, [11, 16, 16, 23, 20, 21], 0, 16],
            [9, 2807165562, [27, 2, 18, 29, 8, 12], 0, 12],
         ]),
    dict(kind='shadow', name='Growlithe (First shadow unset)', seed=0, species=58, unset=True, type='SecondShadow', locks=[[24, 0, 127], [6, 1, 127], [0, 0, 0]],
         results=[
            [0, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [1, 1179959585, [27, 21, 2, 23, 26, 15], 1, 10],
            [2, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [3, 1179959585, [27, 21, 2, 23, 26, 15], 1, 10],
            [4, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [5, 1708122872, [20, 7, 5, 26, 0, 8], 0, 22],
            [6, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [7, 1708122872, [20, 7, 5, 26, 0, 8], 0, 22],
            [8, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [9, 1708122872, [20, 7, 5, 26, 0, 8], 0, 22],
         ]),
    dict(kind='shadow', name='Growlithe (First shadow set)', seed=0, species=58, unset=False, type='SecondShadow', locks=[[24, 0, 127], [6, 1, 127], [0, 0, 0]],
         results=[
            [0, 2644165290, [8, 3, 20, 29, 11, 20], 1, 15],
            [1, 3941593287, [28, 28, 14, 18, 15, 6], 1, 12],
            [2, 2644165290, [8, 3, 20, 29, 11, 20], 1, 15],
            [3, 3941593287, [28, 28, 14, 18, 15, 6], 1, 12],
            [4, 2644165290, [8, 3, 20, 29, 11, 20], 1, 15],
            [5, 2202535314, [0, 24, 6, 17, 15, 1], 0, 14],
            [6, 2644165290, [8, 3, 20, 29, 11, 20], 1, 15],
            [7, 2202535314, [0, 24, 6, 17, 15, 1], 0, 14],
            [8, 2644165290, [8, 3, 20, 29, 11, 20], 1, 15],
            [9, 2202535314, [0, 24, 6, 17, 15, 1], 0, 14],
         ]),
    dict(kind='shadow', name='Salamence (First shadow unset)', seed=0, species=373, unset=True, type='Salamence', locks=[[6, 1, 127], [0, 0, 0]],
         results=[
            [0, 1179959585, [27, 21, 2, 23, 26, 15], 0, 10],
            [1, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [2, 1179959585, [27, 21, 2, 23, 26, 15], 0, 10],
            [3, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [4, 1179959585, [27, 21, 2, 23, 26, 15], 0, 10],
            [5, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [6, 1179959585, [27, 21, 2, 23, 26, 15], 0, 10],
            [7, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
            [8, 1179959585, [27, 21, 2, 23, 26, 15], 0, 10],
            [9, 500003548, [7, 12, 30, 12, 7, 26], 0, 23],
         ]),
    dict(kind='shadow', name='Salamence (First shadow set)', seed=0, species=373, unset=False, type='Salamence', locks=[[6, 1, 127], [0, 0, 0]],
         results=[
            [0, 3941593287, [28, 28, 14, 18, 15, 6], 0, 12],
            [1, 2644165290, [8, 3, 20, 29, 11, 20], 0, 15],
            [2, 3941593287, [28, 28, 14, 18, 15, 6], 0, 12],
            [3, 2644165290, [8, 3, 20, 29, 11, 20], 0, 15],
            [4, 3941593287, [28, 28, 14, 18, 15, 6], 0, 12],
            [5, 2644165290, [8, 3, 20, 29, 11, 20], 0, 15],
            [6, 3941593287, [28, 28, 14, 18, 15, 6], 0, 12],
            [7, 2644165290, [8, 3, 20, 29, 11, 20], 0, 15],
            [8, 3941593287, [28, 28, 14, 18, 15, 6], 0, 12],
            [9, 2644165290, [8, 3, 20, 29, 11, 20], 0, 15],
         ]),
]

def section1():
    print("\n== 1. PokeFinder GameCube test vectors (Profile3 TID 12345 / SID 54321 -> TSV 12345^54321 = %d) ==" % (12345 ^ 54321))
    tsv = 12345 ^ 54321
    allok = True
    for v in PF_VECTORS:
        if v['kind'] == 'nonlock':
            got = pf_generate_nonlock(v['seed'], v['species'], tsv, v['shiny_never'])
        else:
            got = pf_generate_gales_shadow(v['seed'], v['species'], [tuple(l) for l in v['locks']], v['type'], v['unset'], tsv)
        exp = [tuple(r[:1]) + (r[1], r[2], r[3], r[4]) for r in v['results']]
        good = sum(1 for g, e in zip(got, exp) if g[0] == e[0] and g[1] == e[1] and g[2] == e[2] and g[3] == e[3] and g[4] == e[4])
        allok &= check(f"PokeFinder {v['kind']:8s} {v['name']}", good == len(exp) == len(got),
                       f"{good}/{len(exp)} states match; adv0 PID {got[0][1]:08X} IVs {got[0][2]} exp {exp[0][1]:08X} {exp[0][2]}")
    check("all PokeFinder vectors reproduced", allok, f"{len(PF_VECTORS)} vectors, {sum(len(v['results']) for v in PF_VECTORS)} states")

# ----------------------------------------------------------------------------------------------------------------------
# 2. Derivation of the target from the origin seed
# ----------------------------------------------------------------------------------------------------------------------
def derive(origin):
    s = origin; fr = []
    for _ in range(7): s = nxt(s); fr.append(s)
    iv1 = (fr[0] >> 16) & 0x7FFF; iv2 = (fr[1] >> 16) & 0x7FFF
    ab = (fr[2] >> 16) & 1
    pid = ((fr[3] >> 16) << 16) | (fr[4] >> 16)
    alt = ((fr[5] >> 16) << 16) | (fr[6] >> 16)   # PID the game would use instead if (s4,s5) were shiny vs player TSV
    return fr, iv1, iv2, ab, pid, alt

def section2():
    print("\n== 2. Derivation from origin seed (state before IV1) ==")
    fr, iv1, iv2, ab, pid, alt = derive(TARGET['origin'])
    labels = ['IV1 (HP|Atk<<5|Def<<10)', 'IV2 (Spe|SpA<<5|SpD<<10)', 'ability (bit0)', 'PID high', 'PID low', '(reroll PID high)', '(reroll PID low)']
    print(f"  origin s0 = {TARGET['origin']:08X}")
    for i, (s, l) in enumerate(zip(fr, labels), 1):
        print(f"  s{i} = {s:08X}  out(upper16) = {s >> 16:04X}  {l}")
    ivs = unpack(iv1, iv2)
    print(f"  IV1 raw {fr[0] >> 16:04X} -> masked 15-bit {iv1:04X} = {iv1:015b} -> HP={iv1 & 31} Atk={(iv1 >> 5) & 31} Def={(iv1 >> 10) & 31}")
    print(f"  IV2 raw {fr[1] >> 16:04X} -> masked 15-bit {iv2:04X} = {iv2:015b} -> Spe={iv2 & 31} SpA={(iv2 >> 5) & 31} SpD={(iv2 >> 10) & 31}")
    print(f"  ability frame out {fr[2] >> 16:04X} -> bit0 = {ab}; Articuno has one ability (Pressure) so ability index = 0 regardless")
    print(f"  PID = {fr[3] >> 16:04X}{fr[4] >> 16:04X} = {pid:08X} = {pid} ; PID % 25 = {pid % 25} = {NAT[pid % 25]}")
    print(f"  PSV = ({fr[3] >> 16:04X} ^ {fr[4] >> 16:04X}) >> 3 = {((fr[3] >> 16) ^ (fr[4] >> 16)):04X} >> 3 = {psv_of(pid)}")
    print(f"  (if the player's (TID^SID)>>3 were {psv_of(pid)} the game would reroll and produce PID {alt:08X} = {NAT[alt % 25]} instead)")
    check("derived PID == 2F3C902C", pid == TARGET['pid'], f"{pid:08X}")
    check("derived IVs == 31/0/31/29/31/31 (H/A/B/C/D/S)", ivs == TARGET['ivs'], str(ivs))
    check("nature == Calm (PID % 25 == 20)", pid % 25 == 20 and NAT[20] == 'Calm')
    check("PSV == 6114", psv_of(pid) == TARGET['psv'])
    check("not shiny for any player TSV != 6114 (no reroll occurs)", psv_of(pid) == 6114)
    # PokeFinder Static (non-lock) path for Articuno = galesColo index 67 {specie 144, Lv50, Shiny::Never}: same 5 frames
    pf = pf_generate_nonlock(TARGET['origin'], 144, 12345 ^ 54321, True, max_adv=0)[0]
    check("PokeFinder generateNonLock(Articuno) at seed ECFE3E26 advance 0 gives the target", pf[1] == TARGET['pid'] and tuple(pf[2]) == TARGET['ivs'],
          f"PID {pf[1]:08X} IVs {pf[2]} ability {pf[3]}")
    return pid, ivs

# ----------------------------------------------------------------------------------------------------------------------
# 3. Reverse check (PKHeX MethodFinder.GetXDRNGMatch)
# ----------------------------------------------------------------------------------------------------------------------
LAG0, LAG1, RLOWER, RUPPER = 0xE8D1, 0x5F47, 0x55FF8537, 0x55FFBC6C   # PKHeX XDRNG.cs:244-247

def xdrng_get_seeds_pkhex(first, second):
    """Port of PKHeX XDRNG.GetSeeds(Span<uint>, uint first, uint second) (XDRNG.cs:261-292); first/second already << 16.
    Returns the states two frames before `second`'s state, i.e. the state whose next output is `first`... precisely: Prev(Prev(second|low))."""
    res = []
    tmp = (((first - (second * rM)) & MASK) >> 16) * LAG0
    lo = ((tmp + RLOWER) >> 16) & MASK
    up = ((tmp + RUPPER) >> 16) & MASK
    low = (lo * LAG1) % LAG0
    while True:
        seed = prv(second | low)
        if (seed & 0xFFFF0000) == first: res.append(prv(seed))
        low += LAG0
        if low >= 0x10000: break
    if lo != up:
        low = (up * LAG1) % LAG0
        while True:
            seed = prv(second | low)
            if (seed & 0xFFFF0000) == first: res.append(prv(seed))
            low += LAG0
            if low >= 0x10000: break
    return res

def xdrng_get_seeds_brute(first, second):
    res = []
    for low in range(0x10000):
        seed = prv(second | low)
        if (seed & 0xFFFF0000) == first: res.append(prv(seed))
    return res

def get_xdrng_match(pid, ivs, tid=0, sid=0, use_brute=False):
    """Port of PKHeX MethodFinder.GetXDRNGMatch (MethodFinder.cs:254-303). Returns list of (type, origin)."""
    hp, at, df, spa, spd, spe = ivs
    iv1 = hp | (at << 5) | (df << 10); iv2 = spe | (spa << 5) | (spd << 10)
    top = pid & 0xFFFF0000; bot = (pid << 16) & MASK
    seeds = xdrng_get_seeds_brute(top, bot) if use_brute else xdrng_get_seeds_pkhex(top, bot)
    found = []
    for seed in seeds:                       # seed = state before the PID-high frame (s3)
        B = prv(seed); Aa = prv(B)           # B = s2 (IV2 frame), A = s1 (IV1 frame)
        if ((Aa >> 16) & 0x7FFF) == iv1 and ((B >> 16) & 0x7FFF) == iv2:
            found.append(('CXD', prv(Aa))); continue
        tsv = (tid ^ sid) >> 3
        if ((top ^ bot) >> 19) == tsv: continue          # already shiny -> would not have been rerolled
        p2, p1 = seed, B
        if ((p2 ^ p1) >> 19) != tsv: continue            # the prior PID pair must be shiny vs player TSV
        while True:
            B = prv(Aa); Aa = prv(B)
            if ((Aa >> 16) & 0x7FFF) == iv1 and ((B >> 16) & 0x7FFF) == iv2:
                found.append(('CXDAnti', prv(Aa))); break
            p2 = prv(p1); p1 = prv(p2)
            if ((p2 ^ p1) >> 19) != tsv: break
    return found

def section3():
    print("\n== 3. Reverse check: port of PKHeX MethodFinder.GetXDRNGMatch ==")
    pid, ivs = TARGET['pid'], TARGET['ivs']
    top = pid & 0xFFFF0000; bot = (pid << 16) & MASK
    s_pk = sorted(xdrng_get_seeds_pkhex(top, bot)); s_br = sorted(xdrng_get_seeds_brute(top, bot))
    print(f"  XDRNG.GetSeeds(top={top:08X}, bot={bot:08X}) [lag algorithm] -> {[f'{x:08X}' for x in s_pk]}")
    print(f"  XDRNG.GetSeeds brute force (65536 lows)                -> {[f'{x:08X}' for x in s_br]}")
    check("lag-based GetSeeds == brute force GetSeeds", s_pk == s_br)
    for seed in s_pk:
        B = prv(seed); Aa = prv(B)
        print(f"  candidate s3={seed:08X}: s2={B:08X} (out&0x7FFF={((B >> 16) & 0x7FFF):04X} want IV2 {ivs[5] | (ivs[3] << 5) | (ivs[4] << 10):04X}), "
              f"s1={Aa:08X} (out&0x7FFF={((Aa >> 16) & 0x7FFF):04X} want IV1 {ivs[0] | (ivs[1] << 5) | (ivs[2] << 10):04X}) -> origin Prev(s1)={prv(Aa):08X}")
    res = get_xdrng_match(pid, ivs)
    print(f"  GetXDRNGMatch result: {[(t, f'{o:08X}') for t, o in res]}")
    check("reverse check returns exactly one origin, 0xECFE3E26, type CXD", res == [('CXD', TARGET['origin'])])
    check("reverse check identical with brute-force seed recovery", get_xdrng_match(pid, ivs, use_brute=True) == res)
    # independence from the player's TID/SID: CXD branch does not consult them
    check("CXD result independent of player TID/SID (sampled 0/0, 12345/54321, 48912/0)",
          all(get_xdrng_match(pid, ivs, t, s)[0] == ('CXD', TARGET['origin']) for t, s in ((0, 0), (12345, 54321), (48912, 0))))

# ----------------------------------------------------------------------------------------------------------------------
# 4. Lock chain (PKHeX TeamLockResult) for the 5 Articuno TeamLock variants
# ----------------------------------------------------------------------------------------------------------------------
# Encounters3XDShadow.cs:825-899. Locks listed in generation order; Seen -> FramesConsumed 5, unseen -> 7 (NPCLock.cs:14).
# All prior members are shadows without nature lock -> NPCLock.MatchesLock() is always true (NPCLock.cs:37).
ARTICUNO_VARIANTS = {
    'XArticuno (none seen)':                        [('Rhydon', False), ('Moltres', False), ('Exeggutor', False), ('Tauros', False)],
    'XArticunoRhydonMoltresSeen':                   [('Rhydon', True),  ('Moltres', True),  ('Exeggutor', False), ('Tauros', False)],
    'XArticunoRhydonMoltresTaurosSeen':             [('Rhydon', True),  ('Moltres', True),  ('Exeggutor', False), ('Tauros', True)],
    'XArticunoRhydonMoltresExeggutorSeen':          [('Rhydon', True),  ('Moltres', True),  ('Exeggutor', True),  ('Tauros', False)],
    'XArticunoRhydonMoltresExeggutorTaurosSeen':    [('Rhydon', True),  ('Moltres', True),  ('Exeggutor', True),  ('Tauros', True)],
}
NOT_FORCED = 0xFFFFFFFF

class FrameCache:
    """PKHeX FrameCache: index 0 = origin passed in; index i = i reverse steps. this[i] = seed>>16, GetSeed(i) = seed."""
    def __init__(self, origin): self.seeds = [origin]
    def __getitem__(self, i):
        while i >= len(self.seeds): self.seeds.append(prv(self.seeds[-1]))
        return self.seeds[i] >> 16
    def get_seed(self, i):
        self[i]; return self.seeds[i]

class TeamLockResult:
    """Port of PKHeX TeamLockResult (TeamLockResult.cs). tsv = player's (TID^SID)>>3 (XD only). Search bound guards the
    unbounded 'maybe an anti-shiny reroll happened' generators (they are infinite in PKHeX; DFS stops at first success)."""
    def __init__(self, locks, origin_seed, tsv, bound=64):
        self.locks = list(locks)            # generation order
        self.cache = FrameCache(prv(prv(origin_seed)))
        self.tsv = tsv; self.bound = bound
        self.rcsv = NOT_FORCED
        self.team = []                      # (name, pid, frame) pushed in reverse generation order
        self.origin_frame = None
        self.valid = self.find(0, len(self.locks) - 1, None)
        self.origin_seed = self.cache.get_seed(self.origin_frame) if self.valid else None
        self.cpu = None
        if self.valid:
            f = self.origin_frame - 2
            self.cpu = (self.cache[f + 1], self.cache[f], f)   # TID16, SID16, frame

    def frames_consumed(self, idx): return 5 if self.locks[idx][1] else 7

    def find(self, frame, idx, prior_idx):
        if idx < 0: return self.verify_npc(frame)
        for (pid, fid) in self.possible_locks(frame, idx, prior_idx):
            self.team.append((self.locks[idx][0], pid, fid - self.frames_consumed(idx)))
            if self.find(fid, idx - 1, idx): return True
            self.team.pop()
        return False

    def possible_locks(self, ctr, idx, prior_idx):
        # GetPossibleLocks: prior is null or a shadow -> GetSingleLock; a non-shadow prior -> GetAllLocks (not needed here:
        # every prior member of the Articuno team is a shadow).
        return self.single_lock(ctr, idx)

    def single_lock(self, ctr, idx):
        C = self.cache; fc = self.frames_consumed(idx)
        pid = (C[ctr + 1] << 16) | C[ctr]
        # MatchesLock: shadow with no nature lock -> always true
        yield (pid, ctr + fc)
        forced = False; start = 2
        while start < self.bound:
            sv = (C[start + 1] ^ C[start]) >> 3
            if sv == self.tsv:
                pass                                    # anti-shiny rerolled by the player TSV: possible frame
            elif self.rcsv != NOT_FORCED:
                if sv == self.rcsv:
                    self.rcsv = sv; forced = True; start += 2; continue
                if forced: self.rcsv = NOT_FORCED
                return
            yield (pid, start + fc)
            start += 2

    def verify_npc(self, ctr):
        C = self.cache
        tid, sid = C[ctr + 1], C[ctr]
        cpusv = (tid ^ sid) >> 3
        if self.rcsv != NOT_FORCED and self.rcsv != cpusv: return False
        for (_, pid, _) in self.team:
            if psv_of(pid) == cpusv: return False       # XD: no shiny shadow member vs CPU trainer either
        self.origin_frame = ctr + 2
        return True

def section4():
    print("\n== 4. Lock chain: port of PKHeX TeamLockResult for the 5 Articuno TeamLock variants ==")
    print(f"  FrameCache origin = Prev2({TARGET['origin']:08X}) = {prv(prv(TARGET['origin'])):08X}  (frame 0 = Tauros PID low, frame 1 = Tauros PID high)")
    tsv_samples = [0, 1234, 6114 ^ 1, 7000]  # player TSV is unknown; result must hold for any TSV != 6114
    allvalid = True; chains = {}
    for name, locks in ARTICUNO_VARIANTS.items():
        r = TeamLockResult(locks, TARGET['origin'], tsv_samples[0])
        allvalid &= r.valid
        chains[name] = r
        if r.valid:
            desc = ' | '.join(f"{n}@f{f}:{p:08X}(PSV {psv_of(p)})" for (n, p, f) in reversed(r.team))
            print(f"  {name:44s} VALID  {desc}")
            print(f"  {'':44s}        CPU TID/SID @f{r.cpu[2]}: TID {r.cpu[0]:04X}({r.cpu[0]}) SID {r.cpu[1]:04X}({r.cpu[1]}) CPU-SV {(r.cpu[0] ^ r.cpu[1]) >> 3}"
                  f" ; OriginFrame {r.origin_frame} ; pre-team origin seed Cache.GetSeed({r.origin_frame}) = {r.origin_seed:08X}")
        else:
            print(f"  {name:44s} INVALID")
        # TSV independence for the trivial chain (first candidate at every level)
        same = all(TeamLockResult(locks, TARGET['origin'], t).valid for t in tsv_samples)
        allvalid &= same
    check("lock chain VALID for all 5 Articuno TeamLock variants (any sampled player TSV)", allvalid)
    # forward re-generation from the pre-team seed to prove the chain is self-consistent
    r = chains['XArticuno (none seen)']
    s = r.origin_seed
    def u16():
        nonlocal s; s = nxt(s); return s >> 16
    tid = u16(); sid = u16()
    fwd = []
    for nm in ('Rhydon', 'Moltres', 'Exeggutor', 'Tauros'):
        for _ in range(5): u16()                        # temp PID 2 + IV 2 + ability 1
        hi = u16(); lo = u16(); fwd.append((nm, (hi << 16) | lo))
    for _ in range(2): u16()                            # Articuno temp PID
    state_before_iv1 = s
    print(f"  forward from pre-team seed {r.origin_seed:08X}: TID {tid:04X} SID {sid:04X}; " + ', '.join(f"{n} {p:08X}" for n, p in fwd)
          + f"; state before Articuno IV1 = {state_before_iv1:08X}")
    check("forward regeneration from pre-team seed reaches origin ECFE3E26 with the same NPC PIDs",
          state_before_iv1 == TARGET['origin'] and [(n, p) for (n, p, _) in reversed(r.team)] == fwd and (tid, sid) == (r.cpu[0], r.cpu[1]))
    npc_psv = sorted({psv_of(p) for c in chains.values() for (_, p, _) in c.team})
    print(f"  NPC shadow PSVs in the trivial chains (a player TSV equal to one of these shifts that NPC by an anti-shiny reroll; still valid per PKHeX): {npc_psv}")
    check("no NPC shadow in the trivial chain shares PSV 6114 with the Articuno", 6114 not in npc_psv)

# ----------------------------------------------------------------------------------------------------------------------
# 5. Exhaustive direct-path enumeration with HP=Def=SpD=Spe=31
# ----------------------------------------------------------------------------------------------------------------------
def enumerate_direct():
    """Every XDRNG state s1 whose output encodes HP=31, Def=31 (any Atk, any bit15) such that s2 encodes SpD=31, Spe=31 (any SpA).
    Direct path = frames IV1, IV2, ability, PIDhi, PIDlo with no anti-shiny reroll (valid for any player TSV != PSV)."""
    rows = []
    for atk in range(32):
        for b15 in (0, 1):
            hiw = (31 | (atk << 5) | (31 << 10) | (b15 << 15)) << 16
            for low in range(0x10000):
                s1 = hiw | low; s2 = nxt(s1); iv2 = (s2 >> 16) & 0x7FFF
                if (iv2 & 31) != 31 or ((iv2 >> 10) & 31) != 31: continue
                s3 = nxt(s2); s4 = nxt(s3); s5 = nxt(s4)
                pid = ((s4 >> 16) << 16) | (s5 >> 16)
                rows.append((NAT[pid % 25], atk, (iv2 >> 5) & 31, pid, prv(s1)))
    return rows

def section5():
    print("\n== 5. Exhaustive direct-path enumeration: all XDRNG states with HP=Def=SpD=Spe=31 (Atk, SpA, nature free) ==")
    rows = enumerate_direct()
    bynat = Counter(r[0] for r in rows)
    print(f"  total direct-path states with H/B/D/S=31: {len(rows)} (expected ~4096 if the LCG were uniform: 32 Atk x 2 bit15 x 65536 lows / 1024; the exact count is what matters)")
    print(f"  per nature: {dict(sorted(bynat.items(), key=lambda kv: NAT.index(kv[0])))}")
    print(f"  Calm + Careful = {bynat['Calm'] + bynat['Careful']}")
    calm = [r for r in rows if r[0] == 'Calm']
    per_atk = Counter(r[1] for r in calm)
    print(f"  Calm: {len(calm)} states; count per Atk value: {dict(sorted(per_atk.items()))}")
    table = defaultdict(list)
    for (_, atk, spa, pid, org) in calm: table[atk].append((spa, pid, org))
    for atk in sorted(table):
        cells = sorted(table[atk], reverse=True)
        print(f"    Calm Atk={atk:2d}: SpA values {[c[0] for c in cells]}")
    a0 = sorted(table[0], reverse=True)
    print("  Calm Atk=0 full list (SpA, PID, origin): " + ', '.join(f"C{c} {p:08X}@{o:08X}" for c, p, o in a0))
    check("Calm 31/0/31/31/31/31 does NOT occur on the direct path", all(c != 31 for c, _, _ in a0))
    check("Calm 31/0/31/29/31/31 occurs with PID 2F3C902C origin ECFE3E26", (29, TARGET['pid'], TARGET['origin']) in a0)
    check("Calm Atk=0: maximum SpA is 29", max(c for c, _, _ in a0) == 29)
    spa31 = sorted(((atk, pid, org) for (_, atk, spa, pid, org) in calm if spa == 31))
    print(f"  Calm SpA=31 exists only with Atk in {[a for a, _, _ in spa31]}; lowest: Atk={spa31[0][0]} PID {spa31[0][1]:08X} origin {spa31[0][2]:08X}")
    print("  best spread per nature (H/B/D/S=31), three criteria:")
    print("    (a) min Atk with SpA=31 | (b) max SpA with Atk=0 | (c) highest IV sum (Atk+SpA)")
    expect = {'Bold': (0, 31), 'Calm': (5, 31), 'Modest': (4, 31), 'Timid': (6, 31)}
    for n in ('Bold', 'Calm', 'Modest', 'Timid'):
        sub = [r for r in rows if r[0] == n]
        a = min(((atk, pid, org) for (_, atk, spa, pid, org) in sub if spa == 31), default=None)
        b = max(((spa, pid, org) for (_, atk, spa, pid, org) in sub if atk == 0), default=None)
        c = max(sub, key=lambda r: (r[1] + r[2], -r[1]))
        sa = f"31/{a[0]}/31/31/31/31 PID {a[1]:08X} origin {a[2]:08X}" if a else 'none'
        sb = f"31/0/31/{b[0]}/31/31 PID {b[1]:08X} origin {b[2]:08X}" if b else 'none'
        sc = f"31/{c[1]}/31/{c[2]}/31/31 PID {c[3]:08X} origin {c[4]:08X}"
        ea, es = expect[n]
        match = (a is not None and a[0] == ea)
        print(f"    {n:6s} ({len(sub):3d} states): (a) {sa} | (b) {sb} | (c) {sc}  -> claim 31/{ea}/31/{es}/31/31 {'MATCHES criterion (a)' if match else 'NOT found under (a)'}")
    check("Modest best (a) = 31/4/31/31/31/31", min(atk for (n, atk, spa, _, _) in rows if n == 'Modest' and spa == 31) == 4)
    check("Timid best (a) = 31/6/31/31/31/31", min(atk for (n, atk, spa, _, _) in rows if n == 'Timid' and spa == 31) == 6)
    check("Calm best (a) = 31/5/31/31/31/31", min(atk for (n, atk, spa, _, _) in rows if n == 'Calm' and spa == 31) == 5)
    bold_a = min((atk for (n, atk, spa, _, _) in rows if n == 'Bold' and spa == 31), default=None)
    check("Bold: report min Atk with SpA=31 (claimed 0)", bold_a is not None, f"actual min Atk = {bold_a}")
    # Smogon Gen III Battle Frontier leaderboard #1 (Jheisinho): Articuno "Timid / IVs: 6 Atk / 30 SpA" (Open Level 1316,
    # p.77 #1908, 2025-01-28) and "Timid / IVs: 26 Atk / 30 SpA" (Lv50 1001 paste). Both are Hidden Power Grass 70.
    def hp_type_power(h, a, b, c, d, s_):
        t = ((h & 1) + (a & 1) * 2 + (b & 1) * 4 + (s_ & 1) * 8 + (c & 1) * 16 + (d & 1) * 32) * 15 // 63
        pw = (((h >> 1) & 1) + ((a >> 1) & 1) * 2 + ((b >> 1) & 1) * 4 + ((s_ >> 1) & 1) * 8 + ((c >> 1) & 1) * 16
              + ((d >> 1) & 1) * 32) * 40 // 63 + 30
        return ['Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', 'Fire', 'Water', 'Grass',
                'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark'][t], pw
    print("  Smogon #1 (Jheisinho) Articuno spreads on the direct path:")
    for atk, spa in ((6, 30), (26, 30)):
        hits = [(pid, org) for (n, a, c, pid, org) in rows if n == 'Timid' and a == atk and c == spa]
        for pid, org in hits:
            print(f"    Timid 31/{atk}/31/{spa}/31/31 HP {hp_type_power(31, atk, 31, spa, 31, 31)} -> PID {pid:08X} origin {org:08X} PSV {psv_of(pid)}")
        check(f"Jheisinho Timid 31/{atk}/31/{spa}/31/31 exists on the direct path (unique)", len(hits) == 1)
    grass70 = sorted({(a, c) for (n, a, c, _, _) in rows if n == 'Timid' and hp_type_power(31, a, 31, c, 31, 31) == ('Grass', 70)})
    print(f"    all Timid H/B/D/S=31 direct-path spreads with HP Grass 70 (Atk, SpA): {grass70}")
    check("SpA=30 is the highest SpA among Timid HP-Grass-70 direct-path spreads (only Atk 6 and 26)",
          [ac for ac in grass70 if ac[1] == 30] == [(6, 30), (26, 30)] and max(c for _, c in grass70) == 30)
    return rows

# ----------------------------------------------------------------------------------------------------------------------
# 6. Anti-shiny (CXDAnti) path
# ----------------------------------------------------------------------------------------------------------------------
def enumerate_anti(ivs, max_rerolls=2):
    """Frame structure (PKHeX GetXDRNGMatch CXDAnti branch; MethodCXD.GetPID loop 'while shiny: reroll'):
       s1 IV1, s2 IV2, s3 ability, (s4,s5) PID#0, (s6,s7) PID#1, ... ; the game keeps PID#k only if PID#0..#(k-1) are all
       shiny vs the player's TSV (TID^SID) and PID#k is not. So k rerolls REQUIRE player (TID^SID)>>3 == PSV(PID#0) == ... == PSV(PID#(k-1)).
    Returns dict k -> list of (final_pid, required_tsv, origin, pid0)."""
    hp, at, df, spa, spd, spe = ivs
    iv1 = hp | (at << 5) | (df << 10); iv2 = spe | (spa << 5) | (spd << 10)
    out = defaultdict(list); direct = []
    for b15 in (0, 1):
        hiw = (iv1 | (b15 << 15)) << 16
        for low in range(0x10000):
            s1 = hiw | low; s2 = nxt(s1)
            if ((s2 >> 16) & 0x7FFF) != iv2: continue
            s = nxt(s2)                                  # ability frame
            pids = []
            for _ in range(max_rerolls + 1):
                a = nxt(s); b = nxt(a); pids.append(((a >> 16) << 16) | (b >> 16)); s = b
            direct.append((pids[0], prv(s1)))
            for k in range(1, max_rerolls + 1):
                req = psv_of(pids[0])
                if all(psv_of(p) == req for p in pids[:k]) and psv_of(pids[k]) != req:
                    out[k].append((pids[k], req, prv(s1), pids[0]))
    return direct, out

def section6():
    print("\n== 6. Anti-shiny (CXDAnti) path for 31/0/31/31/31/31 ==")
    print("  frame structure: s1=IV1 s2=IV2 s3=ability (s4,s5)=PID#0 (s6,s7)=PID#1 ... ; k rerolls need PSV(PID#0..#k-1) == player (TID^SID)>>3 != PSV(PID#k)")
    direct, anti = enumerate_anti((31, 0, 31, 31, 31, 31), max_rerolls=2)
    dn = Counter(NAT[p % 25] for p, _ in direct)
    print(f"  direct path (k=0) states with 31/0/31/31/31/31: {len(direct)} ; per nature {dict(dn)}")
    print(f"  direct-path Calm count = {dn['Calm']} ; Bold count = {dn['Bold']}")
    for k in (1, 2):
        c = Counter(NAT[p % 25] for p, _, _, _ in anti[k])
        print(f"  k={k} reroll(s): {len(anti[k])} candidates total (per nature {dict(c)})")
    calm1 = [x for x in anti[1] if NAT[x[0] % 25] == 'Calm']
    bold1 = [x for x in anti[1] if NAT[x[0] % 25] == 'Bold']
    print(f"  Calm 31/0/31/31/31/31 via one reroll: {len(calm1)} candidates")
    for p, t, o, p0 in calm1[:3]: print(f"     final PID {p:08X} requires player TSV {t} (PID#0 {p0:08X}), origin {o:08X}")
    print(f"  Bold 31/0/31/31/31/31 via one reroll: {len(bold1)} candidates")
    for p, t, o, p0 in bold1[:3]: print(f"     final PID {p:08X} requires player TSV {t} (PID#0 {p0:08X}), origin {o:08X}")
    print("  examples (any nature, one reroll):")
    for p, t, o, p0 in anti[1][:3]:
        print(f"     origin {o:08X}: PID#0 {p0:08X} (PSV {psv_of(p0)}) shiny only if player TSV={t} -> final PID {p:08X} {NAT[p % 25]} (PSV {psv_of(p)})")
    check("Calm 31/0/31/31/31/31 absent on direct path", dn['Calm'] == 0)
    check("Calm 31/0/31/31/31/31 absent via one anti-shiny reroll", len(calm1) == 0)
    check("Calm 31/0/31/31/31/31 absent via two anti-shiny rerolls", not any(NAT[p % 25] == 'Calm' for p, _, _, _ in anti[2]))
    # the target's own IVs: alternative PIDs reachable by anti-shiny with 31/0/31/29/31/31
    d2, a2 = enumerate_anti(TARGET['ivs'], max_rerolls=1)
    calm_alt = [x for x in a2[1] if NAT[x[0] % 25] == 'Calm']
    print(f"  (for 31/0/31/29/31/31: direct Calm states = {sum(1 for p, _ in d2 if NAT[p % 25] == 'Calm')}, one-reroll Calm candidates = {len(calm_alt)}:"
          + ', '.join(f" {p:08X} needs TSV {t}" for p, t, _, _ in calm_alt) + ")")
    check("target PID 2F3C902C is a direct-path (k=0) result, not an anti-shiny result",
          any(p == TARGET['pid'] for p, _ in d2) and not any(p == TARGET['pid'] for p, _, _, _ in a2[1]))

def main():
    section0(); section1(); section2(); section3(); section4(); section5(); section6()
    bad = [n for n, c in RESULTS if not c]
    print("\n== SUMMARY ==")
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} checks passed")
    print("ALL PASS" if not bad else "FAILED: " + '; '.join(bad))
    return 0 if not bad else 1

if __name__ == '__main__':
    sys.exit(main())
