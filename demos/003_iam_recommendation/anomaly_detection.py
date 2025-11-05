import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

# Load synthetic dataset
df = pd.read_csv('access_requests.csv')

# Encode categorical features
df_encoded = pd.get_dummies(df[['Role', 'SystemAccessRequested', 'Location']])
df_encoded['Hour'] = pd.to_datetime(df['Timestamp']).dt.hour

# Train Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df['AnomalyScore'] = model.fit_predict(df_encoded)

# Flag anomalies
anomalies = df[df['AnomalyScore'] == -1]
print("Detected anomalies:")
print(anomalies)

# Visualization
plt.figure(figsize=(8,5))
plt.hist(df['AnomalyScore'])
plt.title('Anomaly Detection Results')
plt.show()
