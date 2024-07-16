from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')  # Fix for headless environment (optional)
import matplotlib.pyplot as plt
import io
from PIL import Image

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.float32(img.reshape(-1, 3))
    return img

def kmeans_segmentation(image_path, K=5):
    img = preprocess_image(image_path)
    kmeans = KMeans(n_clusters=K)
    kmeans.fit(img)
    centers = np.uint8(kmeans.cluster_centers_)
    segmented_img = centers[kmeans.labels_]
    segmented_img = segmented_img.reshape(img.shape)
    segmented_img = segmented_img.reshape(128, 128, 3)
    return segmented_img

