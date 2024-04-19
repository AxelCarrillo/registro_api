from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Configurar el acceso a la base de datos MySQL
MYSQL_CONFIG = {
    'host': 'bmsrtwle6xkliwejunsm-mysql.services.clever-cloud.com',
    'user': 'uezjewljo9absf77',
    'password': 'te2uJ43DuizIrhOIehoA',
    'database': 'bmsrtwle6xkliwejunsm'
}

# Variable global para almacenar el valor de la tarjeta
card_value = 0.0

# Modelo de datos para el valor de la tarjeta en el POST
class CardValueInput(BaseModel):
    value: str

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

# Endpoint para leer el valor de la tarjeta y obtener datos de la base de datos según el valor RFID
@app.get("/read-card-value/")
async def read_card_value():
    global card_value
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM equipo WHERE rfid = %s"
    cursor.execute(query, (card_value,))
    equipo = cursor.fetchone()
    cursor.close()  # Cierra el cursor después de leer los resultados de la consulta
    conn.close()  # Cierra la conexión después de usarla
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo
