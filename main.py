from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import tensorflow as tf
from PIL import Image
import numpy as np

# FastAPI ilovasini yaratish
app = FastAPI()

# Modelni yuklash
try:
    model = tf.keras.models.load_model("malaria_exam_best_v7.keras")
except Exception as e:
    raise Exception(f"Modelni yuklashda xato: {e}")

# Tasvirni qayta ishlash funksiyasi
def preprocess_image(image: Image.Image) -> np.ndarray:
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((64, 64))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

# Bashorat qilish endpoint’i
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file)
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)[0][0]
        label = "Parasitized" if prediction > 0.5 else "Uninfected"
        confidence = float(prediction) if prediction > 0.5 else float(1 - prediction)
        return {"label": label, "confidence": confidence}
    except Exception as e:
        return {"error": str(e)}

# API’ni ishga tushirish
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)