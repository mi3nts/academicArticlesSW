
import pandas as pd
import glob
import matplotlib.pyplot as plt

withLikelyHoodIPSBME5MinWithHCPCPM   = pd.read_pickle('withLikelyHoodIPSBME5MinWithHCPCPM.pkl')

bam                                  = pd.read_pickle('bam.pkl')

BAMWithCorrected = pd.merge(withLikelyHoodIPSBME5MinWithHCPCPM ,bam, left_index=True, right_index=True, how='inner')
BAMWithCorrected.to_csv('BAMWithCorrected.csv')
BAMWithCorrected.to_pickle('BAMWithCorrected.pkl') 
import matplotlib.pyplot as plt

# Assuming BAMWithCorrected is your DataFrame and already has a datetime index
# Sample data structure for demonstration
# BAMWithCorrected = pd.DataFrame({
#     'pm2_5': [0, 10, 20, 30, 40],
#     'pm2_5HC': [5, 15, 25, 35, 50],
#     'pm2_5BAM': [1, 6, 12, 24, 36]
# }, index=pd.date_range(start='2024-01-01', periods=5))

# Step 3: Plot the multiple time series with dots
plt.figure(figsize=(12, 6))  # Set figure size

# Scatter plot for each variable without symbols
plt.plot(BAMWithCorrected.index, BAMWithCorrected['pm2_5'], label='PM2.5 IPS7100', color='green', linestyle='-', marker='o', markersize=1)
plt.plot(BAMWithCorrected.index, BAMWithCorrected['pm2_5HC'], label='PM2.5 HC', color='orange', linestyle='-', marker='o', markersize=1)
plt.plot(BAMWithCorrected.index, BAMWithCorrected['pm2_5BAM'], label='PM2.5 BAM', color='red', linestyle='-', marker='o', markersize=1)

# Set y-axis limits to be between 0 and 100
# plt.ylim(0, 100)

# Add titles and labels
plt.title('Three PM Values Time Series Plot (Dots Only)')
plt.xlabel('Date')
plt.ylabel('PM Values')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)  # Add grid lines for better visibility
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.legend()  # Show legend
plt.tight_layout()  # Adjust layout to prevent clipping of labels
plt.show()