# Vertragsmanager fuer Home Assistant

Repo: https://github.com/ForgeSnacks/HACS-contractmanager

Verwalte Verträge (Handy, Strom, Miete, Internet, Versicherung, etc.) direkt in Home Assistant.

## Features
- Verträge über die Home Assistant UI anlegen (Config Flow), kein YAML notwendig
- Automatische Berechnung der Kündigungsfrist und des nächsten Verlängerungsdatums
- Sensor pro Vertrag mit Attributen (Anbieter, Kosten, Zyklus, Kündigungsfrist, Vertragsende)
- Sammel-Sensor mit den monatlichen Gesamtkosten aller Verträge
- Automations-freundlich: Sensor-Status = Tage bis zur Kündigungsfrist -> einfache Trigger für Benachrichtigungen

## Icon
Das Integrations-Icon liegt unter `icon/icon.png` (256x256) und `icon/logo.png` (512x512). Für die offizielle HACS-Icon-Anzeige im Store kann es zusätzlich an das [home-assistant/brands](https://github.com/home-assistant/brands) Repo unter `custom_integrations/vertragsmanager/` als icon.png/logo.png eingereicht werden (Pull Request).

## Installation ueber HACS
1. HACS -> Drei-Punkte-Menu -> "Benutzerdefinierte Repositories"
2. URL eintragen: `https://github.com/ForgeSnacks/HACS-contractmanager`, Kategorie "Integration" w#hlen
3. "Vertragsmanager" installieren und Home Assistant neu starten
4. Einstellungen -> Geräte & Dienste -> Integration hinzufügen -> "Vertragsmanager"

## Vertrag anlegen
Jeder Vertrag wird als eigener Config-Entry angelegt:
- Name (z.B. "Handyvertrag Telekom")
- Kategorie (Handy, Strom, Gas, Internet, Miete, Versicherung, Sonstiges)
- Kosten pro Zyklus
- Zyklus (monatlich, jaehrlich)
- Vertragsstart
- Kündigungsfrist in Tagen
- Laufzeit in Monaten (für automatische Verlängerung)

## Sensoren
- `sensor.<vertragsname>` - Status: Tage bis Kündigungsfrist, Attribute mit allen Details
- `sensor.vertragsmanager_gesamtkosten` - monatliche Gesamtkosten aller aktiven Verträge

## Automationsbeispiel
```yaml
automation:
  - alias: "Vertrag kündigen erinnern"
    trigger:
      - platform: numeric_state
        entity_id: sensor.handyvertrag_telekom
        below: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Kündigungsfrist für {{ state_attr('sensor.handyvertrag_telekom','anbieter') }} läuft in weniger als 30 Tagen ab!"
```
