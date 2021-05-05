import streamlit as st
import pickle
import pandas as pd 
import csv

if st.button('Pune'):
    filename='Pune.csv'
    df = pd.read_csv(filename, header=None)
    df_t = df.T
    st.write(df_t)


if st.button('Chennai'):
    filename='Chennai.csv'
    df = pd.read_csv(filename, header=None)
    df_t = df.T
    st.write(df_t)