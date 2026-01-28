import joblib
import numpy as np

# 1. Load the trained model
try:
    model = joblib.load('model.pkl')
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print("❌ Error: 'model.pkl' not found. Run your training script first.")
    exit()

# 2. Define the test data (based on your input)
# Order: [Gender, Age, Duration, Quality, Activity, Stress, BMI, HR, BP_Sys, BP_Dia, Steps]
# Gender: Male=1 (assuming your encoding), BMI: Obese=2 (assuming your encoding)
test_data = np.array([[
    1,      # Gender: Male
    30,     # Age
    4.0,    # Duration (Low)
    4,      # Quality (Low)
    30,     # Activity
    8,      # Stress (High -> strong Insomnia indicator)
    2,      # BMI: CHANGE TO 0 (Normal) instead of 2 (Obese)
    75,     # Heart Rate: CHANGE TO 75 (Lower)
    120,    # BP Systolic: CHANGE TO 120 (Normal)
    80,     # BP Diastolic: CHANGE TO 80 (Normal)
    3000    # Steps
]])

# 3. Make a prediction
try:
    prediction = model.predict(test_data)[0]
    print(f"🔢 RAW PREDICTION NUMBER: {prediction}")
    print(f"\n🔍 Input Data: {test_data}")
    print(f"🧠 Raw Prediction Output: {prediction}")
    print(f"🏷️ Model Classes: {model.classes_}")

    # 4. Interpret the result (Adjust these based on your specific training labels)
    # Common Kaggle dataset mapping: 0=None, 1=Insomnia, 2=Sleep Apnea
    if prediction == 1 or prediction == "Insomnia":
        print("✅ Result: Insomnia Detected (Model is working!)")
    elif prediction == 2 or prediction == "Sleep Apnea":
        print("⚠️ Result: Sleep Apnea Detected")
    else:
        print("ℹ️ Result: Normal / No Disorder")

except Exception as e:
    print(f"❌ Prediction Error: {e}")

    