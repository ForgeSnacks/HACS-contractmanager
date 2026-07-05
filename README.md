# Vertragsmanager fuer Home Assistant

Repo: https://github.com/ForgeSnacks/HACS-contractmanager

Verwalte Vertraege (Handy, Strom, Miete, Internet, Versicherung, etc.) direkt in Home Assistant.

## Features
- Vertraege ueber die Home Assistant UI anlegen (Config Flow), kein YAML notwendig
- Automatische Berechnung der Kuendigungsfrist und des naechsten Verlaengerungsdatums
- Sensor pro Vertrag mit Attributen (Anbieter, Kosten, Zyklus, Kuendigungsfrist, Vertragsende)
- Sammel-Sensor mit den monatlichen Gesamtkosten aller Vertraege
- Automations-freundlich: Sensor-Status = Tage bis zur Kuendigungsfrist -> einfache Trigger fuer Benachrichtigungen

## Icon
Das Integrations-Icon liegt unter `icon/icon.png` (256x256) und `icon/logo.png` (512x512). Fuer die offizielle HACS-Icon-Anzeige im Store kann es zusaetzlich an das [home-assistant/brands](https://github.com/home-assistant/brands) Repo unter `custom_integrations/vertragsmanager/` als icon.png/logo.png eingereicht werden (Pull Request).

## Installation ueber HACS
1. HACS -> Drei-Punkte-Menu -> "Benutzerdefinierte Repositories"
2. URL eintragen: `https://github.com/ForgeSnacks/HACS-contractmanager`, Kategorie "Integration" waehlen
3. "Vertragsmanager" installieren und Home Assistant neu starten
4. Einstellungen -> Geraete & Dienste -> Integration hinzufuegen -> "Vertragsmanager"

## Vertrag anlegen
Jeder Vertrag wird als eigener Config-Entry angelegt:
- Name (z.B. "Handyvertrag Telekom")
- Kategorie (Handy, Strom, Gas, Internet, Miete, Versicherung, Sonstiges)
- Kosten pro Zyklus
- Zyklus (monatlich, jaehrlich)
- Vertragsstart
- Kuendigungsfrist in Tagen
- Laufzeit in Monaten (fuer automatische Verlaengerung)

## Sensoren
- `sensor.<vertragsname>` - Status: Tage bis Kuendigungsfrist, Attribute mit allen Details
- `sensor.vertragsmanager_gesamtkosten` - monatliche Gesamtkosten aller aktiven Vertraege

## Automationsbeispiel
```yaml
automation:
  - alias: "Vertrag kuendigen erinnern"
    trigger:
      - platform: numeric_state
        entity_id: sensor.handyvertrag_telekom
        below: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Kuendigungsfrist fuer {{ state_attr('sensor.handyvertrag_telekom','anbieter') }} laeuft in weniger als 30 Tagen ab!"
```
