import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import pickle

# Create mock dataset
np.random.seed(42)

# Generate 500 realistic samples
n_samples = 500
data = pd.DataFrame({
    'location': np.random.randint(0, 10, size=n_samples),        # e.g., 10 locations
    'rainfall': np.random.uniform(0, 40, size=n_samples),        # rainfall in mm
    'soil_type': np.random.randint(0, 3, size=n_samples),        # assume 3 types
    'growth_stage': np.random.randint(1, 4, size=n_samples)      # stages 1 to 3
})

# Automatically generate flood_risk based on rainfall
def assign_risk(rainfall):
    if rainfall < 10:
        return 0  # Low
    elif rainfall < 25:
        return 1  # Moderate
    else:
        return 2  # High

data['flood_risk'] = data['rainfall'].apply(assign_risk)

# Automatically generate yield_loss with some randomness, based on flood_risk
def assign_loss(risk):
    base = {0: 5, 1: 15, 2: 35}
    noise = np.random.normal(0, 2)
    return max(0, base[risk] + noise)  # ensure yield loss is non-negative

data['yield_loss'] = data['flood_risk'].apply(assign_loss)

# Prepare features and targets
X = data[['location', 'rainfall', 'soil_type', 'growth_stage']]
y_risk = data['flood_risk']
y_loss = data['yield_loss']

# Train models
risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
risk_model.fit(X, y_risk)

loss_model = RandomForestRegressor(n_estimators=100, random_state=42)
loss_model.fit(X, y_loss)

# Save models
with open('flood_risk_model.pkl', 'wb') as f:
    pickle.dump(risk_model, f)

with open('yield_loss_model.pkl', 'wb') as f:
    pickle.dump(loss_model, f)

print("✅ Models trained and saved successfully.")
