from flask import Flask, jsonify, request
from flask_cors import CORS
from bson import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random, string
from pymongo import MongoClient 
app = Flask(__name__)
CORS(app)
a='Cxv24KPcpogXnqgpDAXFerewrf'
app.config['JWT_SECRET_KEY'] = 'Cxv24KPcpogXnqgpDAXF'
jwt = JWTManager(app)
client = MongoClient('mongodb+srv://atonikapp:YY0Gh4ydpa1TPju3@cluster0.ln4xz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['SanCamen']
usuarios_collection = db['usuarios']
equipos_collection = db['equipos']
areas_collection = db['areas']
rutinas_collection = db['rutinas']


######  Funtionality ######
def generateCode(num):
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits,k=num))
    return codigo

###############################


##################### users ############################
@app.route('/login', methods=['POST'])
def login():
    """
    Ruta para iniciar sesión.
    Se envía un JSON con 'usuario' y 'contrasena'.
    """
    data = request.get_json()
    user = usuarios_collection.find_one({"usuario": data['usuario'], "contrasena": data['contrasena'] ,"tipousuario": data["tipousuario"]})
    if user:
        return jsonify({"access_token": create_access_token(identity={"id": str(user['_id']), "tipo": user["tipousuario"],"hospital":user['hospital']})}), 200
    else:
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401
    


@app.route('/logincode', methods=['POST'])
def logincode():
    """
    Ruta para iniciar sesión.
    Se envía un JSON con 'codigo' y 'documento'.
    """
    data = request.get_json()
    user = usuarios_collection.find_one({"codigo": data['codigo'], "tipo": data['tipo']})
    if user:
        return jsonify({"access_token": create_access_token(identity={"id": str(user['_id']), "tipo": user["tipousuario"]})}), 200
    else:
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401
from flask_jwt_extended import jwt_required, get_jwt_identity



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
        "tipo": data['administrador']
    }
    usuarios_collection.insert_one(admin_data)
    return jsonify({"msg": "Administrador creado exitosamente"}), 201

@app.route('/tecnico', methods=['POST'])
@jwt_required()
def create_tecnico():
    """
    Ruta para crear un usuario Técnico.
    Se envía un JSON con 'codigo', 'fechaExpiracion', 'fechaCreacion', 'hospital', 'nombre', 'estado', 'documento', 'firma', 'tipoTecnico'.
    """
    data = request.get_json()
    
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
    hospital_user = usuarios_collection.find_one({"tipo": "hospital"})
    if not hospital_user:
        return jsonify({"msg": "No se encontró el hospital"}), 404
    
    tecnico_data = {
        "codigo": generateCode(6),
        "fechaExpiracion": data['fechaExpiracion'],
        "fechaCreacion": data['fechaCreacion'],
        "hospital": hospital_user['nombre'],
        "nombre": data['nombre'],
        "estado": data['estado'],
        "documento": data['documento'],
        "firma": "",
        "idManteniminetos": [],
        "tipo": data['tecnico']
    }
    usuarios_collection.insert_one(tecnico_data)
    return jsonify({"msg": "Técnico creado exitosamente"}), 201





@app.route('/profesional', methods=['POST'])
@jwt_required()
def create_profesional():
    """
    Ruta para crear un usuario Profesional.
    Se envía un JSON con 'codigo', 'nombre', 'estado', 'hospital', 'fechaCreacion', 'fechaExpiracion', 'tipoProfesional'.
    """

    data = request.get_json()
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400
    
    hospital_user = usuarios_collection.find_one({"tipo": "hospital"})
    if not hospital_user:
        return jsonify({"msg": "No se encontró el hospital"}), 404
    profesional_data = {
        "codigo": generateCode(6),
        "nombre": data['nombre'],
        "documento": data['documento'],
        "estado": data['estado'],
        "hospital": data['hospital'],
        "fechaCreacion": data['fechaCreacion'],
        "fechaExpiracion": data['fechaExpiracion'],
        "tipo": data['profesional'],
    }
    usuarios_collection.insert_one(profesional_data)
    return jsonify({"msg": "Profesional creado exitosamente"}), 201


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
    }
    usuarios_collection.insert_one(encargado_data)
    return jsonify({"msg": "Encargado creado exitosamente"}), 201

