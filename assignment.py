# -*- coding: utf-8 -*-
"""assignment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17alt6j9afQfNo1mNFS_BSn58wjDC5OuC

### 1. Dataset

Samuel Singende
R204440W
"""



#Imports
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import *
import numpy as np
import pickle

# Load the model and tokenizer
model = load_model('best_model2.h5',compile=False)
tokenizer = pickle.load(open('tokenizer1.pkl', 'rb'))




def predict_next_words(model, tokenizer, text, num_words=1):

    for _ in range(num_words):
        # Tokenize and pad the text
        sequence = tokenizer.texts_to_sequences([text])[0]
        sequence = pad_sequences([sequence], maxlen=5, padding='pre')

        # Predict the next word
        predicted_probs = model.predict(sequence, verbose=0)
        predicted = np.argmax(predicted_probs, axis=-1)

        # Convert the predicted word index to a word
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break

        # Append the predicted word to the text
        text += " " + output_word

    return ' '.join(text.split(' ')[-num_words:])



def main():

    
    

    html_temp = """
    <body style="background-color:none;">
    <div style="padding:10px">
    <h2 style="color:white;text-align:center;">Shona Prediction App</h2>
    </div>
    </body>
    """
    st.markdown(html_temp, unsafe_allow_html=True)

    st.title("Fembera mazwi anotevera ........")
    user_input = st.text_input("Nyora mazwi mashanu anovamba mutsara muchiShona: ")
    lst = list(user_input.split())

            

    if st.button("Fembera"):
        
        if (user_input is not None and len(lst)==5):
        
            result =  predict_next_words(model, tokenizer, user_input, num_words=1)
            st.success(result)
        
        else:
            st.write("Tangazve: Nyora mazwi mashanu anovamba mutsara muchiShona")
        
        


if __name__ == '__main__':
    main()
