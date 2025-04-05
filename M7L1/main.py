import telebot

from config import TOKEN 
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import h5py

f = h5py.File("keras_model.h5", mode="r+")
model_config_string = f.attrs.get("model_config")

if model_config_string.find('"groups": 1,') != -1:
    model_config_string = model_config_string.replace('"groups": 1,', '')
f.attrs.modify('model_config', model_config_string)
f.flush()

model_config_string = f.attrs.get("model_config")

assert model_config_string.find('"groups": 1,') == -1

bot = telebot.TeleBot(TOKEN)



def predict(img):
    np.set_printoptions(suppress=True)
    model = load_model("keras_model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(img).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    return class_name[2:],confidence_score

@bot.message_handler(content_types=['photo'])
def save_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = file_info.file_path.split('/')[-1]
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    a,b = get_class(file_name)
    bot.send_message(message.chat.id, f'{a} - {b}')


bot.infinity_polling()