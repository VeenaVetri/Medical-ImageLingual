from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from tensorflow.keras.applications.vgg16 import preprocess_input
import joblib

# imagelingual/xray_classification/VGG_model
knn_model = joblib.load('imagelingual/xray_classification/knn_model.h5')

VGG_model = joblib.load("imagelingual/xray_classification/VGG_model")

CLASSNAMES = ['Abdomen CT','Breast MRI','Chest CT','Cheast Xray','Hand X-Ray','Head CT']

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)
    return img

def predict_class(image_path, model, feature_extractor):
    img = preprocess_image(image_path)
    features = feature_extractor.predict(img)
    features = features.reshape(features.shape[0], -1)
    prediction = model.predict(features)
    return prediction