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

# Conectar a la base de datos
conn = mysql.connector.connect(**MYSQL_CONFIG)
cursor = conn.cursor(dictionary=True)

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
    # Actualizar el valor de la tarjeta global
    global card_value
    card_value = card_input.value
    
    # Aquí puedes realizar cualquier otra lógica de actualización necesaria en la base de datos
    # Por ejemplo, podrías actualizar la base de datos con el nuevo valor de la tarjeta
    
    # Luego, devolver un mensaje de confirmación
    return {"message": "Card value updated successfully"}

# Endpoint para leer el valor de la tarjeta y obtener datos de la base de datos según el valor RFID
@app.get("/read-card-value/")
async def read_card_value():
    # Obtener el valor de la tarjeta RFID
    card_value = get_latest_card_value()  # Suponiendo que tienes una función para obtener el último valor de la tarjeta
    
    # Consultar la base de datos para obtener los datos del equipo asociados con el valor de la tarjeta
    query = "SELECT * FROM equipo WHERE rfid = %s"
    cursor.execute(query, (card_value,))
    equipo = cursor.fetchone()
    
    # Manejar el caso donde no se encuentra ningún equipo con la tarjeta RFID proporcionada
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    # Devolver los datos del equipo
    return equipo
