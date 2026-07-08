# Vertragsmanager für Home Assistant

Eine Custom Integration für Home Assistant zur Verwaltung von Verträgen, Kündigungsfristen und Kosten.

## Installation

### Über HACS (empfohlen)

1. HACS installiert haben
2. Custom Repository hinzufügen: `https://github.com/ForgeSnacks/HACS-contractmanager`
3. Vertragsmanager installieren
4. Home Assistant neu starten
5. Integration über Einstellungen → Integrationen → "+" → "Vertragsmanager" hinzufügen

### Manuell

1. Ordner `vertragsmanager` in `custom_components/` kopieren
2. Home Assistant neu starten
3. Integration hinzufügen

## Konfiguration

Jeder Vertrag wird über die GUI konfiguriert:

- **Name**: Einprägsamer Name für den Vertrag
- **Kategorie**: Handy, Strom, Gas, Internet, Miete, Versicherung, Streaming, etc.
- **Anbieter**: Name des Anbieters
- **Kosten**: Kosten pro Zyklus
- **Zahlungszyklus**: monatlich oder jährlich
- **Vertragsstart**: Startdatum des Vertrags
- **Kündigungsfrist (Tage)**: Anzahl Tage vor Verlängerung
- **Laufzeit (Monate)**: Vertragslaufzeit in Monaten
- **Automatische Verlängerung**: Ja/Nein

Optionale Felder:
- Vertragsnummer, Kundennummer, etc.

## Features

- **Sensoren**: Jeder Vertrag erstellt einen Sensor mit Kündigungsfrist in Tagen
- **Gesamtkosten-Sensor**: Summe aller monatlichen Kosten
- **Device-Support**: Jeder Vertrag wird als eigenes Device mit Entities angezeigt
- **Panel**: Web-UI zur Übersicht aller Verträge
- **Services**: Verträge per Service erstellen
- **Diagnostics**: Debug-Informationen pro Config Entry
- **Repairs**: Automatische Erkennung von Problemen (ungültige Daten, negative Fristen, etc.)

## Services

### `vertragsmanager.create_contract`

Erstellt einen neuen Vertrag.

```yaml
service: vertragsmanager.create_contract
data:
  name: "Mein Vertrag"
  category: "Handy"
  provider: "Provider GmbH"
  cost: 29.99
  cycle: "monatlich"
  start_date: "2024-01-01"
  notice_days: 30
  duration_months: 12
  auto_renew: true
```

## Unterstützung

Issues: [GitHub Issues](https://github.com/ForgeSnacks/HACS-contractmanager/issues)

## Lizenz

MIT License
