#!/usr/bin/env python3
"""Dump a Smogon (XenForo) forum thread to JSONL + Markdown for offline review.

Two modes:
  1) fetch:  python3 smogon_thread_dump.py fetch 3648697 --out ./thread-3648697
     Downloads every page of the thread (public, no login) with a browser User-Agent and a polite delay.
  2) parse:  python3 smogon_thread_dump.py parse ./saved_pages/*.html --out ./thread-3648697
     Parses pages you saved from the browser (Ctrl+S "Webpage, Complete" or SingleFile) if fetching is blocked.

Output: <out>.jsonl (one post per line: page, post_id, author, datetime, permalink, text, quotes)
        <out>.md    (human-readable, one section per page)
Requires: pip install requests beautifulsoup4
"""
import sys, re, json, time, argparse, pathlib
from bs4 import BeautifulSoup

BASE = "https://www.smogon.com/forums/threads/{tid}/page-{page}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def parse_html(html, page_hint=None):
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    # page number
    page = page_hint
    cur = soup.select_one(".pageNav-page--current a") or soup.select_one(".pageNav-page--current")
    if cur and cur.get_text(strip=True).isdigit():
        page = int(cur.get_text(strip=True))
    last = 1
    for a in soup.select(".pageNav-page a"):
        t = a.get_text(strip=True)
        if t.isdigit(): last = max(last, int(t))
    for art in soup.select("article.message"):
        pid = art.get("id", "") or art.get("data-content", "")
        author = art.get("data-author", "")
        t = art.select_one("time")
        dt = t.get("datetime", "") if t else ""
        link = art.select_one("a.u-concealed[href*='/post-'], .message-attribution-main a[href*='post-']")
        permalink = link.get("href", "") if link else ""
        body = art.select_one(".bbWrapper")
        quotes = []
        if body:
            for q in body.select("blockquote"):
                quotes.append(q.get_text("\n", strip=True)[:2000])
                q.decompose()
            text = body.get_text("\n", strip=True)
        else:
            text = ""
        posts.append(dict(page=page, post_id=pid, author=author, datetime=dt, permalink=permalink, text=text, quotes=quotes))
    return posts, page or 1, last

def write_out(all_posts, out):
    out = pathlib.Path(out)
    with open(str(out) + ".jsonl", "w", encoding="utf-8") as f:
        for p in all_posts: f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(str(out) + ".md", "w", encoding="utf-8") as f:
        cur = None
        for p in all_posts:
            if p["page"] != cur:
                cur = p["page"]; f.write(f"\n\n# Page {cur}\n")
            f.write(f"\n## {p['author']} — {p['datetime']}  ({p['post_id']})\n{p['permalink']}\n\n{p['text']}\n")
            for q in p["quotes"]: f.write("\n> " + q.replace("\n", "\n> ") + "\n")
    print(f"wrote {len(all_posts)} posts -> {out}.jsonl / {out}.md")

def cmd_fetch(a):
    import requests
    s = requests.Session(); s.headers["User-Agent"] = UA
    all_posts = []; page = 1; last = 1
    while page <= last:
        r = s.get(BASE.format(tid=a.thread, page=page), timeout=30)
        if r.status_code != 200:
            print(f"page {page}: HTTP {r.status_code} — stopping (Cloudflare? try 'parse' mode with saved HTML)"); break
        posts, pg, last_seen = parse_html(r.text, page)
        last = max(last, last_seen)
        all_posts += posts
        print(f"page {page}/{last}: {len(posts)} posts")
        page += 1; time.sleep(a.delay)
    write_out(all_posts, a.out)

def cmd_parse(a):
    all_posts = []
    for fn in a.files:
        html = open(fn, encoding="utf-8", errors="ignore").read()
        m = re.search(r"page-(\d+)", fn)
        posts, pg, _ = parse_html(html, int(m.group(1)) if m else None)
        all_posts += posts
        print(f"{fn}: page {pg}, {len(posts)} posts")
    all_posts.sort(key=lambda p: (p["page"] or 0, p["post_id"]))
    write_out(all_posts, a.out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("thread"); f.add_argument("--out", default="thread"); f.add_argument("--delay", type=float, default=2.0)
    p = sub.add_parser("parse"); p.add_argument("files", nargs="+"); p.add_argument("--out", default="thread")
    a = ap.parse_args()
    cmd_fetch(a) if a.cmd == "fetch" else cmd_parse(a)
