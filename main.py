import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



st.set_page_config(page_title="AI Resume Reviewer", page_icon="📝", layout="centered")
st.title("AI Resume Reader")
st.markdown("Upload your resume, and receive feedback from an AI-powered machine!")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload your Resume in PDF or TXT format", type=["pdf","txt"]) 
job_role = st.text_input("Enter the job role that you are looking for (optional)")

review = st.button("Review")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()+"\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

    return uploaded_file.read().decode("utf-8")
if review and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content")
            st.stop()

        prompt=f"""Please take a look at this resume and provide constructive feedback. The first thing I 
                want you to do is look at the format. Make sure that there are no inconsistencies within the formatting,
                and this includes some sentences having periods while others do not, varying fonts, varying font sizes,
                make sure the document is black and white and has no images. Next, I want you to look at the content of 
                the resume. This includes seeing if everything is in the right order, with most recent experiences being at
                the top, make sure each bullet starts with an action verb and is in the past tense if the experience ended,
                and the present tense if it is ongoing. Finally, I want you to give them industry specific advice, improvements
                for {job_role if job_role else'general job applications'}

                Resume Content:
                {file_content}

                Please provide the feedback in a clear, structured format and highlight specific things you see in the resume
                and any recommendations you may have."""

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(

            model = "gpt-4o-mini",
            messages=[
                {"role":"system", "content": "You are an expert resume reviewer with years of expereince in HR and recruiting"},
                {"role":"user","content":prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
        st.markdown("||| Analysis Results |||")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occured:{str(e)}")
    