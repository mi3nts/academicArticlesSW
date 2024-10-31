

import pandas as pd
import glob
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import randint
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import joblib

import numpy as np

BAMWithCorrected        = pd.read_pickle('BAMWithCorrected.pkl')


# Check for NaNs in the entire DataFrame
nan_rows = BAMWithCorrected[BAMWithCorrected.isna().any(axis=1)]

# # Display rows with NaN values
# print("Rows with NaN values:")
# print(nan_rows)

BAMWithCorrectedCleaned = BAMWithCorrected.dropna()
BAMWithCorrectedCleaned = BAMWithCorrectedCleaned[BAMWithCorrectedCleaned['pm2_5BAM'] <= 100]


BAMWithCorrectedCleaned.to_csv('BAMWithCorrectedCleaned.csv')

BAMWithCorrectedCleaned.to_pickle('BAMWithCorrectedCleaned.pkl') 


X_selected = BAMWithCorrectedCleaned[['temperature', 'pressure', 'humidity', 'dewPoint',
                                       'pc0_1HC', 'pc0_3HC', 'pc0_5HC', 
                                       'pc1_0HC', 'pc2_5HC', 'pc5_0HC', 
                                       'pc10_0HC','pm0_1HC', 'pm0_3HC',
                                       'pm0_5HC', 'pm1_0HC', 'pm2_5HC',
                                       'pm5_0HC', 'pm10_0HC','pm2_5BAM']]

X = X_selected.drop(columns=['pm2_5BAM'])  # Replace 'target_column' with your actual target column name
y = X_selected['pm2_5BAM']  # Target column


# # Get original indices
# original_indices = X.index

# Split data into train and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Get indices of train and test sets
train_indices = np.where(X.index.isin(X_train.index))[0]
test_indices = np.where(X.index.isin(X_test.index))[0]

print("Training indices:", train_indices)
print("Testing indices:", test_indices)

# Create a regression model
# Initialize the Random Forest Regressor

# Define the Random Forest model
model = RandomForestRegressor(n_estimators=100, max_features=1.0, random_state=42)

# Set up the parameter grid for random search
param_distributions = {
    'n_estimators': randint(50, 200),        # Number of trees
    'max_depth': randint(5, 30),             # Maximum depth of each tree
    'min_samples_split': randint(2, 20),     # Minimum number of samples required to split a node
    'min_samples_leaf': randint(1, 10),      # Minimum number of samples required to be at a leaf node
    'max_features': ['auto', 'sqrt', 'log2'] # Number of features to consider at each split
}

# Set up RandomizedSearchCV
random_search = RandomizedSearchCV(
    model, 
    param_distributions=param_distributions, 
    n_iter=50,  # Number of parameter settings that are sampled
    scoring='neg_mean_squared_error', 
    cv=5,       # 5-fold cross-validation
    random_state=42,
    n_jobs=-1   # Use all available cores
)

# Run the random search and fit to training data
random_search.fit(X_train, y_train)

# Retrieve the best model with optimized hyperparameters
best_model = random_search.best_estimator_

# Make predictions on the test set
y_pred =best_model.predict(X_test)

# Evaluate the optimized model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# print("Best Hyperparameters:", random_search.best_params_)
print("Mean Squared Error:", mse)
print("R^2 Score:", r2)

data_to_save = {
    'X_train': X_train,
    'X_test': X_test,
    'y_train': y_train,
    'y_test': y_test,
    'train_indices': train_indices ,
    'test_indices': test_indices
}

# Save the dictionary to a .pkl file
joblib.dump(data_to_save, 'train_test_split_data.pkl')
print("Data saved successfully!")

joblib.dump(best_model, 'best_random_forest_model.joblib')
print("Model saved successfully!")


# # Train the model
# model.fit(X_train, y_train)

# # Make predictions on the test set
# y_pred = model.predict(X_test)

# joblib.dump(model, 'random_forest_model.joblib')
# print("Model saved successfully!")