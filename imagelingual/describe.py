import easyocr
import pandas as pd
import cv2
from matplotlib import pyplot as plt
import joblib
import numpy as np

print("hi")
print("hi")
# joblib.dump(reader, "reader")
# reader = joblib.load("F:\srp-searched\imagelingual\\reader")
# df = pd.read_csv("F:\\srp-searched\\imagelingual\\dictionary.csv")
df = pd.read_excel("imagelingual/abbreviations.xlsx")

def sharpen_image(image):
    # Define the sharpening filter
    sharpening_filter = np.array([[-1, -1, -1],
                                  [-1, 9, -1],
                                  [-1, -1, -1]])
    
    # Apply the filter to the image
    sharpened_image = cv2.filter2D(image, -1, sharpening_filter)
    print("sharpened")
    return sharpened_image

def preprocess_image():
    image_path = "imagelingual/static/uploads/describe.jpg"
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpened_image = sharpen_image(gray_image)

    cv2.imwrite("imagelingual/static/uploads/sharpened.jpg", sharpened_image)
    print("preprocessed")
    return sharpened_image

def get_text(sharpened):
    image = "imagelingual/static/uploads/describe.jpg"
    reader = easyocr.Reader(['en'])
    print("loaded")
    # if opt:
# .       image = opt
    image=sharpened
    result = reader.readtext(image)
    print("read")
    words = []
    for e in result:
        words.append(e[1])
    print(words)    

    return result, words

def describe(words):
  for ind in range(len(words)):
    e = words[ind]
    # print(e)
    if '/' in e:
      sep = '/'
    elif '%' in e:
      sep = '%'
    elif '*' in e:
      sep = '*'
    else:
      sep = " "

    k = e.split(sep)

    for i in range(len(k)):
      now = k[i]
      condition = df['abbreviation']==now.upper()
      matched = df.loc[condition, 'expansion']
      for j in matched:
        k[i] = j
        print(j)
        break
      else:
        print(now)
    words[ind] = sep.join(k)
    print("---")

  # print("##########")

  for a in words:
      print(a)    
  return words

print("bef")
sharpened = preprocess_image()
print("hello")
result, words = get_text(sharpened)
print(result)
print(words)
expanded = describe(words)

for a in expanded:
   print(a)
