# -*- coding: utf-8 -*-
"""Momento de Retroalimentación: Módulo 2 Análisis y Reporte sobre el desempeño.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dgwf1NJGKN5Do6YYLDLMHwTdhwuH4nKt
"""

import pandas as pd
import numpy as np
import re

from sklearn.utils import shuffle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from google.colab import drive
drive.mount('/content/drive')

# Código para montar Google Drive en Colab
# El comando 'drive.mount' permite acceder a los archivos almacenados en Google Drive.

url = '/content/drive/MyDrive/IMDBDataset.csv'
dataset = pd.read_csv(url)

htmlRegex = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
specialCharacters = re.compile(r"[^a-zA-Z0-9 ]")

def removeSpecialCharacters(column):
    return column.apply(lambda x: re.sub(specialCharacters, "", x))

def removeHTMLCode(column):
    return column.apply(lambda x: re.sub(htmlRegex, "", x))

def convertToLower(column):
    return column.apply(str.lower)

def cleanData(dataframeColumn):
    dataframeColumn = convertToLower(dataframeColumn)
    dataframeColumn = removeHTMLCode(dataframeColumn)
    dataframeColumn = removeSpecialCharacters(dataframeColumn)
    return dataframeColumn

dataset['review'] = cleanData(dataset['review'])
dataset['sentiment'] = cleanData(dataset['sentiment'])

def startTrainingAndTestingData(seed):
    # The positive and negative reviews are filtered into separate datasets
    positiveReviews = dataset[dataset["sentiment"] == "positive"]
    negativeReviews = dataset[dataset["sentiment"] == "negative"]

    # Two series of data are obtained from the positive reviews. One for the input and the other for the output
    positiveInput = positiveReviews["review"].values
    positiveOutput = positiveReviews["sentiment"].values

    # Two series of data are obtained from the negative reviews. One for the input and the other for the output
    negativeInput = negativeReviews["review"].values
    negativeOutput = negativeReviews["sentiment"].values

    # The training and testing series of inputs and outputs are created
    pInput_train, pInput_test, pOutput_train, pOutput_test = train_test_split(
        positiveInput, positiveOutput, train_size=0.50, random_state=seed)
    nInput_train, nInput_test, nOutput_train, nOutput_test = train_test_split(
        negativeInput, negativeOutput, train_size=0.50, random_state=seed)

    # Positive and negative inputs and outputs are concatenated for training
    train_input = np.concatenate((nInput_train, pInput_train), axis=0)
    train_output = np.concatenate((nOutput_train, pOutput_train), axis=0)

    # Positive and negative inputs and outputs are concatenated for testing
    test_input = np.concatenate((nInput_test, pInput_test), axis=0)
    test_output = np.concatenate((nOutput_test, pOutput_test), axis=0)

    # The dataframe is shuffled to get random testing groups
    shIn, shOut = shuffle(test_input, test_output, random_state=12345)

    return train_input, train_output, shIn, shOut

vectorizer = TfidfVectorizer(stop_words="english")

def createAndTrainRegularizedLinearSVCModel(input, output, regularization_type='l2', regularization_strength=1.0):
    # Create a pipeline with TF-IDF vectorization and a regularized LinearSVC model
    vectorizer = TfidfVectorizer(stop_words="english")
    model = make_pipeline(vectorizer, LinearSVC(penalty=regularization_type, C=regularization_strength))

    # Train the model
    model.fit(input, output)

    return model

def predictResultsFromModel(model, input):
    return model.predict(input)

def evaluateModel(outputTest, predictions):
    # Generates the confusion matrix for this model
    confusionMatrix = confusion_matrix(outputTest, predictions)
    # Generates the classification report of the model's predictions
    report = classification_report(outputTest, predictions)

    print("Confusion Matrix: ")
    print(confusionMatrix)

    print("Classification scores: ")
    print(report)

    return confusionMatrix, report  # Return the confusion matrix and classification report

def split_data(seed):
    # First, split the data into train and test
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=seed)
    # Then, split the test data into validation and final test
    validation_data, test_data = train_test_split(test_data, test_size=0.5, random_state=seed)
    return train_data, validation_data, test_data

def diagnose_model(train_data, validation_data, test_data):
    # Separate the data into features (X) and labels (y)
    X_train = train_data['review']
    y_train = train_data['sentiment']

    X_validation = validation_data['review']
    y_validation = validation_data['sentiment']

    X_test = test_data['review']
    y_test = test_data['sentiment']

    # Create and train the model
    model = createAndTrainRegularizedLinearSVCModel(X_train, y_train, regularization_type='l2', regularization_strength=1)

    # Predict on validation and test sets
    validation_predictions = predictResultsFromModel(model, X_validation)
    test_predictions = predictResultsFromModel(model, X_test)

    # Evaluate on validation set
    validation_confusion_matrix, validation_report = evaluateModel(y_validation, validation_predictions)

    # Evaluate on test set
    test_confusion_matrix, test_report = evaluateModel(y_test, test_predictions)

    # Bias diagnosis
    bias = validation_confusion_matrix[0, 1] + validation_confusion_matrix[1, 0]

    # Variance diagnosis
    variance = test_confusion_matrix[0, 1] + test_confusion_matrix[1, 0]

    # Model fit diagnosis
    if bias == 0:
        bias_level = "Low"
    elif bias < 100:
        bias_level = "Medium"
    else:
        bias_level = "High"

    if variance == 0:
        variance_level = "Low"
    elif variance < 100:
        variance_level = "Medium"
    else:
        variance_level = "High"

    if bias_level == "Low" and variance_level == "Low":
        model_fit = "Good Fit"
    elif bias_level == "High" and variance_level == "High":
        model_fit = "Overfit"
    else:
        model_fit = "Underfit"

    # Print Diagnoses and Values
    print(f"Bias Level: {bias_level} (Value: {bias})")
    print(f"Variance Level: {variance_level} (Value: {variance})")
    print(f"Model Fit: {model_fit}")

train_data, validation_data, test_data = split_data(123457890)
diagnose_model(train_data, validation_data, test_data)

