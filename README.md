# 🏥 Sistema de Búsqueda de Medicamentos con IA

Un sistema inteligente para buscar medicamentos usando embeddings de OpenAI y almacenamiento vectorial en Qdrant. Desarrollado para consultar información farmacéutica de manera eficiente.

## 🚀 Características Principales
- Búsqueda semántica de medicamentos
- Información detallada: composición, usos, efectos secundarios
- Filtrado por fabricante y reseñas
- Integración con OpenAI y Qdrant Cloud

## ⚙️ Requisitos
- Python 3.10+
- Cuentas en [OpenAI](https://platform.openai.com/) y [Qdrant Cloud](https://cloud.qdrant.io/)

## 📦 Instalación
```bash
git clone https://github.com/tu-usuario/qdrant_farmacias_chat2.git
cd qdrant_farmacias_chat2
pip install -r requirements.txt
```

## 🔐 Configuración
1. Crea un archivo `.env` con tus credenciales:
```ini
OPENAI_API_KEY=tu_clave_openai
QDRANT_CLOUD_URL=tu_url_qdrant
QDRANT_API_KEY=tu_clave_qdrant
```

## 🧠 Uso del Sistema
```bash
python app.py
```

Ejemplo de búsqueda:
```python
>>> Ingrese su búsqueda (o 'salir' para terminar): medicina para dolor de cabeza con menos efectos secundarios

🔍 Resultados para 'medicina para dolor de cabeza con menos efectos secundarios':

💊 Medicamento 1:
📄 Contenido: Medicine: Dolofort. Composition: Paracetamol 650mg...
🏭 Fabricante: Sanofi India Ltd
⭐ AVG Reviews: 78%
💊 Photo: https://ejemplo.com/imagen.jpg
```

## ⚠️ Seguridad
Nunca compartas ni subas tu archivo `.env` con las claves API

## 📄 Licencia
MIT License 