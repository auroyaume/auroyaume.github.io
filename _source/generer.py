"""Génère les pages du site dans les 6 langues à partir des modèles et de textes.csv.

Usage (depuis la racine du dépôt) :  python _source/generer.py
Voir _source/LISEZMOI.md.
"""
import csv
import html
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "_source")
SITE = "https://auroyaume.github.io"

# Langues du site = langues du jeu. dossier "" = racine (français).
LANGUES = [
    # code CSV, attribut lang, dossier, nom affiché, og:locale, code du formulaire de bug
    ("fr",    "fr",    "",       "Français",           "fr_FR", "fr"),
    ("en",    "en",    "en",     "English",            "en_US", "en"),
    ("es",    "es",    "es",     "Español",            "es_ES", "es"),
    ("pt-BR", "pt-BR", "pt-br",  "Português (Brasil)", "pt_BR", "pt_BR"),
    ("de",    "de",    "de",     "Deutsch",            "de_DE", "de"),
    ("it",    "it",    "it",     "Italiano",           "it_IT", "it"),
]

PAGES = [
    # modèle, chemin de la page (après le dossier de langue)
    ("modele_accueil.html", "/"),
    ("modele_holehop.html", "/holehop/"),
]

GLOBE = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" '
         'stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9'
         'c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3Z"/></svg>')

# Redirection vers la langue du navigateur, seulement sur les pages françaises (racine)
# et seulement si le visiteur n'a pas déjà choisi une langue. Les robots ne sont pas redirigés.
REDIRECT = """<script>
(function(){try{
  if(/bot|crawl|spider|slurp|lighthouse/i.test(navigator.userAgent))return;
  var m={fr:'',en:'/en',es:'/es',pt:'/pt-br',de:'/de',it:'/it'};
  var s=localStorage.getItem('ar_lang');
  var l=s||((navigator.languages&&navigator.languages[0])||navigator.language||'fr').toLowerCase().slice(0,2);
  if(!(l in m))l='en';
  if(m[l])location.replace(m[l]+location.pathname+location.search+location.hash);
}catch(e){}})();
</script>
"""

# Mémorise le choix fait dans le menu des langues, et ferme le menu quand on clique ailleurs.
LANG_SCRIPT = """<script>
document.querySelectorAll('[data-lang]').forEach(function(a){a.addEventListener('click',function(){
  try{localStorage.setItem('ar_lang',a.dataset.lang)}catch(e){}
});});
document.addEventListener('click',function(e){var d=document.querySelector('.lang-menu');
  if(d&&d.open&&!d.contains(e.target))d.open=false;});
</script>"""


def lire_textes():
    with open(os.path.join(SRC, "textes.csv"), encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))
    textes = {}
    for ligne in lignes:
        cle = ligne["cle"].strip()
        if not cle or cle.startswith("#"):
            continue
        textes[cle] = ligne
    return textes


def url(dossier, chemin):
    return (f"/{dossier}" if dossier else "") + chemin


def bloc_hreflang(chemin):
    out = []
    for code, lang, dossier, *_ in LANGUES:
        out.append(f'<link rel="alternate" hreflang="{lang}" href="{SITE}{url(dossier, chemin)}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{chemin}">')
    return "\n".join(out) + "\n"


def menu_langues(courante, chemin, label):
    items = []
    for code, lang, dossier, nom, *_ in LANGUES:
        cur = ' aria-current="true"' if code == courante else ""
        items.append(f'          <li><a href="{url(dossier, chemin)}" hreflang="{lang}" lang="{lang}" '
                     f'data-lang="{lang[:2].lower()}"{cur}>{nom}</a></li>')
    court = courante[:2].upper()
    return (f'      <details class="lang-menu">\n'
            f'        <summary aria-label="{html.escape(label)}">{GLOBE}<span>{court}</span></summary>\n'
            f'        <ul>\n' + "\n".join(items) + "\n        </ul>\n      </details>")


def main():
    textes = lire_textes()
    manquants = []
    for modele, chemin in PAGES:
        gabarit = open(os.path.join(SRC, modele), encoding="utf-8").read()
        for code, lang, dossier, nom, locale, bug in LANGUES:
            v = {k: (row.get(code) or "").strip() for k, row in textes.items()}
            for k, row in textes.items():
                if not v[k]:
                    manquants.append(f"{k} [{code}]")
                    v[k] = (row.get("fr") or "").strip()  # repli sur le français
            v = {k: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;") for k, t in v.items()}
            fr = code == "fr"
            v.update({
                "lang": lang,
                "p": f"/{dossier}" if dossier else "",
                "canonical": SITE + url(dossier, chemin),
                "hreflang": bloc_hreflang(chemin),
                "og_locale": locale,
                "og_image": "/assets/og-holehop.jpg" if fr else "/assets/og-holehop-en.jpg",
                "banner": "/holehop/img/banniere.webp" if fr else "/holehop/img/banniere-en.webp",
                "video": f"/holehop/video/bande-annonce-{lang.lower()}.mp4",
                "poster": f"/holehop/img/poster-{lang.lower()}.webp",
                "conf_href": "/confidentialite/" if fr else "/confidentialite/#en",
                "bug_lang": bug,
                "redirect": REDIRECT if fr else "",
                "lang_menu": menu_langues(code, chemin, textes["lang_label"][code] or "Langue"),
                "lang_script": LANG_SCRIPT,
            })

            def remplace(m):
                k = m.group(1)
                if k not in v:
                    sys.exit(f"Clé inconnue dans {modele} : {k}")
                return v[k]

            page = re.sub(r"\{\{(\w+)\}\}", remplace, gabarit)
            dest = os.path.join(RACINE, *(([dossier] if dossier else []) + chemin.strip("/").split("/")), "index.html") \
                if chemin != "/" else os.path.join(RACINE, dossier, "index.html") if dossier else os.path.join(RACINE, "index.html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                f.write(page)
            print("écrit", os.path.relpath(dest, RACINE))
    if manquants:
        print("\nTextes manquants (remplacés par le français) :")
        for m in sorted(set(manquants)):
            print("  -", m)


if __name__ == "__main__":
    main()
