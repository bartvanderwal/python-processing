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
- Elke 10 punten stijgt het level en neemt de snelheid toe met factor 1.1.
- Bij level-up knipperen score en level-indicator kort.

## Obstakels en speciale acties

- De slang klapt uit wanneer hij dicht bij de speler komt.
- De lage vogel vereist bukken om punten te krijgen.
- High jump activeert wanneer de speler eerst bukt en binnen 0,5 seconde springt.
- Torencactus verschijnt vanaf level 3 en vereist doorgaans high jump.
- Bij een naderende torencactus verschijnt kort:
  - `Prepare for high jump: duck first then quickly jump.`

## Levelsysteem

- De game heeft 10 levels (`MAX_LEVEL = 10`).
- Elke 10 punten stijgt het level.
- Bij elke level-up:
  - De scrollsnelheid stijgt met factor `1.1`.
  - Score en level-indicator knipperen kort.
  - De spawnmix verandert, met hogere spawndichtheid en complexere patronen.

### Progressie per fase

- Level 1, `Enter Cactus Land...`:
  - Introductie van de woestijn.
  - Basisobstakels: lage cactus, hoge cactus en lage vogel.
  - Nog geen slang.
- Level 2, `Snake Sands`:
  - De woestijn wordt drukker en gevaarlijker.
  - Slang komt erbij en klapt dichtbij verder uit.
  - Meer variatie in timing tussen vogel, cactus en slang.
- Level 3, `High Jump Ridge`:
  - Verticale obstakels worden belangrijker.
  - Torencactus komt erbij.
  - High-jump waarschuwing wordt relevant voor grotere obstakels.
- Level 4, `Bird Boss Canyon`:
  - Eerste minibossfase.
  - Reuzenvogel verschijnt.
  - Boss fight met energiemeter van 20 stappen.
  - Boss verslaan vereist 15 hits.
- Level 5, `Fly away`:
  - De route opent richting vliegtuig-sectie.
  - Vliegtuig verschijnt als pickup.
  - Bij landing op het vliegtuig start flight mode.
  - Flight mode: bewegen in linkerhelft, ontwijken van pijpen boven en onder, Flappy Bird-stijl.
- Level 6, `Storm Track`:
  - Tussenfase met hogere druk.
  - Verdere verhoging van snelheid, spawnfrequentie en patrooncomplexiteit.
  - Mix van bekende vijanden vraagt sneller reageren.
- Level 7, `Cactus Fortress`:
  - Tweede minibossfase.
  - Reuzencactus verschijnt.
  - Boss fight met energiemeter van 25 stappen.
  - De cactus heeft 5 takken met elk 5 hits; totaal 25 hits nodig.
- Level 8, `Wild Flats`:
  - Snellere combinatie van grond- en luchtgevaar.
  - Ook snel achter elkaar verschijnende cactussen, vaak twee direct na elkaar en soms zelfs drie als extra uitdaging.
  - Sprongen vragen hier extra controle: tijdens sommige sprongen moet je ook `Pijl omlaag` gebruiken om goed uit te komen.
  - Verdere opschaling van tempo, variatie en reactiedruk.
- Level 9, `Last Stretch`:
  - Voorbereiding op de eindbaas.
  - Hogere druk door snellere spawnmix en minder hersteltijd tussen obstakels.
- Level 10, `Giant Town`:
  - Eindbaasfase.
  - Eindbaas is een reuzenvariant per karakter:
    - Dino: ReuzenDino.
    - Cowboy: ReuzenCowboy.
    - Roadrunner: ReuzenCoyote.
  - Boss gebruikt hetzelfde projectieltype als de speler.
  - Boss verslaan vereist 35 hits, energiemeter van 35 stappen.

### Overzichtskaart en levelkeuze

- De game heeft nu ook een zelfgetekende overzichtskaart.
- Op die kaart kies je het level dat je wilt spelen.
- De kaart geeft per fase een duidelijk visueel gebied of thema, zodat de speler ziet welke omgeving en vijanden bij dat level horen.
- Daardoor werkt de levelprogressie niet alleen als score-opbouw, maar ook als een zichtbare route door de spelwereld.

### Boss- en wapenregels

- Tijdens boss fights schiet de speler met `SPACE`.
- Character-specifiek wapen:
  - Cowboy: `Gun` (zwart).
  - Roadrunner: `TNT` (rood).
  - Dino: vuurprojectiel.

## Assets

Sprite vliegtuig

![Plane still](assets/plane-still.png)

![Plane still](assets/plane-sprite2.png)

- Spelerassets staan in `assets/`.
- Obstakelassets staan in `assets/obstacles/`.
- Belangrijke sprites:
  - `assets/dino-transparant.png`
  - `assets/cowboy-transparant.png`
  - `assets/roadrunner-transparant.png`
  - `assets/airplane-transparant.png`
  - `assets/obstacles/cactus-transparant.png`
  - `assets/obstacles/bird-transparant.png`
  - `assets/snake-transparant.png`

![alt text](assets/explosion.png)

Bron: `https://www.pngarts.com/explore/35406`
