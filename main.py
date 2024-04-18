from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Variable global para almacenar el valor de la tarjeta
card_value = 0.0

# Modelo de datos para el valor de la tarjeta en el POST
class CardValueInput(BaseModel):
    value: float

# Agregar el middleware CORS para permitir el acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir acceso desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Endpoint para actualizar el valor de la tarjeta
@app.post("/update-card-value/")
async def update_card_value(card_input: CardValueInput):
    global card_value
    card_value = card_input.value
    return {"message": "Card value updated successfully"}

# Endpoint para leer el valor de la tarjeta
@app.get("/read-card-value/")
async def read_card_value():
    global card_value
    return {"value": card_value}
