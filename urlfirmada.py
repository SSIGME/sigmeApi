from google.cloud import storage
import datetime

# Reemplaza con la ruta a tu archivo de clave privada
key_file_path = "userviewer.json"

# Reemplaza con el nombre de tu bucket y el nombre del objeto
bucket_name = "sigme-resources"
object_name = "ISAK/NZ730089933.pdf"

# Crea un cliente de Cloud Storage
storage_client = storage.Client.from_service_account_json(key_file_path)
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(object_name)

# Genera la URL firmada con una duración de 1 hora
url = blob.generate_signed_url(
    version="v4",
    expiration=datetime.timedelta(hours=1),
    method="GET",
)

print(f"URL firmada: {url}")
