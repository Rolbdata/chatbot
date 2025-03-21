# import streamlit as st
# from openai import OpenAI


# # Carica le informazioni dal file .txt
# def load_personal_info(file_path="/workspaces/chatbot/informazioni_rolando.txt"):
#     with open(file_path, "r") as file:
#         info = file.read()
#     return info


# # Mostra il titolo e la descrizione
# st.title("Chatbot")
# st.write(
#     "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
#     "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
#     "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
# )

# # Chiedi all'utente la chiave API di OpenAI
# openai_api_key = st.text_input("OpenAI API Key", type="password")
# if not openai_api_key:
#     st.info("Please add your OpenAI API key to continue.", icon="ℹ️")
# else:
#     # Crea un client OpenAI
#     client = OpenAI(api_key=openai_api_key)
    
#     # Carica le informazioni personali dal file
#     personal_info = load_personal_info()
    
#     # Crea una variabile di stato della sessione per memorizzare i messaggi della chat
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
    
#     # Visualizza i messaggi della chat esistenti
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Crea un campo di input per permettere all'utente di immettere un messaggio
#     if prompt := st.chat_input("What is up?"):
#         # Memorizza e visualizza il prompt corrente
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Se l'utente chiede informazioni su Rolando, fornisci le informazioni dal file
#         if "rolando" in prompt.lower():
#             assistant_response = f"Here is the information about Rolando: \n\n{personal_info}"
#         else:
#             # Genera una risposta utilizzando l'API di OpenAI
#             stream = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": m["role"], "content": m["content"]}
#                     for m in st.session_state.messages
#                 ],
#                 stream=True,
#             )
#             # Stream la risposta alla chat
#             with st.chat_message("assistant"):
#                 assistant_response = st.write_stream(stream)
        
#         # Memorizza e visualizza la risposta dell'assistente
#         st.session_state.messages.append({"role": "assistant", "content": assistant_response})



import streamlit as st
from openai import OpenAI
import tiktoken  # Per contare i token

# Funzione per contare i token di un testo (aiuta a mantenere il limite massimo)
def count_tokens(text, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Carica le informazioni dal file .txt
def load_personal_info(file_path="informazioni_rolando.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        info = file.read()
    return info

# Mostra il titolo
st.title("Chatbot di Rolando")

# Input per la chiave API
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Inserisci la tua API Key di OpenAI per continuare.", icon="ℹ️")
else:
    # Crea un client OpenAI
    client = OpenAI(api_key=openai_api_key)

    # Carica le informazioni personali dal file
    personal_info = load_personal_info()

    # Inizializza la cronologia della chat se non esiste
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizza i messaggi precedenti
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dell'utente
    if prompt := st.chat_input("Fai una domanda su Rolando o altro..."):
        # Aggiungi il messaggio dell'utente alla cronologia
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Crea il contesto per OpenAI
        context = (
            "Le seguenti informazioni sono su Rolando. Usa queste informazioni per rispondere alle domande. "
            "Se la domanda non riguarda Rolando, rispondi normalmente. \n\n"
            f"{personal_info}\n\n"
            "Domanda: " + prompt
        )

        # Assicuriamoci di non superare il limite di token
        max_tokens = 50000  # Manteniamo un buffer per la risposta
        token_count = count_tokens(context)

        if token_count > max_tokens:
            st.error("Il contesto è troppo lungo. Riduci la dimensione del file di testo.")
        else:
            # Limitiamo il numero di messaggi salvati per evitare errori di token
            while count_tokens(str(st.session_state.messages)) > 120000:
                st.session_state.messages.pop(0)  # Rimuove i messaggi più vecchi

            # Genera la risposta
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": context}]
            )

            # Otteniamo la risposta e la mostriamo
            assistant_response = response.choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

            # Salviamo il messaggio dell'assistente
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
