# RaspiTRON

Konzolové rozhraní pro PomoTRON - Minimalistická aplikace pro nevidomé pro interakci se StoryTRON serverem.

## Funkce

- Zpracování raw terminal inputu pro okamžité zachycení stisků kláves
- Konfigurovatelné připojení ke StoryTRON serveru
- Minimalistické konzolové rozhraní
- Testování připojení a hlášení stavu
- Volitelné čtení odpovědí nahlas pomocí gTTS

## Instalace

1. Nainstalovat závislosti:
```bash
pip install -r requirements.txt
```

2. Konfigurovat umístění StoryTRON serveru (volitelné):
```bash
export STORYTRON_URL="http://your-server:5000"
```

3. (Volitelné) Nainstalovat audio přehrávač (jeden z):
```bash
sudo apt-get update && sudo apt-get install -y mpg123
# alternativy: sudo apt-get install -y ffmpeg  # (ffplay)
# nebo: sudo apt-get install -y mpv
```

4. Spustit aplikaci:
```bash
python main.py
```

## Použití

- Stiskni jakoukoliv klávesu pro zobrazení kódů kláves a test zpracování vstupu
- Stiskni 'q' pro ukončení
- Stiskni Ctrl+C pro vynucené ukončení

## Konfigurace

Aplikace čte následující proměnné prostředí:

- `STORYTRON_URL`: URL StoryTRON serveru (výchozí: `http://localhost:5000`)
- `RASPITRON_TTS`: Povolit TTS ("1"/"0", výchozí: povoleno)
- `RASPITRON_TTS_LANG`: Jazyk pro gTTS (např. `en`, `cs`; výchozí: `en`)

## Architektura

Aplikace je strukturovaná jako jednoduché konzolové rozhraní které:

1. Nastaví raw terminal mód pro okamžité zachycení stisků kláves
2. Otestuje připojení ke StoryTRON serveru
3. Naslouchá stiskům kláves a okamžitě reaguje
4. Poskytuje základ pro vzory interakce přátelské k nevidomým

## Poznámky k TTS

- TTS používá knihovnu gTTS (Google Text-to-Speech) a lokální přehrávač (`mpg123`/`ffplay`/`mpv`).
- Pokud není nalezen žádný přehrávač, TTS se automaticky vypne.
