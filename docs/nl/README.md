# Unique Waterontharder voor Home Assistant

**Je Unique waterontharder in Home Assistant: zoutniveau, regeneraties en een melding als hij offline gaat.**

Unique Waterontharder leest je ontharder uit via de [Unique Smart API](https://unique-smart.nl), dezelfde dienst die de app van Unique gebruikt. Je hebt alleen de API-key nodig die je van Unique voor je ontharder krijgt.

## Wat je krijgt

Elke ontharder die aan je API-key gekoppeld is, wordt een apparaat, op serienummer, met deze entiteiten:

| Entiteit | Type | Omschrijving |
|---|---|---|
| Zoutniveau | Sensor (%) | Het beschikbare zoutniveau in procenten |
| Regeneraties | Sensor | Het totaal aantal regeneraties |
| Gemiddelde tijd tussen regeneraties | Sensor (tijdsduur, dagen) | De gemiddelde tijd tussen regeneraties; ook te tonen in uren of weken |
| Capaciteit | Sensor (diagnostisch, L) | De hoeveelheid hars in de cilinder; ook te tonen in gallons |
| Laatste update | Sensor (diagnostisch) | Tijdstip van de laatste melding van de ontharder |
| Geregistreerd op | Sensor (diagnostisch, standaard uit) | De registratiedatum van de ontharder |
| Offline-alarm | Binary sensor (probleem) | Aan wanneer de ontharder voor langere tijd niet gezien is |

Een eenheid wijzig je in de instellingen van de entiteit. Een ontharder die later aan je API-key wordt gekoppeld, verschijnt bij de volgende poll vanzelf.

## Aan de slag

Je hebt Home Assistant 2026.3 of nieuwer nodig, en een API-key voor de Unique Smart API, die je bij Unique opvraagt voor je ontharder.

1. **Installeren.** Open de repository in de Marktplaats (HACS vóór Home Assistant 2026.11) en klik op **Download**, en herstart als Home Assistant erom vraagt.

   [![Open je Home Assistant en open een repository in de Marktplaats.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mirkin-pixel&repository=ha-unique-waterontharders&category=integration)

2. **De integratie toevoegen.** Kies onder **Instellingen → Apparaten & diensten → Integratie toevoegen** voor **Unique Waterontharder** en voer je API-key in. De key wordt direct gecontroleerd, en voor elke ontharder in je account wordt een apparaat aangemaakt.
3. **Erop automatiseren.** Bijvoorbeeld een melding als het zout bijna op is; zie [Voorbeeldautomatisering](#voorbeeldautomatisering).

Geen Marktplaats? Kopieer `custom_components/unique_waterontharder` naar de map `custom_components` van je configuratie en herstart.

## Configuratie

Via **Configureren** stel je in hoe vaak de API wordt gepolld, tussen 5 minuten en 24 uur (standaard: 10 minuten). De ontharder zelf meldt zich hooguit eens per paar uur, dus een korter interval levert zelden versere gegevens op.

Wil je een andere API-key gebruiken zonder je entiteiten te verliezen, kies dan **Herconfigureren** in het menu met drie puntjes achter de configuratie. Trekt Unique de key in, dan vraagt Home Assistant er zelf om een nieuwe.

## Voorbeeldautomatisering

Een melding als het zout bijna op is:

```yaml
automation:
  - alias: "Waterontharder: zout bijvullen"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.unique_smart_duo_zoutniveau
        below: 20
    actions:
      - action: notify.mobile_app_jouw_telefoon
        data:
          message: "Het zoutniveau van de waterontharder is onder de 20%. Tijd om bij te vullen!"
```

Vervang `notify.mobile_app_jouw_telefoon` door de notify-actie van je eigen telefoon; je vindt ze onder **Ontwikkelhulpmiddelen → Acties** als `notify.mobile_app_…`. De entiteit-ID van het zoutniveau hangt af van het model en van de taal waarin Home Assistant stond toen de ontharder werd toegevoegd; je vindt hem op de apparaatpagina.

## Over de API

De integratie gebruikt `GET https://unique-smart.nl/api/v1/data` met de API-key als Bearer-token. Er is momenteel geen rate-limiting op de API, dus de integratie pollt bewust standaard maar één keer per 10 minuten.

Tijdstippen uit de API hebben geen UTC-offset en worden gelezen als Nederlandse tijd (`Europe/Amsterdam`), de lokale tijd van de dienst, ongeacht de tijdzone van je eigen Home Assistant.

De API documenteert de eenheid van `capaciteit` niet. Die wordt gelezen als liter hars, de inhoud van de cilinder. Een hardheidscapaciteit in °dH·m³ zou voor dezelfde cilinder ongeveer vijf tot zes keer hoger uitvallen; meldt jouw ontharder een waarde in die orde, [open dan een issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml).

## Problemen oplossen

Blijven entiteiten op `unknown` of `unavailable` staan, kijk dan eerst onder **Instellingen → Systeem → Reparaties**. Geeft de API geen serienummers meer terug, bijvoorbeeld door een wijziging bij Unique, dan staat daar een melding; die verdwijnt vanzelf zodra ze terug zijn.

Verzamel anders de twee onderstaande zaken en voeg ze toe aan een [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml).

**Debug-logging aanzetten.** Ga naar **Instellingen → Apparaten & diensten → Unique Waterontharder**, klik op de drie puntjes en kies **Debug-logging aanzetten**. Reproduceer het probleem en kies daarna **Debug-logging uitzetten**; Home Assistant downloadt de log dan automatisch. Wil je ook over een herstart heen loggen, zet dan dit in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.unique_waterontharder: debug
```

In de debug-log zie je de HTTP-status van elke poll, de volledige API-respons, de gevonden serienummers en elke waarde die de integratie niet kon verwerken. De API-key wordt nooit gelogd.

**Diagnostiek downloaden.** Kies op dezelfde pagina **Diagnostische gegevens downloaden**. Het bestand bevat de configuratie, de gekozen opties en de laatst opgehaalde API-gegevens. De API-key en de serienummers zijn weggelaten, dus je kunt het bestand zo aan een issue hangen.

## Verwijderen

1. Ga naar **Instellingen → Apparaten & diensten → Unique Waterontharder**, klik op de drie puntjes achter de configuratie en kies **Verwijderen**.
2. Verwijder daarna eventueel de integratie zelf uit de Marktplaats (**⋮ → Verwijderen** op de pagina ervan) en herstart Home Assistant.

Er blijven geen gegevens achter; de API-key wordt samen met de configuratie verwijderd.

Wil je één losse ontharder verwijderen die niet meer aan je API-key hangt, open dan de apparaatpagina en kies **Verwijderen**. Ontharders die de API nog wél meldt, kun je zo niet verwijderen: die komen bij de volgende poll gewoon terug. Er wordt nooit automatisch iets verwijderd, zodat een tijdelijk incompleet API-antwoord niet je historie meeneemt.

## Bijwerken

Vanaf 1.0 breekt een update binnen dezelfde hoofdversie niets van wat je erop gebouwd hebt: entiteit-ID's en hun historie blijven zoals ze zijn, en een entiteit blijft meten wat hij meet. Wat er precies beloofd wordt, staat (in het Engels) in [CONTRIBUTING.md](../../CONTRIBUTING.md#what-a-version-number-promises).

## Ondersteuning

Een vraag of idee is welkom in [Discussions](https://github.com/mirkin-pixel/ha-unique-waterontharders/discussions), onder Q&A of Ideas; in het Nederlands mag, antwoorden komen in het Engels zodat iedereen kan meelezen. Iets wat niet werkt hoort in een [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml). Een probleem met de ontharder zelf of je API-key hoort bij [Unique](https://unique-smart.nl).

Heb je iets aan deze integratie, dan kun je [de ontwikkeling sponsoren](https://github.com/sponsors/mirkin-pixel) op GitHub. Hij blijft hoe dan ook gratis en compleet.

Dit is een onofficiële integratie en is niet gelieerd aan Unique. Gebruik op eigen risico.