@app.route('/hospital', methods=['POST'])
@jwt_required()
def create_hospital():
    """
    Ruta para crear un usuario Encargado.
    Se envía un JSON con 'codigo', 'nombre', 'estado', 'hospital', 'fechaCreacion', 'fechaExpiracion', 'tipoEncargado'.
    """
    data = request.get_json()
    existing_user = usuarios_collection.find_one({"documento": data['documento']})
    if existing_user:
        return jsonify({"msg": "Ya existe un usuario con ese documento"}), 400

   
    hospital_data = {
        "nombre": data['nombre'],
        "hospital": "hospital",
        "fechaCreacion": data['fechaCreacion'],
        "fechaExpiracion": data['fechaExpiracion'],
        "tipo": data['hospital'],
        "dias": data['dias'],
        "codigoIdentificaion":generateCode(4),
        "numeroEquipos": data['numeroEquipos'],
        "numeroAreas": data['numeroAreas'],
        "correoContacto": data['correoContacto'],
        "direccion": data['direccion'],
        "imagen":  data["imagen"],
        "telefono": data['telefono'],
        "proximaVisita": data['proximaVisita'],
        "ultimaVisita": data['ultimaVisita'],
        "responsableMantenimiento": data['responsableMantenimiento'],
        "estadoLicencia": True,
    }
    usuarios_collection.insert_one(hospital_data)
    return jsonify({"msg": "Encargado creado exitosamente"}), 201

### Obtener datos hospital
@app.route('/hospital', methods=['GET'])
@jwt_required()
def get_hospital():
    """
    Ruta para obtener un hospital basado en su tipo.
    """
    hospital = usuarios_collection.find_one({"tipo": "hospital"})  # Assuming 'tipo' is the field you're filtering by
    if not hospital:
        return jsonify({"msg": "No se encontró un hospital con ese tipo"}), 404

    hospital['_id'] = str(hospital['_id'])
    
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
        "tipo": data['responsableArea']
    }
    usuarios_collection.insert_one(responsableArea_data)
    return jsonify({"msg": "Técnico creado exitosamente"}), 201


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
            {"$set": {"estado": False}}
        )       
        return jsonify({"msg": "Estado del técnico actualizado a False"}), 200

#### PATCH /usuario/12345 {"nombre": "Carlos López"} o {"documento":"10203102"}#####
@app.route('/usuario/<id>', methods=['PATCH'])
@jwt_required()
def update_usuario(id):
    """
    Ruta para actualizar un usuario responsableArea.
    Se puede actualizar 'nombre' o 'documento' proporcionando el ObjectId del usuario.
    """
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




@app.route('/usuario/updateexp', methods=['PATCH'])
@jwt_required()
def update_exp():
    """""
    Ruta para actualizar la fecha de expiracion de un usuario,
    parametros: documento, fechaExpiracion, estado
    """

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

########## editar final ##########
##################### users ############################
############### Areas #######################

@app.route('/area', methods=['POST'])
@jwt_required()
def create_area():
    hospital = usuarios_collection.find_one({"tipo":"hospital"})
    codearea = hospital["codigoIdentificacion"] + "-" + generateCode(4)
    data = request.get_json()
    Area = {
        "codigoIdentificacion": codearea,
        "hospital": hospital['nombre'],
        "nombre": data['nombre'],
        "idEquipos": [],
        "respondableArea":data["responsableArea"],
        "documentoResponsableArea":data["documentoResponsableArea"]
    }
    areas_collection.insert_one(Area)

@app.route('/areas', methods=['GET'])
@jwt_required()
def get_all_areas():
    """
    Ruta para obtener todas las áreas.
    """
    areas = areas_collection.find()  # Fetch all areas from the collection
    result = []
    
    for area in areas:
        area['_id'] = str(area['_id'])  # Convert ObjectId to string for JSON serialization
        result.append(area)
    
    return jsonify(result), 200


@app.route('/getarea/<codigo>', methods=['GET'])
@jwt_required()
def get_area():
    data = request.get_json()
    area = areas_collection.find_one({"codigoIdentificacion": data['codigo']})
    if not area:
        return jsonify({"error": "Área no encontrada"}), 404
    return jsonify(area), 200


