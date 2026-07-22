## AWS Lambda ハンドラ (関数URL用)
## デプロイ: 13-deploy-advisor.md 参照。GET=UI / POST /advise=推奨手API。
## エンジンはモジュールロード時に読み込み(コールドスタート30-60秒・ウォーム中は使い回し)。
import json, os
import advisor_web  # import時にadvisorエンジンをロード(Lambdaのウォームコンテナで再利用される)
from jpnames import JPS

TOKEN=os.environ.get("ADVISOR_TOKEN","")  # 簡易認証(任意): 設定時は ?t=<TOKEN> が必要

def _page():
    return (advisor_web.PAGE
            .replace("__JPS__", json.dumps(JPS, ensure_ascii=False))
            .replace("__MOVES__", json.dumps(advisor_web.MOVELISTS, ensure_ascii=False)))

def handler(event, context):
    http=(event.get("requestContext") or {}).get("http") or {}
    method=http.get("method","GET"); path=event.get("rawPath","/")
    qs=event.get("queryStringParameters") or {}
    if TOKEN and qs.get("t")!=TOKEN:
        return {"statusCode":403,"body":"forbidden (?t=token)"}
    if method=="GET":
        return {"statusCode":200,
                "headers":{"Content-Type":"text/html; charset=utf-8"},
                "body":_page()}
    if method=="POST" and path.rstrip("/").endswith("advise"):
        try:
            q=json.loads(event.get("body") or "{}")
            res=advisor_web.run_advise(q)
        except Exception as e:
            res={"error":"内部エラー: %s"%e}
        return {"statusCode":200,
                "headers":{"Content-Type":"application/json; charset=utf-8"},
                "body":json.dumps(res,ensure_ascii=False)}
    return {"statusCode":404,"body":"not found"}
