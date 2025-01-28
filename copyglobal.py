from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuración de MongoDB
client = MongoClient("mongodb+srv://ssigmeapp:3F0L4qnW6Hgdd2x4@sigmedataserver.okzbeur.mongodb.net/?retryWrites=true&w=majority&appName=sigmeDataServer")  # Cambia la URL según tu configuración

global_db = client["GLOBAL"]  # Base de datos GLOBAL
rutinas_collection = global_db["rutinas"]  # Colección rutinas

# Función para copiar la colección `rutinas`
def copiar_rutinas(destino_db_name):
    print("Copiando Rutinas")
    try:
        destino_db = client[destino_db_name]  # Conecta a la base de datos destino
        destino_collection = destino_db["rutinas"]  # Colección destino

        # Leer todas las rutinas de la colección `rutinas` en GLOBAL
        rutinas = list(rutinas_collection.find())

        if rutinas:
            # Eliminar el campo _id para evitar conflictos al insertar
            for rutina in rutinas:
                if "_id" in rutina:
                    del rutina["_id"]

            # Insertar las rutinas en la colección destino
            destino_collection.insert_many(rutinas)
            print(f"Copiadas {len(rutinas)} rutinas a {destino_db_name}")
        else:
            print("No hay rutinas para copiar.")
    except Exception as e:
        print(f"Error al copiar las rutinas: {str(e)}")

if __name__ == '__main__':
    destino_db_name = "PALM"  # Cambia por el nombre de tu base de datos destino
    copiar_rutinas(destino_db_name)
    app.run(debug=True)
