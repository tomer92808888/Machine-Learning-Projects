# -*- coding: utf-8 -*-
"""Human Resources Retention

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u2Tb1FYF1EYAsoPG4yiEY37eZ8eXJ4kw

# ***Retention study - Figuring Out Which Employees May Quit***

Loading our MAIN HR Database Records
"""

import pandas as pd

hr_df = pd.read_csv("/content/hr_data.csv")

# Preview the first 5 records of the dataframe
hr_df.head()

# Preview the last 5 records of the dataframe.
hr_df.tail()

# View which columns are categorical
hr_df.select_dtypes(exclude=['int', 'float']).columns

# Display value in categorical columns
print(hr_df["department"].unique())
print(hr_df["salary"].unique())

# How many rows and columns are in our dataset?
hr_df.shape # (rows, columns)

"""## ***Loading our Evaluation and Employee Satisfaction Data***"""

emp_stais_eval = pd.read_excel("/content/employee_satisfaction_evaluation.xlsx")

# Preview the first 5 rows of the new dataframe
emp_stais_eval.head()

# How many rows and columns are in our new dataframe
emp_stais_eval.shape # (Rows, Columns)

"""## ***Merge or Join Tables***"""

main_df = hr_df.set_index('employee_id').join(emp_stais_eval.set_index('EMPLOYEE #'))
main_df = main_df.reset_index()
main_df.head()

"""## ***Is our dataset good? Are there any missing values?***"""

main_df[main_df.isnull().any(axis=1)]

"""Let's fill in the missing blanks with the average values"""

main_df.describe()

main_df.fillna(main_df.mean(), inplace=True)
main_df.head()

main_df[main_df.employee_id == 81315]

# Remove employee ID
main_df_final = main_df.drop(columns='employee_id')

main_df_final.groupby('department').sum()

main_df_final.groupby('department').mean()

main_df_final['left'].value_counts()

"""## ***Correlation Matrix***"""

import matplotlib.pyplot as plt

def plot_corr(df,size=10):
  '''
  Function plots a graphical correlation matrix for each pair of columns in the dataframe

  Input:
      df: pandas Dataframe
      size: vertical and horizontal size of of the plot
  '''

  corr = df.corr()
  fig, ax = plt.subplots(figsize=(size, size))
  ax.legend()
  cax = ax.matshow(corr)
  fig.colorbar(cax)
  plt.xticks(range(len(corr.columns)), corr.columns, rotation = 'vertical')
  plt.yticks(range(len(corr.columns)), corr.columns)


plot_corr(main_df_final)

"""## ***Preparing out Dataset for Machine Learning***"""

# Preform One Hot Encoding on Categorical Data

categorial = ['department', 'salary']
main_df_final = pd.get_dummies(main_df_final, columns=categorial, drop_first=True)
main_df_final.head()

# How many employees in the dataset have left?

len(main_df_final.loc[main_df_final.left == 1])

from sklearn.model_selection import train_test_split

# We remove the label values from our training data
X = main_df_final.drop(['left'], axis=1).values

# We assigned those labels values to our Y dataset
y = main_df_final['left']

# Split it to a 70:30 ratio Train:Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Normalize the data

from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

df_train = pd.DataFrame(X_train)
df_train.head()

df_train.describe()

"""## ***Train the Logistic Regression Model***"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

def train_test(ML_model):
  model = ML_model()
  model.fit(X_train, y_train)

  predictions = model.predict(X_test)

  print("Accuracy {0:.2f}%".format(100*accuracy_score(predictions, y_test)))
  print(confusion_matrix(y_test, predictions))
  print(classification_report(y_test, predictions))


train_test(LogisticRegression)

"""## ***Train the Random Forest Classifier***"""

from sklearn.ensemble import RandomForestClassifier

train_test(RandomForestClassifier)

