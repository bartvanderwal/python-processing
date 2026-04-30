# Software Guidebook

## Doel

Dit document bundelt de spelregels, systems en ontwerpprincipes van de game op één plek.

Gebruik dit bestand als referentie voor:

- levelprogressie;
- powerups en shopgedrag;
- boss-entrances en speciale arena's;
- UI- en feedbackprincipes.

## SGB Conventie

Elk principe en elke structurele beslissing in dit document bevat expliciet een `Waarom`.

- Zonder rationale zijn regels lastig te toetsen en verouderen ze sneller.
- Met rationale kunnen we wijzigingen evalueren op intentie, niet alleen op letterlijke tekst.

## Exception Visibility

Exceptions worden niet stil ingeslikt.

Waarom:

- Een fout zonder logregel is in praktijk nauwelijks te debuggen, zeker in de web-runtime.
- Stil ingeslikte exceptions maken regressies onzichtbaar en laten kapot gedrag doorgaan alsof het "gewoon niet ondersteund" is.
- Browser-, audio- en assetproblemen moeten direct herleidbaar zijn naar de callsite en het bestand dat faalt.

- Geen `except Exception: pass` in projectcode.
- Als een exception bewust wordt opgevangen om runtime of tooling overeind te houden, log dan minimaal context, exceptiontype en melding naar console of stderr.
- Bij herhaalbare runtimefouten mag logging gededupliceerd worden om spam te beperken, maar de eerste fout moet zichtbaar blijven.

## Platform Parity (DEV/PROD)

Lokaal draaien en web-deploy moeten dezelfde game opleveren qua gedrag.

Waarom:

- We willen lokaal snel itereren in Python-modus, zonder dat gedrag later op web functioneel afwijkt.
- Dat voorkomt verrassingen bij release: wat lokaal speelbaar en correct is, moet online dezelfde mechanics tonen.
- Performance kan tussen runtime-omgevingen verschillen; daarom testen we naast lokaal ook regelmatig de web-build zelf.

- Geen platform-specifieke gameplayregels: obstaclelogica, powerups, hitboxes, timing en scoreprogressie zijn identiek op desktop en web.
- Geen content-splitsing per platform: levels, patterns en balanswaarden worden centraal beheerd en niet gedupliceerd in `if IS_WEB` versus lokaal.
- Platform-afhankelijke code mag alleen voor technische runtime-zaken (bijv. input/audio unlock, packaging, pad-resolutie), nooit voor gamebalans of mechanics.
- Performanceproblemen worden opgelost met generieke optimalisaties die overal gelden (assets, renderpad, objectbeheer), niet met afwijkende spelregels op web.

## Creative Integrity

De game gebruikt dezelfde visuele taal op meerdere plekken.

- Sprite-based visualisation (`.png`) heeft de voorkeur boven ad-hoc getekende placeholders zodra een asset beschikbaar is.
- Interactieve keuzes gebruiken kleine, duidelijke kaders met een subtiele pulse of glow.
- Shop-items mogen dus niet ineens als totaal andere UI-componenten verschijnen als ze al als iconen in HUD of shop bestaan.
- Informatie met gameplay-impact moet leesbaar zijn in de wereld zelf, niet alleen als tekst erboven.
- Gevaar krijgt altijd een visuele cue: bijvoorbeeld een landingsgloed onder een vallende bom, of een arena die oplicht bij explosies.
- Level-flow is leerbaar: obstaclevolgordes zijn in basis scripted/hardcoded per level, zodat spelers patronen kunnen herkennen en verbeteren.
- Variatie mag alleen gecontroleerd: vanaf hogere levels uitsluitend via een kleine, vooraf ontworpen set veilige patroonblokken.
- Onmogelijke combinaties zijn verboden: runtime mag geen obstacleketens genereren die niet haalbaar zijn met normale timing/spronghoogte wanneer een powerup net is afgelopen.
- Luchtlevels gebruiken decoratieve parallax-wolken als sfeerlaag en leesbare snelheidsreferentie, nooit als obstacle of misleidende hitbox.
- Menu-tekst boven de luchtlaag gebruikt karakter-afhankelijke contrastkleuren en mag nooit visueel over elkaar heen vallen; titel, startprompt en character-select copy blijven gescheiden blokken.

