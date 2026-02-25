# Guía de Instalación de LLM Local

## 🔒 Garantía de Privacidad

Cuando usas un LLM local:
- ✅ Todos los CVs permanecen en tu computadora
- ✅ No hay llamadas a APIs externas
- ✅ No necesitas conexión a internet (después de descargar el modelo)
- ✅ Los datos nunca salen de tu máquina
- ✅ Sin costos por uso de API

---

## 🎯 OPCIÓN 1: Ollama (RECOMENDADA)

### ¿Por qué Ollama?
- ✅ Más fácil de instalar y usar
- ✅ Gestión automática de modelos
- ✅ Mejor rendimiento optimizado
- ✅ Actualizaciones automáticas

### Paso 1: Instalar Ollama

```bash
# En macOS (tu sistema):
brew install ollama

# Inicia el servicio de Ollama
ollama serve
```

**Nota**: Deja esta terminal abierta con `ollama serve` corriendo. Abre una nueva terminal para los siguientes pasos.

### Paso 2: Descargar un Modelo

En una **nueva terminal**, ejecuta:

```bash
# Modelo recomendado para 8GB RAM + CPU
ollama pull qwen2.5:3b
```

**Modelos según tu hardware:**

### Para 8GB RAM + CPU (modelos ligeros):

| Modelo | Tamaño | RAM | Velocidad | Calidad | Comando |
|--------|--------|-----|-----------|---------|---------|
| `qwen2.5:3b` | 2 GB | ~4 GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **RECOMENDADO** |
| `phi3:mini` | 2.3 GB | ~4 GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Excelente para instrucciones |
| `llama3.2:3b` | 2 GB | ~4 GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Buena calidad |
| `gemma2:2b` | 1.6 GB | ~3 GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Más ligero |

### Para 16GB+ RAM:

| Modelo | Tamaño | RAM | Velocidad | Calidad |
|--------|--------|-----|-----------|---------|
| `llama3.1:8b` | 4.7 GB | ~8 GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| `qwen2.5:7b` | 4.7 GB | ~8 GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| `mistral:7b` | 4.1 GB | ~8 GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |

```bash
# Descargar modelo ligero (8GB RAM):
ollama pull qwen2.5:3b

# Descargar modelo completo (16GB+ RAM):
ollama pull llama3.1:8b
```

### Paso 3: Instalar librería Python

```bash
pip install ollama
```

### Paso 4: Configurar variables de entorno

Edita tu archivo `.env`:

```bash
# En la raíz del proyecto
nano .env
```

Asegúrate de que tenga:

```
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b
```

(Cambia `qwen2.5:3b` por otro modelo si lo prefieres)

### Paso 5: Probar que funciona

```bash
# Prueba rápida
ollama run llama3.1:8b "Hola, ¿cómo estás?"

# Debería responder en español
# Presiona Ctrl+D para salir
```

### Paso 6: Ejecutar el sistema

```bash
# Asegúrate de que ollama serve esté corriendo en otra terminal
python main.py
```

**¡Listo!** Ahora el sistema usa LLM 100% local y privado.

---

## 🎯 OPCIÓN 2: LM Studio (Con Interfaz Gráfica)

### ¿Por qué LM Studio?
- ✅ Interfaz gráfica fácil de usar
- ✅ No necesitas usar la terminal para gestionar modelos
- ✅ Buen rendimiento
- ❌ Menos automatizado que Ollama

### Paso 1: Descargar e Instalar LM Studio

1. Ve a: https://lmstudio.ai/
2. Descarga para macOS
3. Instala la aplicación

### Paso 2: Descargar un Modelo

1. Abre LM Studio
2. Ve a la pestaña "Search"
3. Busca: `llama-3.1-8b-instruct`
4. Descarga el modelo (versión Q4_K_M recomendada - balance entre tamaño y calidad)

**Modelos recomendados en LM Studio:**
- `meta-llama-3.1-8b-instruct-Q4_K_M.gguf` - Recomendado
- `mistral-7b-instruct-v0.2-Q4_K_M.gguf` - Más rápido
- `neural-chat-7b-v3-3-Q4_K_M.gguf` - Bueno para chat

### Paso 3: Iniciar el Servidor Local

1. En LM Studio, ve a la pestaña "Local Server"
2. Selecciona el modelo descargado
3. Click en "Start Server"
4. Debería mostrar: "Server running on http://localhost:1234"

### Paso 4: Instalar librería Python

```bash
pip install openai
```

### Paso 5: Configurar variables de entorno

Edita tu archivo `.env`:

```
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=lmstudio
LOCAL_LLM_MODEL=local-model
```

### Paso 6: Ejecutar el sistema

```bash
python main.py
```

---

## 🎯 OPCIÓN 3: llama-cpp-python (Avanzada)

### ¿Por qué llama-cpp-python?
- ✅ Máximo control sobre el modelo
- ✅ Mejor rendimiento en algunos casos
- ❌ Configuración más compleja
- ❌ Requiere descargar modelos manualmente

### Paso 1: Instalar llama-cpp-python

```bash
# Instalación básica (solo CPU)
pip install llama-cpp-python

# Instalación con soporte para Metal (GPU en Mac - RECOMENDADO)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### Paso 2: Descargar un Modelo GGUF

Ve a HuggingFace y descarga un modelo en formato GGUF:

**Recomendados:**
- Llama 3.1 8B: https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF
- Mistral 7B: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

Descarga el archivo `.gguf` (recomendado: versión Q4_K_M)

Ejemplo:
```bash
# Crear directorio para modelos
mkdir -p ~/llm-models
cd ~/llm-models