"""## ***Train the Deep Learning Model***"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x

import tensorflow.keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

model = Sequential()

model.add(Dense(9, kernel_initializer = "uniform", activation = 'relu', input_dim = 18))
model.add(Dense(1, kernel_initializer = "uniform", activation = 'sigmoid'))

model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ["accuracy"])

# Display Model Summary and Show Parameters
model.summary()

batch_size = 10
epochs = 25

history = model.fit(X_train,
                    y_train,
                    batch_size = batch_size,
                    epochs = epochs,
                    verbose = 1,
                    validation_data = (X_test, y_test))

score = model.evaluate(X_test, y_test, verbose = 0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# Plotting our loss charts
import matplotlib.pyplot as plt

history_dict = history.history

loss_values = history_dict['loss']
val_loss_values = history_dict['val_loss']
epochs = range(1, len(loss_values) + 1)

line1 = plt.plot(epochs, val_loss_values, label = "Valdiation/Test Loss")
line2 = plt.plot(epochs, loss_values, label = "Training Loss")
plt.setp(line1, linewidth = 2.0, marker = '+', markersize = 10.0)
plt.setp(line2, linewidth = 2.0, marker = '4', markersize = 10.0)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.grid(True)
plt.legend()
plt.show()

# Plotting our accuracy charts
import matplotlib.pyplot as plt

history_dict = history.history

loss_values = history_dict['accuracy']
val_loss_values = history_dict['val_accuracy']
epochs = range(1, len(loss_values) + 1)

line1 = plt.plot(epochs, val_loss_values, label = "Valdiation/Test accuracy")
line2 = plt.plot(epochs, loss_values, label = "Training accuracy")
plt.setp(line1, linewidth = 2.0, marker = '+', markersize = 10.0)
plt.setp(line2, linewidth = 2.0, marker = '4', markersize = 10.0)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.grid(True)
plt.legend()
plt.show()

"""## ***Displaying the Classification Report and the Confusion Matrix***"""

predictions = model.predict(X_test)
predictions = (predictions > 0.5)

print(confusion_matrix(y_test, predictions))
print(classification_report(y_test, predictions))

"""## ***Deeper Model***"""

from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Dropout

model2 = Sequential()

# Hidden layer 1
model2.add(Dense(100, activation='relu', input_dim = 18, kernel_regularizer=l2(0.01)))
model2.add(Dropout(0.3, noise_shape=None, seed=None))

# Hidden layer 2
model2.add(Dense(100, activation='relu', kernel_regularizer=l2(0.01)))
model2.add(Dropout(0.3, noise_shape=None, seed=None))

model2.add(Dense(1, activation='sigmoid'))

model2.summary()

model2.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ["accuracy"])

"""## ***Training our Deeper Model***"""

batch_size = 32
epochs = 25

history = model2.fit(X_train,
                     y_train,
                     epochs = epochs,
                     batch_size = batch_size,
                     verbose = 1,
                     validation_data = (X_test, y_test))

score = model2.evaluate(X_test, y_test, verbose = 0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# Plotting our loss charts
import matplotlib.pyplot as plt

history_dict = history.history

loss_values = history_dict['loss']
val_loss_values = history_dict['val_loss']
epochs = range(1, len(loss_values) + 1)

line1 = plt.plot(epochs, val_loss_values, label = "Valdiation/Test Loss")
line2 = plt.plot(epochs, loss_values, label = "Training Loss")
plt.setp(line1, linewidth = 2.0, marker = '+', markersize = 10.0)
plt.setp(line2, linewidth = 2.0, marker = '4', markersize = 10.0)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.grid(True)
plt.legend()
plt.show()

# Plotting our accuracy charts
import matplotlib.pyplot as plt

history_dict = history.history

loss_values = history_dict['accuracy']
val_loss_values = history_dict['val_accuracy']
epochs = range(1, len(loss_values) + 1)

line1 = plt.plot(epochs, val_loss_values, label = "Valdiation/Test accuracy")
line2 = plt.plot(epochs, loss_values, label = "Training accuracy")
plt.setp(line1, linewidth = 2.0, marker = '+', markersize = 10.0)
plt.setp(line2, linewidth = 2.0, marker = '4', markersize = 10.0)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.grid(True)
plt.legend()
plt.show()

"""## ***Final model + Feature importances***"""

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("Accuracy {0:.2f}%".format(100*accuracy_score(predictions, y_test)))
print(confusion_matrix(y_test, predictions))
print(classification_report(y_test, predictions))

main_df_final.drop(["left"], axis=1).columns

import pandas as pd

feature_importances = pd.DataFrame(model.feature_importances_,
                                   index = pd.DataFrame(X_train).columns,
                                   columns =['importance']).sort_values('importance', ascending = False)

feature_importances