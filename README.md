# Puce8 Studio

Studio de musique 8-bit (chiptune), installable sur PC, Android et iPhone :

- **Studio** : séquenceur 4 canaux façon NES (deux ondes carrées, triangle, bruit), accords arpégés, export WAV.
- **Sonothèque** : effets sonores rétro et modernes, générateur aléatoire, instruments à charger dans le Studio.
- **Convertisseur** : transforme un MP3/WAV en son de console (Lo-fi) ou en mélodie chip (détection des notes).

## Organisation

| Chemin | Rôle |
|---|---|
| `puce8-studio.html` | **La source de l'app.** C'est le seul fichier à modifier. |
| `tools/build_pwa.py` | Génère la version installable dans `docs/` |
| `docs/` | Ce que GitHub Pages publie (page, manifeste, service worker, icônes). Ne pas modifier à la main. |

## Modifier et republier

```
python tools/build_pwa.py
git add -A
git commit -m "Mise à jour"
git push
```

GitHub Pages republie en une minute environ. Les appareils où l'app est installée récupèrent la nouvelle version à leur prochaine ouverture avec du réseau.

## Tester sur votre PC

```
python -m http.server 8766 --directory docs
```

Puis ouvrez http://localhost:8766.

## Installer

| Appareil | Comment |
|---|---|
| **PC / Mac** (Chrome, Edge) | Bouton **Installer l'app**, ou l'icône d'installation dans la barre d'adresse |
| **Android** (Chrome) | Bouton **Installer l'app**, ou menu ⋮ → *Installer l'application* |
| **iPhone / iPad** (Safari) | Partager → *Sur l'écran d'accueil* (le bouton de l'app affiche ces instructions) |

Après la première ouverture, l'app marche **hors ligne**.

## Bon à savoir

- **iPhone et bouton silencieux** : l'app demande à iOS de jouer le son même en mode silencieux (iOS 16.4 et plus). Sur un iOS plus ancien, désactivez le mode silencieux.
- **Vos morceaux** sont gardés dans le navigateur de chaque appareil. Pour passer d'un appareil à l'autre, utilisez **Sauver** puis **Ouvrir** (fichier `.json`).
- **Exports sur iPhone** : un fichier exporté s'ouvre dans un aperçu ; touchez Partager → *Enregistrer dans Fichiers*.
