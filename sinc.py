from pymongo import MongoClient, errors
from datetime import datetime
from config import Centros, uriGeneral, periodicaSinc
import threading
import time
Pares=[]
threads=[]

intro=""" 



███████╗██╗ ██████╗ ███╗   ███╗███████╗    ███████╗██╗███╗   ██╗ ██████╗
██╔════╝██║██╔════╝ ████╗ ████║██╔════╝    ██╔════╝██║████╗  ██║██╔════╝
███████╗██║██║  ███╗██╔████╔██║█████╗      ███████╗██║██╔██╗ ██║██║     
╚════██║██║██║   ██║██║╚██╔╝██║██╔══╝      ╚════██║██║██║╚██╗██║██║     
███████║██║╚██████╔╝██║ ╚═╝ ██║███████╗    ███████║██║██║ ╚████║╚██████╗
╚══════╝╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝
                                                                        

                                                                                                         
                                                                                                                    """
                                                                                                                    
print(intro)
def crear_indices(coleccion, campos_indices):
    for campo in campos_indices:
        coleccion.create_index(campo)
        
        
def inicializar_last_updated(collection):

    collection.update_many(
        {"last_updated": {"$exists": False}},
        {"$set": {"last_updated": datetime.min}}
    )


def generarPares():
    campos_indices = ["last_updated"]  # Agrega más campos si es necesario
    GeneralClient = MongoClient(uriGeneral, serverSelectionTimeoutMS=5000)
    
    for conf in Centros:
        if "name" not in Centros[conf]:  # Ignorar entradas sin nombre de base de datos
            continue
        
        CentroLocal = MongoClient(
            Centros[conf]["uri"], serverSelectionTimeoutMS=5000
        )[Centros[conf]["name"]]
        
        CentroGeneral = GeneralClient[Centros[conf]["name"]]
        
     
        colecciones = [
            "usuarios", "areas", "correctivos", "equipos", 
            "preventivos", "reportes", "tipos"
        ]
        
        # Crear índices y añadir pares
        for coleccion in colecciones:
            crear_indices(CentroLocal[coleccion], campos_indices)
            crear_indices(CentroGeneral[coleccion], campos_indices)
            
            # Añadir pares a la lista
            Pares.append((CentroLocal[coleccion], CentroGeneral[coleccion]))
            Pares.append((CentroGeneral[coleccion], CentroLocal[coleccion]))
    
    print("Pares generados con éxito:", len(Pares))


general = MongoClient(
    'mongodb://localhost:27017',
    serverSelectionTimeoutMS=5000  # Tiempo de espera para conexiones
)
db1 = general["Sigme2"]
collection1 = db1['usuarios']



client2 = MongoClient(
    'mongodb://localhost:27017',
    serverSelectionTimeoutMS=5000
)
db2 = client2['Sigme']
collection2 = db2['usuarios']

# Crear índices en las colecciones
collection1.create_index('last_updated')
collection2.create_index('last_updated')

def sync_document(source_doc, target_collection):
    """Sincroniza un documento único respetando el principio de 'último cambio gana'."""
    # Obtiene el documento correspondiente de la colección de destino
    target_doc = target_collection.find_one({'_id': source_doc['_id']})
    
    # Verifica si 'last_updated' existe en source_doc
    if 'last_updated' not in source_doc:
        print(f"Advertencia: El documento con _id={source_doc['_id']} no tiene 'last_updated'. No se sincronizará.")
        return

    # Sincroniza si no existe en el destino o si el documento fuente es más reciente
    if not target_doc or source_doc['last_updated'] > target_doc.get('last_updated', datetime.min):
        target_collection.replace_one({'_id': source_doc['_id']}, source_doc, upsert=True)
        print(f"Documento con _id={source_doc['_id']} sincronizado.")
    else:
        print(f"Documento con _id={source_doc['_id']} ya está actualizado.")
   
        
def sync_document2(source_doc, target_collection):
    """Sincroniza un documento único respetando el principio de 'último cambio gana'."""
    # Obtiene el documento correspondiente de la colección de destino
    target_doc = target_collection.find_one({'_id': source_doc['_id']})
    
    # Verifica si 'last_updated' existe en source_doc
    if 'last_updated' not in source_doc:
        print(f"Advertencia: El documento con _id={source_doc['_id']} no tiene 'last_updated'. No se sincronizará.")
        return

    # Sincroniza si no existe en el destino o si el documento fuente es más reciente
    if not target_doc or source_doc['last_updated'] > target_doc.get('last_updated', datetime.min):
        target_collection.replace_one({'_id': source_doc['_id']}, source_doc, upsert=True)
       
    else:
      pass


def sync_initial(source_collection, target_collection):
    """Sincroniza todos los documentos entre colecciones."""
    try:
        source_docs = source_collection.find({'last_updated': {'$exists': True}})
        for doc in source_docs:
            sync_document2(doc, target_collection)
    except errors.PyMongoError as e:
        print(f"Error en sincronización inicial: {e}")

def change_stream_listener(source_collection, target_collection):
    """Escucha cambios en tiempo real en una colección y los sincroniza."""
    try:
        with source_collection.watch(
            pipeline=[
                {'$match': {'operationType': {'$in': ['insert', 'update', 'replace', 'delete']}}}
            ],
            full_document='updateLookup'
        ) as stream:
            for change in stream:
                if change['operationType'] in ['insert', 'update', 'replace']:
                    updated_doc = change['fullDocument']
                    if updated_doc:
                        sync_document(updated_doc, target_collection)
                elif change['operationType'] == 'delete':
                    target_collection.delete_one({'_id': change['documentKey']['_id']})
    except errors.PyMongoError as e:
        print(f"Error en Change Stream: {e}. Reiniciando...")
        time.sleep(5)  # Esperar antes de reiniciar el listener
        change_stream_listener(source_collection, target_collection)

def start_sync():
    """Inicia la sincronización inicial, los Change Streams y la sincronización periódica."""
    print("Iniciando sincronización inicial...")
 

    generarPares()
    for local, general in Pares:
      sync_initial(local, general)
      sync_initial(general,local)
    print("Verificacando el campo lastUpdate en todos los documentos..")
    for local, general in Pares:
        inicializar_last_updated(local)
        inicializar_last_updated(general)
    print("Iniciando escucha de Change Streams...")
    for col1, col2 in Pares:
        thread = threading.Thread(target=change_stream_listener, args=(col1, col2))
        threads.append(thread)
        thread.start()
       
    print("Iniciando sincronización periódica...")
    print("!Sincronizacion existosa!")
    print("Esperando cambios")
    while True:
        try:
            time.sleep(periodicaSinc)  # Ejecutar cada 10 minutos
            print("Ejecutando sincronización inicial periódica...")
            for local, general in Pares:
                sync_initial(local, general)
                sync_initial(general,local)
        except KeyboardInterrupt:
            print("Sincronización detenida manualmente.")
            break
        except errors.PyMongoError as e:
            print(f"Error en sincronización periódica: {e}")

if __name__ == "__main__":
    try:
        start_sync()
    except errors.ConnectionFailure as e:
        print(f"Error de conexión: {e}")


