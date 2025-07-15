import streamlit as st
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from processing.text_processor import EnhancedDrugTextProcessor

st.title("TF-IDF Vectorizer Trainer for Generic Names")
st.write("Upload an Excel file with a column of generic names. This app will train a TF-IDF vectorizer and let you download the model as a .pkl file.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success(f"Loaded file: {uploaded_file.name} ({len(df)} rows)")
    st.write("**Preview:**")
    st.dataframe(df.head())

    # Let user select the column
    col_options = list(df.columns)
    generic_col = st.selectbox("Select the column with generic names:", col_options)

    if st.button("Train TF-IDF Vectorizer"):
        names = df[generic_col].dropna().astype(str).tolist()
        processor = EnhancedDrugTextProcessor()
        cleaned_names = []
        progress = st.progress(0)
        for i, name in enumerate(names):
            drugs = processor.extract_combination_drugs(name)
            cleaned_names.extend(drugs)
            if i % max(1, len(names)//100) == 0:
                progress.progress(i/len(names))
        cleaned_names = list(set([n for n in cleaned_names if n.strip()]))
        progress.progress(1.0)
        st.success(f"Processed {len(cleaned_names)} unique cleaned names.")

        # Train vectorizer
        st.info("Training TF-IDF vectorizer...")
        vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.9,
            stop_words=None
        )
        vectorizer.fit(cleaned_names)
        st.success("TF-IDF vectorizer trained!")

        # Save to pickle
        pkl_bytes = pickle.dumps(vectorizer)
        st.download_button(
            label="Download Trained TF-IDF Model (.pkl)",
            data=pkl_bytes,
            file_name="tfidf_vectorizer.pkl",
            mime="application/octet-stream"
        ) 