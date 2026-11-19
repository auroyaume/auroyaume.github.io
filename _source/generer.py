"""Génère les pages du site dans les 6 langues à partir des modèles et de textes.csv.

Usage (depuis la racine du dépôt) :  python _source/generer.py
Voir _source/LISEZMOI.md.
"""
import csv
import hashlib
import html
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "_source")
SITE = "https://auroyaume.github.io"

# Langues du site = langues du jeu. dossier "" = racine (anglais depuis le 19/11 ; le français est dans /fr/).
LANGUES = [
    # code CSV, attribut lang, dossier, nom affiché, og:locale, code du formulaire de bug
    ("en",    "en",    "",       "English",            "en_US", "en"),
    ("fr",    "fr",    "fr",     "Français",           "fr_FR", "fr"),
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

# Redirection vers la langue du navigateur, seulement sur les pages de la racine (anglais)
# et seulement si le visiteur n'a pas déjà choisi une langue. Les robots ne sont pas redirigés.
REDIRECT = """<script>
(function(){try{
  if(/bot|crawl|spider|slurp|lighthouse/i.test(navigator.userAgent))return;
  var m={en:'',fr:'/fr',es:'/es',pt:'/pt-br',de:'/de',it:'/it'};
  var s=localStorage.getItem('ar_lang');
  var l=s||((navigator.languages&&navigator.languages[0])||navigator.language||'en').toLowerCase().slice(0,2);
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


# Réseaux sociaux du studio (mêmes comptes pour tous les jeux)
RESEAUX = [
    ("TikTok", "https://www.tiktok.com/@auroyaume_studio",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.6 3c.3 2.4 1.7 3.9 4 4.1v3a7 7 0 0 1-4-1.3v6.1a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v3.1a2.6 2.6 0 1 0 1.7 2.4V3h3Z" fill="#25F4EE" transform="translate(-.8 -.6)"/><path d="M16.6 3c.3 2.4 1.7 3.9 4 4.1v3a7 7 0 0 1-4-1.3v6.1a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v3.1a2.6 2.6 0 1 0 1.7 2.4V3h3Z" fill="#FE2C55" transform="translate(.8 .6)"/><path d="M16.6 3c.3 2.4 1.7 3.9 4 4.1v3a7 7 0 0 1-4-1.3v6.1a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v3.1a2.6 2.6 0 1 0 1.7 2.4V3h3Z" fill="#fff"/></svg>'),
    ("Instagram", "https://www.instagram.com/auroyaume_studio/",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="1.5" y="1.5" width="21" height="21" rx="6" fill="url(#ar-ig)"/><rect x="5.5" y="5.5" width="13" height="13" rx="4" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="12" cy="12" r="3.1" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="16" cy="8" r=".95" fill="#fff"/></svg>'),
    ("YouTube", "https://www.youtube.com/@auroyaume_studio",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22.5 7.2a2.8 2.8 0 0 0-2-2C18.7 4.7 12 4.7 12 4.7s-6.7 0-8.5.5a2.8 2.8 0 0 0-2 2A29 29 0 0 0 1 12a29 29 0 0 0 .5 4.8 2.8 2.8 0 0 0 2 2c1.8.5 8.5.5 8.5.5s6.7 0 8.5-.5a2.8 2.8 0 0 0 2-2A29 29 0 0 0 23 12a29 29 0 0 0-.5-4.8Z" fill="#FF0000"/><path d="M9.8 15.3V8.7l5.7 3.3Z" fill="#fff"/></svg>'),
]
# Dégradé d'Instagram, défini une seule fois en haut de chaque page (référencé par url(#ar-ig))
SVG_DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            '<radialGradient id="ar-ig" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#fdf497"/>'
            '<stop offset=".05" stop-color="#fdf497"/><stop offset=".45" stop-color="#fd5949"/>'
            '<stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285AEB"/></radialGradient>'
            '</defs></svg>')
PSEUDO = "@auroyaume_studio"


def reseaux_icones(classe, sur, aria, indent="      "):
    liens = "".join(
        f'<a href="{u}" target="_blank" rel="noopener me" aria-label="{sur % n}" title="{n}">{svg}</a>'
        for n, u, svg in RESEAUX)
    return f'{indent}<div class="{classe}" role="list" aria-label="{aria}">{liens}</div>'


def reseaux_cartes(sur):
    out = []
    for n, u, svg in RESEAUX:
        out.append(f'        <a class="social-card card" href="{u}" target="_blank" rel="noopener me" aria-label="{sur % n}">'
                   f'{svg}<b>{n}</b><span>{PSEUDO}</span></a>')
    return "\n".join(out)


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
    css_v = hashlib.md5(open(os.path.join(RACINE, "assets", "site.css"), "rb").read()).hexdigest()[:8]
    manquants = []
    for modele, chemin in PAGES:
        gabarit = open(os.path.join(SRC, modele), encoding="utf-8").read()
        for code, lang, dossier, nom, locale, bug in LANGUES:
            v = {k: (row.get(code) or "").strip() for k, row in textes.items()}
            for k, row in textes.items():
                if not v[k]:
                    manquants.append(f"{k} [{code}]")
                    v[k] = (row.get("en") or row.get("fr") or "").strip()  # repli sur l'anglais
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
                "redirect": REDIRECT if not dossier else "",
                "lang_menu": menu_langues(code, chemin, textes["lang_label"][code] or "Langue"),
                "lang_script": LANG_SCRIPT,
                "svg_defs": SVG_DEFS,
                "css_v": css_v,
                "social_head": reseaux_icones("social social-head", v["social_on"], v["social_aria"]),
                "social_foot": reseaux_icones("social", v["social_on"], v["social_aria"], indent="    "),
                "social_cards": reseaux_cartes(v["social_on"]),
                "social_head_plain": reseaux_icones("social social-big", v["social_on"], v["social_aria"], indent="        "),
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
    # Anciennes adresses anglaises (/en/...) : renvoient vers la racine, qui est en anglais depuis le 19/11.
    for _, chemin in PAGES:
        dest = os.path.join(RACINE, "en", *chemin.strip("/").split("/"), "index.html") if chemin != "/" else os.path.join(RACINE, "en", "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
                    f'<title>Au Royaume</title>\n<link rel="canonical" href="{SITE}{chemin}">\n'
                    f'<meta name="robots" content="noindex">\n<meta http-equiv="refresh" content="0; url={chemin}">\n'
                    f'<script>location.replace("{chemin}"+location.search+location.hash)</script>\n'
                    f'</head><body><a href="{chemin}">Au Royaume</a></body></html>\n')
        print("redirection", os.path.relpath(dest, RACINE))
    if manquants:
        print("\nTextes manquants (remplacés par l anglais) :")
        for m in sorted(set(manquants)):
            print("  -", m)


if __name__ == "__main__":
    main()
