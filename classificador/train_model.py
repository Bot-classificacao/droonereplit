import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers import RandomFlip, RandomRotation, RandomZoom
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import os

# Definir paths
train_data_path = os.path.join(os.getcwd(), 'classificadorIA/Treinamento')
validation_data_path = os.path.join(os.getcwd(), 'classificadorIA/Validation')
model_save_path = 'classificadorIA/model_classificacao_faces.h5'
print(train_data_path)
print(validation_data_path)

# Verificar se os diretórios existem
if not os.path.exists(train_data_path):
    raise FileNotFoundError(
        f"Diretório de treinamento não encontrado: {train_data_path}")

if not os.path.exists(validation_data_path):
    raise FileNotFoundError(
        f"Diretório de validação não encontrado: {validation_data_path}")

# Configurações
batch_size = 32
img_width, img_height = 180, 180
kernel_img = 255
img_size = (img_width, img_height)
image_shape = img_size + (3, )
epochs = 20
learning_rate = 0.0001

# Carregar dataset
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_data_path,
    shuffle=True,
    seed=123,
    image_size=img_size,
    batch_size=batch_size,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    validation_data_path,
    shuffle=True,
    seed=123,
    image_size=img_size,
    batch_size=batch_size,
)

class_names = train_ds.class_names
num_classes = len(class_names)

val_ds_card = tf.data.experimental.cardinality(val_ds)
val_ds_batch = val_ds_card // 7
dataset_test = val_ds.take(val_ds_batch)
val_ds = val_ds.skip(val_ds_batch)
# Preparação dos datasets
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
dataset_test = val_ds.prefetch(buffer_size=AUTOTUNE)
# data argumentation pra evitar overfit
data_argumentation = Sequential([
    RandomFlip('horizontal_and_vertical'),
    RandomRotation(0.2),
    RandomZoom((0.2, 0.3))
])
# trasferencia de aprendizads
model_transfer_learning = tf.keras.applications.MobileNetV2(
    input_shape=(image_shape), include_top=False, weights='imagenet')
model_transfer_learning.trainable = True

rescaling = tf.keras.layers.Rescaling(1. / (kernel_img / 2.), offset=-1)
# Criar e compilar o modelo
model = Sequential([
    rescaling,
    data_argumentation,
    # model_transfer_learning,
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(128, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(256, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Flatten(),
    # tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    layers.Dense(num_classes, activation='softmax')
])
model_transfer_learning.summary()
model.compile(
    # optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    # loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    optimizer=tf.keras.optimizers.RMSprop(learning_rate=learning_rate / 10),
    metrics=['accuracy'])

# Callbacks para reduzir a taxa de aprendizado e para early stopping
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=5,
    min_lr=learning_rate,
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,
)

# Treinar o modelo
history = model.fit(train_ds,
                    validation_data=val_ds,
                    epochs=epochs,
                    callbacks=[reduce_lr, early_stopping])

# Salvar o modelo treinado
model.save(model_save_path)

# Plotar resultados
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs_range = range(len(acc))

print('Treinamento concluído!\nAcuracia: {:.2f}%'.format(acc[-1] * 100))
print('Val Acuracia:' + str(val_acc[-1] * 100))

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
