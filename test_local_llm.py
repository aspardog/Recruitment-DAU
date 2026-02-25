#!/usr/bin/env python3
"""
Script de Prueba para LLM Local
Verifica que el LLM local esté configurado correctamente antes de ejecutar el sistema completo.

USO:
    python test_local_llm.py

REQUISITOS:
    - Ollama/LM Studio/llama.cpp instalado y corriendo
    - Modelo descargado
    - Variables de entorno configuradas en .env
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Code directory to path
code_dir = Path(__file__).parent / "Code"
parameters_dir = Path(__file__).parent / "Parameters"
sys.path.insert(0, str(code_dir))
sys.path.insert(0, str(parameters_dir))

print("="*70)
print("PRUEBA DE LLM LOCAL - Sistema de Evaluación de CVs")
print("="*70)
print()

# Check configuration
print("📋 VERIFICANDO CONFIGURACIÓN...")
print()

use_local_llm = os.environ.get('USE_LOCAL_LLM', 'false').lower() == 'true'
backend = os.environ.get('LOCAL_LLM_BACKEND', 'ollama')
model = os.environ.get('LOCAL_LLM_MODEL', 'llama3.1:8b')

print(f"USE_LOCAL_LLM: {use_local_llm}")
print(f"LOCAL_LLM_BACKEND: {backend}")
print(f"LOCAL_LLM_MODEL: {model}")
print()

if not use_local_llm:
    print("❌ ERROR: USE_LOCAL_LLM no está configurado como 'true'")
    print()
    print("Para usar LLM local, edita tu archivo .env y configura:")
    print("  USE_LOCAL_LLM=true")
    print("  LOCAL_LLM_BACKEND=ollama")
    print("  LOCAL_LLM_MODEL=llama3.1:8b")
    print()
    sys.exit(1)

# Import local LLM analyzer
print("📦 IMPORTANDO ANALIZADOR LOCAL...")
print()

try:
    from local_llm_analyzer import LocalLLMAnalyzer
    print("✓ LocalLLMAnalyzer importado correctamente")
    print()
except ImportError as e:
    print(f"❌ ERROR: No se pudo importar LocalLLMAnalyzer")
    print(f"   Detalle: {e}")
    print()
    print("Soluciones:")
    if backend == 'ollama':
        print("  1. Instala Ollama: brew install ollama")
        print("  2. Inicia Ollama: ollama serve")
        print("  3. Instala el paquete Python: pip install ollama")
    elif backend == 'lmstudio':
        print("  1. Descarga LM Studio: https://lmstudio.ai/")
        print("  2. Inicia el servidor local en LM Studio")
        print("  3. Instala el paquete Python: pip install openai")
    elif backend == 'llamacpp':
        print("  1. Instala llama-cpp-python: pip install llama-cpp-python")
        print("  2. Descarga un modelo GGUF")
        print("  3. Configura LOCAL_LLM_MODEL_PATH en .env")
    print()
    sys.exit(1)

# Initialize analyzer
print("🚀 INICIALIZANDO ANALIZADOR...")
print()

try:
    analyzer = LocalLLMAnalyzer()
    print("✓ Analizador inicializado correctamente")
    print()
except Exception as e:
    print(f"❌ ERROR al inicializar el analizador:")
    print(f"   {e}")
    print()
    print("Verifica que:")
    if backend == 'ollama':
        print("  - Ollama esté corriendo: ollama serve")
        print("  - El modelo esté descargado: ollama pull llama3.1:8b")
        print("  - Verifica modelos instalados: ollama list")
    elif backend == 'lmstudio':
        print("  - LM Studio esté corriendo")
        print("  - El servidor local esté iniciado en LM Studio")
        print("  - El puerto sea 1234 (default)")
    elif backend == 'llamacpp':
        print("  - El archivo del modelo exista en la ruta especificada")
        print("  - La ruta sea correcta en LOCAL_LLM_MODEL_PATH")
    print()
    sys.exit(1)

# Test CV
print("📄 CV DE PRUEBA...")
print()

test_cv = """
Juan Pérez
Analista de Datos

