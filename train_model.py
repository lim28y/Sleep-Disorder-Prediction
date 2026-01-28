import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load Data
try:
    df = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: csv file not found.")
    exit()

# 2. Cleaning
df['BMI Category'] = df['BMI Category'].replace('Normal Weight', 'Normal')
df['Sleep Disorder'] = df['Sleep Disorder'].fillna('None')
df[['Systolic', 'Diastolic']] = df['Blood Pressure'].str.split('/', expand=True).astype(int)

# 3. Mappings
df['Sleep Disorder'] = df['Sleep Disorder'].map({'None': 0, 'Insomnia': 1, 'Sleep Apnea': 2})
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
df['BMI Category'] = df['BMI Category'].map({'Normal': 0, 'Overweight': 1, 'Obese': 2})

# 4. SELECT FEATURES 
feature_cols = [
    'Gender', 
    'Age', 
    'Sleep Duration', 
    'Quality of Sleep', 
    'Physical Activity Level', 
    'Stress Level', 
    'BMI Category', 
    'Heart Rate', 
    'Systolic', 
    'Diastolic',
    'Daily Steps'  
]

X = df[feature_cols]
y = df['Sleep Disorder']

# 5. Train
print("Training Model ...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train.values, y_train)

# 6. Save
joblib.dump(model, 'model.pkl')
print("Success")