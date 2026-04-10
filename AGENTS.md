# AGENTS.md

In 2026 ontkom je ook niet meer aan de hype van AI, of meer precies LLM, Large Language models, en de moderne maar snel ingevoerde wijze van 'Agentic coding'. In aanvulling op de README.md daarom deze AGENTS.md met wat info voor zowel de mens als de AI agent zoals Codex, Claude of Cursor.

## Richtlijnen voor deze Python Processing codebase

Deze codebase is een eigen Python-implementatie van Processing en wijkt op veel punten af van de originele Java Processing API. Niet alle functies uit Java Processing zijn hier beschikbaar. Gebruik altijd de lokale documentatie ([api.md](api.md)) en de code in de map `processing/` als referentie voor beschikbare functies.

### Belangrijkste aandachtspunten

- **Gebruik alleen functies die in api.md of de code zelf staan.** Neem niet automatisch aan dat alle Java Processing functies werken.
- **Voorbeeld:** Er zijn géén functies als `loop()` of `no_loop()`. De event-loop wordt geregeld door `run()` in `processing/processing.py`.
- **Wil je gedrag aanpassen (zoals stoppen met tekenen bij game over), gebruik dan een eigen variabele:**

```python
game_over = False


    global game_over
    if game_over:
        # Toon game over scherm
        return
    # ... normale game logica ...
    if botsing:
        game_over = True
```

### Misverstanden voorkomen

- Ga er niet vanuit dat Java Processing functies (zoals `saveFrame()`, `beginShape()`, `endShape()`, enz.) automatisch werken.
- Controleer altijd in [api.md](api.md) of de functie bestaat, of kijk in de code onder `processing/`.

## Zie ook

- [api.md](api.md)
- [processing/processing.py](processing/processing.py)
- [processing/system.py](processing/system.py)
- [processing/utils.py](processing/utils.py)

---

## Opmerking over pygame-patterns

- Er is een SKILL.md aanwezig voor pygame-patterns in `.agents/skills/pygame-patterns/SKILL.md`.
- Deze skill is vooral bedoeld voor projecten met een pyproject.toml en geavanceerde pygame setup.
- Dit project gebruikt requirements.txt en een eigen processing-API, dus niet alle pygame-patterns zijn direct toepasbaar.
