# Interface Utilisateur - Blokus

Spécification de l'interface web pour jouer à Blokus.

---

## Vue d'ensemble

### Layout Global

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HEADER (Logo + Indicateur de Tour)                                      │
├───────────┬────────────────────────────┬────────────────────────────────┤
│           │                            │  ┌──────────────────────────┐  │
│  SCORES   │                            │  │                          │  │
│  (colonne)│                            │  │   PIÈCES DISPONIBLES     │  │
│ Name J1   │                            │  │    (Grille 3x7)          │  │
│ Score J1  │     PLATEAU 20×20          │  │  [Toutes visibles]       │  │
│           │       (600×600)            │  └──────────────────────────┘  │
│ Name J2   │                            │                                │
│ Score J2  │                            │         (espace vide)          │
│   ...     │                            │                                │
│           │                            │  ┌──────────┐                  │
│           │                            │  │SÉLECTION │ (preview net)    │
│           │                            │  │          │                  │
├───────────┴────────────────────────────┴──┴──────────┴──────────────────┤
│ CONTRÔLES : 🔄 Rotation (R)  |  🔃 Symétrie (S)  |  ⏭️ Passer (Esp)     │
└─────────────────────────────────────────────────────────────────────────┘

[MENU MODAL OVERLAY - Au démarrage]
- Choix nb joueurs (2, 3, 4)
- Config Joueur (Nom, Couleur, Type [Humain/IA], Persona IA)
- Start Player (Aléatoire / Fixe)

```

---

## Zones de l'Interface

### 1. Plateau de Jeu (Canvas)

- **Taille** : 600×600 pixels (30px par case)
- **Rendu** : HTML5 Canvas 2D avec `image-rendering: -webkit-optimize-contrast` pour la netteté.
- **Grille** : Fond crème, grille grise subtile.
- **Coins de départ** : Marqués avec cercles colorés.

### 2. Panneau des Pièces (Droite - Haut)

- **Largeur** : 650px (légèrement plus large que le plateau pour l'alignement).
- **Contenu** : 21 pièces affichées en grille 3x7.
- **Comportement** : Pas de scroll vertical, scroll horizontal automatique si besoin (mais tout est visible par défaut).
- **État** : Pièces utilisées grisées.

### 3. Panneau de Sélection (Droite - Bas)

- **Position** : Aligné en bas avec le plateau.
- **Focus** : Affiche la pièce actuellement sélectionnée en grand.
- **Rendu** : Canvas optimisé (cellules entières) pour éviter tout flou.

### 4. Barre de Scores (Gauche)

- **Format** : Colonne verticale latérale.
- **Affichage par Joueur** :

  ```
  [Avatar/Couleur]
  Nom du Joueur
  Score: -89
  ```

- **Structure** : Le nom et le score sont sur deux lignes distinctes pour permettre des noms longs.
- **Mise en avant** : Le joueur actif est mis en évidence visuellement (fond ou bordure brillante).
- **Indicateurs** : Couleurs personnalisables (défaut : Bleu, Vert, Jaune, Rouge).

### 5. Menu de Configuration (Modal)

- **Apparition** : Au chargement de la page (overlay bloquant).
- **Options Globales** :
  - **Nombre de Joueurs** : 2, 3 ou 4.
  - **Mode de Jeu** : "Standard" (20x20) ou "Duo" (14x14) - *Visible uniquement si 2 joueurs*.
  - **Premier Joueur** : "Aléatoire" ou choix spécifique (J1..J4).
- **Configuration Individuelle (par joueur)** :
  - **Nom** : Champ texte (ex: "Papa", "IA Tueur").
  - **Couleur** : Sélecteur de couleur.
  - **Type** : Toggle "Humain" ou "IA".
  - **Persona (si IA)** : Liste déroulante (ex: Agressive, Défensive, Aléatoire).
- **Action** : Bouton "Lancer la Partie" qui initialise le jeu.

---

## Interactions

### 1. Sélection et Placement (Click-to-Select)

1. **Sélection** : Clic sur une pièce dans le panneau de droite.
   - La pièce apparaît dans la zone "Sélection".
   - Un contour violet indique la sélection dans le panneau.
2. **Prévisualisation (Hover)** :
   - Déplacement de la souris sur le plateau.
   - La pièce suit le curseur (snapping sur la grille).
   - **Feedback Visuel** :
     - La pièce garde sa couleur de joueur (ex: bleu).
     - **Contour Vert** : Placement valide.
     - **Contour Rouge** : Placement invalide.
3. **Placement** : Clic gauche pour valider la position.
   - Si valide : la pièce est posée, le tour passe.
   - Si invalide : rien ne se passe.

### 2. Contrôles et Raccourcis

- **Rotation** : Bouton 🔄 ou touche `R` (90° horaire).
  - La prévisualisation se met à jour instantanément sous la souris (pas de disparition).
- **Symétrie** : Bouton 🔃 ou touche `S` (Miroir horizontal).
- **Passer** : Bouton ⏭️ ou touche `Espace` (Si aucun coup possible).
- **Annuler Sélection** : Touche `Escape`.

### 3. Fin de Partie (Modal)

- **Déclenchement** : Quand plus aucun joueur ne peut jouer.
- **Affichage** :
  - Classement final des joueurs.
  - Vainqueur mis en avant.
- **Actions** :
  - Bouton "Rejouer" (relance avec même config).
  - Bouton "Retour au Menu" (retour à l'écran d'accueil).

---

## Responsive

- **Desktop** : Layout 3 colonnes (Scores | Plateau | Pièces).
- **Tablet/Mobile** : Le layout s'adapte en colonne unique si l'écran est trop étroit.
