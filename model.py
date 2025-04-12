import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError

def load_trained_model():
    # Compile manually with the correct loss object
    model = load_model("fast_model.keras", compile=False)
    model.compile(optimizer='adam', loss=MeanSquaredError())
    return model

# Prepare feature vector and scale
def preprocess_input(features):
    # Fake scaler range for now (replace with actual MinMaxScaler if needed)
    scaler = MinMaxScaler()
    dummy = np.array([
        [0, 100, 250, 100, 1, 0, 100],  # min
        [150, 100, 310, 0, 5, 200, 200]  # max
    ])
    scaler.fit(dummy)

    features_scaled = scaler.transform([features])
    return np.reshape(features_scaled, (1, 1, len(features)))  # (batch, time, features)

# Predict from real-time data
def predict_congestion(model, features):
    X = preprocess_input(features)
    return float(model.predict(X, verbose=0)[0][0])

def build_fast_model(input_shape=(5, 7)):
    model = tf.keras.Sequential([
        tf.keras.layers.GRU(128, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.Dropout(0.3),

        tf.keras.layers.GRU(64, return_sequences=True),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.GRU(32),
        tf.keras.layers.Dense(16, activation='relu'),

        tf.keras.layers.Dense(1)  # Output layer
    ])
    model.compile(optimizer='adam', loss=MeanSquaredError())
    return model

def train_and_save():
    time_steps = 5
    features = 7
    samples = 1000

    # Create sequential time-series dummy data
    X = np.random.rand(samples, time_steps, features)
    y = np.random.rand(samples, 1)

    model = build_fast_model(input_shape=(time_steps, features))
    model.fit(X, y, epochs=100, batch_size=64, verbose=1)

    model.save("fast_model.keras")
    print("✅ Model trained and saved as fast_model.keras")

if __name__ == "__main__":
    train_and_save()