EDUCACIÓN:
- Maestría en Ciencia de Datos, Universidad Nacional (2020-2022)
- Licenciatura en Estadística, Universidad Pública (2015-2019)

EXPERIENCIA:
- Analista de Datos Senior, Tech Corp (2022-presente)
  • Análisis de datos con Python y R
  • Desarrollo de modelos de machine learning
  • Visualización de datos con Tableau

- Analista Junior, Data Company (2020-2022)
  • Limpieza y procesamiento de datos
  • Análisis estadístico con R
  • Reportes en SQL

HABILIDADES TÉCNICAS:
- Lenguajes: Python (avanzado), R (avanzado), SQL (intermedio)
- Machine Learning: scikit-learn, TensorFlow, pandas
- Control de versiones: Git, GitHub
- Análisis estadístico: regresión, análisis multivariado
- Visualización: matplotlib, seaborn, ggplot2

IDIOMAS:
- Español (nativo)
- Inglés (fluido - TOEFL 105/120)

PROYECTOS:
- Sistema de predicción de ventas usando LSTM (Python)
- Análisis de sentimiento en redes sociales (R)
- Dashboard interactivo para KPIs de negocio (Tableau)
"""

print(test_cv[:300] + "...")
print()

# Analyze CV
print("🔍 ANALIZANDO CV CON LLM LOCAL...")
print("   (Esto puede tomar 10-30 segundos dependiendo de tu hardware)")
print()

try:
    import time
    start_time = time.time()

    result = analyzer.analyze_cv(test_cv)

    elapsed_time = time.time() - start_time

    print(f"✓ Análisis completado en {elapsed_time:.1f} segundos")
    print()

except Exception as e:
    print(f"❌ ERROR durante el análisis:")
    print(f"   {e}")
    print()
    print("Posibles causas:")
    print("  - El modelo no está respondiendo en formato JSON")
    print("  - Memoria insuficiente")
    print("  - El servicio se detuvo durante el análisis")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Display results
print("="*70)
print("📊 RESULTADOS DEL ANÁLISIS")
print("="*70)
print()

print(f"Required Skills:   {result['required_skills']['percentage']:>6.1f}%")
print(f"Preferred Skills:  {result['preferred_skills']['percentage']:>6.1f}%")
print(f"Education:         {result['education']['percentage']:>6.1f}%")
print(f"Experience:        {result['experience']['percentage']:>6.1f}%")
print()
print(f"Match Rate Total:  {result['summary']['match_rate']:>6.1f}%")
print()

# Show some details
print("="*70)
print("📝 DETALLE DE ALGUNAS SKILLS")
print("="*70)
print()

# Show top 3 required skills
print("Top Required Skills:")
req_skills = result['required_skills']['details']
sorted_req = sorted(req_skills.items(), key=lambda x: x[1]['llm_raw_score'], reverse=True)[:3]

for skill_name, skill_data in sorted_req:
    score = skill_data['llm_raw_score']
    evidence = skill_data['evidence'][:100] + "..." if len(skill_data['evidence']) > 100 else skill_data['evidence']
    print(f"  • {skill_name}: {score}/100")
    print(f"    Evidencia: {evidence}")
    print()

# Success message
print("="*70)
print("✅ PRUEBA EXITOSA - El LLM local está funcionando correctamente")
print("="*70)
print()
print("Próximos pasos:")
print("  1. Coloca tus CVs en PDF en la carpeta 'Data Analyst/'")
print("  2. Ejecuta: python main.py")
print("  3. Revisa los resultados en la carpeta 'Finalists/'")
print()
print(f"Rendimiento estimado para 2000 CVs:")
print(f"  - Tiempo aproximado: {2000 * elapsed_time / 60:.0f} minutos ({2000 * elapsed_time / 3600:.1f} horas)")
print(f"  - Costo: $0 (100% local y privado)")
print()
print("🔒 PRIVACIDAD GARANTIZADA: Todos tus datos permanecen en tu computadora")
print()
