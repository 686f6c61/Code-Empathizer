#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Utilidades para Interacción con GitHub API
=============================================================================

Este módulo proporciona una interfaz para interactuar con la API de GitHub,
permitiendo descargar y analizar repositorios públicos para Code Empathizer.

FUNCIONALIDADES PRINCIPALES:
---------------------------
- Autenticación con token de GitHub (Personal Access Token)
- Descarga selectiva de archivos de código fuente
- Extracción inteligente de contenido por extensión
- Manejo de rate limiting con reintentos automáticos
- Caché de resultados para optimizar llamadas repetidas
- Soporte para múltiples formatos de URL de repositorios

FORMATOS DE URL SOPORTADOS:
--------------------------
- https://github.com/user/repo
- https://github.com/user/repo.git
- git@github.com:user/repo.git
- user/repo (formato corto)

LÍMITES DE ARCHIVOS POR TAMAÑO DE REPOSITORIO:
---------------------------------------------
Para evitar exceder los límites de la API de GitHub, se aplican límites
dinámicos según el tamaño del repositorio:
    - Pequeños (<50 archivos):   150 archivos máximo
    - Medianos (50-200):         80 archivos máximo
    - Grandes (200-500):         40 archivos máximo
    - Muy grandes (>500):        20 archivos máximo

EJEMPLO DE USO:
--------------
    >>> from github_utils import GitHubRepo
    >>> repo = GitHubRepo()  # Usa GITHUB_TOKEN del .env
    >>> files = repo.get_repository_files("facebook/react")
    >>> print(f"Descargados {len(files)} archivos")

DEPENDENCIAS:
------------
- PyGithub: Cliente oficial de la API de GitHub
- python-dotenv: Para cargar el token desde .env

VARIABLES DE ENTORNO:
--------------------
- GITHUB_TOKEN: Token de acceso personal con permisos public_repo

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

# =============================================================================
# IMPORTACIONES
# =============================================================================
# Cliente oficial de GitHub para Python
from github import Github, GithubException, Auth

# Librerías estándar
import os                    # Operaciones del sistema de archivos
from typing import Dict, Any, List  # Type hints
import tempfile              # Directorios temporales
import logging               # Sistema de logging
from pathlib import Path     # Manejo de rutas
import ast                   # Análisis de sintaxis Python
import re                    # Expresiones regulares
import pytz                  # Zonas horarias
import time                  # Funciones de tiempo
import yaml                  # Parser YAML
from datetime import datetime  # Manejo de fechas

