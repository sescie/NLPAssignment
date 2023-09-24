# -*- coding: utf-8 -*-
"""assignment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17alt6j9afQfNo1mNFS_BSn58wjDC5OuC

### 1. Dataset

Samuel Singende
R204440W
"""

file = open("/content/drive/MyDrive/shona_text.txt","r")
shona_text = file.read()

from google.colab import drive
drive.mount('/content/drive')

shona_text

len(shona_text)

data = shona_text.lower()
print(data[500:550])

import re
data = re.sub('https://\S+', '', data)
data = re.sub('www\S+', '', data)

#REMOVING PUNCTUATIONS


punc = '''!()-[]{};:'"\,‘’“”<>./?@#$%^&*+_~→'''

for word in data:
  if word in punc:
    data = data.replace(word, "")

print(data)

# Removing the  words with digits

pattern = r'[0-9]'
data = re.sub(pattern, '', data)

print(data)

"""### 2. Vocabulary"""

from keras.preprocessing.text import Tokenizer

# Tokenize and preprocess
tokenizer = Tokenizer()
tokenizer.fit_on_texts([data])
total_words = len(tokenizer.word_index) + 1

"""### 3. Word Embeddings"""

from gensim.models import Word2Vec

# Train word2vec model with gensim
sentences = [sentence.split() for sentence in shona_text.split('.')]
model_gensim = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
model_gensim.save("word2vec.model")

"""### 4. RNN Models"""

from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional

model1 = Sequential()
model1.add(Embedding(total_words, 100, input_length=5))
model1.add(Bidirectional(LSTM(150, return_sequences=True)))
model1.add(Dropout(0.2))
model1.add(LSTM(100))
model1.add(Dense(total_words, activation='softmax'))

model1.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

"""##### With its own embedding layer:

##### With pre-trained embeddings:
"""

# Load the word2vec model
import numpy as np
model_gensim = Word2Vec.load("word2vec.model")
embedding_matrix = np.zeros((total_words, 100))
for word, i in tokenizer.word_index.items():
    try:
        embedding_vector = model_gensim.wv[word]
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
    except KeyError:

        pass


model2 = Sequential()
model2.add(Embedding(total_words, 100, weights=[embedding_matrix], input_length=5, trainable=False))
model2.add(Bidirectional(LSTM(150, return_sequences=True)))
model2.add(Dropout(0.2))
model2.add(LSTM(100))
model2.add(Dense(total_words, activation='softmax'))

model2.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

"""### 5. Training & Testing"""

import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

input_sequences = []
for line in shona_text.split('.'):
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

input_sequences = np.array(pad_sequences(input_sequences, maxlen=6, padding='pre'))
X, y = input_sequences[:, :-1], input_sequences[:, -1]
y = keras.utils.to_categorical(y, num_classes=total_words)

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.4, random_state=42)

# Training Model 1
history1 = model1.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, verbose=1)

# Training Model 2
history2 = model2.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, verbose=1)

"""### Model Evaluation"""

val_loss_model1 = history1.history['val_loss'][-1]
val_loss_model2 = history2.history['val_loss'][-1]

print(f"Validation Loss for Model 1: {val_loss_model1}")
print(f"Validation Loss for Model 2: {val_loss_model2}")

if val_loss_model1 < val_loss_model2:
    best_model = model1
    best_model_name = "best_model1.h5"
else:
    best_model = model2
    best_model_name = "best_model2.h5"

best_model.save(best_model_name)
print(f"Saved the best model as {best_model_name}")

params_model1 = model1.count_params()
params_model2 = model2.count_params()

print(f"Model 1 has {params_model1} parameters.")
print(f"Model 2 has {params_model2} parameters.")

from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the previously saved model
model = load_model('best_model1.h5')

def predict_next_words(model, tokenizer, text, num_words=1):
    """
    Predict the next set of words using the trained model.

    Args:
    - model (keras.Model): The trained model.
    - tokenizer (Tokenizer): The tokenizer object used for preprocessing.
    - text (str): The input text.
    - num_words (int): The number of words to predict.

    Returns:
    - str: The predicted words.
    """
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


# Prompt the user for input
user_input = input("Please type five words in Shona: ")

# Predict the next words
predicted_words = predict_next_words(model, tokenizer, user_input, num_words=3)
print(f"The next words might be: {predicted_words}")

