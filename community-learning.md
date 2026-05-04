# Workshop programmeren - Community learning

## 1. Individueel (ca. 10 minuten)

### Voorbereiding

Installeer de programmeersoftware op je eigen laptop: kopieer de map "Python" van de usb-stick naar een map op je laptop, bijvoorbeeld je Bureaublad.

Zorg dat je een werkende internetverbinding hebt. Als je al Eduroam hebt van je eigen school, heb je automatisch verbinding met Eduroam van de HAN. Als je geen Eduroam hebt, kun je een verbinding maken met het HAN Guest-netwerk.

In de map Python vind je het programma Thonny. Dat is het programma waar we in gaan programmeren. Start het programma.

We gaan gebruik maken van een aantal tekenfuncties, die samen Python-processing heten. Informatie daarover vind je hier: [https://github.com/AIM-HBO-ICT-Voorlichting/python-processing](https://github.com/AIM-HBO-ICT-Voorlichting/python-processing)

## 2. In twee-/drietallen (ca. 35 minuten)

### Stap 1: Simpele auto tekenen

Afbeelding met tekst, schermopname, diagram, lettertype.

Door AI gegenereerde inhoud is mogelijk onjuist.

Doel:

- Begrijpen hoe je basisvormen tekent en positioneert.

Opdracht:

- Teken een simpele auto door te programmeren met Python-processing.

Voorbeelden van vragen die je aan ChatGPT kunt stellen:

- "Welke functies kan ik gebruiken om een rechthoek en cirkels te tekenen met Python-processing?"
- Let op: ChatGPT is niet vanzelf bekend met Python-processing. Je moet daarom de link van hierboven meegeven met je eerste vraag.
- "Hoe bepaal ik zelf de x- en y-coordinaten zodat de cirkels onder de rechthoek staan? Gebruik geen variabelen en geen formules."

Wat je hierdoor leert:

- Gebruik van `rect()` en `ellipse()` of `circle()`.
- Coordinaten begrijpen.
- Relatie tussen vormen zien, zoals carrosserie en wielen.

### Stap 2: Auto in een functie zetten

Doel:

- Een functie maken voor hergebruik.

Opdracht:

- Maak een herbruikbare functie om de auto op verschillende plekken te kunnen tekenen.

Voorbeelden van vragen:

- "Hoe kan ik mijn tekeninstructies in een functie stoppen?"
- "Hoe kan ik de auto meerdere keren tekenen zonder de code te kopieren?"
- "Hoe kan ik x en y doorgeven aan mijn functie zodat de auto ergens anders wordt getekend?"
- "Welke informatie moet ik doorgeven aan de functie zodat de auto op een andere plek kan staan?"
- "Welke aanpassingen moet ik maken aan de wielen als ik de auto op een andere x-positie teken?"

Wat je leert:

- Functies maken en gebruiken.
- Herbruikbaarheid van code.
- Het basisidee van parameters voorbereiden.
- Functieparameters begrijpen.
- Coordinaten dynamisch gebruiken.
- Hergebruik van code toepassen.

### Stap 3: Auto laten bewegen

Doel:

- Leren over state, logic en view.

Opdracht:

- Laat de auto over het scherm bewegen, vanaf de linker onderkant.

Hints en vragen:

- "Welke variabele moet ik onthouden tussen frames om de x-positie bij te houden?"
- "Hoe kan ik x elke herhaling van `draw()` laten toenemen?"
- "Wat gebeurt er als ik niets doe aan de randen?"
- "Hoe worden state, logic en view hier toegepast?"

Wat je leert:

- State gebruiken om positie op te slaan.
- Het verschil tussen state en view begrijpen.
- De eerste stap naar animatie zetten.

Als er nog tijd is:

### Stap 5: Omdraaien bij de randen

Doel:

- De auto heen en weer laten gaan.

Opdracht:

- Zorg ervoor dat de auto teruggaat als hij de rechterkant van het scherm bereikt, en weer van links naar rechts gaat als hij de linkerkant weer heeft bereikt.

Hints en vragen:

- "Hoe kan ik controleren of de auto de rechterrand of linkerrand raakt?"
- "Hoe kan ik de beweging omkeren als de rand is bereikt?"
- "Waarom gebruik je eigenlijk twee `if`-statements voor de randen?"
- "Welke variabele verandert als de auto van richting verandert?"

Wat je leert:

- Logic toepassen om state aan te passen.
- De animatie compleet maken, heen en weer.
- `if`-statements gebruiken voor randcontrole.

### Stap 6: Starten en stoppen met spatie

Doel:

- Interactiviteit toevoegen met het toetsenbord.

Opdracht:

- Maak het programma zo dat de auto pas start als je op een toets drukt, en weer stopt als je opnieuw op een toets drukt.

Hints en vragen:

- "Welke variabele kan onthouden of de auto moet bewegen of niet?"
- "Welke functie wordt uitgevoerd wanneer ik een toets indruk in Python-processing?"
- "Hoe kan ik de waarde van een boolean omkeren bij een toets?"
- "Hoe combineer ik start/stop-logica met de beweging van de auto?"
- "Hoe worden state, logic en view hier toegepast?"

Wat je leert:

- Booleans gebruiken als start/stop-schakelaar.
- Event-driven programmeren.
- Samenwerking van state en logic.

## 3. Met je groep (ca. 15 minuten)

### Stap 7: Maak een PowerPoint-presentatie met 3 slides

Doel:

- Uitleggen hoe de auto werkt met state, logic en view.
- Leren structureren van informatie.
- Code en ontwerpideeën visualiseren.

### Slide 1: Introductie van het project

Wat erop moet staan:

- Titel van het project.
- Kort doel.
- Screenshot of schets van de auto.

Hints en vragen aan ChatGPT:

- "Hoe kan ik kort uitleggen wat dit project doet?"
- "Welke afbeelding of schets laat het beste zien wat de auto doet?"
- "Hoe kan ik de opdracht in een zin samenvatten?"

Wat je leert:

- De context van het project uitleggen.
- Een simpele visuele weergave maken.

### Slide 2: State en logic

Wat erop moet staan:

- State: welke variabelen onthouden iets tussen herhalingen van `draw()`?
- Logic: welke regels veranderen de state?
- Eventueel een diagram of schema:

```text
[state] --> [logic] --> nieuwe state
```

Hints en vragen aan ChatGPT:

- "Welke variabelen in mijn programma onthouden iets over de auto?"
- "Welke regels in mijn code veranderen die variabelen?"
- "Kan je me helpen een schema te maken dat laat zien hoe state en logic samenwerken?"

Wat je leert:

- Het verschil tussen onthouden van waarden, state, en regels of condities, logic.
- Visueel laten zien hoe de auto beweegt.

### Slide 3: View en samenwerking

Wat erop moet staan:

- View: wat wordt er getekend op het scherm?
- Samenwerking van state, logic en view: hoe de variabelen, state, en regels, logic, samen bepalen wat de gebruiker ziet.
- Eventueel een flow-diagram:

```text
[state] -> [logic] -> [view] -> [scherm]
```

Hints en vragen aan ChatGPT:

- "Welke delen van mijn code zorgen alleen voor tekenen?"
- "Hoe leg ik uit dat view de state gebruikt maar niet verandert?"
- "Hoe kan ik een schema maken dat laat zien hoe alles samenwerkt?"

Wat je leert:

- State, logic en view visueel en conceptueel uitleggen.
- Verbanden tussen code en output duidelijk maken.

## 4. Voor thuis

Beantwoord voor jezelf de volgende vragen:

- Wat heb ik in deze les geleerd?
- Welke feedback heb ik gekregen op de kwaliteit van wat ik heb gemaakt?
- Waarom is mijn werk van goede kwaliteit?

### Wil je meer?

Afbeelding met voertuig, auto, landvoertuig, ontwerp.

Door AI gegenereerde inhoud is mogelijk onjuist.

- Teken een mooiere auto.
- Of gebruik een plaatje van een auto, dier of poppetje.
- Bedenk een spel.
