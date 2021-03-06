# -*- coding: utf-8 -*-
"""Who do we target for Donations

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Fk_uBzbtSoj_NsHwvnnIWJmXWpXyQ8b9

#Who do we target for Donations

- We have a dataset of people we approached for doners for our Election campaign
- We have their education, job, income, ethnicity 
- We know high income earners are better to approach for political donations

### Let's build a classifier that predicts income levels based on a person's attributes. 
Those will be the persons we appraoch first for political donations
"""

import pandas as pd

census = pd.read_csv('/content/adult.data') 

# Preview our data
census.head()

"""Where are our column names? They're given separately"""

column_names = ['age', 'workclass', 'fnlwgt','education','education-num','marital-status','occupation',
                'relationship','race','sex','capital-gain','capital-loss','hours-per-week','native-country', 'Income']

census = pd.DataFrame(census.values, columns = column_names)
census.head()

print ("Rows     : " ,census.shape[0])
print ("Columns  : " ,census.shape[1])
print ("\nFeatures : \n" ,census.columns.tolist())
print ("\nMissing values :  ", census.isnull().sum().values.sum())
print ("\nUnique values :  \n",census.nunique())

census.info()

"""### They're all object datatype, can Pandas automatically fix this?"""

# Use Pandas's infer_objects
census = census.infer_objects()
census.head()

census.info()

"""# Exploratory Data Analysis"""

# Use strip to remove white space characters before and after our data
census['Income'] = census['Income'].str.strip()
census.head()

# Total number of records
n_records = census.shape[0]

# Number of records where individual's income is more than $50,000
n_greater_50k = census.loc[census['Income'] == '>50K'].shape[0]

# Number of records where individual's income is at most $50,000
n_at_most_50k = census[census['Income'] == '<=50K'].shape[0]

# Percentage of individuals whose income is more than $50,000
greater_percent = (n_greater_50k / n_records) * 100

# Print the results
print("Total number of records: {}".format(n_records))
print("Individuals making more than $50,000: {}".format(n_greater_50k))
print("Individuals making at most $50,000: {}".format(n_at_most_50k))
print("Percentage of individuals making more than $50,000: {:.2f}%".format(greater_percent))

# Visualizations
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="whitegrid", color_codes=True)
sns.factorplot("sex", col='education', data=census, hue='Income', kind="count", col_wrap=4);

# Age Histogram 
census.hist(column='age')

census.hist(column='capital-gain')

census.hist(column='capital-loss')

import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(12,4))

census.hist('capital-gain', bins=20, ax=axes[0])
census.hist('capital-loss', bins=20, ax=axes[1])

skewed = ['capital-gain', 'capital-loss']
census[skewed] = census[skewed].apply(lambda x: np.log(x + 1))
census.head()

fig, axes = plt.subplots(1, 2, figsize=(12,4))

census.hist('capital-gain', bins=20, ax=axes[0])
census.hist('capital-loss', bins=20, ax=axes[1])

# fnlwgt: final weight. In other words, this is the number of people the census believes the entry represents
census.drop(['fnlwgt'], axis=1, inplace=True)
census.head()

# Check for nulls
census[census.isnull().any(axis=1)]

# Find '?' in dataset column occupation
census[census['occupation'] == " ?"]

census[census['native-country'] == " ?"]

## Drop missing data
#census = census[census['workclass'] != " ?"]
census = census[census['occupation'] != " ?"]
census = census[census['native-country'] != " ?"]

"""# Preparing our data for Modeling"""

from sklearn.preprocessing import MinMaxScaler