Waarom:

- De Chrome Dino-vluchtstukken voelen sterker als luchtspace wanneer de achtergrond subtiel meebeweegt.
- Parallax helpt snelheid en diepte lezen zonder extra gameplay-ruis toe te voegen.
- Wolken mogen de obstacleleesbaarheid niet aantasten; daarom blijven ze puur decoratief.
- Ook in het menu moet tekst boven de lucht onmiddellijk leesbaar blijven; gekozen karakter en luchtkleur bepalen dus mee welke donkere contrastkleur daar werkt.

![Cowboy dead](cowboy-dead.png)

## Geen Defensieve Gameplay-Fallbacks

Gameplaycode mag niet stilletjes ander gedrag kiezen als een asset, API, state of aanname ontbreekt.

Waarom:

- Fallbacks maken fouten onzichtbaar en daardoor lastig te reproduceren.
- Testen wordt onbetrouwbaar als code onder onbekende omstandigheden "iets anders" doet dan het ontworpen gedrag.
- Bij AI-assisted development moeten ontbrekende assets, ontbrekende API's en kapotte aannames expliciet zichtbaar worden, anders bouwt de agent verder op een verborgen fout.
- Een hard failure met een duidelijke oorzaak is beter dan een speelbare maar verkeerde toestand.

- Geen stille fallback van ontbrekende gameplay-assets naar oude sprites.
- Geen alternatieve mechanics bij ontbrekende functies of ongeldige state.
- Geen brede `try/except` rond gameplaylogica om fouten te maskeren.
- Wel toegestaan: expliciete platform-adapters voor technische runtimeverschillen, mits gameplaygedrag gelijk blijft en fouten zichtbaar blijven.

## Audio Feedback

Sprong-audio moet het type sprong duidelijk maken.

Waarom:

- Een high jump moet niet alleen visueel waarneembaar zijn, maar zowel visueel als auditief.
- Het `weeh`-geluid past bij dat high-jump moment en maakt het effect direct herkenbaar.
- Dit ondersteunt timingleren, vooral bij snelle obstacle-combinaties.

- Normale sprong: gebruik `jump.wav` voor alle karakters.
- Versterkte/high jump (duck-jump, high-jump powerup of actieve jump shoes): gebruik `weeh.wav` voor alle karakters.

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
- Level 6 heeft een afwijkende minibossflow: aan het einde van de pipe/flappy flight-sectie verschijnt een Zeppelin in de lucht in plaats van een ground-hub.
- Die Zeppelin wordt verslagen vanuit het eigen gele vliegtuig met een schot-aanval; de boss is dus onderdeel van `flight_mode` en niet van de gewone boss hub.

Waarom:

- De overgang van level 5 naar 6 bouwt al een luchtmechanic op; een luchtboss benut die bestaande skill direct.
- Een ground-hub zou de opgebouwde flight-spanning onnodig onderbreken.
- De speler moet dezelfde besturing en voertuigfantasie behouden tijdens het gevecht.

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
  - miniboss `flight Zeppelin`: `18` punten;
  - miniboss `2`: `15` punten;
  - eindbaas: `35` punten.

### Obstakelgeneratiebeleid

- Levels `1` t/m `7` zijn primair leerbaar en gebruiken vaste obstaclepatronen.
- Vanaf level `8` is beperkte variatie toegestaan, maar alleen met curated templates (geen vrije RNG-combinatie van losse obstakels).
- Elke template voor level `8+` moet handmatig speelbaar gevalideerd zijn.
- Validatieregel: ook als een high-jump powerup leeg is, moet de speler met normale sprong een uitwijkroute of haalbare timing houden.
- Templates die directe "soft-lock" situaties kunnen veroorzaken (zoals te krappe multi-cactusketens zonder herstelmoment) zijn niet toegestaan.

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
- Aan het eind van deze luchtsectie verschijnt de Zeppelin-tussenbaas.
- De speler blijft in het gele vliegtuig en schiet de Zeppelin neer vanuit de lucht.

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
