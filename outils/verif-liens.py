#!/usr/bin/env python3
"""MAP : contrôle des liens des fiches (sites, documents, sources).

Lit les liens écrits dans index.html et dans le tableur « Fiches », les teste,
et écrit un rapport en Markdown (rapport-liens.md). Bibliothèque standard seulement.

Usage : python3 outils/verif-liens.py [index.html] [--sans-tableur]
Code de sortie : 0 dans tous les cas (le rapport dit ce qui ne va pas).
"""
import csv, io, re, ssl, sys, socket, datetime, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

SHEET_CSV = ("https://docs.google.com/spreadsheets/d/1OvMK2Vcqw4762-3AzemTimyZ8yymhf6DgB7W-GE2o_E"
             "/gviz/tq?tqx=out:csv&sheet=Fiches")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36 MAP-verif-liens")
# Liens techniques de l'appli, pas des fiches
IGNORE = re.compile(r"(fonts\.(googleapis|gstatic)\.com|tile\.openstreetmap|openstreetmap\.org/copyright|"
                    r"google\.[a-z.]+/maps|maps\.google|cdnjs\.|cdn\.jsdelivr|unpkg\.com|supabase\.co|"
                    r"docs\.google\.com/spreadsheets|w3\.org|leafletjs|github\.com/mapannuaire|wa\.me|"
                    r"mapannuaire\.github\.io|example\.)", re.I)
URL_RE = re.compile(r"https?://[^\s\"'`<>\\)\]]+")


def clean(u):
    return u.rstrip(".,;:»")


def from_html(path):
    s = open(path, encoding="utf-8").read()
    ids = [(m.start(), m.group(1)) for m in re.finditer(r'(?:\bid|"id")\s*:\s*"([^"]+)"', s)]
    names = [(m.start(), m.group(1)) for m in re.finditer(r'(?:[{,\s]n|"n")\s*:\s*"([^"]+)"', s)]
    if not ids:
        return {}
    known = {i for _, i in ids}
    name_of = {i: next((n for q, n in names if q > p), i) for p, i in ids}
    # autres tables rangées par identifiant de fiche : "id": { ... } ou "id": [ ... ]
    keyed = [(m.start(), m.group(1)) for m in re.finditer(r'"([A-Za-z0-9-]+)"\s*:\s*[\{\[]', s) if m.group(1) in known]
    ids = sorted(ids + keyed)
    start, end = ids[0][0], ids[-1][0] + 20000
    found = {}
    for m in URL_RE.finditer(s, start, end):
        u = clean(m.group(0))
        if IGNORE.search(u):
            continue
        pos = m.start()
        fid = None
        for p, i in ids:
            if p > pos:
                break
            fid = (p, i)
        if not fid:
            continue
        found.setdefault(u, set()).add((fid[1], name_of.get(fid[1], fid[1])))
    return found


def from_sheet():
    try:
        req = urllib.request.Request(SHEET_CSV, headers={"User-Agent": UA})
        txt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    except Exception as e:
        print("Tableur illisible :", e, file=sys.stderr)
        return {}
    rows = list(csv.reader(io.StringIO(txt)))
    if not rows:
        return {}
    h = [c.strip().lower() for c in rows[0]]
    col = lambda n: h.index(n) if n in h else -1
    ci, cn = col("identifiant"), col("nom")
    found = {}
    for r in rows[1:]:
        fid = r[ci] if 0 <= ci < len(r) else ""
        nm = r[cn] if 0 <= cn < len(r) else fid
        for c in ("site", "documents"):
            k = col(c)
            if 0 <= k < len(r):
                for u in URL_RE.findall(r[k]):
                    u = clean(u)
                    if not IGNORE.search(u):
                        found.setdefault(u, set()).add((fid or "?", nm))
    return found


def check(u):
    """ok, casse (introuvable), ou incertain (le site refuse les robots, délai dépassé…)."""
    ctx = ssl.create_default_context()
    last = ""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(u, method=method, headers={"User-Agent": UA, "Accept": "*/*",
                                                                     "Accept-Language": "fr-FR,fr;q=0.9"})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                return "ok", str(r.status)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (404, 410):
                if method == "GET":
                    return "casse", last
                continue
            if method == "HEAD":
                continue
            return "incertain", last
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.gaierror):
                return "casse", "domaine introuvable"
            if isinstance(reason, ssl.SSLError):
                return "incertain", "certificat"
            last = str(reason)[:60]
        except (socket.timeout, TimeoutError):
            last = "délai dépassé"
        except Exception as e:
            last = type(e).__name__
    return "incertain", last or "?"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else "index.html"
    links = from_html(path)
    if "--sans-tableur" not in sys.argv:
        for u, fs in from_sheet().items():
            links.setdefault(u, set()).update(fs)
    urls = sorted(links)
    with ThreadPoolExecutor(max_workers=16) as ex:
        res = dict(zip(urls, ex.map(check, urls)))
    broken = [(u, why) for u, (st, why) in res.items() if st == "casse"]
    unsure = [(u, why) for u, (st, why) in res.items() if st == "incertain"]
    today = datetime.date.today().strftime("%d/%m/%Y")
    out = [f"Contrôle du {today} : **{len(urls)} liens** testés, **{len(broken)} cassés**, "
           f"{len(unsure)} à revoir (le site refuse les robots ou répond mal), "
           f"{len(urls) - len(broken) - len(unsure)} qui marchent.", ""]
    fiche = lambda u: " ; ".join(sorted(f"{n} (`{i}`)" for i, n in links[u]))
    if broken:
        out += ["## Liens cassés", "", "Page introuvable (404) ou domaine disparu : à corriger dans le tableur ou dans l'appli.", "",
                "| Fiche | Lien | Problème |", "| --- | --- | --- |"]
        out += [f"| {fiche(u)} | {u} | {why} |" for u, why in sorted(broken, key=lambda x: fiche(x[0]))]
        out.append("")
    if unsure:
        out += ["<details><summary>À revoir à la main (" + str(len(unsure)) + ")</summary>", "",
                "| Fiche | Lien | Réponse |", "| --- | --- | --- |"]
        rows = [f"| {fiche(u)} | {u} | {why} |" for u, why in sorted(unsure, key=lambda x: fiche(x[0]))]
        out += rows[:150] + ([f"| … | {len(rows) - 150} autres | |"] if len(rows) > 150 else [])
        out += ["", "</details>", ""]
    out.append("_Rapport créé par la tâche « MAP - contrôle des liens » (outils/verif-liens.py)._")
    open("rapport-liens.md", "w", encoding="utf-8").write("\n".join(out))
    open("nb-casses.txt", "w").write(str(len(broken)))
    print(out[0])


if __name__ == "__main__":
    main()
          