# Initialize a scaler, then apply it to the features
scaler = MinMaxScaler() # default=(0, 1)
numerical = ['age', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']

# Make a copy of the our original df
census_minmax_transform = pd.DataFrame(data = census)

# Scale our numerica data
census_minmax_transform[numerical] = scaler.fit_transform(census_minmax_transform[numerical])

census_minmax_transform.head()

# Get raw income numbers and drop it from our census_minmax_transform dataframe
income_raw = census_minmax_transform['Income']
census_minmax_transform = census_minmax_transform.drop('Income', axis = 1)

# One-hot encode the 'features_log_minmax_transform' data using pandas.get_dummies()
features_final = pd.get_dummies(census_minmax_transform)

# Encode the 'income_raw' data to numerical values
from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
income = income_raw.apply(lambda x: 0 if x == "<=50K" else 1)
income = pd.Series(encoder.fit_transform(income_raw))

# Print the number of features after one-hot encoding
encoded = list(features_final.columns)
print("{} total features after one-hot encoding.".format(len(encoded)))

print(encoded)

census_minmax_transform.nunique()

from sklearn.model_selection import train_test_split

# Split the 'features' and 'income' data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_final, income, test_size = 0.2, random_state = 0)

# Show the results of the split
print("Training set has {} samples.".format(X_train.shape[0]))
print("Testing set has {} samples.".format(X_test.shape[0]))

# Calculate accuracy
accuracy = n_greater_50k / n_records

# Calculating precision
precision = n_greater_50k / (n_greater_50k + n_at_most_50k)

#Calculating recall
recall = n_greater_50k / (n_greater_50k + 0)

# Calculate F-score using the formula above for beta = 0.5
fscore =  (1  + (0.5*0.5)) * ( precision * recall / (( 0.5*0.5 * (precision))+ recall))

# Print the results 
print("Naive Predictor: [Accuracy score: {:.4f}, F-score: {:.4f}]".format(accuracy, fscore))

from sklearn.metrics import fbeta_score, accuracy_score
from time import time

def train_predict(learner, sample_size, X_train, y_train, X_test, y_test): 
    '''
    inputs:
       - learner: the learning algorithm to be trained and predicted on
       - sample_size: the size of samples (number) to be drawn from training set
       - X_train: features training set
       - y_train: income training set
       - X_test: features testing set
       - y_test: income testing set
    '''
    
    results = {}
    
    # Fit the learner to the training data using slicing with 'sample_size'
    start = time() # Get start time
    learner = learner.fit(X_train[:sample_size],y_train[:sample_size])
    end = time() # Get end time
    
    # Calculate the training time
    results['train_time'] = end - start
        
    #  Get the predictions on the test set,
    #  then get predictions on the first 300 training samples
    start = time() # Get start time
    predictions_test = learner.predict(X_test)
    predictions_train = learner.predict(X_train[:300])
    end = time() # Get end time
    
    # Calculate the total prediction time
    results['pred_time'] = end - start
            
    # Compute accuracy on the first 300 training samples
    results['acc_train'] = accuracy_score(y_train[:300],predictions_train)
        
    # Compute accuracy on test set
    results['acc_test'] = accuracy_score(y_test,predictions_test)
    
    # Compute F-score on the the first 300 training samples
    results['f_train'] = fbeta_score(y_train[:300],predictions_train,0.5)
        
    # Compute F-score on the test set
    results['f_test'] = fbeta_score(y_test,predictions_test,0.5)
       
    # Success
    print("{} trained on {} samples.".format(learner.__class__.__name__, sample_size))
        
    # Return the results
    return results

"""# Let's train and compare 3 Classifiers"""

# Import the three supervised learning models from sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier

# Initialize the three models, the random states are set to 101 so we know how to reproduce the model later
clf_A = DecisionTreeClassifier(random_state=101)
clf_B = SVC(random_state = 101)
clf_C = AdaBoostClassifier(random_state = 101)

# Calculate the number of samples for 1%, 10%, and 100% of the training data
samples_1 = int(round(len(X_train) / 100))
samples_10 = int(round(len(X_train) / 10))
samples_100 = len(X_train)

# Collect results on the learners
results = {}
for clf in [clf_A, clf_B, clf_C]:
    clf_name = clf.__class__.__name__
    results[clf_name] = {}
    for i, samples in enumerate([samples_1, samples_10, samples_100]):
        results[clf_name][i] = \
        train_predict(clf, samples, X_train, y_train, X_test, y_test)

#Printing out the values
for i in results.items():
    print(i[0])
    display(pd.DataFrame(i[1]).rename(columns={0:'1%', 1:'10%', 2:'100%'}))

from sklearn.metrics import confusion_matrix

plt.figure(figsize=(30,12))

for i,model in enumerate([clf_A,clf_B,clf_C]):
    cm = confusion_matrix(y_test, model.predict(X_test))
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] # normalize the data

    # view with a heatmap
    plt.figure(i)
    sns.heatmap(cm, annot=True, annot_kws={"size":10}, 
            cmap='Blues', square=True, fmt='.3f')
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.title('Confusion matrix for:\n{}'.format(model.__class__.__name__));

