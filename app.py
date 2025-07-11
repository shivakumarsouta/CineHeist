import streamlit as st

st.set_page_config(page_title="Home | CineHeist",page_icon="Images/favicon.ico", layout="wide")

st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1>Welcome to the CineHeist</h1>
            <h3>Your movie matchmaker</h3>
    </div>
""", unsafe_allow_html=True)

st.divider()

st.write("#### Navigate to different pages using the sidebar.")