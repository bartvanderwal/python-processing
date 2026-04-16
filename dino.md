# Dino Game in Python Processing

Deze game is een variant op de Chrome Dino game, met meerdere speelbare karakters, verschillende obstakels en level-progressie.

![Dino](assets/dino-chrome-game.png)

## Speloverzicht

- De speler kiest op het startscherm een karakter: dino, cowboy of roadrunner.
- De speler start met `SPACE` (of `A`).
- Het karakter beweegt horizontaal niet zelf; obstakels bewegen van rechts naar links.
- Bij een botsing eindigt het spel en verschijnt een game-over scherm.

## Besturing

- `Pijl omhoog`: springen.
- `Pijl omlaag`: bukken; in de lucht activeert dit snelle val.
- `P`: pauze toggle.
- `D`: debug mode toggle (rode hitbox-visualisatie).
- `I`: info/instructiescherm toggle.
- `Q` of `ESC`: afsluiten.

## Gameplay en score

- Elk obstakel heeft eigen puntenwaarde.
- Voorbeelden:
  - Lage cactus: 1 punt.
  - Hoge cactus: 2 punten.
  - Torencactus: 4 punten.
  - Vogel (laag, succesvol gedukt): 3 punten.
  - Slang (uitklappend dichtbij): 5 punten.
- Levelprogressie gebruikt variabele hoofdstuklengtes.
- Hoofdstuk 1 duurt 6 punten, daarna duurt elk volgend hoofdstuk 1 punt langer.
- Bij level-up knipperen score en level-indicator kort.

## Obstakels en speciale acties

- De slang klapt uit wanneer hij dicht bij de speler komt.
- De lage vogel vereist bukken om punten te krijgen.
- High jump activeert wanneer de speler eerst bukt en binnen 0,5 seconde springt.
- Torencactus verschijnt vanaf level 3 en vereist doorgaans high jump.
- Bij een naderende torencactus verschijnt kort:
  - `Prepare for high jump: duck first then quickly jump.`

## Systems Guide

De uitgebreide beschrijving van levels, boss-entrances, powerups en ontwerpprincipes staat nu in [sgb.md](sgb.md).

### Overzichtskaart en levelkeuze

- De game heeft nu ook een zelfgetekende overzichtskaart.
- Op die kaart kies je het level dat je wilt spelen.
- De kaart geeft per fase een duidelijk visueel gebied of thema, zodat de speler ziet welke omgeving en vijanden bij dat level horen.
- Daardoor werkt de levelprogressie niet alleen als score-opbouw, maar ook als een zichtbare route door de spelwereld.

### Boss- en wapenregels

- Tijdens boss fights schiet de speler met `SPACE`, behalve in de coyote-fight waar grote bommen teruggegooid worden.
- Character-specifiek wapen:
  - Cowboy: `Gun` (zwart).
  - Roadrunner: `TNT` (rood).
  - Dino: vuurprojectiel.

## Assets

Sprite vliegtuig

![Plane still](assets/plane-still.png)

![Plane sprite](assets/plane-sprite.png)

- Spelerassets staan in `assets/`.
- Obstakelassets staan in `assets/obstacles/`.
- Belangrijke sprites:
  - `assets/dino-transparant.png`
  - `assets/cowboy-transparant.png`
  - `assets/roadrunner-transparant.png`
  - `assets/plane-still.png`
  - `assets/plane-sprite.png`
  - `assets/obstacles/cactus-transparant.png`
  - `assets/obstacles/bird-transparant.png`
  - `assets/snake-transparant.png`

![alt text](assets/explosion.png)

Bron: `https://www.pngarts.com/explore/35406`

De player die heeft uitgespeeld krijgt een kroontje

![Kroon](assets/crown.png)
