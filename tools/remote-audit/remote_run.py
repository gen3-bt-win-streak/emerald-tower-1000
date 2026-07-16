## リモート監査ジョブ(別セッション用・自己完結)
## 使い方: PYTHONHASHSEED=0 python3 remote_run.py <job>
##   job: scarfA | scarfB | arm10 | arm11 | arm12 | smoke
## 結果: ../../results/remote_audit_results.jsonl に1行JSONを追記(git操作は呼び出し側で)
import json, os, sys, time, collections

os.chdir(os.path.dirname(os.path.abspath(__file__)))
assert os.environ.get('PYTHONHASHSEED') == '0', 'PYTHONHASHSEED=0 で起動すること(再現性の要件)'
os.environ.setdefault('FIDELITY2', '1')

JOB = sys.argv[1] if len(sys.argv) > 1 else 'smoke'
RESULTS = os.path.abspath('../../results/remote_audit_results.jsonl')
os.makedirs(os.path.dirname(RESULTS), exist_ok=True)

_src = open('sim_v3marathon.py').read()
exec(_src[:_src.index('if __name__==')])

SNAP = json.load(open('losses_snapshot.json'))
LOST25 = set(SNAP['25000000']['losses'])
ALL_LOSSES = [s for v in SNAP.values() for s in v['losses']]

_b0 = bld
def make_bld(over):
    def b2():
        t = _b0()
        for m in t:
            if m.species in over:
                v = over[m.species]
                if isinstance(v, tuple):
                    m.item = v[0]
                    for k, x in v[1].items(): m.stats[k] = x
                else:
                    m.item = v
        return t
    return b2

def emit(rec):
    rec['job'] = JOB
    open(RESULTS, 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('RESULT:', json.dumps(rec, ensure_ascii=False), flush=True)

def fresh_range(n0, n1, label):
    fl = []; base_losses = 0; t0 = time.time()
    for i in range(n0, n1):
        seed = 25000000 + i; _battle_no[0] = i + 1
        truth = 'loss' if seed in LOST25 else 'win'
        if truth == 'loss': base_losses += 1
        _, r = G['play_battle'](seed=seed)
        got = 'win' if r == 'win' else 'loss'
        if got != truth: fl.append((seed, truth, got))
        if (i - n0 + 1) % 1000 == 0:
            print('%s %d/%d flips=%d (%.2f s/b)' % (label, i - n0 + 1, n1 - n0, len(fl), (time.time() - t0) / (i - n0 + 1)), flush=True)
    w2l = sum(1 for f in fl if f[1] == 'win')
    return dict(n=n1 - n0, base_losses=base_losses, w2l=w2l, l2w=len(fl) - w2l, flips=fl)

def loss_replay():
    lw = 0
    for seed in ALL_LOSSES:
        base = (seed // 1000000) * 1000000; _battle_no[0] = seed - base + 1
        _, r = G['play_battle'](seed=seed)
        if r == 'win': lw += 1
    return dict(loss_n=len(ALL_LOSSES), loss_rescue=lw)

if JOB == 'smoke':
    G['our_team'] = make_bld({'Metagross': 'Silk Scarf'})
    rec = fresh_range(0, 30, 'smoke')
    print('smoke OK:', rec)
elif JOB == 'scarfA':
    G['our_team'] = make_bld({'Metagross': 'Silk Scarf'})
    emit(dict(name='スカーフfresh 13k-23k', **fresh_range(13000, 23000, 'scarfA')))
elif JOB == 'scarfB':
    G['our_team'] = make_bld({'Metagross': 'Silk Scarf'})
    emit(dict(name='スカーフfresh 23k-33k', **fresh_range(23000, 33000, 'scarfB')))
elif JOB == 'arm10':
    G['our_team'] = make_bld({'Latios': 'Shell Bell'})
    emit(dict(name='⑩ラティ:光の粉→貝殻の鈴', **fresh_range(0, 3000, 'arm10'), **loss_replay()))
elif JOB == 'arm11':
    G['our_team'] = make_bld({'Metagross': 'Focus Band'})
    emit(dict(name='⑪グロス:残飯→きあいのハチマキ', **fresh_range(0, 3000, 'arm11'), **loss_replay()))
elif JOB == 'arm12':
    G['our_team'] = make_bld({'Latios': 'Scope Lens'})
    emit(dict(name='⑫ラティ:光の粉→ピントレンズ', **fresh_range(0, 3000, 'arm12'), **loss_replay()))
elif JOB == 'arm6':
    G['our_team'] = make_bld({'Latios': 'Twisted Spoon'})
    emit(dict(name='⑥ラティ:光の粉→まがったスプーン', **fresh_range(0, 3000, 'arm6'), **loss_replay()))
elif JOB == 'arm7':
    G['our_team'] = make_bld({'Swampert': 'Soft Sand'})
    emit(dict(name='⑦ラグ:ツメ→やわらかいすな', **fresh_range(0, 3000, 'arm7'), **loss_replay()))
elif JOB == 'arm8':
    G['our_team'] = make_bld({'Zapdos': 'Never Melt Ice'})
    emit(dict(name='⑧サンダー:ラム→とけないこおり', **fresh_range(0, 3000, 'arm8'), **loss_replay()))
elif JOB == 'arm9':
    G['our_team'] = make_bld({'Zapdos': 'Leftovers'})
    emit(dict(name='⑨サンダー:ラム→残飯', **fresh_range(0, 3000, 'arm9'), **loss_replay()))
elif JOB == 'arm13':
    ## 臆病サンダー(特攻349/素早328)+じしゃく: ゲンガー上取り+エンテイ同速解消(ユーザー提案)
    G['our_team'] = make_bld({'Zapdos': ('Magnet', {'spa': 349, 'spe': 328})})
    emit(dict(name='⑬サンダー:臆病+じしゃく', **fresh_range(0, 3000, 'arm13'), **loss_replay()))
elif JOB == 'arm14':
    G['our_team'] = make_bld({'Zapdos': ('Never Melt Ice', {'spa': 349, 'spe': 328})})
    emit(dict(name='⑭サンダー:臆病+とけないこおり', **fresh_range(0, 3000, 'arm14'), **loss_replay()))
else:
    raise SystemExit('unknown job: ' + JOB)
print('JOB %s 完了' % JOB, flush=True)
