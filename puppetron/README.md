# PuppeTRON

Web frontend pro ovládání StoryTRON systému přes mobil.
Puppet master rozhraní pro správu AI agentů a komunikaci s pomo zařízením.

## Rychlý start

### 1. Instalace závislostí

```bash
# Vytvoření virtuálního prostředí
python3 -m venv env

# Aktivace virtuálního prostředí
source env/bin/activate

# Instalace závislostí
pip install -r requirements.txt
```

### 2. Konfigurace

```bash
# Nastavení URL StoryTRON API (výchozí: http://localhost:5000)
export STORYTRON_URL=http://your-storytron-server:5000

# Port pro PuppeTRON (výchozí: 3000)
export PORT=3000

# Debug režim
export DEBUG=true
```

### 3. Spuštění

```bash
python app.py
```

Aplikace bude dostupná na `http://0.0.0.0:3000`

## Funkce

### 📊 Dashboard
- Zobrazuje stav StoryTRON systému
- Ukazuje aktivního agenta
- Rychlé přepínání mezi agenty
- Odesílání zpráv do pomo zařízení
- Auto-refresh každých 30 sekund

### 🤖 Správa agentů
- Seznam všech dostupných agentů
- Přepínání aktivního agenta
- Detail informací o agentech

### 💬 Chat test
- Testování komunikace s aktivním agentem
- Rychlé zprávy pro testování
- Real-time konverzace

### 📱 Mobilní rozhraní
- Optimalizováno pro telefony
- Terminal/hacker styl vzhledu
- Touch-friendly ovládání

## API komunikace

PuppeTRON komunikuje se StoryTRON přes REST API:

- `GET /` - Status check StoryTRON
- `GET /agents` - Seznam agentů
- `POST /agents/<id>/activate` - Přepnutí agenta
- `POST /chat` - Chat s aktivním agentem

## Vývoj

### Struktura projektu

```
puppetron/
├── app.py              # Hlavní Flask aplikace
├── requirements.txt    # Python závislosti
├── templates/          # HTML šablony
│   ├── base.html       # Základní layout
│   ├── dashboard.html  # Hlavní dashboard
│   ├── agents.html     # Správa agentů
│   ├── chat.html       # Chat rozhraní
│   └── error.html      # Error stránky
└── README.md           # Dokumentace
```

### Styling
- Terminal/retro vzhled s zeleným textem
- Responsive design pro mobily
- CSS Grid pro layout agentů
- Courier New font pro konzolový styl

### Budoucí funkce
- WebSocket pro real-time updates
- Historie konverzací
- Push notifikace
- Pokročilé nastavení agentů
