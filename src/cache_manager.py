#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Módulo de Gestión de Caché - Almacenamiento de Resultados de Análisis
=============================================================================

Este módulo implementa un sistema de caché para almacenar y recuperar resultados
de análisis de repositorios, evitando llamadas repetidas a la API de GitHub.

CARACTERÍSTICAS PRINCIPALES:
---------------------------
- Almacenamiento en disco en formato JSON
- TTL (Time To Live) configurable (default: 24 horas)
- Identificación por hash MD5 del nombre del repositorio
- Versionado de caché para compatibilidad
- Metadatos de última actualización
- Limpieza automática de entradas expiradas

ESTRUCTURA DE CACHÉ:
-------------------
cache/
├── <hash_repo_1>.json
├── <hash_repo_2>.json
└── ...

FORMATO DE ARCHIVO DE CACHÉ:
---------------------------
{
    "repo_name": "user/repo",
    "commit_hash": "abc123...",
    "timestamp": "2025-01-01T12:00:00",
    "version": "2.2.2",
    "data": { ... métricas del análisis ... }
}

EJEMPLO DE USO:
--------------
    >>> from cache_manager import CacheManager, CachedAnalyzer
    >>>
    >>> # Uso básico del CacheManager
    >>> cache = CacheManager(cache_dir="cache", ttl_hours=24)
    >>>
    >>> # Guardar en caché
    >>> cache.set("facebook/react", analysis_data, "abc123")
    >>>
    >>> # Recuperar de caché
    >>> cached = cache.get("facebook/react", "abc123")
    >>> if cached:
    ...     print("Datos recuperados de caché")
    >>>
    >>> # Uso con CachedAnalyzer (decorator pattern)
    >>> analyzer = CachedAnalyzer(github_repo, cache_manager)
    >>> results = analyzer.analyze("user/repo")  # Automáticamente usa caché

CONFIGURACIÓN:
-------------
El TTL puede configurarse mediante la variable de entorno CACHE_TTL (en segundos)
o mediante el parámetro ttl_hours del constructor.

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
import json                              # Serialización JSON
import os                                # Operaciones del sistema
import hashlib                           # Generación de hashes MD5
import time                              # Funciones de tiempo
from typing import Dict, Any, Optional   # Type hints
from datetime import datetime, timedelta # Manejo de fechas y tiempos
import logging                           # Sistema de logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cache for repository analysis results"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live for cache entries in hours
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        # Create metadata file if it doesn't exist
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            with open(metadata_path, 'w') as f:
                json.dump({}, f)
    
    def get_cache_key(self, repo_name: str, commit_hash: Optional[str] = None) -> str:
        """Generate cache key for a repository
        
        Args:
            repo_name: Repository name (owner/repo)
            commit_hash: Optional commit hash for specific version
            
        Returns:
            Cache key string
        """
        if commit_hash:
            key_string = f"{repo_name}:{commit_hash}"
        else:
            key_string = repo_name
        
        # Create a hash for the filename
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, repo_name: str, commit_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached analysis results
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
            
        Returns:
            Cached analysis results or None if not found/expired
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                logger.info(f"Cache expired for {repo_name}")
                self.delete(repo_name, commit_hash)
                return None
            
            logger.info(f"Cache hit for {repo_name}")
            return cached_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {repo_name}: {e}")
            return None
    
    def set(self, repo_name: str, data: Dict[str, Any], commit_hash: Optional[str] = None):
        """Store analysis results in cache
        
        Args:
            repo_name: Repository name
            data: Analysis results to cache
            commit_hash: Optional commit hash
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'repo_name': repo_name,
                'commit_hash': commit_hash,
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Update metadata
            self._update_metadata(repo_name, cache_key, commit_hash)
            
            logger.info(f"Cached analysis results for {repo_name}")
            
        except Exception as e:
            logger.error(f"Error caching results for {repo_name}: {e}")
    
    def delete(self, repo_name: str, commit_hash: Optional[str] = None):
        """Delete cached results for a repository
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_path):
            os.remove(cache_path)
            logger.info(f"Deleted cache for {repo_name}")
            
        # Update metadata
        self._remove_from_metadata(cache_key)
    
    def clear_all(self):
        """Clear all cached data"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json') and filename != 'metadata.json':
                os.remove(os.path.join(self.cache_dir, filename))
        
        # Clear metadata
        with open(os.path.join(self.cache_dir, "metadata.json"), 'w') as f:
            json.dump({}, f)
        
        logger.info("Cleared all cache")
    
    def clear_expired(self):
        """Clear only expired cache entries"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            expired_keys = []
            for cache_key, info in metadata.items():
                cached_time = datetime.fromisoformat(info['timestamp'])
                if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                    # Delete cache file
                    cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                    expired_keys.append(cache_key)
            
            # Update metadata
            for key in expired_keys:
                metadata.pop(key, None)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data
        
        Returns:
            Dictionary with cache statistics
        """
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            total_size = 0
            file_count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                'total_entries': len(metadata),
                'total_files': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir,
                'ttl_hours': self.ttl_hours
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}
    
    def _update_metadata(self, repo_name: str, cache_key: str, commit_hash: Optional[str]):
        """Update cache metadata"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata[cache_key] = {
                'repo_name': repo_name,
                'commit_hash': commit_hash,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
    
    def _remove_from_metadata(self, cache_key: str):
        """Remove entry from metadata"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata.pop(cache_key, None)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error removing from metadata: {e}")


class CachedAnalyzer:
    """Analyzer wrapper with caching support"""
    
    def __init__(self, cache_manager: CacheManager, analyzer):
        self.cache_manager = cache_manager
        self.analyzer = analyzer
    
    def analyze_repo(self, repo_name: str, commit_hash: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Analyze repository with caching
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
            force: Force re-analysis even if cached
            
        Returns:
            Analysis results
        """
        # Check cache first
        if not force:
            cached_result = self.cache_manager.get(repo_name, commit_hash)
            if cached_result:
                return cached_result
        
        # Perform analysis
        result = self.analyzer.analizar_repo(repo_name)
        
        # Cache the result
        if result:
            self.cache_manager.set(repo_name, result, commit_hash)
        
        return result