# -*- coding: utf-8 -*-
"""
Author : HARMANN SINGH MANN
Harvard dogs


!pip install kaggle

!mkdir .kaggle

import json
token = {'username':'harmann98','key':'3bb952ac87beb7a4c850aa1292cbdc12'}
with open('/content/.kaggle/kaggle.json', 'w') as file:
    json.dump(token, file)

!cp /content/.kaggle/kaggle.json ~/.kaggle/kaggle.json

!kaggle config set -n path -v{/content}

!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d jessicali9530/stanford-dogs-dataset

!unzip '/content/{/content}/datasets/jessicali9530/stanford-dogs-dataset/stanford-dogs-dataset.zip' """

input_path= '/content/images/Images'

pip install tf-nightly

import os
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
print("Loaded all libraries")

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

image_size = (200, 200)
batch_size = 32

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "/content/images/Images",
    validation_split=0.2,
    subset="training",
    label_mode = 'int',
    seed = 1337,
    image_size=image_size,
    batch_size=batch_size,
)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "/content/images/Images",
    validation_split=0.2,
    subset="validation",
    label_mode = 'int',
    seed =1337,
    image_size=image_size,
    batch_size=batch_size,
)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.title(int(labels[i]))
        plt.axis("off")

data_augmentation_train = keras.Sequential(
    [
        layers.experimental.preprocessing.RandomFlip("horizontal"),
        layers.experimental.preprocessing.RandomRotation(0.1),
        layers.experimental.preprocessing.Rescaling(scale =1./255),
        layers.experimental.preprocessing.RandomHeight(0.1),
        layers.experimental.preprocessing.RandomWidth(0.1)
     
    ]
)

data_augmentation_test = keras.Sequential(
    [
        layers.experimental.preprocessing.Rescaling(scale =1./255)
     
    ]
)

plt.figure(figsize=(10, 10))
for images, _ in train_ds.take(1):
    for i in range(9):
        augmented_images = data_augmentation_train(images)
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(augmented_images[0].numpy().astype("uint8"))
        plt.axis("off")

#Inception V3 

from tensorflow.keras.applications.inception_v3 import InceptionV3

pre_trained_model = InceptionV3(input_shape=(200,200,3),
                                               include_top=False,
                                               weights='imagenet')

for layer in pre_trained_model.layers:
  layer.trainable = False

pre_trained_model.summary()

augmented_train_ds = train_ds.map(
  lambda x, y: (data_augmentation_train(x, training=True), y))

augmented_val_ds = val_ds.map(
  lambda x, y: (data_augmentation_test(x, training=True), y))

import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from keras.optimizers import Adam
from keras import regularizers

global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
Dl_1 = tf.keras.layers.Dropout(rate = 0.2)
#pre_prediction_layer = tf.keras.layers.Dense(240, activation='tanh')
#Dl_2 = tf.keras.layers.Dropout(rate = 0.2)
prediction_layer = tf.keras.layers.Dense(120,activation='softmax')

#Add dropout Layer
model_V3 = tf.keras.Sequential([
  pre_trained_model,
  global_average_layer,
  Dl_1,
  #pre_prediction_layer,
  #Dl_2,
  prediction_layer
])

model_V3.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model_V3.summary()

# Callbacks

lr_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, verbose=2, mode='max')
early_stop = EarlyStopping(monitor='val_loss', min_delta=0.1, patience=1, mode='min')



tf.keras.backend.clear_session()



hist = model_V3.fit(
           augmented_train_ds.repeat(), steps_per_epoch=int(8000/batch_size), 
           epochs=30, validation_data=augmented_val_ds.repeat(), 
           validation_steps=int(2000/batch_size) , callbacks=[lr_reduce])

fig, ax = plt.subplots(1, 2, figsize=(10, 3))
ax = ax.ravel()

for i, met in enumerate(['accuracy', 'loss']):
    ax[i].plot(hist.history[met])
    ax[i].plot(hist.history['val_' + met])
    ax[i].set_title('Model {}'.format(met))
    ax[i].set_xlabel('epochs')
    ax[i].set_ylabel(met)
    ax[i].legend(['train', 'val'])
