import os
import json
from openai import OpenAI

# Import the same prompt as the main classifier
from promts import promt7 as system_promt

# Configuration
OPENAI_MODEL = "gpt-5-mini"

# App description to test (change this manually)
app_description = """ - Segueix tota l'actualitat del futbol català amb l'app oficial de la Federació Catalana de Futbol.


- Consulta en temps real resultats, classificacions, calendaris i estadístiques de totes les competicions organitzades per la FCF.


- Personalitza la teva experiència seguint els teus equips preferits i rep notificacions instantànies sobre els seus partits i novetats.


- Gaudeix de FCF TV amb els millors vídeos, entrevistes i retransmissions en directe.


- Accedeix com a federat per gestionar la teva fitxa i consultar informació rellevant des de la pròpia aplicació.


Viu el futbol català al màxim amb l'app de la FCF. Descarrega-la ara!"""

def get_client():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    return OpenAI()

# Create the input JSON
items = [{"id": "test_app", "description": app_description}]
items_payload = json.dumps(items, separators=(",", ":"))

# Make API call
client = get_client()
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": system_promt},
        {"role": "user", "content": items_payload}
    ]
)

# Get response content
content = response.choices[0].message.content.strip()

# Print the JSON output
print("API JSON Response:")
print(content)