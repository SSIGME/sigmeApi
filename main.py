import json
from urllib.parse import quote
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from bson import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random, string
from pymongo import MongoClient 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from datetime import timedelta
import subprocess
from werkzeug.utils import secure_filename
from google.cloud import storage
import requests
import os 
import socket

app = Flask(__name__)
CORS(app)
a='Cxv24KPcpogXnqgpDAXFerewrf'
app.config['JWT_SECRET_KEY'] = 'Cxv24KPcpogXnqgpDAXF'
jwt = JWTManager(app)
client = MongoClient('mongodb+srv://ssigmeapp:3F0L4qnW6Hgdd2x4@sigmedataserver.okzbeur.mongodb.net/?retryWrites=true&w=majority&appName=sigmeDataServer')
user = 'userhospital'
password = 'Thegostmane1!'
db = client['ISAK']
usuarios_collection = db['usuarios']
equipos_collection = db['equipos']
tipos_collection = db['tipos']
areas_collection = db['areas']
UPLOAD_FOLDER = '/home/server/LocalImagesAndDocuments'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UPLOAD_ROOT = '/home/server/LocalImagesAndDocuments'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Máximo tamaño de archivo: 16MB


def generateCode(num):
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits,k=num))
    return codigo

def generateCodeNumber(num):
    codigo = ''.join(random.choices(string.digits,k=num))
    return codigo

def obtener_hora_actual():
    # Obtener la hora actual en UTC como objeto datetime
    return datetime.now(timezone.utc)
@app.route("/health", methods=['GET'])
def health_check():
    return "OK", 200


def serve_document(codigoHospital, codigoEquipo, filename):
    # Ruta local donde se encuentran los PDFs
    base_url = 'http://sigme-server.local'
    local_file_path = f'{base_url}/{codigoHospital}/{codigoEquipo}/{codigoEquipo}-{filename}.pdf'
    file_in_server = f'/home/server/LocalImagesAndDocuments/{codigoHospital}/{codigoEquipo}/{codigoEquipo}-{filename}.pdf'
    print(f"Local file path: {local_file_path}")
    if not os.path.exists(file_in_server):
        return None
    try:
        return local_file_path
    except Exception as e:
        print(f"Error al servir el archivo local: {str(e)}")
        return None

@app.route('/document/<codigoHospital>/<codigoEquipo>/<tipoDocumento>', methods=['GET'])
def document(codigoHospital, codigoEquipo, tipoDocumento):
    if tipoDocumento == "calibracion":
        filename = "Certificado_de_calibracion"
        url = serve_document(codigoHospital, codigoEquipo, filename)
        return jsonify({"url": url}), 200
    if tipoDocumento == "Guia_Rapida":
        filename = "Guia_Rapida"
        url = serve_document(codigoHospital, codigoEquipo, filename)
        return jsonify({"url": url}), 200
    if tipoDocumento == "Plan_Mantenimiento":
        filename = "Plan_Mantenimiento"
        url = serve_document(codigoHospital, codigoEquipo, filename)
        return jsonify({"url": url}), 200
    if tipoDocumento == "Manual":
        filename = "Manual_De_Uso"
        url = serve_document(codigoHospital, codigoEquipo, filename)
        return jsonify({"url": url}), 200
    if tipoDocumento == "Limpieza":
        filename = "Protocolo_Limpieza"
        url = serve_document(codigoHospital, codigoEquipo, filename)
        return jsonify({"url": url}), 200
    else:
        return jsonify({"msg": "Tipo de documento no válido"}), 400


@app.route('/delete/equipo/<codigoHospital>/<codigoEquipo>', methods=['DELETE'])
def delete_equipo(codigoHospital, codigoEquipo):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    areas_collection = db['areas']
    equipo = equipos_collection.find_one({"codigoIdentificacion": codigoEquipo})
    if not equipo:
        return jsonify({"msg": "Equipo no encontrado"}), 404
    areas_collection.update_one(
        {"nombre": equipo["area"]},
        {"$pull": {"idEquipos": codigoEquipo}}
    )
    equipos_collection.delete_one({"codigoIdentificacion": codigoEquipo})
    return jsonify({"msg": "Equipo eliminado exitosamente"}), 200

@app.route('/upload_image/<codigoHospital>/<codigoEquipo>', methods=['POST'])
def upload_image(codigoHospital, codigoEquipo):
    # Verifica si el archivo está presente en la solicitud
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    file = request.files['file']

    # Verifica si el nombre del archivo es válido
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo inválido'}), 400

    # Verifica si el archivo tiene una extensión permitida
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        return jsonify({'error': 'El archivo debe ser una imagen (JPG, JPEG, PNG)'}), 400

    # Asegura que el nombre del archivo sea seguro
    filename = secure_filename(file.filename)

    # Construye la ruta para guardar el archivo
    upload_path = os.path.join(UPLOAD_ROOT, codigoHospital, codigoEquipo)

    # Crea la carpeta si no existe
    os.makedirs(upload_path, exist_ok=True)

    # Ruta final del archivo
    file_path = os.path.join(upload_path, f'{codigoEquipo}.jpg')

    try:
        # Guarda el archivo en el servidor
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'Error al guardar el archivo: {str(e)}'}), 500

    return jsonify({'message': 'Imagen subida exitosamente', 'path': file_path}), 200

def serve_image(codigoHospital, filename):
    # Carpeta base donde NGINX sirve los archivos
    base_url = 'http://sigme-server.local'

    # Construye la ruta del archivo en el servidor
    file_path = os.path.join(codigoHospital, filename, f'{filename}.jpg')

    # Codifica correctamente el nombre de archivo y la carpeta para evitar problemas con espacios o caracteres especiales
    file_path_encoded = quote(file_path)
    print(f"{base_url}/{file_path_encoded}")
    # Devuelve la URL completa para acceder a la imagen
    return f"{base_url}/{file_path_encoded}"




