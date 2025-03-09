import os
import json
import time  # Importa la biblioteca time
import logging  # Importa el módulo logging
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv  # Añade esta importación

# Carga las variables de entorno al inicio del script
load_dotenv()

# Configuración del logging
logging.basicConfig(level=logging.INFO)  # Configura el nivel de logging a DEBUG
logger = logging.getLogger(__name__)  # Crea un logger

def normalize_value(value):
    """
    Normaliza un valor:
      - Si es None, retorna una cadena vacía.
      - Si es una cadena, elimina espacios al inicio y al final.
      - En otros casos, retorna el valor sin modificar.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value

def normalize_record(record):
    """
    Normaliza un registro (diccionario) recorriendo todos sus campos.
    Si el valor es un diccionario o una lista, se aplica la normalización de forma recursiva.
    """
    normalized = {}
    for key, value in record.items():
        if isinstance(value, dict):
            normalized[key] = normalize_record(value)
        elif isinstance(value, list):
            normalized[key] = [normalize_value(item) for item in value]
        else:
            normalized[key] = normalize_value(value)
    return normalized

# --- Configuración de Credenciales ---
# Elimina los valores por defecto
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# --- Inicialización del Embedding de OpenAI ---
# Se utiliza el modelo "text-embedding-ada-002" (1536 dimensiones)
embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY,
    model="text-embedding-ada-002"
)

# --- Carga y Normalización de Registros desde el Archivo ---
# Cambiar el nombre del archivo de entrada
with open("medicina_en.json", "r", encoding="utf-8") as f:
    raw_records = json.load(f)

# Normalizamos cada registro para evitar problemas de formato
records = [normalize_record(record) for record in raw_records]

# --- Creación de Documentos con Content y Metadata ---
# Modificar los campos según la nueva estructura
documents = []
for record in records:
    #print(record)
    content = (
        f"Medicine: {record.get('Medicine Name', '')}. "
        f"Composition: {record.get('Composition', '')}. "
        f"Uses: {record.get('Uses', '')}. "
        f"Side Effects: {record.get('Side_effects', '')}. "
    )
    
    metadata = {
        "manufacturer": record.get("Manufacturer", ""),
        #"excellent_review": record.get("Excellent Review %", 0),
        "average_review": record.get("Average Review %", 0),
        #"poor_review": record.get("Poor Review %", 0),
        "image_url": record.get("Image URL", "")
    }
    
    documents.append(Document(page_content=content, metadata=metadata))
    #print(documents)

# --- Validación de la Existencia de la Colección en Qdrant ---
collection_name = "vademecum_medicamentos_en"

time.sleep(1)
# Se crea un cliente de Qdrant (usando qdrant_client) para validar la existencia de la colección.
try:
    qdrant_client = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_API_KEY)
    logger.debug("Qdrant client creado exitosamente")
    
    # Verifica si la colección existe
    collections = qdrant_client.get_collections()
    collection_names = [col.name for col in collections.collections]
    logger.debug("Colecciones disponibles: %s", collection_names)  # Log de colecciones

    if collection_name not in collection_names:
        # La colección no existe, se crea con los parámetros indicados:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        logger.info(f"Colección '{collection_name}' creada.")
        
        # --- Creación del Vector Store en Qdrant ---
        vectorstore = QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=collection_name,
            url=QDRANT_CLOUD_URL,
            api_key=QDRANT_API_KEY,
        )
        logger.info("Vector store creado exitosamente en Qdrant.")
    else:
        logger.info(f"Colección '{collection_name}' ya existe.")
        
except Exception as e:
    logger.error("Error al crear el cliente Qdrant o al verificar colecciones: %s", e)
    raise SystemExit("No se puede continuar sin conexión a Qdrant") from e

# --- Inicialización del Vector Store ---
try:
    qdrant_client = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_API_KEY)
    
    # Verificar existencia de la colección
    collection_info = qdrant_client.get_collection(collection_name)
    logger.info(f"Usando colección existente: {collection_name}")
    
    # Inicializar vectorstore para consultas
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings
    )

except Exception as e:
    logger.error("Error al acceder a Qdrant: %s", e)
    raise SystemExit("No se puede conectar a Qdrant") from e

# --- Sistema de Consultas ---
# Actualizar el filtro y parámetros de búsqueda
def hacer_consulta(query: str, k: int = 3):  # Reducir resultados por defecto
    try:
        results = vectorstore.similarity_search(
            query, 
            k=k,
            # Filtro opcional por fabricante
            # filter={"manufacturer": "Sanofi India Ltd"}
        )
        print(f"\n🔍 Resultados para '{query}':")
        for i, doc in enumerate(results, 1):
            print(f"\n💊 Medicamento {i}:")
            print(f"📄 Contenido: {doc.page_content}")
            print(f"🏭 Fabricante: {doc.metadata.get('manufacturer', '')}")
            print(f"⭐ AVG Reviews: {doc.metadata.get('average_review', '')}%")            
            print(f"💊 Photo: {doc.metadata.get('image_url', '')}%")
    except Exception as e:
        logger.error("Error en la consulta: %s", e)

# --- Interfaz de Consultas ---
if __name__ == "__main__":
    while True:
        query = input("\n💊 Ingrese su búsqueda (o 'salir' para terminar): ")
        if query.lower() == 'salir':
            break
        hacer_consulta(query=query)