# Módulos internos
from language_analyzers.factory import AnalyzerFactory  # Factory de analizadores

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class GitHubRepo:
    """
    Cliente para interactuar con repositorios de GitHub.
    
    Esta clase proporciona métodos para analizar repositorios de GitHub,
    extrayendo código fuente y calculando métricas de calidad mediante
    los analizadores de lenguaje disponibles.
    
    Gestiona automáticamente los límites de la API de GitHub y proporciona
    reintentos cuando se alcanzan los límites de velocidad.
    
    Attributes:
        token (str): Token de autenticación de GitHub.
        github (Github): Cliente de PyGithub.
    
    Raises:
        ValueError: Si no se encuentra el token de GitHub en las variables
            de entorno.
    """
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Token de GitHub no encontrado")
        auth = Auth.Token(self.token)
        self.github = Github(auth=auth)
        self.config = self._cargar_config()

    def _cargar_config(self) -> Dict[str, Any]:
        """Carga la configuración desde config.yaml"""
        try:
            config_path = Path(__file__).parent.parent / "config.yaml"
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar config.yaml: {e}. Usando valores por defecto.")
            return {
                'github': {
                    'file_limits': {
                        'small_repos': {'max_files': 150, 'threshold_kb': 0},
                        'medium_repos': {'max_files': 80, 'threshold_kb': 10000},
                        'large_repos': {'max_files': 40, 'threshold_kb': 50000},
                        'very_large_repos': {'max_files': 20, 'threshold_kb': 100000}
                    }
                }
            }

    def _get_max_files_limit(self, repo_size_kb: int) -> int:
        """Obtiene el límite de archivos según el tamaño del repositorio"""
        limits = self.config.get('github', {}).get('file_limits', {})

        if repo_size_kb > limits.get('very_large_repos', {}).get('threshold_kb', 100000):
            return limits.get('very_large_repos', {}).get('max_files', 20)
        elif repo_size_kb > limits.get('large_repos', {}).get('threshold_kb', 50000):
            return limits.get('large_repos', {}).get('max_files', 40)
        elif repo_size_kb > limits.get('medium_repos', {}).get('threshold_kb', 10000):
            return limits.get('medium_repos', {}).get('max_files', 80)
        else:
            return limits.get('small_repos', {}).get('max_files', 150)

    def analizar_repo(self, repo_name: str) -> Dict[str, Any]:
        """Analiza un repositorio y retorna sus métricas"""
        try:
            repo = self.github.get_repo(repo_name)
            
            # Obtener metadata básica
            metadata = {
                "nombre": repo.name,
                "url": repo.html_url,
                "descripcion": repo.description or "Sin descripción",
                "url_clone": repo.clone_url,
                "rama_default": repo.default_branch,
                "fecha_creacion": repo.created_at.isoformat(),
                "fecha_ultimo_push": repo.pushed_at.isoformat(),
                "lenguaje_principal": repo.language or "No especificado",
                "tamano_kb": float(repo.size)
            }
            
            # Límite de archivos según configuración
            MAX_FILES_TO_ANALYZE = self._get_max_files_limit(repo.size)

            # Advertencia para repositorios grandes
            large_threshold = self.config.get('github', {}).get('file_limits', {}).get('large_repos', {}).get('threshold_kb', 50000)
            if repo.size > large_threshold:
                logger.warning(f"⚠️  Repositorio grande detectado ({repo.size/1024:.1f}MB). Limitando análisis a {MAX_FILES_TO_ANALYZE} archivos.")
                print(f"\n⚠️  Repositorio grande detectado ({repo.size/1024:.1f}MB)")
                print(f"   Analizando hasta {MAX_FILES_TO_ANALYZE} archivos para optimizar el tiempo de análisis...")
                print(f"   Para un análisis completo, considere clonar el repositorio localmente.")
            
            # Obtener archivos de código soportados
            archivos_codigo = {}
            archivos_analizados = 0
            extensiones_soportadas = AnalyzerFactory.get_supported_extensions()
            
            try:
                # Para repos muy grandes, usar estrategia optimizada
                if repo.size > 30000:  # Más de 30MB
                    print(f"   🚀 Usando estrategia de análisis rápido...")
                    contents = repo.get_contents("")
                    
                    # Primero analizar archivos en la raíz
                    root_files = [f for f in contents if f.type == "file"]
                    subdirs = [d for d in contents if d.type == "dir"][:5]  # Solo primeros 5 directorios
                    
                    # Procesar archivos de la raíz
                    for file_content in root_files:
                        if archivos_analizados >= MAX_FILES_TO_ANALYZE:
                            break
                        for ext in extensiones_soportadas:
                            if file_content.path.endswith(ext):
                                try:
                                    if file_content.size > 1024 * 1024:  # Saltar archivos > 1MB
                                        break
                                    contenido = file_content.decoded_content.decode('utf-8')
                                    archivos_codigo[file_content.path] = contenido
                                    archivos_analizados += 1
                                    if archivos_analizados % 10 == 0:
                                        print(f"   📄 {archivos_analizados} archivos analizados...")
                                except Exception as e:
                                    logger.warning(f"Error leyendo {file_content.path}: {str(e)}")
                                break
                    
                    # Procesar solo algunos subdirectorios
                    for subdir in subdirs:
                        if archivos_analizados >= MAX_FILES_TO_ANALYZE:
                            break
                        try:
                            subdir_contents = repo.get_contents(subdir.path)
                            for file_content in subdir_contents[:20]:  # Max 20 archivos por subdirectorio
                                if archivos_analizados >= MAX_FILES_TO_ANALYZE:
                                    break
                                if file_content.type == "file":
                                    for ext in extensiones_soportadas:
                                        if file_content.path.endswith(ext):
                                            try:
                                                if file_content.size > 1024 * 1024:
                                                    break
                                                contenido = file_content.decoded_content.decode('utf-8')
                                                archivos_codigo[file_content.path] = contenido
                                                archivos_analizados += 1
                                                if archivos_analizados % 10 == 0:
                                                    print(f"   📄 {archivos_analizados} archivos analizados...")
                                            except Exception as e:
                                                logger.warning(f"Error leyendo {file_content.path}: {str(e)}")
                                            break
                        except:
                            continue
                else:
                    # Estrategia normal para repos pequeños
                    contents = repo.get_contents("")
                    while contents and archivos_analizados < MAX_FILES_TO_ANALYZE:
                        file_content = contents.pop(0)
                        if file_content.type == "dir":
                            # Solo añadir directorios si no hemos alcanzado el límite
                            if archivos_analizados < MAX_FILES_TO_ANALYZE:
                                contents.extend(repo.get_contents(file_content.path))
                        else:
                            # Verificar si el archivo tiene una extensión soportada
                            for ext in extensiones_soportadas:
                                if file_content.path.endswith(ext):
                                    try:
                                        # Saltar archivos muy grandes (más de 1MB)
                                        if file_content.size > 1024 * 1024:
                                            logger.info(f"Saltando archivo grande: {file_content.path} ({file_content.size/1024:.1f}KB)")
                                            break
                                            
                                        contenido = repo.get_contents(file_content.path).decoded_content.decode('utf-8')
                                        archivos_codigo[file_content.path] = contenido
                                        archivos_analizados += 1
                                        
                                        # Mostrar progreso cada 10 archivos para repos grandes
                                        if archivos_analizados % 10 == 0:
                                            print(f"   📄 {archivos_analizados} archivos analizados...")
                                            
                                        # Verificar límite
                                        if archivos_analizados >= MAX_FILES_TO_ANALYZE:
                                            logger.info(f"Límite de {MAX_FILES_TO_ANALYZE} archivos alcanzado")
                                            break
                                    except Exception as e:
                                        logger.warning(f"Error leyendo {file_content.path}: {str(e)}")
                                    break
            except Exception as e:
                logger.error(f"Error obteniendo contenido del repo: {str(e)}")

            # Inicializar métricas con valores numéricos
            metricas_totales = {
                'metadata': metadata,
                'nombres': {'descriptividad': 0.0},
                'documentacion': {'cobertura_docstrings': 0.0},
                'modularidad': {
                    'funciones_por_archivo': 0.0,
                    'clases_por_archivo': 0.0,
                    'cohesion_promedio': 0.0,
                    'acoplamiento_promedio': 0.0
                },
                'complejidad': {
                    'complejidad_ciclomatica': 0.0,
                    'max_nivel_anidacion': 0.0,
                    'longitud_promedio_funciones': 0.0
                },
                'manejo_errores': {
                    'cobertura_manejo_errores': 0.0,
                    'especificidad_excepciones': 0.0,
                    'densidad_try_except': 0.0
                },
                'pruebas': {
                    'cobertura_pruebas': 0.0,
                    'densidad_asserts': 0.0,
                    'funciones_test': 0.0
                },
                'seguridad': {
                    'validacion_entradas': 0.0,
                    'uso_funciones_peligrosas': 1.0,
                    'total_validaciones': 0.0
                },
                'consistencia_estilo': {
                    'consistencia_nombres': 0.0,
                    'espaciado_consistente': 0.0,
                    'longitud_lineas_consistente': 0.0
                }
            }

            # Actualizar metadata con archivos analizados
            metadata['archivos_analizados'] = archivos_analizados
            if archivos_analizados >= MAX_FILES_TO_ANALYZE:
                metadata['nota_limite'] = f"Análisis limitado a {MAX_FILES_TO_ANALYZE} archivos"
            
            # Analizar archivos usando el factory multi-lenguaje
            if archivos_codigo:
                print(f"\n📊 Procesando métricas de {archivos_analizados} archivos...", flush=True)
                print(f"   🔍 Iniciando análisis multi-lenguaje...", flush=True)
                analisis_multi = AnalyzerFactory.analyze_multi_language_project(archivos_codigo)
                print(f"   ✅ Análisis multi-lenguaje completado", flush=True)
                
                # Extraer métricas del lenguaje principal o hacer promedio ponderado
                if analisis_multi['primary_language']:
                    lenguaje_principal = analisis_multi['primary_language']
                    metricas_principales = analisis_multi['languages'][lenguaje_principal]['metrics']
                    
                    # Actualizar métricas totales con las del análisis
                    for categoria in metricas_totales:
                        if categoria != 'metadata' and categoria in metricas_principales:
                            metricas_totales[categoria] = metricas_principales[categoria]
                
                # Agregar información sobre lenguajes analizados
                if 'total_metrics' in analisis_multi:
                    metricas_totales['metadata']['lenguajes_analizados'] = analisis_multi['total_metrics'].get('languages_analyzed', [])
                    metricas_totales['metadata']['archivos_analizados'] = analisis_multi['total_metrics'].get('total_files', 0)
                    metricas_totales['metadata']['empathy_score_global'] = analisis_multi['total_metrics'].get('overall_empathy_score', 0)
                
                # Agregar métricas de duplicación del lenguaje principal
                if analisis_multi['primary_language'] and 'duplication' in analisis_multi['languages'][analisis_multi['primary_language']]:
                    metricas_totales['duplicacion'] = analisis_multi['languages'][analisis_multi['primary_language']]['duplication']
                
                # Agregar análisis de dependencias del lenguaje principal
                if analisis_multi['primary_language'] and 'dependencies' in analisis_multi['languages'][analisis_multi['primary_language']]:
                    metricas_totales['dependencias'] = analisis_multi['languages'][analisis_multi['primary_language']]['dependencies']
                
                # Agregar análisis de patrones del lenguaje principal
                if analisis_multi['primary_language'] and 'patterns' in analisis_multi['languages'][analisis_multi['primary_language']]:
                    metricas_totales['patrones'] = analisis_multi['languages'][analisis_multi['primary_language']]['patterns']
                
                # Agregar análisis de rendimiento del lenguaje principal
                if analisis_multi['primary_language'] and 'performance' in analisis_multi['languages'][analisis_multi['primary_language']]:
                    metricas_totales['rendimiento'] = analisis_multi['languages'][analisis_multi['primary_language']]['performance']
                
                # Agregar análisis de comentarios del lenguaje principal
                if analisis_multi['primary_language'] and 'comments' in analisis_multi['languages'][analisis_multi['primary_language']]:
                    metricas_totales['comentarios'] = analisis_multi['languages'][analisis_multi['primary_language']]['comments']
            else:
                logger.warning("No se encontraron archivos de código soportados en el repositorio")

            return metricas_totales

        except GithubException as e:
            if e.status == 403:
                logger.warning("Límite de rate alcanzado, esperando reset...")
                self.esperar_reset_rate_limit()
                return self.analizar_repo(repo_name)
            else:
                logger.error(f"Error de GitHub: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error analizando repo {repo_name}: {str(e)}")
            return None

    def esperar_reset_rate_limit(self):
        """Espera hasta que se resetee el límite de rate de GitHub"""
        rate_limit = self.github.get_rate_limit()
        reset_time = rate_limit.core.reset
        current_time = datetime.now(pytz.UTC)
        wait_time = (reset_time - current_time).total_seconds()
        
        if wait_time > 0:
            print(f"\n⏳ Esperando {wait_time/60:.1f} minutos hasta que se resetee el límite...")
            print(f"🕐 Hora estimada de reinicio: {reset_time.strftime('%H:%M:%S')}")
            
            while wait_time > 0:
                mins, secs = divmod(int(wait_time), 60)
                print(f"\r⌛ Tiempo restante: {mins:02d}:{secs:02d}", end='')
                time.sleep(1)
                wait_time -= 1
            
            print("\n✅ ¡Límite reseteado! Continuando con el análisis...")
            time.sleep(1)

    @staticmethod
    def extraer_usuario_repo(repo_input: str) -> str:
        """Extrae el formato usuario/repo de una URL de GitHub"""
        if '/' in repo_input and 'github.com' not in repo_input:
            return repo_input
        
        match = re.search(r'github\.com/([^/]+/[^/]+)/?$', repo_input)
        if match:
            return match.group(1)
        
        raise ValueError("Formato inválido. Use 'usuario/repo' o una URL de GitHub válida")

    def get_repo_info(self, url: str) -> Dict[str, Any]:
        """Obtiene información básica del repositorio"""
        try:
            # Extraer owner/repo de la URL
            parts = url.strip("/").split("/")
            repo_full_name = f"{parts[-2]}/{parts[-1]}"
            
            repo = self.github.get_repo(repo_full_name)
            
            return {
                "nombre": repo.name,
                "url": repo.html_url,
                "descripcion": repo.description,
                "url_clone": repo.clone_url,
                "rama_default": repo.default_branch,
                "fecha_creacion": repo.created_at.isoformat(),
                "fecha_ultimo_push": repo.pushed_at.isoformat(),
                "lenguaje_principal": repo.language,
                "tamano_kb": repo.size
            }
        except Exception as e:
            logger.error(f"Error obteniendo info del repo: {str(e)}")
            raise

    def get_code_files(self, repo_url: str, extensions: List[str] = None) -> Dict[str, str]:
        """Obtiene todos los archivos de código del repositorio"""
        try:
            repo = self.github.get_repo(repo_url)
            contents = repo.get_contents("")
            code_files = {}
            
            # Límite de archivos según configuración
            MAX_FILES = self._get_max_files_limit(repo.size)
            files_count = 0

            # Si no se especifican extensiones, usar todas las soportadas
            if extensions is None:
                extensions = AnalyzerFactory.get_supported_extensions()
                
            while contents and files_count < MAX_FILES:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    if files_count < MAX_FILES:
                        contents.extend(repo.get_contents(file_content.path))
                else:
                    # Verificar si el archivo tiene una extensión soportada
                    for ext in extensions:
                        if file_content.path.endswith(ext):
                            try:
                                # Saltar archivos muy grandes
                                if file_content.size > 1024 * 1024:  # 1MB
                                    break
                                    
                                code_files[file_content.path] = file_content.decoded_content.decode('utf-8')
                                files_count += 1
                                if files_count >= MAX_FILES:
                                    break
                            except Exception as e:
                                logger.warning(f"Error decodificando {file_content.path}: {str(e)}")
                            break

            return code_files
        except Exception as e:
            logger.error(f"Error obteniendo archivos de código: {str(e)}")
            raise

    @staticmethod
    def get_repo_from_input(tipo: str) -> str:
        """Obtiene URL del repositorio desde input del usuario"""
        repos_disponibles = [
            "https://github.com/usuario1/repo1",
            "https://github.com/usuario2/repo2"
        ]
        
        print(f"\nREPOSITORIO {tipo.upper()}")
        print("-" * 20)
        for i, repo in enumerate(repos_disponibles, 1):
            print(f"{i}. {repo}")
            
        while True:
            try:
                opcion = int(input(f"\nSeleccione repositorio {tipo} (1-{len(repos_disponibles)}): "))
                if 1 <= opcion <= len(repos_disponibles):
                    return repos_disponibles[opcion - 1]
            except ValueError:
                print("Por favor, ingrese un número válido.")