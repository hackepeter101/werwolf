# Werwolf Spiel

Ein unterhaltsames Werwolf-Spiel in Python.

## Schnellstart (ein Befehl mit curl)

Mit diesem Befehl lädst du `install.sh` direkt von GitHub, klonst das Projekt, installierst Python (falls nötig) und erstellst eine virtuelle Umgebung:

```bash
curl -fsSL https://raw.githubusercontent.com/hackepeter101/werwolf/main/install.sh | bash -s -- werwolf
```

Danach starten:

```bash
cd werwolf
source .venv/bin/activate
python werwolf.py
```

## Alternative: lokal mit install.sh

Wenn du das Repository schon lokal hast:

```bash
./install.sh werwolf
```

## Hinweis für Windows

Der `curl | bash` Schnellstart ist für Linux/macOS gedacht.
Unter Windows nutze am besten WSL oder führe die Schritte in Git Bash aus.

## Virtuelle Umgebung deaktivieren

Wenn du fertig bist:

```bash
deactivate
```
