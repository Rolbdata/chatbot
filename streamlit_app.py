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
import tiktoken

# Imposta la tua API key (occhio a non condividerla pubblicamente!)
OPENAI_API_KEY = "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"  # Sostituisci con la tua vera API Key

# Carica le informazioni dal file
def load_personal_info(file_path="informazioni_rolando.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Conta i token di un testo
def count_tokens(text, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Inizializza elementi nella sessione
if "messages" not in st.session_state:
    st.session_state.messages = []
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

# Carica info e client
personal_info = load_personal_info()
client = OpenAI(api_key=OPENAI_API_KEY)

# Titolo
st.title("Chatbot di Rolando")
st.markdown("🤖 Puoi fare **fino a 3 domande** riguardo **Rolando**.")

# Mostra chat precedente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utente
if st.session_state.questions_asked >= 3:
    st.warning("Hai raggiunto il limite massimo di 3 domande. Grazie per aver usato il chatbot!", icon="⚠️")
else:
    if prompt := st.chat_input("Fai una domanda su Rolando..."):
        if "rolando" not in prompt.lower():
            st.error("Puoi fare solo domande relative a **Rolando**.")
        else:
            st.session_state.questions_asked += 1
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            context = (
                "Le seguenti informazioni sono su Rolando. Usa SOLO queste informazioni per rispondere. "
                "Se non puoi rispondere basandoti su di esse, rispondi 'Non lo so'.\n\n"
                f"{personal_info}\n\n"
                f"Domanda: {prompt}"
            )

            if count_tokens(context) > 50000:
                st.error("Il contesto è troppo lungo. Riduci la dimensione del file.")
            else:
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "system", "content": context}]
                )
                assistant_response = response.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
