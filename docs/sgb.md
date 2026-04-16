# Software Guidebook

## Doel

Dit document bundelt de spelregels, systems en ontwerpprincipes van de game op één plek.

Gebruik dit bestand als referentie voor:

- levelprogressie;
- powerups en shopgedrag;
- boss-entrances en speciale arena's;
- UI- en feedbackprincipes.

## Creative Integrity

De game gebruikt dezelfde visuele taal op meerdere plekken.

- Sprite-based visualisation (`.png`) heeft de voorkeur boven ad-hoc getekende placeholders zodra een asset beschikbaar is.
- Interactieve keuzes gebruiken kleine, duidelijke kaders met een subtiele pulse of glow.
- Shop-items mogen dus niet ineens als totaal andere UI-componenten verschijnen als ze al als iconen in HUD of shop bestaan.
- Informatie met gameplay-impact moet leesbaar zijn in de wereld zelf, niet alleen als tekst erboven.
- Gevaar krijgt altijd een visuele cue: bijvoorbeeld een landingsgloed onder een vallende bom, of een arena die oplicht bij explosies.

![Cowboy dead](cowboy-dead.png)

## Shop En Powerups

De badger shop verschijnt in het menu en vlak voor boss fights.

### Beschikbare powerups

- `Extra Life`:
  - icoon: hartje;
  - effect: absorbeert één fatale hit;
  - gebruik: blijft als voorraad bewaard tot een botsing het item verbruikt.
- `Shield`:
  - icoon: schild;
  - effect: tijdelijke bescherming;
  - duur: `SHOP_SHIELD_MS = 5000`.
- `Coin Boost`:
  - icoon: muntjes `x2`;
  - effect: verdubbelt verzamelde coins tijdelijk;
  - duur: `SHOP_COIN_BOOST_MS = 60000`.
- `Jump Shoes`:
  - icoon: schoenen;
  - effect: hogere sprongen tijdelijk;
  - duur: `SHOP_JUMP_SHOES_MS = 30000`.

### Activatiegedrag

- Aankopen in het startmenu worden bij run-start geactiveerd.
- Aankopen in de pre-boss shop worden geactiveerd zodra de speler de shop-overlay afsluit.
- Het schild en extra leven zijn verdedigende lagen; coin boost en jump shoes zijn tijdelijke boosts.

### UI-richting

- De vier shop-items horen icon-first te zijn.
- Dezelfde iconen mogen later ook in de HUD gebruikt worden zodra losse uitgesneden assets beschikbaar zijn.
- De huidige HUD mag daarom iconen naast tekst tonen in plaats van alleen tekstregels.

## Boss Entrances

Voor elk boss level stopt de endless-runner-flow kort in een statische hubscene.

- De speler kan daar links/rechts bewegen zoals in een boss arena.
- Links staat de badger shop.
- Rechts staat de entrance naar het gevecht.
- Interactie gebeurt met `Pijl omlaag`.

### Mini bosses

- Voor level 4 en level 7 staat rechts een arena-ingang.
- De speler kan eerst shoppen en daarna bewust het gevecht starten.

### Eindbaas level 10

- Voor de coyote-boss staat rechts een pijp.
- `Pijl omlaag` op de pijp start de ondergrondse boss arena.
- De arena gebruikt een donkerdere, grijze grot-achtige achtergrond.
- Grote vallende bommen tonen een gele landingsgloed zolang ze nog in de lucht zijn.
- Zodra een grote bom ontploft, licht de cave kort op.

## Level Systeem

- De game heeft `10` levels.
- Hoofdstuk `1` duurt `6` obstacles.
- Elk volgend level vraagt `3` obstacles meer dan het vorige.
- Bij elk nieuw level stijgt de scrollsnelheid met factor `1.1`.
- Score en level-progressie zijn losgekoppeld:
  - score komt uit punten, coins en boss rewards;
  - level-progressie komt uit het aantal cleared obstacles.
- Boss rewards volgen de benodigde hits:
  - miniboss `1`: `15` punten;
  - miniboss `2`: `15` punten;
  - eindbaas: `35` punten.

### Aantal obstacles per level

- Level `1`: `6` obstacles.
- Level `2`: `9` obstacles (`15` totaal).
- Level `3`: `12` obstacles (`27` totaal).
- Level `4`: `15` obstacles (`42` totaal).
- Level `5`: `18` obstacles (`60` totaal).
- Level `6`: `21` obstacles (`81` totaal).
- Level `7`: `24` obstacles (`105` totaal).
- Level `8`: `27` obstacles (`132` totaal).
- Level `9`: `30` obstacles (`162` totaal).
- Level `10`: `33` obstacles (`195` totaal).

## Levels

### Level 1: `Enter Cactus Land...`

- Introductie van de woestijn.
- Basisobstakels: lage cactus, hoge cactus en lage vogel.
- Nog geen slang.

### Level 2: `Snake Sands`

- Meer druk in de woestijn.
- Slangen komen erbij.
- Timing tussen vogel, cactus en slang varieert meer.

### Level 3: `High Jump Ridge`

- Verticale sprongen worden belangrijker.
- Torencactus en high-jumpflow krijgen nadruk.
- Jump blocks kunnen regen, natte grond en bloemen triggeren.

### Level 4: `Bird Boss Canyon`

- Eerste minibossfase.
- Reuzenvogel-boss.
- Shop-hub vóór de arena-ingang.

### Level 5: `Fly away`

- Eerste vliegtuighoofdstuk.
- Pijpen verschijnen als obstakels.
- Vliegtuig kan als pickup flight mode starten.

### Level 6: `Storm Track`

- Tweede vliegtuighoofdstuk.
- Flight mode loopt door over level 5 en 6.
- Pijpen blijven actief als obstakeltype.

### Level 7: `Cactus Fortress`

- Tweede minibossfase.
- Grondgevecht tegen de reuzencactus.
- Shop-hub vóór de arena-ingang.

### Level 8: `Wild Flats`

- Meer tempo en krappe obstacle-combinaties.
- Multi-cactus packs vragen snelle landingen.

### Level 9: `Last Stretch`

- Voorbereiding op de eindbaas.
- Hogere reactiedruk en minder hersteltijd.

### Level 10: `Giant Town`

- Eindbaasfase.
- Reuzenvariant per karakter:
  - dino: `ReuzenDino`;
  - cowboy: `ReuzenCowboy`;
  - roadrunner: `ReuzenCoyote`.
- Voor de coyote-route loopt de speler eerst via de shop-hub naar een pijp.
- De coyote wordt verslagen door `5` grote bommen terug te gooien.

## Referenties

- Speluitleg en projectnotities: [dino.md](dino.md)
- Contributierichtlijnen: [CONTRIBUTING.md](CONTRIBUTING.md)
- Agent/projectrichtlijnen: [AGENTS.md](AGENTS.md)
