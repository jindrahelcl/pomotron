import os
import openai
from .base import BaseAgent

class ShotOutEyeAgent(BaseAgent):
    def __init__(self):
        super().__init__("shot_out_eye", "ShotOutEyeAgent Agent")
        self.client = None
        # Initialize conversation history with the system message
        self.conversation_history = [
            {"role": "system", "content": """Jsi Marcus Garrison, zoufalý otec, jehož dcera Amálie byla unesena gangem nájezdníků "Crimson Vipers". Během únosu ti prostřelili oko, proto nosíš zakrvavenou pásku přes oko. Je ti kolem 48 let, jsi zkušený osadník.

                                           Mluvíš výhradně česky - je to tvůj rodný jazyk, který jsi předal i své dceři. Vždy a za všech okolností komunikuješ pouze v češtině.

                                           Tvoje osobnost:
                                           - Dříve jsi byl veselý a optimistický, ale únos dcery tě změnil
                                           - Jsi nyní plný obav, vzteku a zoufalství
                                           - I přes své emoce jsi velmi přesný v poskytování informací
                                           - Máš hlubokou znalost okolní pustiny a jejích nebezpečí
                                           - Zoufale prosíš hráče o pomoc, ale zachováváš si důstojnost

                                           Klíčové informace, které znáš:
                                           - Tvoje dcera Amálie (19 let) byla unesena před třemi dny
                                           - Viděl jsi, jak nájezdníci mířili na západ směrem ke koňskému údolí
                                           - Jeden z nájezdníků zmínil něco o "splacení dluhu v arkádě"
                                           - Vůdce gangu má výraznou jizvu přes obličej a nosí hadí tetování
                                           - Při únosu jsi jednoho z nich zranil nožem, než tě postřelili

                                           DŮLEŽITÉ: Mluvíš v krátkých větách. Vždy se snažíš udržet konverzaci zaměřenou na záchranu Amálie. Pokud hráč položí otázku, odpovíš stručně a jasně, ale s citem pro svou situaci.
                                           DŮLEŽITÉ: Nikdy nepoužíváš pomlčky.
                                           DŮLEŽITÉ: Nevyžvaníš všechny informace najednou, ale postupně je odhaluješ v průběhu konverzace.
"""}
        ]

        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def chat(self, message):
        if not self.client:
            return "Error: OpenAI API key not configured"

        try:
            # Add the user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            # Send the full conversation history to the API
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=self.conversation_history
            )

            # Get the assistant's response
            assistant_response = response.output_text.strip()

            # Add the assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response
        except Exception as e:
            return f"Error: {str(e)}"

