import joblib
import numpy as np
import pandas as pd

# 1. Load Model
try:
    model = joblib.load('model.pkl')
    print("✅ Model Loaded successfully!")
except:
    print("❌ Error: model.pkl not found.")
    exit()

print("\n--- 🕵️ HUNTING FOR CLASS LABELS (0, 1, 2) ---")
print("Testing various patient profiles to see what triggers each number...\n")

# 2. Define 3 Archetypes to test
# We use lists of profiles to try and hit every class
test_profiles = [
    # PROFILE A: The "Healthy" Person (Young, good sleep, normal weight)
    [1, 25, 8.0, 9, 60, 3, 0, 70, 120, 80, 8000],
    
    # PROFILE B: The "Classic Insomniac" (Older, Overweight, High Stress, Low Sleep)
    # *Note: In this dataset, Insomnia is often linked to Overweight (BMI=1)*
    [1, 50, 5.0, 4, 30, 8, 1, 75, 130, 85, 3000],

    # PROFILE C: The "Classic Apnea" (Older, Obese, High BP, Snoring/High HR)
    [1, 55, 6.0, 5, 30, 5, 2, 95, 145, 95, 2000],
    
    # PROFILE D: Extreme Apnea (Very Obese, Very High BP)
    [1, 60, 5.0, 3, 10, 8, 2, 98, 150, 100, 1000],
    
    # PROFILE E: High Stress Normal Weight (Often predicted Normal in this dataset, but let's try)
    [1, 30, 5.0, 4, 40, 9, 0, 80, 125, 82, 4000]
]

labels_found = {}

# 3. Run Predictions
for i, profile in enumerate(test_profiles):
    # Reshape for model
    data = np.array([profile])
    pred = model.predict(data)[0]
    
    # Store the first example we find for each number
    if pred not in labels_found:
        labels_found[pred] = profile
        
        # Determine likely label based on medical logic
        likely_label = "Unknown"
        bmi = profile[6]
        bp_sys = profile[8]
        stress = profile[5]
        
        if bmi == 2 and bp_sys > 135:
            likely_label = "Likely Sleep Apnea (Obese + High BP)"
        elif bmi == 0 and stress < 5:
            likely_label = "Likely Normal (Healthy)"
        elif stress > 6 and profile[2] < 6:
            likely_label = "Likely Insomnia (High Stress + Low Sleep)"
            
        print(f"👉 Model Output {pred} triggered by: {likely_label}")
        print(f"   Stats: BMI={bmi}, BP={bp_sys}, Stress={stress}, Sleep={profile[2]}h\n")

# 4. Summary for your App.py
print("-" * 30)
print("🏁 CONCLUSION FOR APP.PY")
print("-" * 30)

found_classes = sorted(labels_found.keys())

if 0 in found_classes and 1 in found_classes and 2 in found_classes:
    print("✅ Great! We found examples for 0, 1, and 2.")
    print("Compare the descriptions above to your App.py code:")
    print("If Output 1 was 'Obese + High BP', then 1 = Apnea.")
    print("If Output 2 was 'High Stress', then 2 = Insomnia.")
else:
    print(f"⚠️ Warning: We only triggered these classes: {found_classes}")
    print("Your model might be very biased and rarely predicts the missing class.")