## v4 ブラウザ・アドバイザー
## PCで起動 → 同じWi-FiのスマホからタップUIで盤面入力 → ボット(条項+2手読み)の推奨手を表示。
## 使い方: PYTHONHASHSEED=0 FIDELITY2=1 python3 advisor_web.py
##   → 表示されるURL(例 http://192.168.x.x:8787)をスマホのブラウザで開く。
import json, threading, socket, os, sys
_D=os.path.dirname(os.path.abspath(__file__)); os.chdir(_D); sys.path.insert(0,_D)  # どこから起動してもOKに
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import advisor  # エンジン読み込み(20-30秒)。make_foe/build_battle/fmt_act/G/v3_choose を再利用
from jpnames import JPS

G=advisor.G; v3_choose=advisor.v3_choose
LOCK=threading.Lock()
SPECIES=sorted(advisor.bySp.keys())
MOVELISTS={sp:[advisor.jpmv(m) for m in sorted({m for e in advisor.bySp[sp] for m in e['moves']})] for sp in SPECIES}
STATUS={"":None,"まひ":"PAR","やけど":"BRN","ねむり":"SLP","こおり":"FRZ","どく":"PSN"}
OURJP=["サンダー","メタグロス","ラティオス","ラグラージ"]

PAGE=r"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>v4 アドバイザー</title>
<style>
:root{--bg:#0C1512;--panel:#132019;--line:#23392E;--ink:#E6F2EA;--sub:#9DB8AA;--acc:#2FBF8F;--dan:#E5484D;--chip:#1B2B23}
@media (prefers-color-scheme: light){:root{--bg:#F3F8F4;--panel:#fff;--line:#D3E2D7;--ink:#17251D;--sub:#5B7265;--acc:#0E9F6E;--dan:#C93338;--chip:#E4EFE7}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",Meiryo,system-ui,sans-serif;font-size:16px;line-height:1.5}
.wrap{max-width:560px;margin:0 auto;padding:14px 12px 90px}
h1{font-size:17px;margin:4px 0 12px}
.sec{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:10px}
.sec h2{font-size:13px;color:var(--sub);margin:0 0 8px;letter-spacing:.06em}
label{font-size:12px;color:var(--sub);display:block;margin-bottom:2px}
input,select{background:var(--chip);border:1px solid var(--line);border-radius:8px;color:var(--ink);font-size:16px;padding:8px}
input[type=number]{width:74px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-bottom:8px}
.grow{flex:1;min-width:150px}
.mv{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:3px 10px;margin:2px;font-size:13px;cursor:pointer;user-select:none}
.mv.on{background:var(--acc);color:#06130D;border-color:var(--acc)}
.ourrow{display:grid;grid-template-columns:1fr 80px 100px;gap:6px;align-items:center;margin-bottom:6px}
.ourrow .nm{font-weight:700}
.go{position:fixed;left:0;right:0;bottom:0;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:var(--bg);border-top:1px solid var(--line)}
.go button{width:100%;max-width:560px;display:block;margin:0 auto;background:var(--acc);color:#06130D;font-size:18px;font-weight:800;border:none;border-radius:12px;padding:14px}
#out{border-left:4px solid var(--acc)}
#out .act{font-size:20px;font-weight:800;margin:4px 0}
#out .note{font-size:12px;color:var(--sub)}
#out.err{border-left-color:var(--dan)}
.spin{opacity:.6}
</style></head><body><div class="wrap">
<h1>🗼 v4 アドバイザー <span style="font-size:12px;color:var(--sub)">条項＋2手読み＝ボットの頭脳</span></h1>

<div class="sec" id="out" style="display:none"></div>

<div class="sec"><h2>敵（場の1〜2体）</h2>
 <div id="foes"></div>
 <div class="row"><div><label>敵の控え残り</label><select id="bench"><option>2</option><option>1</option><option>0</option></select></div>
 <div><label>ターン</label><input type="number" id="turn" value="1" min="1"></div></div>
</div>

<div class="sec"><h2>こちら（場の2体に✓・現在HPと状態）</h2><div id="ours"></div></div>

<div class="go"><button onclick="advise()">推奨手を出す</button></div>
</div>
<datalist id="dex"></datalist>
<script>
const JPS=__JPS__, MOVES=__MOVES__;
const MAXHP=[322,364,302,404]; // サンダー/メタグロス/ラティオス/ラグラージ の最大HP(v4凍結値・実機と一致) — CI自動デプロイ稼働
const JP2EN={}; Object.entries(JPS).forEach(([e,j])=>JP2EN[j]=e);
const dex=document.getElementById('dex');
Object.keys(MOVES).map(sp=>JPS[sp]||sp).sort((a,b)=>a.localeCompare(b,'ja')).forEach(name=>{let o=document.createElement('option');o.value=name;dex.appendChild(o);});
function norm(v){v=v.trim();if(!v)return null;if(MOVES[v])return v;if(JP2EN[v]&&MOVES[JP2EN[v]])return JP2EN[v];
 const lv=v.toLowerCase();for(const sp in MOVES){if(sp.toLowerCase()===lv)return sp;}return null;}
const ST=["","まひ","やけど","ねむり","こおり","どく"];
function stSel(id){return `<select id="${id}">`+ST.map(s=>`<option>${s||"状態なし"}</option>`).join("")+`</select>`;}
function foeBlock(i){return `<div class="row"><div class="grow"><label>敵${i===0?"A":"B（いなければ空）"}</label>
 <input list="dex" id="fsp${i}" style="width:100%" oninput="mvRender(${i})" autocomplete="off"></div>
 <div><label>HP%</label><input type="number" id="fhp${i}" value="100" min="0" max="100"></div>
 <div><label>状態</label>${stSel("fst"+i)}</div></div>
 <div id="fmv${i}" style="margin-bottom:6px"></div>`;}
document.getElementById('foes').innerHTML=foeBlock(0)+foeBlock(1);
function mvRender(i){const sp=norm(document.getElementById('fsp'+i).value);const el=document.getElementById('fmv'+i);
 if(!sp){el.innerHTML="";return;}
 el.innerHTML='<label>見えた技をタップ（型の絞り込み・任意）</label>'+MOVES[sp].map((m,j)=>`<span class="mv" data-i="${j+1}" onclick="this.classList.toggle('on')">${m}</span>`).join("");}
document.getElementById('ours').innerHTML=[0,1,2,3].map(i=>`<div class="ourrow">
 <span class="nm"><input type="checkbox" id="oact${i}" ${i<2?"checked":""}> ${["サンダー","メタグロス","ラティオス","ラグラージ"][i]}</span>
 <input type="number" id="ohp${i}" value="${MAXHP[i]}" min="0" max="${MAXHP[i]}">${stSel("ost"+i)}</div>`).join("");
async function advise(){
 const out=document.getElementById('out'); out.style.display="block"; out.classList.remove("err");
 out.innerHTML='<div class="act spin">計算中…（数秒）</div>';
 const foes=[];
 for(const i of [0,1]){const sp=norm(document.getElementById('fsp'+i).value);
  if(!sp){if(i===0){out.classList.add("err");out.innerHTML='<div class="act">敵Aを入力してください</div>';return;}continue;}
  const obs=[...document.querySelectorAll('#fmv'+i+' .mv.on')].map(x=>+x.dataset.i);
  foes.push({sp,hp:+document.getElementById('fhp'+i).value,st:document.getElementById('fst'+i).value.replace("状態なし",""),obs});}
 const actives=[0,1,2,3].filter(i=>document.getElementById('oact'+i).checked);
 if(actives.length!==2){out.classList.add("err");out.innerHTML='<div class="act">こちらの「場の2体」に✓を2つ</div>';return;}
 const body={turn:+document.getElementById('turn').value,bench:+document.getElementById('bench').value,foes,
  actives,hp:[0,1,2,3].map(i=>+document.getElementById('ohp'+i).value),
  st:[0,1,2,3].map(i=>document.getElementById('ost'+i).value.replace("状態なし",""))};
 try{
  const sep=location.search?'&':'?';
  const r=await fetch('advise'+location.search+sep+'d='+encodeURIComponent(JSON.stringify(body)),{method:'GET'});
  const d=await r.json();
  if(d.error){out.classList.add("err");out.innerHTML='<div class="act">'+d.error+'</div>';return;}
  out.innerHTML='<h2 style="font-size:13px;color:var(--sub);margin:0">★ 推奨手</h2>'+d.acts.map(a=>'<div class="act">'+a+'</div>').join("")+
   '<div class="note">前提: 敵は候補セットの最速型で仮置き／ダメージ判定は全546セットの最悪ケース（ボットと同一基準）</div>';
  window.scrollTo({top:0,behavior:'smooth'});
 }catch(e){out.classList.add("err");out.innerHTML='<div class="act">通信エラー: '+e+'</div>';}
}
</script></body></html>"""

def run_advise(q):
    team=G['our_team']()
    order=q["actives"]+[i for i in range(4) if i not in q["actives"]]
    mons=[team[i] for i in order]
    for k,i in enumerate(order):
        m=mons[k]
        m.hp=max(0,min(m.max_hp,int(q["hp"][i])))  # 実数HP(実機の現在HP)をそのまま。範囲外はクランプ
        m.status=STATUS.get(q["st"][i] or "",None)
    foes=[]
    for f in q["foes"]:
        if f["sp"] not in advisor.bySp: return {"error":"不明な敵種族: %s"%f["sp"]}
        foes.append(advisor.make_foe(f["sp"],max(0,min(100,f["hp"])),STATUS.get(f.get("st","") or "",None),f.get("obs",[])))
    b=advisor.build_battle(max(1,q["turn"]),mons,(foes+[None,None])[:2],max(0,min(2,q["bench"])))
    advisor._battle_no[0]=1
    acts=v3_choose(b)
    lines=[advisor.fmt_act(m,acts.get(m)) for m in b.active["us"] if m and m.hp>0]
    return {"acts":lines}

TOKEN=os.environ.get("ADVISOR_TOKEN","")  # 公開デプロイ時の簡易認証: 設定時は ?t=<TOKEN> 必須

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _auth_ok(self):
        if not TOKEN: return True
        from urllib.parse import urlparse, parse_qs
        q=parse_qs(urlparse(self.path).query)
        return q.get("t",[""])[0]==TOKEN
    def _send(self,code,body,ctype="application/json; charset=utf-8"):
        data=body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if not self._auth_ok(): self._send(403,'forbidden (?t=token)','text/plain'); return
        from urllib.parse import urlparse, parse_qs
        p=urlparse(self.path)
        if p.path.rstrip("/").endswith("advise"):   # GET /advise?d=<json>（CloudFront OAC経路）
            try:
                d=parse_qs(p.query).get("d",["{}"])[0]
                with LOCK: res=run_advise(json.loads(d or "{}"))
            except Exception as e:
                res={"error":"内部エラー: %s"%e}
            self._send(200,json.dumps(res,ensure_ascii=False)); return
        page=PAGE.replace("__JPS__",json.dumps(JPS,ensure_ascii=False)).replace("__MOVES__",json.dumps(MOVELISTS,ensure_ascii=False))
        self._send(200,page,"text/html; charset=utf-8")
    def do_POST(self):
        if not self._auth_ok(): self._send(403,'{"error":"forbidden"}'); return
        if not self.path.split("?")[0].rstrip("/").endswith("advise"): self._send(404,'{"error":"not found"}'); return
        try:
            q=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
            with LOCK: res=run_advise(q)
        except Exception as e:
            res={"error":"内部エラー: %s"%e}
        self._send(200,json.dumps(res,ensure_ascii=False))

if __name__=="__main__":
    port=int(os.environ.get("PORT","8787"))  # Cloud Run等は$PORTを注入
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(("8.8.8.8",80)); ip=s.getsockname()[0]; s.close()
    except Exception: ip="このPCのIP"
    print("="*50)
    print(" v4 ブラウザ・アドバイザー 起動")
    print("  PCで:    http://localhost:%d"%port)
    print("  スマホで: http://%s:%d (同じWi-Fi)"%(ip,port))
    print("="*50)
    ThreadingHTTPServer(("0.0.0.0",port),H).serve_forever()
