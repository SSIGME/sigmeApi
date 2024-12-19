from flask import Flask, jsonify, request
from flask_cors import CORS
from bson import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)

client = MongoClient('mongodb://mongo:POsHMuKHBuIzgPQKaaZBMKdTJJheHjJv@junction.proxy.rlwy.net:38928')
db = client['Sancarmen']
usuarios_collection = db['usuarios']
zona_horaria = timezone('America/Bogota')

def actualizar_estado_usuarios_expirados():
    """
    Actualiza el estado de los usuarios cuya fecha de expiración ha pasado.
    Esta función obtiene la fecha actual en UTC y actualiza el campo 'estado' 
    a False para todos los documentos en la colección 'usuarios_collection' 
    cuya 'fechaExpiracion' es menor que la fecha actual.
    """
    fecha_actual = datetime.now(zona_horaria)
    result = usuarios_collection.update_many(
        {"fechaExpiracion": {"$lt": fecha_actual}}, 
        {"$set": {"estado": False}}
    )
    
    return f"Se actualizaron {result.modified_count} usuarios."


def actualizar_exp_licencia():
    days=usuarios_collection.find_one({"tipo":"hospital"})["dias"] 
    print("Dias restantes: ",days)  
    if days <= 0:
        usuarios_collection.update_one(
        {"tipo":"hospital"},
        {"estadoLicencia": False})
        print("Licencia")
        
    else:          
        dias = usuarios_collection.update_one(
         {"tipo":"hospital"},
         {"$inc": {"dias": -1}})
        print("Dias restantes restados: ", days - 1)  





actualizar_estado_usuarios_expirados()
actualizar_exp_licencia()    