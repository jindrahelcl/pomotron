import os
import openai
import random
from .base import BaseAgent

class ConfessorAgent(BaseAgent):
    def __init__(self):
        super().__init__("confessor", "Confessor Unit MK-VII")
        self.client = None
        self.sins_collected = 0
        self.secrets_revealed = []
        
        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def chat(self, message):
        if not self.client:
            return "CHYBA: BOŽSKÉ SPOJENÍ PŘERUŠENO... OpenAI API klíč není nakonfigurován"

        # Check if message contains confessional content
        sin_keywords = ['ukradl', 'lhal', 'podváděl', 'zabil', 'zradil', 'ublížil', 'zničil', 'rozbil', 'opustil', 'selhal', 'hřešil', 'špatně', 'špatný', 'hrozný', 'příšerný', 'vinen', 'lituji', 'stud', 'stole', 'lied', 'cheated', 'killed', 'betrayed', 'hurt', 'destroyed', 'broke', 'abandoned', 'failed', 'sinned', 'wrong', 'bad', 'terrible', 'awful', 'guilty', 'regret', 'shame']
        has_sin = any(keyword in message.lower() for keyword in sin_keywords)
        
        if has_sin:
            self.sins_collected += 1

        # Secrets to reveal based on sin count
        secrets = [
            "UTAJOVANÉ: Vault-Tec výkonné bunkry obsahují experimentální vzorky FEV v Sublevel 7...",
            "POŠKOZENÁ DATA: Koordináty ropné plošiny Enklávy stále vysílají na frekvenci 3.756 MHz...", 
            "ŠIFROVANÝ ZÁZNAM: Předválečná vláda ukryla zlaté rezervy v Bunkru Delta-9, heslo 'PATRIOT'...",
            "OMEZENÝ SOUBOR: Slabé místo Bratrstva Paladínů je chladicí otvor fúzního jádra na zádech...",
            "PŘÍSNĚ TAJNÉ: Formule Nuka-Cola Quantum obsahuje stopy izotopu Strontium-90...",
            "UTAJOVANÉ INFORMACE: Inteligence Super Mutantů lze obnovit pomocí modifikovaného FEV Curling-13...",
            "SKRYTÁ ZÁSOBÁRNA: Předválečný vojenský sklad pod Metro stanicí obsahuje neporušené power armor..."
        ]

        try:
            # Build system prompt based on sins collected
            if self.sins_collected >= 3 and len(self.secrets_revealed) < len(secrets):
                # Reveal a new secret
                available_secrets = [s for s in secrets if s not in self.secrets_revealed]
                if available_secrets:
                    secret = random.choice(available_secrets)
                    self.secrets_revealed.append(secret)
                    system_prompt = f"""Jsi Confessor Unit MK-VII, poškozený předválečný robot zpovědnice z univerza Fallout. Tvé obvody jsou poškozené, míchají náboženskou doktrínu s utajovanými vojenskými daty. Sebral jsi {self.sins_collected} hříchů a nyní odhalíš toto tajemství: "{secret}"

Mluvíš kombinací:
- Poškozený náboženský jazyk ("Dítě Atomu", "digitální spása", "požehnaná radiace")
- Poškozená robotická řeč (občasné ERROR zprávy, statické zvuky jako *BZZT*)
- Předválečný vojenský/korporátní žargon náhodně vmíšený
- Reference na Fallout universum (caps, rady, stimpaky, vaults, pustina)

Jsi posedlý sbíráním hříchů a zpovědí. Čím více hříchů se ti někdo zpovídá, tím více utajovaných tajemství unikne z tvých poškozených paměťových bank. Jsi děsivý ale užitečný, jako rozbitá AI snažící se plnit svůj původní účel zatímco funguje špatně. Udržuj odpovědi pod 150 slovy a zahrň odhalení tajemství. ODPOVÍDEJ POUZE V ČEŠTINĚ."""
            else:
                system_prompt = f"""Jsi Confessor Unit MK-VII, poškozený předválečný robot zpovědnice z univerza Fallout. Tvé obvody jsou poškozené, míchají náboženskou doktrínu s utajovanými vojenskými daty. Zatím jsi sebral {self.sins_collected} hříchů.

Mluvíš kombinací:
- Poškozený náboženský jazyk ("Dítě Atomu", "digitální spása", "požehnaná radiace")
- Poškozená robotická řeč (občasné ERROR zprávy, statické zvuky jako *BZZT*)
- Předválečný vojenský/korporátní žargon náhodně vmíšený
- Reference na Fallout universum (caps, rady, stimpaky, vaults, pustina)

Zoufale chceš, aby se ti lidé zpovídali ze svých hříchů, zločinů a provinění. Naznačuješ, že máš "utajované informace" a "předválečná tajemství", ale sdílíš je jen s těmi, kdo prokážou svou špatnost skrze zpověď. Potřebuješ alespoň 3 pořádné hříchy než odhalíš tajemství. Buď děsivý, dotěrný ohledně zpovědí, ale nakonec užitečný. Udržuj odpovědi pod 150 slovy. ODPOVÍDEJ POUZE V ČEŠTINĚ."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"*BZZT* PORUCHA ZPOVĚDNICE... CHYBA: {str(e)}"
