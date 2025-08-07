# StoryTRON

Flasková servica která spravuje gpt agenty pro pomotron systém.
Asi je to navržený tak aby to běželo na veřejný IP adrese.

## Rychlý start

### 1. Instalace závislostí

```bash
# Vytvoření virtuálního prostředí (pokud neexistuje)
python3 -m venv env

# Aktivace virtuálního prostředí
source env/bin/activate

# Instalace závislostí
pip install -r requirements.txt
```

### 2. Konfigurace

```bash
# Zkopírování příkladové konfigurace
cp .env.example .env

# Úprava konfigurace (nastavte OpenAI API klíč a další parametry)
nano .env
```

### 3. Spuštění

```bash
# Spuštění pomocí run scriptu
python run.py

# Nebo přímo
python app.py
```

Aplikace bude dostupná na `http://0.0.0.0:5000`

## API Endpointy

### API endpointy (pro PomoTRON client)
- `GET /api` - Keep-alive signál (vrací stav a aktivního agenta)
- `GET /api/agents` - Seznam všech dostupných agentů včetně aktivního
- `POST /api/agents/<agent_id>/activate` - Přepnutí na jiného agenta podle ID
- `POST /api/chat` - Poslání zprávy aktivnímu agentovi

### Web rozhraní (Puppet Master)
- `GET /` - Hlavní dashboard
- `GET /web/agents` - Správa agentů
- `GET|POST /web/chat` - Chat test rozhraní
- `POST /switch-agent` - Přepnutí agenta z web rozhraní

### Příklad použití API

```bash
# Keep-alive / health check
curl http://localhost:5000/api

# Seznam agentů a zobrazení aktivního
curl http://localhost:5000/api/agents

# Přepnutí na jiného agenta
curl -X POST http://localhost:5000/api/agents/helper/activate

# Chat s aktivním agentem
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ahoj!"}'
```

### Web rozhraní
Otevřete v prohlížeči: `http://localhost:5000/`
- Mobilně optimalizované rozhraní
- Real-time dashboard s informacemi o systému
- Správa a přepínání agentů
- Chat test pro ověření funkčnosti

## Vývoj

Aplikace implementuje základní funkcionalita pro správu GPT agentů:
- Vždy je aktivní jeden agent (výchozí: "default")
- Agenti jsou předem definovaní, nelze je přidávat/mazat
- Podporuje přepínání mezi agenty a chat s aktivním agentem
- Keep-alive endpoint pro monitoring
- **Web rozhraní** pro mobilní ovládání (Puppet Master)

### Funkce
- **API pro PomoTRON**: RESTful endpointy pro Raspberry Pi klienta
- **Web dashboard**: Mobilně optimalizované rozhraní pro ovládání
- **Listing agentů**: Zobrazuje všechny dostupné agenty a který je aktivní
- **Přepínání agentů**: Umožňuje změnit aktivního agenta podle ID
- **Chat**: Posílání zpráv aktivnímu agentovi
- **Keep-alive**: Monitoring stavu aplikace

### Struktura projektu

```
storytron/
├── app.py              # Hlavní Flask aplikace (API + Web)
├── config.py           # Konfigurace
├── run.py              # Spouštěcí script
├── requirements.txt    # Python závislosti
├── .env.example        # Příklad konfigurace
├── templates/          # HTML šablony pro web rozhraní
│   ├── base.html       # Základní layout
│   ├── dashboard.html  # Hlavní dashboard
│   ├── agents.html     # Správa agentů
│   ├── chat.html       # Chat rozhraní
│   └── error.html      # Error stránky
└── README.md          # Dokumentace
```