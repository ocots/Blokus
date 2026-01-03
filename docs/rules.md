# Règles du Jeu Blokus

## Vue d'ensemble

- **Joueurs** : 2 à 4 (optimal : 4)
- **Plateau** : Grille 20×20
- **Pièces** : 21 polyominoes par joueur (1 à 5 carrés)
- **Durée** : 20-30 minutes

---

## Les 21 Pièces

### Monomino (1 pièce = 1 carré)

```text
I1: ■
```

### Domino (1 pièce = 2 carrés)

```text
I2: ■ ■
```

### Triminoes (2 pièces = 3 carrés chacune)

```text
I3: ■ ■ ■          L3: ■ ■
                       ■
```

### Tetrominoes (5 pièces = 4 carrés chacune)

```text
I4: ■ ■ ■ ■        O4: ■ ■       T4:   ■
                       ■ ■           ■ ■ ■

L4: ■              S4: ■ ■
    ■                    ■ ■
    ■ ■
```

### Pentominoes (12 pièces = 5 carrés chacune)

```text
F:   ■ ■           I5: ■ ■ ■ ■ ■       L5: ■
   ■ ■                                     ■
     ■                                     ■
                                           ■ ■

N: ■               P: ■ ■              T5:   ■
   ■ ■                ■ ■                  ■ ■ ■
     ■ ■              ■                      ■

U: ■   ■           V: ■                W: ■
   ■ ■ ■              ■                   ■ ■
                      ■ ■ ■                 ■ ■

X:   ■             Y:   ■              Z: ■ ■
   ■ ■ ■              ■ ■                   ■
     ■                  ■                   ■ ■
                        ■
```

**Résumé** : 1 + 1 + 2 + 5 + 12 = **21 pièces** = **89 carrés** par joueur

---

## Règles de Placement

### Premier coup

- Chaque joueur place sa première pièce dans **son coin** de départ
- La pièce doit **couvrir la case d'angle**

### Coups suivants

1. **Contact diagonal obligatoire** : La nouvelle pièce doit toucher au moins une de vos pièces déjà posées **par un coin** (diagonale)

2. **Contact par les côtés interdit** : Vos propres pièces ne doivent **jamais** se toucher par un bord (arête)

3. **Chevauchement interdit** : Pas de superposition avec les pièces adverses

```
✅ VALIDE : Contact par un coin (diagonal)

    1   2   3   4   5
  ┌───┬───┬───┬───┬───┐
1 │   │ ▓ │ ▓ │   │   │  ▓ = Pièce existante (L3)
  ├───┼───┼───┼───┼───┤
2 │   │   │ ▓ │   │   │
  ├───┼───┼───┼───┼───┤
3 │   │   │   │ ░ │ ░ │  ░ = Nouvelle pièce (I2)
  ├───┼───┼───┼───┼───┤     ↖ Contact diagonal en (3,3)-(3,4)
4 │   │   │   │   │   │
  └───┴───┴───┴───┴───┘


❌ INVALIDE : Contact par un bord (arête)

    1   2   3   4   5
  ┌───┬───┬───┬───┬───┐
1 │   │ ▓ │ ▓ │   │   │  ▓ = Pièce existante
  ├───┼───┼───┼───┼───┤
2 │   │   │ ▓ │ ░ │ ░ │  ░ = Nouvelle pièce
  ├───┼───┼───┼───┼───┤     ✗ Contact par le bord entre (2,3) et (2,4)
3 │   │   │   │   │   │
  └───┴───┴───┴───┴───┘


❌ INVALIDE : Pas de contact avec vos pièces

    1   2   3   4   5
  ┌───┬───┬───┬───┬───┐
1 │   │ ▓ │ ▓ │   │   │  ▓ = Pièce existante
  ├───┼───┼───┼───┼───┤
2 │   │   │ ▓ │   │   │
  ├───┼───┼───┼───┼───┤
3 │   │   │   │   │   │
  ├───┼───┼───┼───┼───┤
4 │   │   │   │   │ ░ │  ░ = Nouvelle pièce
  ├───┼───┼───┼───┼───┤     ✗ Aucun contact diagonal
5 │   │   │   │   │ ░ │
  └───┴───┴───┴───┴───┘
```

---

## Déroulement

1. Chaque joueur joue à tour de rôle (sens horaire)
2. Un joueur **doit** jouer s'il le peut
3. Un joueur **passe** s'il n'a aucun coup valide
4. La partie se termine quand **tous les joueurs** ont passé

---

## Calcul du Score

- Chaque carré **non placé** = **-1 point**
- **Bonus** : +15 points si toutes les pièces sont placées
- **Bonus supplémentaire** : +5 points si la dernière pièce était le monomino

**Le joueur avec le score le plus élevé gagne.**

---

## Variantes

### Blokus Duo (2 joueurs)

- Plateau 14×14
- Points de départ : (5,5) et (10,10)
- Chaque joueur a toutes ses 21 pièces

### Blokus 2 joueurs (sur plateau standard)

- Chaque joueur contrôle **2 couleurs**
- Joue alternativement avec chaque couleur