@app.route('/area/<codigo>', methods=['PUT'])
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


############### Areas Final #######################










############### Equipos #######################
@app.route('/equipo/<codigoIdentificacion>', methods=['GET'])
@jwt_required()
def get_equipo(codigoIdentificacion):
    equipo = equipos_collection.find_one({"codigoIdentificacion": codigoIdentificacion})
    if equipo:
        return jsonify(equipo), 200
    else:
        return jsonify({"error": "Equipo no encontrado"}), 404

@app.route('/equipo', methods=['POST'])
@jwt_required()
def equipo():
    hospital = usuarios_collection.find_one({"tipo":"hospital"})
    area = usuarios_collection.find_one({"tipo":"area"})
    codigoEquipo = hospital["codigoIdentificacion"] + "-" + area["codigoIdentificacon"] + "-" + generateCode(4)
    data = request.get_json()
    equipo = {
        "codigoIdentificacion": codigoEquipo,
        "hospital": hospital['nombre'],
        "area": data["area"],
        "documentoResponsableArea": data["documentoResponsableArea"],
        "Tipo": data.get("Tipo"),                       
        "Marca": data.get("Marca"),
        "Modelo": data.get("Modelo"),
        "Serie": data.get("Serie"),
        "UltimoMantenimiento": "",
        "ProximaVisita": usuarios_collection.find_one({"tipo":"hospital"})["proximaVisita"],
        "HojaVida": [],
        "GuiaRapida": data.get("GuiaRapida"),
        "Manual": data.get("Manual"),
        "Rutinamantenimiento": data.get("Rutinamantenimiento"),
        "Imagen": data.get("Imagen"),
        "ReportesCalibracion": data.get("ReportesCalibracion"),
        "RecomendacionesUso": data.get("RecomendacionesUso"),
    
    }
    equipos_collection.insert_one(equipo)



@app.route('/getequipos/<codigoarea>', methods=['GET'])
@jwt_required()
def get_equipos():
    data = request.get_json()
    area = areas_collection.find_one({"codigoIdentificacion": data['codigoarea']})
    if not area:
        return jsonify({"error": "Área no encontrada"}), 404
    else:
        equipos = equipos_collection.find({"area": area['nombre']})
        return jsonify(equipos), 200


############### Final Equipos #######################


############ Mantenimientos ################
@app.route('/mantenimiento', methods=['POST'])
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

@app.route('/firmar_mantenimiento', methods=['POST'])
@jwt_required()
def firmar_mantenimiento():
    data = request.get_json()
    codigo_identificacion = data["codigoIdentificacionEquipo"]
    numero_reporte = data["numeroReporte"]


    equipo = equipos_collection.find_one({"codigoIdentificacion": codigo_identificacion, "HojaVida.numeroReporte": numero_reporte})
    
    if equipo:

        equipos_collection.update_one(
            {
                "codigoIdentificacion": codigo_identificacion,
                "HojaVida.numeroReporte": numero_reporte
            },
            {
                "$set": {
                    "HojaVida.$.firmaRecibidor": data["firmaRecibidor"],
                    "HojaVida.$.estado": True
                }
            }
        )
        return jsonify({"message": "Mantenimiento actualizado con éxito"}), 200
    else:
        return jsonify({"error": "Mantenimiento o equipo no encontrado"}), 404

 ############ Final Mantenimientos ################   


############## Rutinas ################

@app.route('/rutina', methods=['POST'])
@jwt_required()
def create_rutina():
    hospital = usuarios_collection.find_one({"tipo":"hospital"})
    data = request.get_json()
    Rutina = {
        "hospital": hospital['nombre'],
        "tipoequipo": data['equipo'],
        "preguntas": data['preguntas'],
    }
    rutinas_collection.insert_one(Rutina)

@app.route('/getrutina', methods=['GET'])
@jwt_required()
def get_rutina():
    data = request.get_json()
    rutina = rutinas_collection.find_one({"tipoequipo": data['tipoequipo']})
    if not rutina:
        return jsonify({"error": "Rutina no encontrada para este equipo"}), 404
    return jsonify(rutina), 200
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
    
    # Return the list of codigos
    return jsonify(codigos), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