"""# Results Analysis
- AdaBoost is the most appropriate for our task.

- It performs the best on the testing data, in terms of both the accuracy and f-score. 
- It also takes resonably low time to train on the full dataset, which is just a fraction of the 60 seconds taken by SVM, the next best classifier to train on the full training set. So it should scale well even if we have more data.

- By default, Adaboost uses a decision stump i.e. a decision tree of depth 1 as its base classifier, which can handle categorical and numerical data. Weak learners are relatively faster to train, so the dataset size is not a problem for the algorithm.

### But how does Adaboost work?
Adaboost works by combining several simple learners (just like Random Forests), to create an ensemble of learners that can predict whether an individual earns above 50k or not.

Each of the learners, in our case decision trees, are created using “features” we have about individuals (eg. age, occupation, education, etc) create a set of rules that can predict a person’s income.

During the training process, which lasts for several rounds, the Adaboost algorithm looks at instances where it has predicted badly, and prioritizes the correct prediction of those instances in the next round of raining.

With each round, the model finds the best learner (or decision tree) to incorporate into the ensemble, repeating the process for the specified number of rounds, or till we can’t improve the predictions further.

All the learners are then combined to make a final ensembled model, where they each vote to predict if a person earns more than 50k or not. Usually we take the majority of the votes to make a final prediction.

Using this model with the census information of individuals, we can predict the same information for a potential new donor and predict if they earn more than 50K or not, and thus make a decision on the likeliness of them donating to charity.
"""

# Import 'GridSearchCV', 'make_scorer', and any other necessary libraries
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer

# Initialize the classifier
clf = AdaBoostClassifier(base_estimator=DecisionTreeClassifier())

# Create the parameters list you wish to tune
parameters = {'n_estimators':[50, 120], 
              'learning_rate':[0.1, 0.5, 1.],
              'base_estimator__min_samples_split' : np.arange(2, 8, 2),
              'base_estimator__max_depth' : np.arange(1, 4, 1)
             }

# Make an fbeta_score scoring object
scorer = make_scorer(fbeta_score,beta=0.5)

# Perform grid search on the classifier using 'scorer' as the scoring method
grid_obj = GridSearchCV(clf, parameters,scorer)

# Fit the grid search object to the training data and find the optimal parameters
grid_fit = grid_obj.fit(X_train,y_train)

# Get the estimator
best_clf = grid_fit.best_estimator_

# Make predictions using the unoptimized and model
predictions = (clf.fit(X_train, y_train)).predict(X_test)
best_predictions = best_clf.predict(X_test)

# Report the before-and-afterscores
print("Unoptimized model\n------")
print("Accuracy score on testing data: {:.4f}".format(accuracy_score(y_test, predictions)))
print("F-score on testing data: {:.4f}".format(fbeta_score(y_test, predictions, beta = 0.5)))
print("\nOptimized Model\n------")
print("Final accuracy score on the testing data: {:.4f}".format(accuracy_score(y_test, best_predictions)))
print("Final F-score on the testing data: {:.4f}".format(fbeta_score(y_test, best_predictions, beta = 0.5)))
print(best_clf)

# Train the supervised model on the training set 
model = AdaBoostClassifier().fit(X_train,y_train)

# Extract the feature importances
importances = model.feature_importances_
importances