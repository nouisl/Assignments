# Noushin Islam (Student no. 201508438)
# Assignment 2 - COMP336

# To run the code locally use: python3 Assignment2.py
# Make sure to open your terminal in the directory with this file saved on it when running it

# Importing libraries and functions
# Need to be installed locally using pip if not already installed
import pandas as pd
import numpy as np
from functools import reduce
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 1
print('\n1)\n')
# Change this string to the path of the txt/csv file used if run on a different machine   
file = 'stock_data.csv'
# Load data from csv file into a pandas dataframe
data = pd.read_csv(file)
# Convert data in 'date' into dtype datetime 
data['date'] = data['date'].astype(dtype='datetime64')
# Output the data
print(data)

# 2
print('\n2)\n')
# Create sorted list of entries in 'name' without duplications
name = sorted(data['Name'].drop_duplicates())
# Print output
print('Number of names:', len(name))
print('First 5 names: ', name[:5])
print('Last 5 names: ', name[-5:])

# 3
print('\n3)\n')
# Set the first and last date
firstDate = pd.to_datetime('2014-07-01')
lastDate = pd.to_datetime('2017-12-31')
# Create dataframes containing the first and last dates of the companies
firsts = data.loc[data.groupby('Name')['date'].idxmin()]
lasts = data.loc[data.groupby('Name')['date'].idxmax()]
# Create lists of names that need to be removed based on the first and last dates
firstRem = firsts[firsts['date']>firstDate]['Name'].tolist()
lastRem = lasts[lasts['date']<lastDate]['Name'].tolist()
# Create a list of the names to be removed 
removed = sorted(set(firstRem).union(set(lastRem)))
# Delete the names from the data
data = data[~data['Name'].isin(removed)]
# Create a list of the names remaining
remaining = sorted(set(name) - set(removed))
# Print output
print ('Companies removed: ', removed)
print ('Companies remaining: ', len(remaining))

# 4
print('\n4)\n')
# Create dataframe containing a list of all dates for each name
allDates = data.groupby('Name')['date'].apply(list).reset_index(name='date')
# Find the common dates and turn them into a dataframe 
commonDates = np.unique(reduce(np.intersect1d, allDates['date']))
commonDates = pd.DataFrame(commonDates, columns=['date'])
# Filter out unnecessary dates
dates = commonDates[(commonDates['date'] >= firstDate) & (commonDates['date'] <= lastDate)]['date']
# Change data to contain common dates
data = data[data['date'].isin(dates)]
# Print output
print ('Dates remaining: ', len(dates))
print ('First 5 dates: ', (dates.head(5).dt.strftime('%Y-%m-%d').tolist()))
print ('Last 5 dates: ', (dates.tail(5).dt.strftime('%Y-%m-%d').tolist()))

# 5
print('\n5)\n')
# Create a new pandas dataframe 
dataframe = pd.DataFrame(index = dates, columns = remaining)
# Function to fill the dataframe with the close values
def fill(x):
	dataframe.loc[x['date'],x['Name']] = x['close']
	return 0
# Apply function to data
data.apply(lambda x: fill(x), axis=1)
# Print output
print('First 5:\n', dataframe[:5])
print('\nLast 5:\n', dataframe[-5:])

# 6
print('\n6)\n')
# Function to calculate return for each name
def get_returns(y):
	return (y - y.shift(1)) / y.shift(1)
# Calculate return for all names
returns = dataframe.apply(get_returns)[1:]
# Set NA data to 0
returns.fillna(0, inplace = True)
# Print output
print('First 5:\n', returns[:5])
print('\nLast 5:\n', returns[-5:])

# 7
print('\n7)\n')
# Initialize PCA object
pca = PCA()
# Calculate the principal components of the returns
transformedData = pca.fit_transform(returns)
components = pca.components_
# Sort the PC's by eigenvalue
sortedComponents = components[np.argsort(-pca.explained_variance_)]
# Print output
print(sortedComponents[:5])

# 8
print('\n8)\n')
# Calculate the explained variance ratios
explainedVarianceRatios = pca.explained_variance_ratio_
# Calculate the percentage of variance explained by the first PC
percentage = explainedVarianceRatios[0]
# Print output
print('Percentage of variance by the the 1st PC: ', percentage, '%')
# Plot the first 20 explained variance ratios
firstTwenty = explainedVarianceRatios[:20]
plt.bar(range(0, 20), firstTwenty)
# Label both axis
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.xticks(range(0, 20, 1))
# Show plot
plt.show()
plt.close()

# 9
print('\n9)\n')
# Calculate the cumulative variance ratios
cumulativeVarianceRatios = np.cumsum(explainedVarianceRatios)
# Set an index to mark the PC for which the cumulative variance ratios is >= 0.95%
index = np.where(cumulativeVarianceRatios >= 0.95)[0][0]
plt.plot(range(len(cumulativeVarianceRatios)), cumulativeVarianceRatios)
plt.plot(index, cumulativeVarianceRatios[index], 'ro')
plt.annotate((index, cumulativeVarianceRatios[index]), xy=(index, cumulativeVarianceRatios[index]), \
	xytext=(index, cumulativeVarianceRatios[index]-0.05))
# Label both axis
plt.xlabel('Principal Component')
plt.ylabel('Cumulative Variance Ratio')
# Show plot
plt.show()
plt.close()

# 10
print('\n10)\n')
# Use scaler to normalise the dataframe for the columns to have zero mean and unit variance
scaler = StandardScaler()
scaler.fit(returns)
normalized = scaler.transform(returns)
# 10.7
# Initialize PCA object
pca = PCA()
# Calculate the principal components of the returns
transformedData = pca.fit_transform(normalized)
components = pca.components_
# Sort the PC's by eigenvalue
sortedComponents = components[np.argsort(-pca.explained_variance_)]
# Print output
print(sortedComponents[:5])
# 10.8
# Calculate the explained variance ratios
explainedVarianceRatios = pca.explained_variance_ratio_
# Calculate the percentage of variance explained by the first PC
percentage = explainedVarianceRatios[0] 
# Print output
print('Percentage of variance by the the 1st PC: ', percentage, '%')
# Plot the first 20 explained variance ratios
firstTwenty = explainedVarianceRatios[:20]
plt.bar(range(0, 20), firstTwenty)
# Label both axis
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.xticks(range(0, 20, 1))
# Show plot
plt.show()
plt.close()
# 10.9
# Calculate the cumulative variance ratios
cumulativeVarianceRatios = np.cumsum(explainedVarianceRatios)
# Set an index to mark the PC for which the cumulative variance ratios is >= 0.95%
index = np.where(cumulativeVarianceRatios >= 0.95)[0][0]
plt.plot(range(len(cumulativeVarianceRatios)), cumulativeVarianceRatios)
plt.plot(index, cumulativeVarianceRatios[index], 'ro')
plt.annotate((index, cumulativeVarianceRatios[index]), xy=(index, cumulativeVarianceRatios[index]), \
	xytext=(index, cumulativeVarianceRatios[index]-0.05))
# Label both axis
plt.xlabel('Principal Component')
plt.ylabel('Cumulative Variance Ratio')
# Show plot
plt.show()
plt.close()


