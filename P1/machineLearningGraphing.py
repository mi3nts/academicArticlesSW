import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.feature_selection import RFE


loaded_data = joblib.load('train_test_split_data.pkl')

# Access the individual variables
X_train = loaded_data['X_train']
X_test  = loaded_data['X_test']
y_train = loaded_data['y_train']
y_test  = loaded_data['y_test']

print("Data loaded successfully!")

model = joblib.load('best_random_forest_model.joblib')
print("Model loaded successfully!")

# Calculate correlation matrix
# correlation_matrix = df.corr()
# sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
# plt.show()

# Check correlation with target variable
# target_correlation = correlation_matrix['target_column'].abs().sort_values(ascending=False)
# print("Features correlated with target:\n", target_correlation)


# Get feature importances
feature_importances = pd.Series(model.feature_importances_, index=X_train.columns)
feature_importances = feature_importances.sort_values(ascending=False)
print("Feature Importances:\n", feature_importances)

# Plot feature importances
feature_importances.plot(kind='bar')
plt.title('Feature Importance')
plt.show()


