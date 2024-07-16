from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet import preprocess_input
from sklearn.decomposition import PCA
import numpy as np
import os
import joblib
import glob

key = dict()
key["bladder"] = "Bladder"
key["bowel"] = "Bowel"
key["gallbladder"] = "Gall Bladder"
key["liver"] = "Liver"
key["kidney"] = "Kidney"
key['spleen'] = "Spleen"

def extract_features(nn_model,model, fine_tune=False):
    ImgPath = 'imagelingual/static/uploads'
    ProcessedPath = 'imagelingual/abdominal_ultrasound_classification/new/feature_'+nn_model
    savepath =ProcessedPath
    imagelist = os.listdir(ImgPath)
    for image1 in imagelist:
        # print(image1)
        if image1=="ultrasound.jpg":
            image_pre, ext = os.path.splitext(image1)
            imgfile = ImgPath+'/'+ image1
            img = image.load_img(imgfile, target_size=(64, 64))
            x = image.img_to_array(img)      # shape:(64,64,3)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)   # shape:(1,64,64,3)
            print(x.shape)
            want = model.predict(x)
            print(np.shape(want))   # shape:(1,2048)

            # normalize
            a = np.min(want)
            b = np.max(want)
            want = (want-a)/(b-a)
            if(not os.path.exists(savepath)):
                os.makedirs(savepath)
            np.save(os.path.join(savepath,"temp"+'.npz'),want)       

def extract_features_pca(nn_model):
    raw_feature_path = 'imagelingual/abdominal_ultrasound_classification/new/feature_' + nn_model
    ProcessedPath = 'imagelingual/abdominal_ultrasound_classification/new/feature_' + nn_model +'_pca'
    test_list = []
    test_files = glob.glob(raw_feature_path+'\*')

    for f in test_files:
        x = np.load(f)
        x = np.squeeze(x, axis=0)
        test_list.append(x)

    test_list = np.array(test_list)  
    print(test_list.shape) 

    train_mean = joblib.load("imagelingual/abdominal_ultrasound_classification/train_mean") 
    test_list -= train_mean
    
    pca = joblib.load("imagelingual/abdominal_ultrasound_classification/pca_model")
    test_pca = pca.transform(test_list)
    print( test_pca.shape)    
    
    test_pca_list = test_pca.tolist()
    
    for i in range(len(test_pca_list)):
        test_pca_list[i] = np.expand_dims(test_pca_list[i], axis=0)
    for i in range(len(test_pca_list)):
        test_feature = test_pca_list[i]
        test_file = test_files[i]
        test_file = os.path.split(test_file)[1]
        image_pre, ext = os.path.splitext(os.path.splitext(test_file)[0])
        savepath = ProcessedPath
        if (not os.path.exists(savepath)):
            os.makedirs(savepath)
        np.save(os.path.join(savepath,"temp"+'.npz'), test_feature)

# THE ONE THE ONE

def calculate_cityblock_distance(test_vec, train_vec):
    distance = np.sum(np.abs(test_vec - train_vec))
    return distance

def train_knn_model(nn_model, pca=False):
    testlist = []
    databaselist = []
    test_class_list = []
    data_class_list = []

    # Paths for test and train directories
    test_dir = 'imagelingual/abdominal_ultrasound_classification/new/feature_' + nn_model +"_pca"
    train_dir = 'imagelingual/abdominal_ultrasound_classification/dataset/feature_' + nn_model + '_pca/train'

    # Read image feature vectors and the labels
    for test_img in os.listdir(test_dir):
        testlist.append(os.path.join(test_dir, test_img))
        test_class = test_img.split('-')[0]
        test_class_list.append(test_class)

    for train_img in os.listdir(train_dir):
        databaselist.append(os.path.join(train_dir, train_img))
        train_class = train_img.split('-')[0]
        data_class_list.append(train_class)

    # k=3
    k = 3

    predictions = dict()
    for test_img, test_class in zip(testlist, test_class_list):
        distances = []
        for train_img, train_class in zip(databaselist, data_class_list):
            test_vec = np.load(test_img)
            train_vec = np.load(train_img)
            distance = calculate_cityblock_distance(test_vec, train_vec)
            distances.append((distance, train_class))

        # Sort distances and get the top k nearest neighbors
        distances.sort(key=lambda x: x[0])
        nearest_neighbors = distances[:k]

        # Count occurrences of each class among the nearest neighbors
        counts = {}
        for _, neighbor_class in nearest_neighbors:
            counts[neighbor_class] = counts.get(neighbor_class, 0) + 1

        # Get the class with the highest count
        prediction = max(counts, key=counts.get)
        predictions["temp"] = prediction
        predictions["temp"] = key[predictions['temp']]

    return predictions