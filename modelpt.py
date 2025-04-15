import os
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def build_lstm_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.GRU(128, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.GRU(64, return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1)  # Output layer
    ])
    model.compile(optimizer='adam', loss=MeanSquaredError())
    return model


def preprocess_data(data, time_steps):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps), :-1])
        y.append(data[i + time_steps, -1])
    return np.array(X), np.array(y)


def train_and_save_model(data, time_steps, model_path):
    # Normalize the data
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Preprocess data into sequences
    X, y = preprocess_data(data_scaled, time_steps)

    # Build and train the model
    model = build_lstm_model((time_steps, X.shape[2]))
    model.fit(X, y, epochs=50, batch_size=64, verbose=1)

    # Save the model and scaler
    model.save(model_path)
    np.save('scaler.npy', scaler.scale_)
    np.save('scaler_min.npy', scaler.min_)


def load_trained_model(model_path):
    model = load_model(model_path, compile=False)
    model.compile(optimizer='adam', loss=MeanSquaredError())
    return model

def predict(model, scaler, input_sequence):
    # Normalize the input sequence
    input_scaled = (input_sequence - scaler.min_) / scaler.scale_
    input_scaled = np.expand_dims(input_scaled, axis=0)  # Add batch dimension

    # Make prediction
    prediction_scaled = model.predict(input_scaled)
    # Inverse transform the prediction
    prediction = prediction_scaled * scaler.scale_[-1] + scaler.min_[-1]
    return prediction

