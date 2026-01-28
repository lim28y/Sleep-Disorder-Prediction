import joblib

# Load Model
try:
    model = joblib.load('model.pkl')
    print("✅ Model Loaded!")
except:
    print("❌ Error: model.pkl not found")
    exit()

# 1. Check Expected Number of Features
try:
    # Works for Sklearn models (RandomForest, DecisionTree, etc.)
    n_features = model.n_features_in_
    print(f"\n🔢 The model expects exactly {n_features} columns of data.")
except:
    print("\n⚠️ Could not detect feature count (might be a pipeline).")

# 2. Check Class Names (What 0, 1, 2 actually mean)
try:
    classes = model.classes_
    print(f"🏷️ The model knows these classes: {classes}")
    print("   (Index 0 = First, Index 1 = Second, etc.)")
except:
    print("⚠️ Could not detect class names.")

# 3. Check for Scaler/Preprocessing
print(f"\nType of object loaded: {type(model)}")