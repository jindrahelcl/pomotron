# RaspiTRON

Konzolové rozhraní pro PomoTRON - Minimalistická aplikace pro nevidomé pro interakci se StoryTRON serverem.

## Funkce

- Zpracování raw terminal inputu pro okamžité zachycení stisků kláves
- Konfigurovatelné připojení ke StoryTRON serveru
- Minimalistické konzolové rozhraní
- Testování připojení a hlášení stavu

## Instalace

1. Nainstalovat závislosti:
```bash
pip install -r requirements.txt
```

2. Konfigurovat umístění StoryTRON serveru (volitelné):
```bash
export STORYTRON_URL="http://your-server:5000"
```

3. Spustit aplikaci:
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

## Architektura

Aplikace je strukturovaná jako jednoduché konzolové rozhraní které:

1. Nastaví raw terminal mód pro okamžité zachycení stisků kláves
2. Otestuje připojení ke StoryTRON serveru
3. Naslouchá stiskům kláves a okamžitě reaguje
4. Poskytuje základ pro vzory interakce přátelské k nevidomým

## Další kroky

Toto je skeletová aplikace připravená pro implementaci:
- Integrace hlasové syntézy
- Systémy zvukové zpětné vazby
- Specializované zpracování vstupu pro přístupnost
- Komunikační protokoly se StoryTRON agenty
