# Site Au Royaume : les 6 langues

Le site existe dans les 6 langues du jeu : français (à la racine), anglais `/en/`, espagnol `/es/`, portugais du Brésil `/pt-br/`, allemand `/de/` et italien `/it/`.

**Ne modifie pas à la main** `index.html`, `holehop/index.html` ni les dossiers de langue : ils sont **générés**. Pour changer le site, on passe par ce dossier `_source/`.

## Les fichiers

- `textes.csv` : tous les textes du site, avec une ligne par texte et une colonne par langue (`fr`, `en`, `es`, `pt-BR`, `de`, `it`). Il s'ouvre dans Excel ou LibreOffice ; enregistre-le en **CSV UTF-8**.
- `modele_accueil.html` et `modele_holehop.html` : la mise en page. Chaque `{{cle}}` y est remplacée par le texte de la langue.
- `generer.py` : il fabrique les 12 pages (2 pages × 6 langues).

## Changer un texte

1. Modifie la ligne dans `textes.csv`, dans les 6 colonnes.
2. Depuis la racine du dépôt, lance `python _source/generer.py`.
3. Commit et push.

Si une case est vide, la page prend le texte français et le script affiche la liste des textes manquants.

Les noms des mondes et des objets du jeu (La Prairie / The Meadow…, « Signaler un bug », « Réglages »…) sont repris de `minigolf/translations/hole_hop.csv` : garde-les identiques au jeu.

## Ajouter un texte ou une section

Ajoute une ligne dans `textes.csv` (nouvelle clé), mets `{{ta_cle}}` dans le modèle, puis relance le script.

## Sortie de Hole Hop (fait le 18/11)

*Fait le 18/11 : bouton Google Play actif (`com.auroyaume.holehop`), pastille « Disponible sur Google Play » (`pill_live`), descriptions sans « Bientôt ». Pour mémoire, la marche suivie :*

Dans `modele_holehop.html` :

1. Décommente le bouton `<a class="gp live" …>`.
2. Remplace `NOM.DU.PAQUET` par l'identifiant du jeu.
3. Supprime la pastille `{{pill_soon}}`.

Dans `modele_accueil.html`, remplace aussi la pastille de la carte Hole Hop. Ensuite, relance le script.

## Réseaux sociaux

Les liens TikTok, Instagram et YouTube (`@auroyaume_studio`) sont dans la liste `RESEAUX` en haut de `generer.py`. On les retrouve à 4 endroits :

- dans l'en-tête (sur ordinateur) ;
- dans la section « Suis l'aventure » de l'accueil ;
- dans la partie Aide de Hole Hop ;
- dans le pied de page.

Pour ajouter un réseau, ajoute une ligne (nom, lien, icône SVG) dans cette liste, puis relance le script. Les pages `confidentialite/` et `mentions-legales/` ne sont pas générées : leurs icônes de pied de page se modifient à la main.

## Ajouter un jeu (plus tard)

1. Crée `modele_<jeu>.html` sur le modèle de `modele_holehop.html`.
2. Ajoute ses textes dans `textes.csv`.
3. Ajoute la page dans la liste `PAGES` de `generer.py`.
4. Mets sa carte sur l'accueil.

## Ce qui n'est pas généré

`confidentialite/`, `mentions-legales/` (en français, avec un résumé en anglais `#en`), `holehop/bug/` (déjà en 6 langues, appelé par le jeu) et `holehop/version.json`.

## La langue des visiteurs

Les pages françaises envoient automatiquement le visiteur vers la langue de son navigateur (l'anglais pour toute autre langue). Si le visiteur choisit une langue dans le menu, ce choix est mémorisé et passe avant celle du navigateur. Les robots des moteurs de recherche ne sont pas redirigés.
