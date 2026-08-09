# Unique Water Softener for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Default-orange?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/mirkin-pixel/ha-unique-waterontharders?style=for-the-badge)](https://github.com/mirkin-pixel/ha-unique-waterontharders/releases)

[English](#english) | [Nederlands](#nederlands)

---

## English

Custom integration for [Home Assistant](https://www.home-assistant.io/) that reads your **Unique water softener** through the [Unique Smart API](https://unique-smart.nl).

The integration polls the API every 10 minutes for all softeners linked to your API key. Each softener is created as a device (keyed by serial number) with the following entities:

| Entity | Type | Description |
|---|---|---|
| Salt level | Sensor (%) | The available salt level in percent |
| Regenerations | Sensor | The total number of regenerations |
| Average time between regenerations | Sensor (days) | The average time in days between regenerations |
| Capacity | Sensor (diagnostic) | The resin capacity |
| Last update | Sensor (diagnostic) | Time of the last report from the softener |
| Registered at | Sensor (diagnostic, disabled by default) | The registration date of the softener |
| Offline alert | Binary sensor (problem) | On when the softener has not been seen for a longer period |

### Installation

Requires Home Assistant 2026.3 or newer.

#### Via HACS (recommended)

This integration is available in the HACS default store.

1. Open HACS in Home Assistant.
2. Search for **Unique Waterontharder** and click **Download**.
3. Restart Home Assistant.

Or use this direct link:

[![Open your Home Assistant instance and open the repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mirkin-pixel&repository=ha-unique-waterontharders&category=integration)

#### Manual

1. Copy the `custom_components/unique_waterontharder` folder into the `custom_components` folder of your Home Assistant configuration.
2. Restart Home Assistant.

### Configuration

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Unique Waterontharder**.
3. Enter your API key. You can request this key from Unique for your softener.

The integration validates the key immediately and then automatically creates a device for every softener in your account.

### Removal

1. Go to **Settings → Devices & services → Unique Waterontharder**.
2. Click the three dots next to the configuration and choose **Delete**.
3. Optionally remove the integration itself via HACS (**HACS → Unique Waterontharder → ⋮ → Remove**) and restart Home Assistant.

No data is left behind; the API key is removed together with the configuration.

To remove a single softener that is no longer linked to your API key, open its device page and choose **Delete**. Softeners that the API still reports cannot be deleted this way: they would simply reappear on the next poll. Nothing is ever removed automatically, so a temporarily incomplete API response cannot take your history with it.

### Example automation

Notification when the salt is running low:

```yaml
automation:
  - alias: "Water softener: refill salt"
    trigger:
      - platform: numeric_state
        entity_id: sensor.unique_smart_duo_salt_level
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "The salt level of the water softener is below 20%. Time to refill!"
```

### About the API

The integration uses `GET https://unique-smart.nl/api/v1/data` with the API key as a Bearer token. The API currently has no rate limiting; this integration therefore deliberately polls only once every 10 minutes (the softener itself reports at most once every few hours). Timestamps from the API contain no UTC offset and are interpreted as Dutch time (`Europe/Amsterdam`), the local time of the service, regardless of the timezone of your own Home Assistant installation.

### Troubleshooting

If entities stay `unknown` or `unavailable`, collect the two things below and attach them to an [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues).

**Enable debug logging.** Go to **Settings → Devices & services → Unique Waterontharder**, click the three dots and choose **Enable debug logging**. Reproduce the problem, then choose **Disable debug logging** — Home Assistant downloads the log automatically.

To log across a restart, add this to `configuration.yaml` instead:

```yaml
logger:
  default: warning
  logs:
    custom_components.unique_waterontharder: debug
```

Debug logging shows the HTTP status of every poll, the full API response, the serial numbers found, and any value the integration could not parse. The API key is never logged.

**Download diagnostics.** On the same page, choose **Download diagnostics**. The file contains the configuration entry and the last API data, with the API key redacted.

### Development

Tests run with [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) and require Python 3.14 or newer:

```bash
pip install -r requirements_test.txt
pytest --cov
```

Releases follow the standard HACS flow: bump `version` in `manifest.json`, merge to the default branch, then publish a GitHub release with a matching tag (for example `v0.2.0` for version `0.2.0`). The release workflow verifies that the tag matches the manifest version and attaches a zip of the integration to the release.

### Disclaimer

This is an unofficial integration and is not affiliated with Unique. Use at your own risk.

---

## Nederlands

Custom integration voor [Home Assistant](https://www.home-assistant.io/) die je **Unique waterontharder** uitleest via de [Unique Smart API](https://unique-smart.nl).

De integratie haalt elke 10 minuten de gegevens op van alle ontharders die aan je API-key gekoppeld zijn. Elke ontharder wordt als apparaat aangemaakt (op serienummer), met de volgende entiteiten:

| Entiteit | Type | Omschrijving |
|---|---|---|
| Zoutniveau | Sensor (%) | Het beschikbare zoutniveau in procenten |
| Regeneraties | Sensor | Het totaal aantal regeneraties |
| Gemiddelde tijd tussen regeneraties | Sensor (dagen) | De gemiddelde tijd in dagen tussen regeneraties |
| Capaciteit | Sensor (diagnostisch) | De hoeveelheid hars-capaciteit |
| Laatste update | Sensor (diagnostisch) | Tijdstip van de laatste melding van de ontharder |
| Geregistreerd op | Sensor (diagnostisch, standaard uit) | De registratiedatum van de ontharder |
| Offline-alarm | Binary sensor (probleem) | Aan wanneer de ontharder voor langere tijd niet gezien is |

### Installatie

Vereist Home Assistant 2026.3 of nieuwer.

#### Via HACS (aanbevolen)

Deze integratie is beschikbaar in de standaard HACS-store.

1. Open HACS in Home Assistant.
2. Zoek naar **Unique Waterontharder** en klik op **Download**.
3. Herstart Home Assistant.

Of gebruik deze directe link:

[![Open your Home Assistant instance and open the repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mirkin-pixel&repository=ha-unique-waterontharders&category=integration)

#### Handmatig

1. Kopieer de map `custom_components/unique_waterontharder` naar de map `custom_components` van je Home Assistant-configuratie.
2. Herstart Home Assistant.

### Configuratie

1. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**.
2. Zoek naar **Unique Waterontharder**.
3. Voer je API-key in. Deze key vraag je op bij Unique voor jouw ontharder.

De integratie valideert de key direct en maakt daarna automatisch een apparaat aan voor elke ontharder in je account.

### Verwijderen

1. Ga naar **Instellingen → Apparaten & diensten → Unique Waterontharder**.
2. Klik op de drie puntjes achter de configuratie en kies **Verwijderen**.
3. Verwijder daarna eventueel de integratie zelf via HACS (**HACS → Unique Waterontharder → ⋮ → Verwijderen**) en herstart Home Assistant.

Er blijven geen gegevens achter; de API-key wordt samen met de configuratie verwijderd.

Wil je één losse ontharder verwijderen die niet meer aan je API-key hangt, open dan de apparaatpagina en kies **Verwijderen**. Ontharders die de API nog wél meldt, kun je zo niet verwijderen: die zouden bij de volgende poll gewoon terugkomen. Er wordt nooit automatisch iets verwijderd, zodat een tijdelijk incompleet API-antwoord niet je historie meesleept.

### Voorbeeldautomatisering

Melding wanneer het zout bijna op is:

```yaml
automation:
  - alias: "Waterontharder: zout bijvullen"
    trigger:
      - platform: numeric_state
        entity_id: sensor.unique_smart_duo_zoutniveau
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Het zoutniveau van de waterontharder is onder de 20%. Tijd om bij te vullen!"
```

### Over de API

De integratie gebruikt `GET https://unique-smart.nl/api/v1/data` met de API-key als Bearer-token. Er is momenteel geen rate-limiting op de API; deze integratie pollt daarom bewust maar één keer per 10 minuten (de ontharder zelf meldt zich hooguit eens per paar uur). Tijdstippen uit de API bevatten geen UTC-offset en worden gelezen als Nederlandse tijd (`Europe/Amsterdam`), de lokale tijd van de dienst, ongeacht de tijdzone van je eigen Home Assistant-installatie.

### Problemen oplossen

Blijven entiteiten op `unknown` of `unavailable` staan? Verzamel dan de twee onderstaande zaken en voeg ze toe aan een [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues).

**Debug-logging aanzetten.** Ga naar **Instellingen → Apparaten & diensten → Unique Waterontharder**, klik op de drie puntjes en kies **Debug-logging aanzetten**. Reproduceer het probleem en kies daarna **Debug-logging uitzetten** — Home Assistant downloadt de log dan automatisch.

Wil je ook over een herstart heen loggen, zet dan dit in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.unique_waterontharder: debug
```

In de debug-log zie je de HTTP-status van elke poll, de volledige API-respons, de gevonden serienummers en elke waarde die de integratie niet kon verwerken. De API-key wordt nooit gelogd.

**Diagnostiek downloaden.** Kies op dezelfde pagina **Diagnostische gegevens downloaden**. Het bestand bevat de configuratie en de laatst opgehaalde API-gegevens, met de API-key weggehaald.

### Ontwikkeling

Tests draaien met [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) en vereisen Python 3.14 of nieuwer:

```bash
pip install -r requirements_test.txt
pytest --cov
```

Releases volgen de standaard HACS-werkwijze: verhoog `version` in `manifest.json`, merge naar de default branch en publiceer daarna een GitHub-release met een bijpassende tag (bijvoorbeeld `v0.2.0` voor versie `0.2.0`). De release-workflow controleert of de tag overeenkomt met de manifest-versie en voegt een zip van de integratie toe aan de release.

### Disclaimer

Dit is een onofficiële integratie en is niet gelieerd aan Unique. Gebruik op eigen risico.