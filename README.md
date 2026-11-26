# Unique Water Softener for Home Assistant

[![HACS](https://img.shields.io/badge/Home_Assistant_Marketplace-Default-purple?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/mirkin-pixel/ha-unique-waterontharders?style=for-the-badge)](https://github.com/mirkin-pixel/ha-unique-waterontharders/releases)
[![Sponsor](https://img.shields.io/badge/Sponsor-ea4aaa?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/mirkin-pixel)

**Your Unique water softener in Home Assistant: salt level, regenerations and an alert when it goes offline.**

**Nederlands:** [de documentatie in het Nederlands](docs/nl/README.md)

Unique Water Softener reads your softener through the [Unique Smart API](https://unique-smart.nl), the same service the Unique app uses. All it needs is the API key Unique gives you for your softener.

## What you get

Every softener linked to your API key becomes a device, keyed by its serial number, with these entities:

| Entity | Type | Description |
|---|---|---|
| Salt level | Sensor (%) | The available salt level in percent |
| Regenerations | Sensor | The total number of regenerations |
| Average time between regenerations | Sensor (duration, days) | The average time between regenerations; can be shown in hours or weeks |
| Capacity | Sensor (diagnostic, L) | The amount of resin in the cylinder; can be shown in gallons |
| Last update | Sensor (diagnostic) | Time of the last report from the softener |
| Registered at | Sensor (diagnostic, disabled by default) | The registration date of the softener |
| Offline alert | Binary sensor (problem) | On when the softener has not been seen for a longer period |

A unit is changed in the entity's settings. A softener that is added to your API key later shows up by itself on the next poll.

## Get started

You need Home Assistant 2026.3 or newer, and an API key for the Unique Smart API, which you request from Unique for your softener.

1. **Install.** Open the repository in the Marketplace (HACS before Home Assistant 2026.11) and click **Download**, then restart when Home Assistant asks.

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mirkin-pixel&repository=ha-unique-waterontharders&category=integration)

2. **Add the integration.** Under **Settings → Devices & services → Add integration**, choose **Unique Waterontharder** and enter your API key. The key is checked straight away, and a device is created for every softener in your account.
3. **Automate on it.** For example a notification when the salt runs low; see [Example automation](#example-automation).

No Marketplace? Copy `custom_components/unique_waterontharder` into the `custom_components` folder of your configuration and restart.

## Configuration

Under **Configure** you set how often the API is polled, between 5 minutes and 24 hours (default: 10 minutes). The softener itself reports at most once every few hours, so a shorter interval rarely yields fresher data.

To use a different API key without losing your entities, choose **Reconfigure** in the three-dot menu of the entry. If Unique revokes the key, Home Assistant asks for a new one by itself.

## Example automation

A notification when the salt is running low:

```yaml
automation:
  - alias: "Water softener: refill salt"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.unique_smart_duo_salt_level
        below: 20
    actions:
      - action: notify.mobile_app_your_phone
        data:
          message: "The salt level of the water softener is below 20%. Time to refill!"
```

Replace `notify.mobile_app_your_phone` with the notify action of your own phone; **Developer tools → Actions** lists them under `notify.mobile_app_…`. The entity ID of the salt level depends on the model and the language Home Assistant was set to when the softener was added; you find it on the device page.

## About the API

The integration uses `GET https://unique-smart.nl/api/v1/data` with the API key as a Bearer token. The API has no rate limiting at the moment, so the integration deliberately polls only once every 10 minutes by default.

Timestamps from the API carry no UTC offset and are read as Dutch time (`Europe/Amsterdam`), the local time of the service, whatever the time zone of your own Home Assistant.

The API does not document the unit of `capaciteit`. It is read as litres of resin, the volume of the cylinder. A hardness capacity in °dH·m³ would be roughly five to six times higher for the same cylinder, so if your softener reports a value in that range instead, please [open an issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml).

## Troubleshooting

If entities stay `unknown` or `unavailable`, look under **Settings → System → Repairs** first. When the API stops returning serial numbers, for example after a change on the side of Unique, a message there says so; it disappears by itself once they are back.

Otherwise, collect the two things below and attach them to an [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml).

**Enable debug logging.** Go to **Settings → Devices & services → Unique Waterontharder**, click the three dots and choose **Enable debug logging**. Reproduce the problem, then choose **Disable debug logging**; Home Assistant downloads the log automatically. To log across a restart, add this to `configuration.yaml` instead:

```yaml
logger:
  default: warning
  logs:
    custom_components.unique_waterontharder: debug
```

Debug logging shows the HTTP status of every poll, the full API response, the serial numbers found, and any value the integration could not parse. The API key is never logged.

**Download diagnostics.** On the same page, choose **Download diagnostics**. The file contains the configuration entry, the selected options and the last API data. The API key and the serial numbers are left out, so the file is safe to attach to an issue.

## Removal

1. Go to **Settings → Devices & services → Unique Waterontharder**, click the three dots next to the entry and choose **Delete**.
2. Optionally remove the integration itself from the Marketplace (**⋮ → Remove** on its page) and restart Home Assistant.

No data is left behind; the API key is removed together with the entry.

To remove a single softener that is no longer linked to your API key, open its device page and choose **Delete**. Softeners the API still reports cannot be deleted this way: they would simply come back on the next poll. Nothing is ever removed automatically, so a temporarily incomplete API response cannot take your history with it.

## Upgrading

From 1.0 on, an upgrade within the same major version does not break what you built on it: entity IDs and their history stay as they are, and an entity keeps what it measures. What exactly is promised is in [CONTRIBUTING.md](CONTRIBUTING.md#what-a-version-number-promises).

## Development

Working on the integration itself is covered in [CONTRIBUTING.md](CONTRIBUTING.md). It needs Python 3.14 or newer and nothing else: no Home Assistant installation of your own.

```bash
pip install -r requirements_test.txt
ruff check . && ruff format --check . && mypy && pytest --cov
```

## Support

A question or an idea is welcome in [Discussions](https://github.com/mirkin-pixel/ha-unique-waterontharders/discussions), under Q&A or Ideas. Something that does not work goes in an [issue](https://github.com/mirkin-pixel/ha-unique-waterontharders/issues/new?template=bug_report.yml). A problem with the softener itself or your API key goes to [Unique](https://unique-smart.nl).

If this integration is useful to you, you can [sponsor its development](https://github.com/sponsors/mirkin-pixel) on GitHub. It stays free and complete either way.

This is an unofficial integration and is not affiliated with Unique. Use at your own risk.
