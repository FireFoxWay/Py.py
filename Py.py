import streamlit as st
 #streamlit run "/Users/karthikeyakoduru/Desktop/Py.py"

st.set_page_config(page_title="My App", page_icon="✨")

st.title("Hello 👋☺️")
st.caption("Enter details below and click **Run**")

# Inputs (replace with what your code needs)
name = st.text_input("Name", value="")
age = st.number_input("Age", min_value=0, step=1, value=0)
salutation = st.selectbox("Sir/Madam", options=["sir", "madam"], index=0)

a = st.number_input("a", value=0, step=1)
b = st.number_input("b", value=0, step=1)

if  st.button("Run"):
    st.success(f"Hello {'little ' if age < 18 else ''} {salutation} {name}, Good morning!")
    st.write("**Results**")
    st.write("a != b:", a != b)
    st.write("a == b:", a == b)
