import streamlit as st
import pandas as pd
import numpy as np

st.title("Dashboard Uji Beban RAM")
st.write("Meng-generate 1.000.000 titik data acak...")
data = pd.DataFrame(np.random.randn(50000, 20), columns=[f"Col {i}" for i in range(20)])
st.line_chart(data["Col 1"].head(1000))
