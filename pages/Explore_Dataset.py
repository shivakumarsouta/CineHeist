import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dataset | CineHeist",page_icon="Images/favicon.ico", layout="wide")
st.title("Explore the Dataset")

@st.cache_data
def load_data():
    return pd.read_csv("dataset.csv")

movies_df = load_data()

st.write("### Dataset Overview")
st.dataframe(movies_df.head(10))

st.write("### Dataset Statistics")
st.write(movies_df.describe())