@app.route('/upload_multiple_pdfs/<codigoHospital>/<codigoEquipo>', methods=['POST'])
def upload_multiple_pdfs(codigoHospital, codigoEquipo):
    files = request.files.getlist('files')
    print(request.files)

    if len(files) < 1:
        return jsonify({"msg": "Se requiere por lo menos un archivo PDF"}), 400

    for file in files:
        if file.filename == '':
            print("File has no name")
            return jsonify({"msg": "Uno de los archivos no tiene nombre"}), 400

        if not allowed_file(file.filename):
            print("File extension is not PDF")
            return jsonify({"msg": "Todos los archivos deben ser PDFs"}), 400

        filename = secure_filename(file.filename)

        # Crear la ruta completa para guardar el archivo localmente
        local_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{codigoHospital}/{codigoEquipo}/{codigoEquipo}-{filename}')

        # Crear directorios si no existen
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Guardar el archivo localmente
        try:
            file.save(local_file_path)
            print(f"Archivo guardado en: {local_file_path}")
        except Exception as e:
            print("Error al guardar el archivo localmente", str(e))
            return jsonify({"msg": "Error al guardar los archivos en el servidor", "error": str(e)}), 500

    return jsonify({"msg": "PDFs subidos exitosamente al servidor"}), 200

@app.route('/HojaVida/<codigoEquipo>/<codigoHospital>', methods=['POST'])
def hojavida(codigoEquipo, codigoHospital):
    try:
        data = request.get_json()
        db = client[codigoHospital]
        equipos_collection = db['equipos']

        equipos_collection.update_one(
                {"codigoIdentificacion": codigoEquipo},
                {
                    "$set": { "last_updated": obtener_hora_actual() },
                    "$push": { "parametrosTecnicos": data }
                }
            )
        return jsonify({"msg": "Hoja de vida actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"msg": "Error al actualizar la hoja de vida", "error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    """
    Ruta para iniciar sesión y verificar que el usuario sea de tipo 'administrador'.
    Se envía un JSON con 'usuario' y 'contrasena'.
    """
    data = request.get_json()
    db = client[data["codigoHospital"]]
    usuarios_collection = db['usuarios']
    print(data)
    # Buscar usuario en la base de datos con el tipo de usuario 'administrador'
    user = usuarios_collection.find_one({"documento": data['usuario'], "tipo": "administrador"})


    if user and check_password_hash(user['contrasena'], data['contrasena']):
        print(check_password_hash(user['contrasena'], data['contrasena']))
        access_token = create_access_token(
        identity=json.dumps({
        "id": str(user['_id']),
        "tipo": user["tipo"],
        "hospital": user['hospital']
    })
)
        return jsonify({
            "access_token": access_token,
            "tipo": user["tipo"],
            "hospital": user["hospital"],
        }), 200
    else:
        print("no funciona")
        return jsonify({"msg": "Usuario o contraseña incorrectos o no tiene permisos de administrador"}), 401




@app.route('/login/code', methods=['POST'])
def logincode():
    """
    Ruta para iniciar sesión.
    Se envía un JSON con 'codigo' y 'documento'.
    """
    data = request.get_json()
    print(data)
    
    # Obtener la base de datos correspondiente según el hospital
    db = client[data["codigoHospital"]]
    usuarios_collection = db['usuarios']
    
    # Buscar al usuario con los datos proporcionados
    user = usuarios_collection.find_one({
        "estado": True,
        "codigo": data['codigo'],
        "tipo": data['tipo']
    })
    
    if user:
        # Serializar los datos del usuario a JSON
        user_data = json.dumps({
            "id": str(user['_id']),
            "tipo": user["tipo"],
            "codigo": user["codigo"],
            "hospital": data["codigoHospital"],  # Almacenar el codigoHospital
            "nombre": user["nombre"]
        })
        
        # Crear el token con el objeto serializado en `identity`
        response = {
            "access_token": create_access_token(
                identity=user_data  # Se pasa el objeto serializado como cadena JSON
            ),
            "firmaEstado": user.get("firmaEstado")  # Obtener firmaEstado del usuario
        }

        return jsonify(response), 200
    else:
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401


@app.route('/protected/<tipo>', methods=['GET'])
@jwt_required()
def protected_route(tipo):
    """
    Ruta protegida que verifica el tipo de usuario.
    Se pasa 'tipo' en la URL para verificar contra el tipo del usuario en la base de datos.
    """

    current_user = get_jwt_identity()
    user_id = current_user['id']

    
    user = usuarios_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    
   
    if user['tipousuario'] != tipo:
        return jsonify({"msg": "No tiene permiso para acceder a este recurso"}), 403
    
  
    return jsonify({"msg": "Acceso permitido", "user_id": user_id, "tipo": user['tipousuario']}), 200

#[.]
@app.route('/user/firma', methods=['POST'])
@jwt_required()
def update_user_firma():
    """
    Ruta para actualizar la firma de un técnico.
    Recibe un JSON con 'codigoHospital', 'codigo' y 'firma' para actualizar la firma y el estado de firma.
    """
    data = request.get_json()
    db = client[data["codigoHospital"]]
    usuarios_collection = db['usuarios']
    
    # Buscamos el técnico por su código
    tecnico = usuarios_collection.find_one({"codigo": data['codigo']})

    if tecnico:
        # Actualizamos la firma y el estado de firma a true
        usuarios_collection.update_one(
            {"codigo": data['codigo']},
            {
            "$set": {
                "firma": data['firma'],
                "firmaEstado": True,
                "last_updated": obtener_hora_actual()
            }
            }
        )
        return jsonify({"msg": "Firma del técnico actualizada exitosamente"}), 200
    else:
        # Si no se encuentra el técnico, devolvemos un mensaje de error
        return jsonify({"msg": "Técnico no encontrado"}), 404

@app.route('/user/firma', methods=['GET'])
@jwt_required()
def get_firma():
    """
    Ruta para obtener la firma de un técnico.
    Se envía un JSON con 'codigoHospital' y 'codigo'.
    """
    user = get_jwt_identity()
    user = json.loads(user)
    db = client[user["hospital"]]
    usuarios_collection = db['usuarios']
    codigouser = user["codigo"]
    usuario = usuarios_collection.find_one({"codigo": codigouser})
    if usuario:
        return jsonify({"firma": usuario['firma']}), 200
    else:
        return jsonify({"msg": "Técnico no encontrado"}), 404

########## crear ##########
@app.route('/administrador', methods=['POST'])
@jwt_required()
def create_administrador():
    """
    Ruta para crear un usuario Administrador.
    Se envía un JSON con 'usuario', 'contrasena', 'nombre', 'hospital' y 'tipoAdministrador'.
    """
    data = request.get_json()
    if a == data["a"]:
        existing_user = usuarios_collection.find_one({"documento": data['documento']})
        if existing_user:
            return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
    
        hospital_user = usuarios_collection.find_one({"tipo": "hospital"})
        if not hospital_user:
         return jsonify({"msg": "No se encontró el hospital"}), 404
    admin_data = {
        "usuario": data['usuario'],
        "contrasena": data['contrasena'],
        "documento": data['documento'],
        "nombre": data['nombre'],
        "hospital": hospital_user['nombre'],
        "tipo": data['administrador'],
        "last_updated":obtener_hora_actual()
    }
    usuarios_collection.insert_one(admin_data)
    return jsonify({"msg": "Administrador creado exitosamente"}), 201

@app.route('/tecnico', methods=['POST'])
@jwt_required()
def create_tecnico():
    """
    Ruta para crear o actualizar un usuario Técnico.
    Se envía un JSON con 'codigoHospital', 'fechaExpiracion', 'nombre', 'documento', 'empresa'.
    """
    data = request.get_json()
    db = client[data["codigoHospital"]]
    usuarios_collection = db['usuarios']
    existing_user = usuarios_collection.find_one({"documento": data['documento']})

    if existing_user:
        # Si el técnico ya existe, actualizamos los datos necesarios
        usuarios_collection.update_one(
            {"documento": data['documento']},
            {
                "$set": {
                    "nombre": data['nombre'],
                    "empresa": data['empresa'],
                    "fechaExpiracion": data['fechaExpiracion'],
                    "estado": True,
                    "last_updated": obtener_hora_actual()
                }
            }
        )
        return jsonify({"msg": "Datos del técnico actualizados exitosamente"}), 200
    else:
        # Si el técnico no existe, lo creamos
        tecnico_data = {
            "codigo": generateCode(6),
            "fechaExpiracion": data['fechaExpiracion'],
            "fechaCreacion": datetime.now().strftime("%Y-%m-%d"),
            "hospital": data["codigoHospital"],
            "nombre": data['nombre'],
            "estado": True,
            "documento": data['documento'],
            "firma": "",
            "firmaEstado": False,
            "empresa": data["empresa"],
            "idManteniminetos": [],
            "tipo": 'tecnico',
            "last_updated":obtener_hora_actual()
        }
        usuarios_collection.insert_one(tecnico_data)
        return jsonify({"msg": "Técnico creado exitosamente"}), 201

@app.route('/profesional', methods=['POST'])
@jwt_required()
def create_profesional():
    """
    Ruta para crear un usuario Profesional.
    Se envía un JSON con 'nombre', 'fechaExpiracion', 'empresa', 'documento', 'codigoHospital', 'fechaExpiracionEstado'.
    """
    data = request.get_json()
    db = client[data["codigoHospital"]]
    usuarios_collection = db['usuarios']
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    hospital = usuarios_collection.find_one({"tipo": "hospital"})
    code = hospital["codigoIdentificacion"] + "-" + generateCode(6)
    
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
    
    if not hospital:
        return jsonify({"msg": "No se encontró el hospital"}), 404
    
    profesional_data = {
        "codigo": code,
        "nombre": data['nombre'],
        "documento": data['documento'],
        "estado": data['fechaExpiracionEstado'],
        "hospital": hospital['nombre'],
        "fechaCreacion": obtener_hora_actual(),
        "fechaExpiracion": data['fechaExpiracion'],
        "empresa": data['empresa'],
        "tipo": "profesional",
        "last_updated": obtener_hora_actual(),
    }
    
    usuarios_collection.insert_one(profesional_data)
    return jsonify({"msg": "Profesional creado exitosamente"}), 201


@app.route('/profesionales/<codigoHospital>', methods=['GET'])
@jwt_required()
def get_profesionales(codigoHospital):
    """
    Ruta para obtener todos los profesionales.
    """
    db = client[codigoHospital]
    usuarios_collection = db['usuarios']
    profesionales = usuarios_collection.find({"tipo": {"$in": ["profesional", "responsableArea"]}})
    result = []
    for profesional in profesionales:
        profesional['_id'] = str(profesional['_id'])
        result.append(profesional)
    
    return jsonify(result), 200


@app.route('/encargado', methods=['POST'])
@jwt_required()
def create_encargado():
    """
    Ruta para crear un usuario Encargado.
    Se envía un JSON con 'codigo', 'nombre', 'estado', 'hospital', 'fechaCreacion', 'fechaExpiracion', 'tipoEncargado'.
    """
    data = request.get_json()
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
        
        
    hospital_user = usuarios_collection.find_one({"tipo": "hospital"})
    if not hospital_user:
        return jsonify({"msg": "No se encontró el hospital"}), 404

    data = request.get_json()
    encargado_data = {
        "codigo": generateCode(6),
        "nombre": data['nombre'],
        "estado": data['estado'],
        "hospital": data['hospital'],
        "documento": data['documento'],
        "fechaCreacion": data['fechaCreacion'],
        "fechaExpiracion": data['fechaExpiracion'],
        "tipo": data['encargado'],
        "last_updated":obtener_hora_actual()
    }
    usuarios_collection.insert_one(encargado_data)
    return jsonify({"msg": "Encargado creado exitosamente"}), 201

@app.route('/hospital', methods=['POST'])
def create_hospital():
    """
    Ruta para crear un hospital y un usuario administrador.
    Se envía un JSON con los datos del hospital y del administrador.
    """
    data = request.get_json()

    # Validar que el código del hospital está presente
    if 'codigo' not in data:
        return jsonify({"error": "El campo 'codigo' es obligatorio"}), 400

    # Usar el código del hospital para nombrar la base de datos
    hospital_db_name = data['codigo']
    db = client[hospital_db_name]  # Crear/seleccionar la base de datos
    usuarios_collection = db['usuarios']  # Crear/seleccionar la colección de usuarios

    # Datos del hospital a insertar
    hospital_data = {
        "nombre": data['nombre'],
        "hospital": "hospital",
        "fechaCreacion": data['fechaCreacion'],
        "fechaExpiracion": data['fechaExpiracion'],
        "tipo": "hospital",
        "codigoIdentificacion": 'PALM',
        "numeroEquipos": 0,
        "numeroAreas": 0,
        "correoContacto": data['correoContacto'],
        "direccion": data['direccion'],
        "imagen": data["imagen"],
        "telefono": data['telefono'],
        "departamento": data['departamento'],
        "ciudad": data['ciudad'],
        "proximaVisita": '',
        "ultimaVisita": '',
        "responsableMantenimiento": data['responsableMantenimiento'],
        "estadoLicencia": True,
        "last_updated": obtener_hora_actual()
    }

    # Datos del administrador a insertar
    admin_data = {
        "nombre": data['nombreAdministrador'],
        "contrasena": generate_password_hash(data['contrasenaAdministrador']),
        "documento": data['documento'],
        "tipo": "administrador",
        "hospital": data['nombre'],
        "last_updated": obtener_hora_actual()
    }

    # Insertar datos en la colección de usuarios
    usuarios_collection.insert_one(hospital_data)
    usuarios_collection.insert_one(admin_data)

    return jsonify({"msg": f"Base de datos '{hospital_db_name}' y usuario administrador creados exitosamente"}), 201
### Obtener datos hospital
@app.route('/hospital/<codigoHospital>', methods=['GET'])
def get_hospital(codigoHospital):
    """
    Ruta para obtener un hospital basado en su tipo.
    """
    db = client[codigoHospital]
    usuarios_collection = db['usuarios']
    hospital = usuarios_collection.find_one({"tipo": "hospital"})  # Assuming 'tipo' is the field you're filtering by
    if not hospital:
        return jsonify({"msg": "No se encontró un hospital con ese tipo"}), 404
    else:
        hospital['_id'] = str(hospital['_id'])
        hospital['imagen'] = serve_image(codigoHospital, "hospital")
        return jsonify(hospital), 200


@app.route('/responsableArea', methods=['POST'])
@jwt_required()
def create_responsableArea():
    """
    Ruta para crear un usuario responsableArea.
    Se envía un JSON con 'codigo', 'fechaExpiracion', 'fechaCreacion', 'hospital', 'nombre', 'estado', 'documento', 'firma', 'tipoTecnico'.
    """
    data = request.get_json()
    
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400

    hospital_user = usuarios_collection.find_one({"tipo": "hospital"})
    if not hospital_user:
        return jsonify({"msg": "No se encontró el hospital"}), 404

    responsableArea_data = {
        "codigo": generateCode(6),
        "hospital": hospital_user['nombre'],
        "nombre": data['nombre'],
        "estado": data['estado'],
        "area": data['area'],
        "documento": data['documento'],
        "firma": "",
        "idManteniminetos": [],
        "tipo": data['responsableArea'],
        "last_updated":obtener_hora_actual(),
    }
    usuarios_collection.insert_one(responsableArea_data)
    return jsonify({"msg": "Técnico creado exitosamente"}), 201

#[.]
@app.route('/get/users/<hospital>/<tipo>', methods=['GET'])
@jwt_required()
def get_users(hospital, tipo):
    """
    Ruta para obtener todos los profesionales según el hospital y tipo.
    """
    db = client[hospital]
    usuarios_collection = db['usuarios']
    usuarios = usuarios_collection.find({"tipo": tipo})
    result = []

    for usuario in usuarios:
        usuario['_id'] = str(usuario['_id'])  # Convertir ObjectId a string
        result.append(usuario)
       
    print(result)
    return jsonify(result), 200
########## crear final ##########
########## editar ##########
@app.route('/usuario/<codigo>', methods=['PUT'])
@jwt_required()
def update_usuario_estado(codigo):
    """
    Ruta para cambiar el estado de un técnico a False usando su código.
    """
    tipo = get_jwt_identity()["tipo"]

    if tipo != "administrador":
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403
    else:
        tecnico = usuarios_collection.find_one({"codigo": codigo})
        if not tecnico:
            return jsonify({"msg": "Técnico no encontrado"}), 404
        usuarios_collection.update_one(
            {"codigo": codigo},
            {"$set": {"estado": False, 
                      "last_updated": obtener_hora_actual()
                      }}
        )       
        return jsonify({"msg": "Estado del técnico actualizado a False"}), 200

""" #### PATCH /usuario/12345 {"nombre": "Carlos López"} o {"documento":"10203102"}#####
@app.route('/usuario/<id>', methods=['PATCH'])
@jwt_required()
def update_usuario(id):
    Ruta para actualizar un usuario responsableArea.
    Se puede actualizar 'nombre' o 'documento' proporcionando el ObjectId del usuario.
    data = request.get_json()
    
    # Verificar si el usuario existe
    jefe_area = usuarios_collection.find_one({"_id": ObjectId(id)})
    if not jefe_area:
        return jsonify({"msg": "No se encontró el usuario con ese ID"}), 404
    
  
    update_fields = {}
    
    if 'nombre' in data:
        update_fields['nombre'] = data['nombre']
    
    if 'documento' in data:
        # Verificar si el nuevo documento ya está en uso por otro usuario
        existing_user = usuarios_collection.find_one({"documento": data['documento']})
        if existing_user and existing_user['_id'] != ObjectId(id):
            return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
        update_fields['documento'] = data['documento']
    
    # Si hay campos para actualizar, ejecutar la actualización
    if update_fields:
        usuarios_collection.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
        return jsonify({"msg": "Usuario actualizado exitosamente"}), 200
    else:
        return jsonify({"msg": "No se proporcionaron campos para actualizar"}), 400
 """


@app.route('/usuario/valid/<documento>', methods=['GET'])
@jwt_required()
def update_Vencimiento(documento):
    """
    Ruta para veriricar si existe el documento de los usuarios
    """
    usuario = usuarios_collection.find_one({"documento": documento})
    if not usuario:
        return jsonify({"msg": "No se encontró el usuario con ese documento"}), 100
    

    return jsonify(usuario), 200




""" @app.route('/usuario/updateexp', methods=['PATCH'])
@jwt_required()
def update_exp():
    Ruta para actualizar la fecha de expiracion de un usuario,
    parametros: documento, fechaExpiracion, estado

    data = request.get_json()

    usuario = usuarios_collection.find_one({"documento": data['documento']})
    if not usuario:
        return jsonify({"msg": "No se encontró el usuario con ese documento"}), 404
  
    update_fields = {}
    
    if 'fechaExpiracion' in data:
        update_fields['fechaExpiracion'] = data['fechaExpiracion']
        update_fields["estado"] = True
    else:
        return jsonify({"msg": "Faltan campos para actualizar"}), 400
    
    if update_fields:
        usuarios_collection.update_one({"documento": data["documento"]}, {"$set": update_fields})
        return jsonify({"msg": "Usuario actualizado exitosamente"}), 200
    else:
        return jsonify({"msg": "No se proporcionaron campos para actualizar"}), 400

########## editar final ########## """
##################### users ############################
############### Areas #######################

@app.route('/area', methods=['POST'])
def create_area():
    data = request.get_json()
    db = client[data["codigoHospital"]]
    codearea = data["codigoHospital"] + "-" + generateCode(4)
    areas_collection = db['areas']
    users_collection = db['usuarios']
    area = areas_collection.find_one({"nombre": data['nombre']})
    if area is not None:
        return jsonify({"msg": "Ya existe un área con ese nombre"}), 206
    else:
        Area = {
            "codigoIdentificacion": codearea,
            "hospital": data['codigoHospital'],
            "nombre": data['nombre'],
            "idEquipos": [],
            "last_updated":obtener_hora_actual(),
            "responsableArea":data["responsableArea"],
            "documentoResponsableArea":data["documentoResponsableArea"],
            "icono": data["icono"],
        }
        areas_collection.insert_one(Area)
        profesional = users_collection.find_one(
            {"documento": data["documentoResponsableArea"]},
        )
        if profesional is not None:
            users_collection.update_one(
                {"documento": data["documentoResponsableArea"]},
                {"$set": {"tipo": "responsableArea", "estado": True, "codigo":generateCode(6), "area": data['nombre'], "last_updated":obtener_hora_actual()}},
            )
    return jsonify({"msg": "Area creada y usuario actualizado"}), 201

@app.route('/getareas/<codigoHospital>', methods=['GET'])
def get_all_areas(codigoHospital):
    db = client[codigoHospital]
    areas_collection = db['areas']
    areas = areas_collection.find()  # Fetch all areas from the collection
    result = []
    
    for area in areas:
        area['_id'] = str(area['_id'])  # Convert ObjectId to string for JSON serialization
        result.append(area)
    
    return jsonify(result), 200

@app.route('/rutina/<codigoHospital>', methods=['POST'])
def createtipo(codigoHospital):
    data = request.get_json()
    db = client[codigoHospital]
    rutinas_collection = db['rutinas']
    tipoequipo = data["tipoequipo"]
    marca = data["marca"]
    modelo = data["modelo"]
    preguntas = data["preguntas"]
    rutina = rutinas_collection.find_one({"tipo": tipoequipo, "marca": marca, "modelo": modelo})
    if rutina is not None:
        return jsonify({"msg": "Ese equipo ya tiene una rutina"}), 206
    else:
        rutina = {
            "hospital": codigoHospital,
            "tipo": tipoequipo,
            "marca": marca,
            "modelo": modelo,
            "preguntas": preguntas,
            "last_updated":obtener_hora_actual(),
        }
        rutinas_collection.insert_one(rutina)

       
    return jsonify({"msg": "Tipo creado"}), 201

@app.route('/preventivo/<codigoHospital>', methods=['POST'])
def create_preventivo(codigoHospital):
    data = request.get_json()
    db = client[codigoHospital]
    rutinas_collection = db['rutinas']
    hospital_data = usuarios_collection.find_one({"tipo": "hospital"})
    hospital = hospital_data['nombre'] if hospital_data else "Desconocido"
    rutina = {
        "hospital": hospital,
        "tipoequipo": data.get('tipoequipo'),
        "modelo": data.get('modelo'),
        "marca": data.get('marca'),
        "preguntas": data.get('preguntas', []),
        "last_updated":obtener_hora_actual(),
    }
    rutinas_collection.insert_one(rutina)
    return jsonify({"msg": "Rutina creada exitosamente"}), 201

@app.route('/marcas/<tipo>/<codigoHospital>', methods=['GET'])
def getmarcas(tipo, codigoHospital):
    """-
    Ruta para obtener todos los tipos de equipos.
    """
    db = client[codigoHospital]
    rutinas_collection = db['rutinas']
    coincidentes = rutinas_collection.find({"tipo": tipo}, {"marca": 1, "_id": 0})
    result = []
    if coincidentes is None:
        return jsonify({"msg": "No se encontraron marcas para este tipo"}), 404
    else:
        for marca in coincidentes:
            if marca['marca'] not in result:
                result.append(marca['marca'])
        return jsonify(result), 200


@app.route('/tipos/<codigoHospital>', methods=['GET'])
def get_tipos(codigoHospital):
    db = client[codigoHospital]
    """
    Ruta para obtener todos los tipos de equipos.
    """
    rutinas_collection = db['rutinas']
    tipos = rutinas_collection.find()  # Fetch all areas from the collection
    print(tipos)
    result = []
    for tipo in tipos:
        tipo = tipo['tipo']
        if tipo not in result:
            result.append(tipo)
            print("Estos son los tips",result)
    return jsonify(result), 200

@app.route('/modelos/<tipo>/<marca>/<codigoHospital>', methods=['GET'])
def get_modelos(tipo, marca, codigoHospital):
    """
    Ruta para obtener todos los tipos de equipos.
    """
    db = client[codigoHospital]
    rutinas_collection = db['rutinas']

    modeloscoincidentes = rutinas_collection.find({"tipo": tipo, "marca": marca}, {"modelo": 1, "_id": 0})
    result = []
    for modelo in modeloscoincidentes:
        modelo = modelo['modelo']
        if modelo not in result:
            result.append(modelo)
    return jsonify(result), 200


@app.route('/getarea/<codigoHospital>/<codigoArea>', methods=['GET'])
def get_area(codigoHospital, codigoArea):
    db = client[codigoHospital]
    areas_collection = db['areas']
    area = areas_collection.find_one({"codigoIdentificacion": codigoArea})
    if not area:
        return jsonify({"error": "Área no encontrada"}), 404
    else:
        area['_id'] = str(area['_id'])
        return jsonify(area), 200

""" @app.route('/area/<codigo>', methods=['PUT'])
@jwt_required()
def update_responsable_area(codigo):

    area = areas_collection.find_one({"codigo": codigo})
    
    if not area:
        return jsonify({"error": "Área no encontrada"}), 404

    # Obtener los nuevos datos enviados en el cuerpo de la solicitud
    data = request.get_json()
    
    # Validar que el nuevo nombre y documento del responsable existan en los datos recibidos
    if "responsableArea" not in data or "documentoResponsableArea" not in data:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Actualizar los campos del responsable
    areas_collection.update_one(
        {"codigo": codigo},
        {"$set": {
            "responsableArea": data["responsableArea"],
            "documentoResponsableArea": data["documentoResponsableArea"]
        }}
    )

    return jsonify({"message": "Responsable de área actualizado correctamente"}), 200

 """
############### Areas Final #######################

############### Equipos #######################
@app.route('/equipo/<codigoHospital>/<codigoIdentificacion>', methods=['GET'])
def get_equipo(codigoIdentificacion, codigoHospital):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    print(codigoIdentificacion, codigoHospital)
    equipo = equipos_collection.find_one({"codigoIdentificacion": codigoIdentificacion})
    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404
    else:
        equipo['_id'] = str(equipo['_id'])
        equipo['Imagen'] = serve_image(codigoHospital, codigoIdentificacion)
        return jsonify(equipo), 200

def convert_objectid(data):
    """ Recursively convert ObjectId to string in a MongoDB document """
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
    
@app.route('/equipo', methods=['POST'])
def equipo():
    data = request.get_json()
    db = client[data["codigoHospital"]]
    equipos_collection = db['equipos']
    areas_collection = db['areas']
    area = areas_collection.find_one({"nombre": data["area"]})
    if area is None:
        return jsonify({"msg": "No se encontró el área"}), 404
    
    documentoResponsable = area['documentoResponsableArea']
    codigoEquipo = area["codigoIdentificacion"] + "-" + generateCode(4)
    equipo = {
        "codigoIdentificacion": codigoEquipo,
        "area": area["nombre"],
        "documentoResponsableArea": documentoResponsable,
        "Tipo": data.get("tipo"),                       
        "Marca": data.get("marca"),
        "Modelo": data.get("modelo"),
        "Serie": data.get("serie"),
        "UltimoMantenimiento": "",
        "ProximaVisita": "",
        "HojaVida": [],
        "GuiaRapida":"",
        "Manual": "",
        "Rutinamantenimiento": "",
        "Imagen": codigoEquipo + ".jpg",
        "ReportesCalibracion": "",
        "last_updated":obtener_hora_actual(),
        "RecomendacionesUso": "",
    }
    areas_collection.update_one(
        {"nombre": data["area"]},
        {"$push": {"idEquipos": codigoEquipo}}
    )
    equipos_collection.insert_one(equipo)

    return jsonify({"msg": "Equipo creado exitosamente", "codigoIdentificacion": codigoEquipo}), 201

@app.route('/getequipos/<codigoHospital>/<codigoArea>', methods=['GET'])
def get_equipos(codigoHospital,codigoArea):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    areas_collection = db['areas']
    area = areas_collection.find_one({"codigoIdentificacion": codigoArea})
    equipos = equipos_collection.find({"area": area["nombre"]})
    result = []
    for equipo in equipos:
        equipo['Imagen'] = serve_image(codigoHospital,equipo["codigoIdentificacion"])
        print(equipo)
        equipo['_id'] = str(equipo['_id'])
        result.append(equipo)
    return jsonify(result), 200 
############### Final Equipos #######################


############ Mantenimientos ################
""" @app.route('/mantenimiento', methods=['POST'])
@jwt_required()
def mantenimiento():
    hospital = usuarios_collection.find_one({"tipo":"hospital"})
    data = request.get_json()
    mantenimiento = {
        "fecha": data["fecha"],
        "tecnico":data["tecnico"],
        "estado":data["estado"],
        "tipoMantenimiento":["tipoMantenimiento"],
        "firmaTecnico":data["FirmaTecnico"],
        "numeroReporte":data["numeroReporte"],
        "observaciones":data["observaciones"],
        "recibidor":areas_collection.find_one["nombre":data["area"]["documentoResponsableArea"]],
        "hospital": hospital['nombre'],
        "area": data["area"],
        "firmaRecibidor":"",
        "codigoIdentificacionEquipo":data["codigoIdentificaionEquipo"],
        "UltimoMantenimiento": "",
        "ProximaVisita": usuarios_collection.find_one({"tipo":"hospital"})["proximaVisita"],
        "preguntas":data["preguntas"]
    }
    equipos_collection.update_one(
            {"codigoIdentificacion": data["codigoIdentificaionEquipo"]},
            {
                "$push": {"HojaVida": mantenimiento},
                "$set": {"UltimoMantenimiento": data["fecha"]}
            }
        )
 """
@app.route('/mantenimiento', methods=['POST'])
@jwt_required()
def mantenimientocreate():
    try:
        # Obtener el token y deserializar la identidad
        tecnico_serializado = get_jwt_identity()
        tecnico = json.loads(tecnico_serializado)

        # Verificar la estructura deserializada
        print("Identidad del técnico:", tecnico)

        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Verificar campos necesarios
        if not data:
            return jsonify({"msg": "Datos inválidos"}), 400

        # Conectar a la base de datos
        db = client[data["codigoHospital"]]
        equipos_collection = db['equipos']
        codeMantenimiento = int(data["idMantenimiento"])

        # Crear el objeto de mantenimiento
        mantenimiento = {
            "fecha": data["fecha"],
            "idMantenimiento": codeMantenimiento,
            "codigoIdentificacionEquipo": data['IdEquipo'],
            "tipoMantenimiento": data['tipoMantenimiento'],
            "tenico": tecnico['nombre'],  # Acceder al campo deserializado
            "hospital": tecnico['hospital'],
            "respuestas": data['respuestas'],
            "firmaTecnico": data['firma'],
            "finished": data['finished'],
            "duracion": data['duracion'],
            "firmadoPorRecibidor": False
        }

        # Verificar si el mantenimiento ya existe
        mantenimiento_existente = equipos_collection.find_one(
            {"codigoIdentificacion": data['IdEquipo'], "HojaVida.idMantenimiento": codeMantenimiento}
        )

        if mantenimiento_existente:
            equipos_collection.update_one(
                {"codigoIdentificacion": data['IdEquipo']},
                {"$pull": {"HojaVida": {"idMantenimiento": codeMantenimiento}}}
            )
            equipos_collection.update_one(
                {"codigoIdentificacion": data['IdEquipo']},
                {"$push": {"HojaVida": mantenimiento}}
            )
            return jsonify({"msg": "Mantenimiento sobreescrito exitosamente"}), 201
        else:
            equipos_collection.update_one(
                {"codigoIdentificacion": data['IdEquipo']},
                {"$push": {"HojaVida": mantenimiento}}
            )
            return jsonify({"msg": "Mantenimiento creado exitosamente desde 0"}), 201

    except Exception as e:
        print(f"Error interno: {str(e)}")
        return jsonify({"msg": "Error interno del servidor", "error": str(e)}), 500

@app.route('/mantenimiento/<codigoHospital>/<codigoEquipo>/<tipomantenimiento>', methods=['GET'])
def get_mantenimiento(codigoHospital, codigoEquipo, tipomantenimiento):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    equipo = equipos_collection.find_one({"codigoIdentificacion": codigoEquipo})
    if not equipo:
        return jsonify({"msg": "Equipo no encontrado"}), 404

    mantenimientos = [
        mantenimiento for mantenimiento in equipo.get("HojaVida", [])
        if not mantenimiento.get("finished", True) and mantenimiento.get("tipoMantenimiento") == tipomantenimiento
    ]

    if not mantenimientos:
        return jsonify([]), 200

    return jsonify(mantenimientos), 200

@app.route('/firmar_mantenimiento/<codigoHospital>/<codigoEquipo>/<idMantenimiento>', methods=['POST'])
@jwt_required()
def firmar_mantenimiento(codigoHospital,codigoEquipo,idMantenimiento):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    usuarios_collection = db['usuarios']
    responsable = get_jwt_identity()
    responsable = json.loads(responsable)
    responsable = usuarios_collection.find_one({"codigo": responsable["codigo"]})
    mantenimiento = equipos_collection.find_one({"codigoIdentificacion": codigoEquipo, "HojaVida.idMantenimiento": int(idMantenimiento)})
    if not mantenimiento:
        return jsonify({"msg": "Mantenimiento no encontrado"}), 404
    else:
        print("Se ha encontrado",mantenimiento)
        equipos_collection.update_one(
            {"codigoIdentificacion": codigoEquipo, "HojaVida.idMantenimiento": int(idMantenimiento)},
            {"$set": {
                "firmaResponsable": responsable["firma"],
                "HojaVida.$.firmadoPorRecibidor": True,
                "last_updated": obtener_hora_actual()
            }}
        )
        return jsonify({"msg": "Mantenimiento firmado exitosamente"}), 200

 ############ Final Mantenimientos ################   


############## Rutinas ################


@app.route('/preventivo/<tipoequipo>/<marca>/<modelo>', methods=['GET'])
def get_preventivo(tipoequipo, marca, modelo):
    db = client['GCIW']
    rutinas_collection = db['rutinas']
    preventivo = rutinas_collection.find_one({"tipo": tipoequipo, "marca": marca, "modelo": modelo})
    if preventivo is not None:
        rutina = {
            "preguntas": preventivo.get('preguntas', []),
        }
        return jsonify(rutina), 200
    else:
        preventivo = rutinas_collection.find_one({"tipo": {"$regex": f'^{tipoequipo}$', "$options": "i"}, "marca": "GENERAL"})
        if preventivo is not None:
            del preventivo['_id'], preventivo['tipoequipo'], preventivo['marca'], preventivo['modelo'], preventivo['hospital']
            return jsonify(preventivo), 200
        else:
            print("No se encontró la rutina del mantenimiento preventivo")
            return jsonify({"msg": "No se encontró la rutina del mantenimiento preventivo"}), 404

@app.route('/correctivo', methods=['POST'])
def create_correctivo():
    data = request.get_json()
    db = client[data["codigoHospital"]]
    rutinas = db['rutinas']
    hospital_data = usuarios_collection.find_one({"tipo": "hospital"})
    hospital = hospital_data['nombre'] if hospital_data else "Desconocido"
    rutina = {
        "hospital": hospital,
        "tipoequipo": data.get('tipoequipo'),
        "modelo": data.get('modelo'),
        "marca": data.get('marca'),
        "preguntas": data.get('preguntas', []),
        "last_updated":obtener_hora_actual(),
    }
    rutinas.insert_one(rutina)
    return jsonify({"msg": "Rutina creada exitosamente"}), 201

@app.route('/correctivo/<tipoequipo>/<marca>/<modelo>', methods=['GET'])
def get_correctivo(tipoequipo, marca, modelo):
    db = client['GCIW']
    rutinas_collection = db['rutinas']
    correctivo = rutinas_collection.find_one({"tipoequipo": tipoequipo, "marca": marca, "modelo": modelo, "tipo_mantenimiento": "correctivo"})
    if correctivo is not None:
        del correctivo['_id'], correctivo['tipoequipo'], correctivo['marca'], correctivo['modelo'], correctivo['hospital']
        for pregunta in correctivo.get('preguntas', []):
            if pregunta['tipo'] == "cerrada":
                pregunta['opciones'] = [str(opcion) for opcion in pregunta['opciones']]
            else:
                pregunta['opciones'] = ""  # Establece un arreglo vacío si no hay opciones
        return jsonify(correctivo), 200
    else:
        correctivo = rutinas_collection.find_one({"tipoequipo": {"$regex": f'^{tipoequipo}$', "$options": "i"}, "marca": "GENERAL"})
        if correctivo is not None:
            del correctivo['_id'], correctivo['tipoequipo'], correctivo['marca'], correctivo['modelo'], correctivo['hospital']
            return jsonify(correctivo), 200
        else:
            return jsonify({"msg": "No se encontró la rutina del mantenimiento correctivo"}), 404

############## Final Rutinas ################
@app.route('/codigos', methods=['GET'])
@jwt_required()
def listar_codigos():
    """
    Ruta para listar todos los códigos con el nombre del dueño del código.
    Solo devuelve usuarios que tienen el parámetro 'codigo'.
    """
    # Query the database for users with 'codigo' present
    usuarios = usuarios_collection.find({"codigo": {"$exists": True}}, {"codigo": 1, "nombre": 1, "_id": 0})
    
    # Create a list of codigos only for users that have 'codigo'
    codigos = [{"codigo": usuario["codigo"], "nombre": usuario["nombre"]} for usuario in usuarios]
    return jsonify(codigos), 200
    
@app.route('/api/reporte/<codigoHospital>', methods=['POST'])
def guardar_reporte(codigoHospital):
    db = client[codigoHospital]  # Nombre de la base de datos
    reportes_collection = db["reportes"]
    try:
        reporte = request.get_json()
        print("Datos JSON del reporte:", reporte)
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        reporte["fecha"] = fecha_actual
        reporte["last_updated"]=obtener_hora_actual()
        resultado = reportes_collection.insert_one(reporte)
        return jsonify({"mensaje": "Reporte guardado exitosamente", "id": str(resultado.inserted_id)}), 201
    except Exception as e:
        print("Error al guardar el reporte:", e)
        return jsonify({"error": "Hubo un error al guardar el reporte"}), 500
@app.route('/api/reportes/<codigoHospital>', methods=['GET'])
def obtener_reportes(codigoHospital):
    db = client[codigoHospital]  # Nombre de la base de datos
    reportes_collection = db["reportes"]
    try:
        reportes = list(reportes_collection.find())
        for reporte in reportes:
            reporte['_id'] = str(reporte['_id'])

        return jsonify(reportes), 200
    except Exception as e:
        print("Error al obtener los reportes:", e)
        return jsonify({"error": "Hubo un error al obtener los reportes"}), 500

@app.route('/finished_mantenimiento/<codigoHospital>/<codigoEquipo>/<idMantenimiento>', methods=['GET'])
@jwt_required()
def get_finished_mantenimiento(codigoHospital, codigoEquipo, idMantenimiento):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    equipo = equipos_collection.find_one({"codigoIdentificacion": codigoEquipo})
    if not equipo:
        return jsonify({"msg": "Equipo no encontrado"}), 404

    mantenimiento = next((m for m in equipo.get("HojaVida", []) if str(m.get("idMantenimiento")) == idMantenimiento), None)
    if not mantenimiento:
        return jsonify({"msg": "Mantenimiento no encontrado"}), 404
    mantenimiento = {
        "idMantenimiento": mantenimiento.get("idMantenimiento"),
        "fecha": mantenimiento.get("fecha"),
        "modelo": equipo.get("Modelo"),
        "marca": equipo.get("Marca"),
        "serie": equipo.get("Serie"),
        "ubicacion": equipo.get("area"),
        "tipo": equipo.get("Tipo"),
        "duracion": mantenimiento.get("duracion"),
        "respuestas": mantenimiento.get("respuestas"),
        "firmaTecnico": mantenimiento.get("firmaTecnico"),
        "firmaResponsable": mantenimiento.get("firmaRecibidor"),
        "firmadoPorRecibidor": mantenimiento.get("firmadoPorRecibidor"),
    }
    print("Mantenimiento finalizado:", mantenimiento)
    return jsonify(mantenimiento), 200
@app.route('/pendientes/<codigoHospital>/<codigoUsuario>', methods=['GET'])
def getpendientes(codigoHospital, codigoUsuario):
    db = client[codigoHospital]
    equipos_collection = db['equipos']
    usuarios_collection = db['usuarios']
    areas_collection = db['areas']
    user = usuarios_collection.find_one({"codigo": codigoUsuario})
    if not user:
        print("Usuario no encontrado")
        return jsonify({"msg": "Usuario no encontrado"}), 404
    area = areas_collection.find_one({"nombre": user.get("area")})
    if not area:
        print("Área no encontrada")
        return jsonify({"msg": "El usuario no es responsable de ningún área"}), 404
    equipos = equipos_collection.find({"area": area["nombre"]})
    pendientes = []
    for equipo in equipos:
        for mantenimiento in equipo.get("HojaVida", []):
                mantenimiento_pendiente = {
                    "idMantenimiento": mantenimiento.get("idMantenimiento"),
                    "codigoEquipo": equipo.get("codigoIdentificacion"),
                    "tipo": equipo.get("Tipo"),
                    "tenico": mantenimiento.get("tenico"),
                    "fecha": mantenimiento.get("fecha"),
                    "tipoMantenimiento": mantenimiento.get("tipoMantenimiento"),
                    "firmadoPorRecibidor": mantenimiento.get("firmadoPorRecibidor"),
                }
                print("Mantenimiento pendiente:", mantenimiento_pendiente)  
                pendientes.append(mantenimiento_pendiente)
                
    return jsonify(pendientes), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', 
            port=5000, 
            debug=True
            )
