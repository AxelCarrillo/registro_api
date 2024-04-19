from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from datetime import datetime

app = FastAPI()

# Configurar el acceso a la base de datos MySQL
MYSQL_CONFIG = {
    'host': 'bmsrtwle6xkliwejunsm-mysql.services.clever-cloud.com',
    'user': 'uezjewljo9absf77',
    'password': 'te2uJ43DuizIrhOIehoA',
    'database': 'bmsrtwle6xkliwejunsm'
}

# Variable global para almacenar el valor de la tarjeta
card_value = None

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
    print("Leyendo valor de la tarjeta RFID:", card_value)
    if card_value is None:
        raise HTTPException(status_code=400, detail="No se ha leído ningún valor de tarjeta RFID")
    
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM equipo WHERE rfid = %s"
    cursor.execute(query, (card_value,))
    equipo = cursor.fetchone()
    cursor.close()
    conn.close()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo

# Endpoint para registrar la hora y fecha del ingreso utilizando el código RFID
@app.post("/register-entry/")
async def register_entry():
    global card_value
    print("Registrando entrada con valor de tarjeta RFID:", card_value)
    if card_value is None:
        raise HTTPException(status_code=400, detail="No se ha leído ningún valor de tarjeta RFID")
    
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    try:
        # Busca el equipo correspondiente al código RFID
        query_equipo = "SELECT id_equipo FROM equipo WHERE rfid = %s"
        cursor.execute(query_equipo, (card_value,))
        equipo_id = cursor.fetchone()
        if not equipo_id:
            raise HTTPException(status_code=404, detail="Equipo no encontrado para el código RFID proporcionado")

        # Registra la hora y fecha del ingreso en la tabla registros_rfid
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Formatea la marca de tiempo
        query_registro = "INSERT INTO registros_rfid (rfid_equipo, timestamp, id_equipo) VALUES (%s, %s, %s)"
        cursor.execute(query_registro, (card_value, timestamp, equipo_id[0]))
        conn.commit()
        return {"message": "Hora y fecha de ingreso registradas correctamente"}
    except Exception as e:
        conn.rollback()  # Revierte la transacción en caso de error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