# Descargar con wget o manualmente desde el navegador
# Ejemplo: Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

### Paso 3: Configurar variables de entorno

Edita tu archivo `.env`:

```
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=llamacpp
LOCAL_LLM_MODEL_PATH=/Users/tuusuario/llm-models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

Cambia la ruta al lugar donde descargaste el modelo.

### Paso 4: Ejecutar el sistema

```bash
python main.py
```

---

## 🔍 Verificación y Pruebas

### Probar el LLM Local

Crea un archivo de prueba `test_local_llm.py`:

```python
from Code.local_llm_analyzer import LocalLLMAnalyzer

# Inicializar analizador local
analyzer = LocalLLMAnalyzer()

# CV de prueba
test_cv = """
John Doe
Software Engineer

Skills:
- Python (5 years)
- R programming
- Machine Learning
- Git

Education:
Master's in Computer Science
Universidad Nacional

Experience:
Data Analyst at Tech Company (2 years)
"""

# Analizar
print("Analizando CV con LLM local...")
result = analyzer.analyze_cv(test_cv)

# Mostrar resultados
print(f"\nResultados:")
print(f"Required Skills: {result['required_skills']['percentage']:.1f}%")
print(f"Education: {result['education']['percentage']:.1f}%")
print(f"Match rate: {result['summary']['match_rate']:.1f}%")
```

Ejecuta:
```bash
python test_local_llm.py
```

---

## 📊 Comparación de Rendimiento

### Para 2000 CVs:

| Método | Tiempo | Costo | Privacidad | RAM Necesaria |
|--------|--------|-------|------------|---------------|
| **Groq (cloud)** | 40 min | $0.60 | ❌ Cloud | 2 GB |
| **Ollama (llama3.1:8b)** | 2-3 horas | $0 | ✅ 100% local | 8 GB |
| **Ollama (llama3.1:70b)** | 8-10 horas | $0 | ✅ 100% local | 64 GB |
| **LM Studio** | 2-3 horas | $0 | ✅ 100% local | 8 GB |

**Nota**: El tiempo puede variar según tu procesador. En un Mac M1/M2/M3, el rendimiento es excelente.

---

## ⚡ Optimización de Rendimiento

### 1. Usar GPU (Metal en Mac)

Si usas llama-cpp-python, instala con soporte Metal:

```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall
```

### 2. Ajustar temperatura

En `.env`:
```
LLM_TEMPERATURE=0.1  # Más bajo = más consistente
```

### 3. Usar modelos cuantizados

Los modelos Q4_K_M son 4x más pequeños que los originales con ~95% de la calidad.

### 4. Procesar en lotes

El sistema ya usa caché automático. Los CVs ya analizados no se vuelven a procesar.

---

## 🐛 Solución de Problemas

### Error: "Ollama not running"

**Solución:**
```bash
# Asegúrate de que ollama esté corriendo
ollama serve
```

### Error: "Model not found"

**Solución:**
```bash
# Descarga el modelo
ollama pull llama3.1:8b

# Verifica que esté instalado
ollama list
```

### Error: "Out of memory"

**Solución:**
- Usa un modelo más pequeño: `mistral:7b` en lugar de `llama3.1:70b`
- Cierra otras aplicaciones
- Considera usar la versión Q4 o Q5 del modelo (más comprimida)

### El análisis es muy lento

**Solución:**
- Usa un modelo más pequeño (7B-8B en lugar de 70B)
- Verifica que estés usando GPU (Metal en Mac)
- Reduce `LLM_MAX_TOKENS` en `Parameters/model_parameters.py`

### El LLM no retorna JSON válido

**Solución:**
- Asegúrate de que el modelo sea reciente (Llama 3.1+, Mistral v0.2+)
- Aumenta `LLM_MAX_RETRIES` en `Parameters/model_parameters.py`
- El sistema tiene reintentos automáticos

---

## 🔄 Cambiar entre Local y Cloud

### Para volver a usar Groq (cloud):

Edita `.env`:
```
USE_LOCAL_LLM=false
GROQ_API_KEY=tu_api_key_aqui
```

### Para volver a usar Local:

Edita `.env`:
```
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
```

---

## 📝 Recomendaciones Finales

**Para tu caso (privacidad en CVs):**

1. ✅ **Usa Ollama** - Es la opción más fácil y eficiente
2. ✅ **Modelo: llama3.1:8b** - Balance perfecto entre velocidad y calidad
3. ✅ **Deja el caché activado** - Evita reprocesar CVs
4. ✅ **Procesa por lotes** - Deja correr el sistema durante la noche si tienes muchos CVs

**Configuración óptima para privacidad y rendimiento:**

```env
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.1
CACHE_ENABLED=true
```

Con esta configuración:
- 100% privado y local
- Buena velocidad de análisis
- Excelente calidad de resultados
- Sin costos por API
- Cache para evitar reprocesar CVs ya analizados

---

## 🆘 Soporte

Si tienes problemas:

1. Verifica que el servicio esté corriendo (`ollama serve` o LM Studio)
2. Revisa los logs en la terminal
3. Prueba con el script de prueba `test_local_llm.py`
4. Verifica que tengas suficiente RAM disponible
5. Consulta la documentación oficial:
   - Ollama: https://ollama.ai/
   - LM Studio: https://lmstudio.ai/docs
