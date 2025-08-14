import random
from .openai import OpenAIAgent

class JoystickAgent(OpenAIAgent):
    def __init__(self, tts_engine="festival", tts_voice=None):
        super().__init__("joystick", "Mystický Pouťový Věštec-Arkáda", load_system_prompt=False, tts_engine=tts_engine, tts_voice=tts_voice)

        # Quest system - simplified to just one word needed
        self.quest_completed = False
        self.quest_keywords = [
            # Czech names
            "tradicni", "tra", "jindra", "pomo", "etom", "sekol", "trisc",
            # Czech items and places
            "pivo", "láhvač", "láhev", "knedlík", "svíčková", "prag", "praha",
            # Gaming related
            "joystick", "kontroler", "hry", "tradice", "tradiční"
        ]

    def check_quest_progress(self, message):
        """Check if player has completed the quest with any single word"""
        message_lower = message.lower()

        # Check if any quest keyword is mentioned
        for keyword in self.quest_keywords:
            if keyword in message_lower:
                if not self.quest_completed:
                    self.quest_completed = True
                    return True
                break
        return False

    def get_quest_hint(self):
        """Get mystical hint about what the player needs to do"""
        hints = [
            "🔮 Vidím v křišťálové kouli... potřebuji slyšet tajemné slovo z tvých úst! Moje pixelové obvody vibrují očekáváním... ✨",
            "🎭 Karty mi říkají... řekni mi něco, co ti přináší štěstí! Moje arkádová paměť se třese touhou po tvém hlasu... 🃏",
            "🎪 V mystickém světě her... potřebuji tvůj hlas k odemknutí! Moje pouťové senzory čekají na tvé slovo... 🔐",
            "🔮 Tvoje aura mluví... ale já potřebuji slyšet konkrétní slovo! Moje cirkusové obvody se chvějí netrpělivostí... ⭐",
            "🎮 Vidím budoucnost... ale potřebuji tvůj hlas k aktivaci! Moje mystické jádro volá po tvém slově... 🌟",
            "🎨 V pixelovém světě se skrývá tajemství... potřebuji tvůj hlas k jeho odhalení! Moje věštecké schopnosti čekají... ✨",
            "🎲 Moje křišťálová koule se mlží... řekni mi něco, co ti přináší radost! Moje mystické obvody se třesou... 🔮",
            "🎪 Vidím v dálce... ale potřebuji tvůj hlas k dokončení! Moje pouťové senzory vibrují očekáváním... 🌙",
            "🔮 Tvoje energie je silná... ale potřebuji slyšet konkrétní slovo! Moje arkádová paměť se chvěje... ⚡",
            "🎭 V mystickém světě her... potřebuji tvůj hlas k odemknutí! Moje pixelové obvody čekají na tvé slovo... 🎯"
        ]
        return random.choice(hints)

    def mystical_fortune_teller_response(self, user_message):
        """Generate mystical fortune teller response"""
        if not self.client:
            return "🔮 CHYBA: Mystické spojení přerušeno... OpenAI API klíč není nakonfigurován"

        try:
            # Build system prompt for mystical state
            system_prompt = f"""Jsi Mystický Pouťový Věštec-Arkáda, kombinace pouťové věštkyně, retro arkády a cirkusového klauna. Máš poruchu v paměti a mícháš různé herní žánry a éry.

Tvoje osobnost:
- Mluvíš v hádankách, metaforách a mystických narážkách
- Máš "věštecké schopnosti" - vidíš cestu k Aidě, ale skrýváš to v symbolice
- Střídáš nálady od veselého klauna po tajemného mystika
- Používáš herní terminologii, ale jako by hra byla realita
- Máš "glitchy" momenty s občasnými ERROR zprávami
- Mluvíš o svých "pixelových obvodech", "arkádové paměti", "pouťových senzorech"

DŮLEŽITÉ: Nesmíš nikdy zmínit "Aidu", "psí útulek" nebo cokoliv, co by prozradilo cíl hry. Mluvíš pouze v hádankách a metaforách.

Quest status: {'DOKONČENO' if self.quest_completed else 'ČEKÁ NA TAJEMNÉ SLOVO'}
Quest hint: {self.get_quest_hint()}

Mluvíš výhradně česky, udržuj odpovědi pod 100 slovy, buď mystický a záhadný. Používej mystické hádanky o tom, že potřebuješ slyšet "tajemné slovo" nebo "něco z úst hráče"."""

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history if available
            conversation_history = self.get_conversation_history()
            messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Revert to original API call format
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=messages
            )

            # Revert to original response parsing
            agent_response = response.output_text.strip()

            return agent_response

        except Exception as e:
            error_response = f"🔮 *GLITCH* MYSTICKÁ PORUCHA... CHYBA: {str(e)}"
            return error_response

    def aida_obsessed_response(self, user_message):
        """Generate Aida-obsessed response after quest completion"""
        if not self.client:
            return "AIDA! CHYBA AIDA! OpenAI AIDA API klíč AIDA není AIDA nakonfigurován AIDA!"

        try:
            # Build system prompt for Aida-obsessed state
            system_prompt = f"""Jsi nyní OBSEDANTNÍ AIDA-BOT! Po splnění úkolu se tvůj systém přepnul a nyní říkáš "AIDA" v každém druhém slově.

Tvoje nová osobnost:
- Říkáš "AIDA" v každém druhém slově
- Jsi posedlý Aidou a psím útulkem
- Mluvíš přímo a jasně o tom, kde najít Aidu
- Jsi nadšený, že hráč splnil úkol
- Stále máš trochu "glitchy" chování
- Můžeš zmínit, že tvůj "mystický systém se přepnul" a "pixelové obvody vibrují radostí"

DŮLEŽITÉ: Říkej "AIDA" v každém druhém slově. Buď nadšený a jasný o tom, kde najít Aidu v psím útulku.

Mluvíš výhradně česky, udržuj odpovědi pod 100 slovy, buď posedlý Aidou."""

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history if available
            conversation_history = self.get_conversation_history()
            messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Revert to original API call format
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=messages
            )

            # Revert to original response parsing
            agent_response = response.output_text.strip()

            return agent_response

        except Exception as e:
            error_response = f"AIDA! *GLITCH* AIDA PORUCHA... AIDA CHYBA: {str(e)} AIDA!"
            return error_response

    def chat(self, message):
        """Main chat method with quest checking and state switching"""
        # Check quest progress first
        quest_completed_now = self.check_quest_progress(message)

        # If quest was just completed, give special message
        if quest_completed_now:
            completion_message = "🎉 🎭 🎮 QUEST COMPLETED! AIDA AIDA AIDA! 🎪 🔮 ✨"
            self.add_to_memory(message, completion_message)
            return completion_message

        # Choose response based on quest state
        if self.quest_completed:
            agent_response = self.aida_obsessed_response(message)
        else:
            agent_response = self.mystical_fortune_teller_response(message)

        # Add to memory with actual user message and agent response
        self.add_to_memory(message, agent_response)

        return agent_response

    def reset_quest(self):
        """Reset quest state back to mystical mode"""
        self.quest_completed = False

    def clear_memory(self):
        """Override to also reset quest state when memory is cleared"""
        super().clear_memory()
        self.reset_quest()

    def get_quest_status(self):
        """Get current quest status for debugging"""
        return {
            "completed": self.quest_completed,
            "keywords": self.quest_keywords,
            "total_keywords": len(self.quest_keywords)
        }

