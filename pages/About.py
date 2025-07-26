import streamlit as st

st.set_page_config(page_title="About | CineHeist",page_icon="Images/favicon.ico", layout="wide")
st.title("About This App")

st.markdown("""
    This Movie Recommendation System is a multipage app built with **Streamlit**. 
    It uses **TF-IDF Vectorization** and **Cosine Similarity** to recommend movies based on user input.
    
    ### Features
    - Plot-based movie recommendations.
    - Movie title based movie recommendations.
    - Dataset exploration.
    - Links to IMDb for detailed movie information.

    ### Credits
    - Built with ❤️ using Python and Streamlit.

    ### Links
    - [GitHub Repository](https://github.com/shivakumarsouta/cineheist)
""")