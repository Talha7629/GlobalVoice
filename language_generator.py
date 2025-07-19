import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF  # For PDF export

# Load environment variables from .env
load_dotenv()

# Set up Gemini model using your API key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Define the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
    ("human", "{input}"),
])

# Output parser
output_parser = StrOutputParser()

# Combine the prompt, model, and parser into a chain
chain = prompt | llm | output_parser

# Streamlit page setup
st.set_page_config(page_title="🌍 GlobalVoice", page_icon="🌍")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_history" not in st.session_state:
    st.session_state.selected_history = None
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

# Sidebar branding
st.sidebar.title("🌍 GlobalVoice")
st.sidebar.markdown("Your AI-powered **Language Translator**")
st.sidebar.markdown("---")

# New Chat Button (resets input only)
if st.sidebar.button("➕ New Chat"):
    st.session_state.current_text = ""
    st.session_state.selected_history = None
    st.rerun()

# Full language list
languages = sorted([
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Assamese", "Azerbaijani",
    "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Burmese",
    "Catalan", "Cebuano", "Chinese (Simplified)", "Chinese (Traditional)", "Corsican", "Croatian", "Czech",
    "Danish", "Dhivehi", "Dutch", 
    "English", "Esperanto", "Estonian",
    "Filipino", "Finnish", "French", "Frisian", "Galician", "Georgian", "German", "Greek", "Gujarati",
    "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian",
    "Icelandic", "Igbo", "Indonesian", "Irish", "Italian",
    "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Kinyarwanda", "Korean", "Kurdish (Kurmanji)", "Kyrgyz",
    "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish",
    "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian", "Myanmar (Burmese)",
    "Nepali", "Norwegian",
    "Odia (Oriya)", "Pashto", "Persian", "Polish", "Portuguese", "Punjabi",
    "Romanian", "Russian", "Samoan", "Sanskrit", "Scots Gaelic", "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala",
    "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish",
    "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Turkish", "Turkmen", "Twi",
    "Ukrainian", "Urdu", "Uyghur", "Uzbek",
    "Vietnamese", "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"
])

# Sidebar language selection
st.sidebar.subheader("Choose Target Language")
selected_language = st.sidebar.selectbox("Translate to:", languages)

# Sidebar - Translation History (clickable)
st.sidebar.subheader("📜 Translation History")
if st.session_state.history:
    for idx, (inp, lang, out) in enumerate(reversed(st.session_state.history), 1):
        if st.sidebar.button(f"{idx}. {inp[:20]} → {lang}", key=f"history_{idx}"):
            st.session_state.selected_history = (inp, lang, out)
            st.session_state.current_text = inp
            st.rerun()
else:
    st.sidebar.write("No translations yet.")

# Clear history button
if st.session_state.history:
    if st.sidebar.button("🗑 Clear History"):
        st.session_state.history.clear()
        st.session_state.selected_history = None
        st.session_state.current_text = ""
        st.rerun()

# Export buttons (TXT and PDF)
if st.session_state.history:
    # TXT Export
    history_text = "\n\n".join(
        [f"Input: {inp}\nLanguage: {lang}\nOutput: {out}" for inp, lang, out in st.session_state.history]
    )
    st.sidebar.download_button(
        label="⬇️ Export History (TXT)",
        data=history_text.encode("utf-8"),
        file_name="globalvoice_history.txt",
        mime="text/plain"
    )

    # PDF Export (Fixed for bytearray issue)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for inp, lang, out in st.session_state.history:
        pdf.multi_cell(0, 10, f"Input: {inp}\nLanguage: {lang}\nOutput: {out}\n\n")

    # Convert to bytes (no encode needed)
    pdf_output = bytes(pdf.output(dest='S'))

    st.sidebar.download_button(
        label="⬇️ Export History (PDF)",
        data=pdf_output,
        file_name="globalvoice_history.pdf",
        mime="application/pdf"
    )

# Main title
st.title("🌍 GlobalVoice - AI Translator")

# Pre-fill input (if user clicked history or starting new chat)
input_text = st.text_area("Enter text in any language:", value=st.session_state.current_text, height=120)

# Translate button
if st.button("Translate"):
    if input_text.strip() and selected_language:
        response = chain.invoke({
            "input_language": selected_language,
            "output_language": selected_language,
            "input": input_text
        })

        # Display translation
        st.markdown(f"### 🌐 Translated ({selected_language}):")
        st.write(response)

        # Save to history
        st.session_state.history.append((input_text, selected_language, response))
        st.session_state.current_text = input_text
    else:
        st.warning("Please enter text to translate.")

# Footer
st.markdown("---")
st.caption("Powered by Google Gemini & LangChain")
