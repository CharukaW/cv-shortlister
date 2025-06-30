
import streamlit as st
import fitz  # PyMuPDF
import docx2txt
import pandas as pd
import re
from io import BytesIO

# Helper: extract text
def extract_text(file):
    text = ""
    if file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    elif file.name.lower().endswith((".docx", ".doc")):
        text = docx2txt.process(file)
    return text

# Helper: extract grade
def extract_grade(text, subject):
    pat = rf"{subject}.{{0,20}}([A-E1-9])"
    m = re.search(pat, text, re.IGNORECASE)
    return m.group(1).upper() if m else ""

def main():
    st.title("✈️ CV Shortlister – Airport Service Assistant")

    criteria = st.sidebar.header("Set Shortlisting Criteria")
    min_ol = st.sidebar.selectbox("Min O/L English", ["A","B","C","D"], index=2)
    min_al = st.sidebar.selectbox("Min A/L General English", ["A","B","C","D"], index=2)
    exp_req = st.sidebar.checkbox("Require ≥ 6 months customer service experience")

    uploaded = st.file_uploader("Upload CVs (PDF or DOCX)", accept_multiple_files=True)
    if not uploaded:
        st.info("Upload one or more CV files to process.")
        return

    data = []
    for f in uploaded:
        text = extract_text(f)
        ol = extract_grade(text, "English")
        al = extract_grade(text, "General English")
        exp = "Experience" in text and len(re.findall(r"\b(years|months)\b", text, re.IGNORECASE)) > 0
        skills = ", ".join(re.findall(r"(Customer|Communication|Interpersonal|Teamwork)", text, re.IGNORECASE))
        name = f.name.split(".")[0]

        shortlisted = (
            (ol and ol <= min_ol) and
            (al and al <= min_al) and
            (not exp_req or exp)
        )
        data.append({
            "Name": name,
            "O/L English": ol or "N/A",
            "A/L General English": al or "N/A",
            "Customer Exp": "Yes" if exp else "No",
            "Skills": skills,
            "Shortlisted": "✅" if shortlisted else "❌"
        })

    df = pd.DataFrame(data)
    st.dataframe(df)

    to_excel = st.button("📥 Download Results as Excel")
    if to_excel:
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(label="Download Excel", data=buffer, file_name="cv_shortlist.xlsx", mime="application/vnd.ms-excel")

if __name__ == "__main__":
    main()
