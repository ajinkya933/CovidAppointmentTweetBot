import streamlit as st
import pickle
import pandas as pd 
if st.button('Pune'):

    filename='Pune.data'
    infile = open(filename,'rb')
    new_dict = pickle.load(infile)
    infile.close()

    # print(new_dict)

    st.write('Pune availability: %s' % new_dict)


if st.button('Chennai'):

    filename='Chennai.data'
    infile = open(filename,'rb')
    new_dict = pickle.load(infile)
    infile.close()

    # print(new_dict)
    df = pd.DataFrame(list(new_dict),columns = ['Products'])


    st.write(df)
