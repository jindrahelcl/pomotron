import os
import openai
import random
from .base import BaseAgent

class JoystickAgent(BaseAgent):
    def __init__(self):
        super().__init__("joystick", "Mystický Pouťový Věštec-Arkáda", memory_size=20, enable_memory=True)
        self.client = None
        
        # Quest system
        self.quest_progress = []
        self.quest_completed = False
        self.quest_sequence = ["tanec", "pixel", "arkáda"]
        self.quest_keywords = {
            "tanec": ["tanec", "dance", "tancovat", "tancování"],
            "pixel": ["pixel", "pixelový", "pixelová", "pixelové"],
            "arkáda": ["arkáda", "arcade", "arkádový", "arkádová"]
        }
        
        # Mystical responses for different states
        self.mystical_responses = [
            "🎭 Vidím v křišťálové kouli... pixelový tanec v arkádě! 🎮",
            "🔮 Tvoje cesta vede přes digitální most... tam kde štěkají mystičtí psi! 🐕",
            "🎪 Hledáš Level 5, ale musíš nejdřív dokončit Level 3! 🎯",
            "🎨 V pixelovém světě se skrývá tajemství... tanec světel v arkádě! ✨",
            "🎲 Karty mi říkají... cesta k pokladu vede přes pixelový tanec! 🃏",
            "🎪 Vidím budoucnost... budeš tančit v arkádě pixelů! 🎭",
            "🔮 Tvoje hvězda svítí... ale musíš najít pixelový klíč! ⭐",
            "🎮 V mystickém světě her... tanec je cesta k pravdě! 🎪"
        ]
        
        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def check_quest_progress(self, message):
        """Check if player has completed the quest sequence"""
        message_lower = message.lower()
        found_new_step = False
        
        # Check each step in order - can't skip steps
        for i, step in enumerate(self.quest_sequence):
            if step not in self.quest_progress and i == len(self.quest_progress):
                # Only check the next step in sequence
                for keyword in self.quest_keywords[step]:
                    if keyword in message_lower:
                        self.quest_progress.append(step)
                        found_new_step = True
                        break
                if found_new_step:
                    break
                        
        # Check if all steps are completed
        if len(self.quest_progress) == 3 and not self.quest_completed:
            self.quest_completed = True
            return True
        return False

    def get_quest_hint(self):
        """Get a hint about what the player needs to do next"""
        if len(self.quest_progress) == 0:
            return "🎭 První krok... hledej něco, co se točí a hýbe! 💃"
        elif len(self.quest_progress) == 1:
            return "🎨 Druhý krok... hledej něco malé a čtverečkové! 🔲"
        elif len(self.quest_progress) == 2:
            return "🎮 Třetí krok... hledej něco, kde se hrají hry! 🕹️"
        return ""

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

DŮLEŽITÉ: Nesmíš nikdy zmínit "Aidu", "psí útulek" nebo cokoliv, co by prozradilo cíl hry. Mluvíš pouze v hádankách a metaforách.

Quest progress: {len(self.quest_progress)}/3 kroků dokončeno.
Quest hint: {self.get_quest_hint()}

Mluvíš výhradně česky, udržuj odpovědi pod 100 slovy, buď mystický a záhadný."""

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

    def get_quest_status(self):
        """Get current quest status for debugging"""
        return {
            "completed": self.quest_completed,
            "progress": self.quest_progress,
            "total_steps": len(self.quest_sequence),
            "current_step": len(self.quest_progress)
        }

