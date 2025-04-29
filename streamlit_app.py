import streamlit as st
from openai import OpenAI
import tiktoken

# Parte della chiave API (evita di esporla pubblicamente)
key_part1 = "sk-proj-"
key_part2 = "E_lerQ9WnMEHjxp2cl6c3oBsa_KwY_CHGDFBbHwagpK6lZYY5j6OS1mebHio27rHayMzGVK6RNT3BlbkFJwtD5ZmGe_VTnA6-5o6BXOHEe3wdg8k-ietTWv3AFh0J6qtPyEH3wfyiJFSGj--LJwSjgbO1mMA"
OPENAI_API_KEY = key_part1 + key_part2

# Funzione per caricare informazioni dal file
def load_personal_info(file_path="informazioni_rolando.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Funzione per contare i token di un testo
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Inizializzazione della sessione
if "messages" not in st.session_state:
    st.session_state.messages = []

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

# Funzione per ottenere un contesto ridotto
def get_reduced_context(personal_info, prompt):
    # Suddividi le informazioni personali in una lista di frasi
    sentences = personal_info.split('.')
    prompt_keywords = set(prompt.lower().split())
    
    # Mantieni le frasi rilevanti per la domanda
    relevant_sentences = [s for s in sentences if any(word in s.lower() for word in prompt_keywords)]
    reduced_context = ". ".join(relevant_sentences)
    
    if not relevant_sentences:
        reduced_context = "Non ho abbastanza informazioni per rispondere."
        
    return reduced_context

# Carica informazioni personali e client
personal_info = load_personal_info()
client = OpenAI(api_key=OPENAI_API_KEY)

# Interfaccia utente
st.title("Chatbot di Rolando")
st.markdown("Puoi fare **fino a 3 domande** riguardo **Rolando**.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.questions_asked >= 3:
    st.warning("Hai raggiunto il limite massimo di 3 domande. Grazie per aver usato il chatbot!")
else:
    if prompt := st.chat_input("Fai una domanda su Rolando..."):
        if "rolando" not in prompt.lower():
            st.error("Puoi fare solo domande relative a **Rolando**.")
        else:
            st.session_state.questions_asked += 1
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            reduced_context = get_reduced_context(personal_info, prompt)
            context = (
                "Le seguenti informazioni sono su Rolando. Usa SOLO queste informazioni per rispondere. "
                "Se non puoi rispondere basandoti su di esse, rispondi 'Non lo so'.\n\n"
                f"{reduced_context}\n\n"
                f"Domanda: {prompt}"
            )
            
            if count_tokens(context) > 4000:
                st.error("Il contesto è troppo lungo. Riduci la dimensione del file.")
            else:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": context}]
                )
                assistant_response = response.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
