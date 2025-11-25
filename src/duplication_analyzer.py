#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Módulo de Análisis de Duplicación de Código
=============================================================================

Este módulo detecta código duplicado en repositorios utilizando técnicas de
hashing y análisis de similitud de líneas. La detección de duplicación es
importante para identificar oportunidades de refactorización.

METODOLOGÍA DE DETECCIÓN:
------------------------
1. Normalización de líneas (eliminar espacios, comentarios)
2. Extracción de bloques de código de tamaño mínimo
3. Generación de hash MD5 por bloque normalizado
4. Identificación de bloques con hash idéntico
5. Cálculo de estadísticas de duplicación

MÉTRICAS CALCULADAS:
-------------------
- porcentaje_global: % de líneas duplicadas respecto al total
- bloques_encontrados: Número de bloques únicos duplicados
- total_ocurrencias: Total de instancias de código duplicado
- lineas_duplicadas: Número total de líneas duplicadas
- archivos_afectados: Lista de archivos con duplicación
- mayor_duplicacion: Archivo con más duplicación

UMBRALES DE INTERPRETACIÓN:
--------------------------
- < 5%:   Excelente - Muy poca duplicación
- 5-15%:  Bueno - Dentro de límites aceptables
- 15-25%: Moderado - Considerar refactorización
- > 25%:  Alto - Refactorización recomendada

CONFIGURACIÓN:
-------------
- min_block_size: Mínimo de líneas para considerar un bloque (default: 5)
- ignore_whitespace: Si ignorar espacios en blanco (default: True)

EJEMPLO DE USO:
--------------
    >>> from duplication_analyzer import DuplicationAnalyzer
    >>>
    >>> # Configurar analizador
    >>> analyzer = DuplicationAnalyzer(min_block_size=5)
    >>>
    >>> # Analizar archivos
    >>> files = {"file1.py": "...", "file2.py": "..."}
    >>> results = analyzer.find_duplicates(files)
    >>>
    >>> print(f"Duplicación: {results['porcentaje_global']}%")
    >>> print(f"Bloques duplicados: {results['bloques_encontrados']}")

ALGORITMO:
---------
Para cada archivo:
  1. Dividir en líneas
  2. Para cada posición i:
     a. Extraer bloque de min_block_size líneas
     b. Normalizar cada línea del bloque
     c. Calcular hash MD5 del bloque normalizado
     d. Agregar al diccionario hash -> [ubicaciones]
  3. Identificar hashes con múltiples ubicaciones

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
import hashlib                       # Generación de hashes MD5
import re                            # Expresiones regulares
from typing import Dict, List, Tuple, Any  # Type hints
from collections import defaultdict  # Diccionarios con valores por defecto
import logging                       # Sistema de logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


class DuplicationAnalyzer:
    """
    Analizador de duplicación de código.
    
    Detecta bloques de código duplicado usando técnicas de hashing
    y análisis de similitud de líneas.
    """
    
    def __init__(self, min_block_size: int = 5, ignore_whitespace: bool = True):
        """
        Inicializa el analizador de duplicación.
        
        Args:
            min_block_size: Tamaño mínimo de bloque para considerar duplicación.
            ignore_whitespace: Si ignorar espacios en blanco en la comparación.
        """
        self.min_block_size = min_block_size
        self.ignore_whitespace = ignore_whitespace
        
    def normalize_line(self, line: str) -> str:
        """
        Normaliza una línea de código para comparación.
        
        Args:
            line: Línea de código a normalizar.
            
        Returns:
            str: Línea normalizada.
        """
        # Remover comentarios de línea
        line = re.sub(r'//.*|#.*|<!--.*?-->', '', line)
        
        if self.ignore_whitespace:
            # Remover espacios extra y normalizar
            line = re.sub(r'\s+', ' ', line.strip())
            
        return line
    
    def extract_blocks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extrae bloques de código del contenido.
        
        Args:
            content: Contenido del archivo.
            file_path: Ruta del archivo.
            
        Returns:
            List[Dict]: Lista de bloques con metadata.
        """
        lines = content.split('\n')
        blocks = []
        
        for i in range(len(lines) - self.min_block_size + 1):
            block_lines = []
            original_lines = []
            
            for j in range(self.min_block_size):
                line = lines[i + j]
                normalized = self.normalize_line(line)
                
                # Saltar líneas vacías o solo comentarios
                if normalized.strip():
                    block_lines.append(normalized)
                    original_lines.append(line)
            
            # Solo procesar bloques con contenido significativo
            if len(block_lines) >= self.min_block_size:
                block_content = '\n'.join(block_lines)
                block_hash = hashlib.md5(block_content.encode()).hexdigest()
                
                blocks.append({
                    'hash': block_hash,
                    'content': block_content,
                    'original_content': '\n'.join(original_lines),
                    'file_path': file_path,
                    'start_line': i + 1,
                    'end_line': i + self.min_block_size,
                    'size': len(block_lines)
                })
        
        return blocks
    
    def find_duplicates(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Encuentra duplicaciones en múltiples archivos.
        
        Args:
            files_content: Diccionario {file_path: content}.
            
        Returns:
            Dict: Análisis de duplicación completo.
        """
        all_blocks = []
        blocks_by_hash = defaultdict(list)
        
        # Extraer bloques de todos los archivos
        for file_path, content in files_content.items():
            if not content.strip():
                continue
                
            file_blocks = self.extract_blocks(content, file_path)
            all_blocks.extend(file_blocks)
            
            # Agrupar por hash
            for block in file_blocks:
                blocks_by_hash[block['hash']].append(block)
        
        # Encontrar duplicados (bloques con el mismo hash)
        duplicates = {}
        total_duplicated_lines = 0
        files_with_duplicates = set()
        
        for block_hash, blocks in blocks_by_hash.items():
            if len(blocks) > 1:  # Duplicado encontrado
                duplicates[block_hash] = {
                    'occurrences': len(blocks),
                    'blocks': blocks,
                    'size': blocks[0]['size'],
                    'content_preview': blocks[0]['content'][:200] + '...' if len(blocks[0]['content']) > 200 else blocks[0]['content']
                }
                
                # Contar líneas duplicadas
                total_duplicated_lines += blocks[0]['size'] * (len(blocks) - 1)
                
                # Marcar archivos afectados
                for block in blocks:
                    files_with_duplicates.add(block['file_path'])
        
        # Calcular estadísticas
        total_lines = sum(len(content.split('\n')) for content in files_content.values())
        duplication_percentage = (total_duplicated_lines / max(total_lines, 1)) * 100
        
        # Encontrar archivo con más duplicación
        file_duplication_stats = defaultdict(int)
        for duplicate_info in duplicates.values():
            for block in duplicate_info['blocks']:
                file_duplication_stats[block['file_path']] += duplicate_info['size']
        
        most_duplicated_file = None
        max_duplication = 0
        if file_duplication_stats:
            most_duplicated_file = max(file_duplication_stats.items(), key=lambda x: x[1])
            max_duplication = (most_duplicated_file[1] / max(len(files_content[most_duplicated_file[0]].split('\n')), 1)) * 100
        
        return {
            'porcentaje_global': round(duplication_percentage, 2),
            'bloques_encontrados': len(duplicates),
            'total_ocurrencias': sum(dup['occurrences'] for dup in duplicates.values()),
            'lineas_duplicadas': total_duplicated_lines,
            'archivos_afectados': list(files_with_duplicates),
            'total_archivos': len(files_content),
            'mayor_duplicacion': {
                'archivo': most_duplicated_file[0] if most_duplicated_file else None,
                'porcentaje': round(max_duplication, 2) if most_duplicated_file else 0
            } if most_duplicated_file else None,
            'duplicates_details': duplicates,
            'summary': self._generate_summary(duplicates, duplication_percentage, len(files_with_duplicates))
        }
    
    def _generate_summary(self, duplicates: Dict, percentage: float, affected_files: int) -> str:
        """
        Genera un resumen textual del análisis.
        
        Args:
            duplicates: Duplicados encontrados.
            percentage: Porcentaje de duplicación.
            affected_files: Número de archivos afectados.
            
        Returns:
            str: Resumen del análisis.
        """
        if percentage < 5:
            level = "Excelente"
            description = "Muy poca duplicación detectada"
        elif percentage < 15:
            level = "Bueno" 
            description = "Duplicación dentro de límites aceptables"
        elif percentage < 25:
            level = "Moderado"
            description = "Duplicación moderada, considere refactorización"
        else:
            level = "Alto"
            description = "Alta duplicación, refactorización recomendada"
        
        return f"{level}: {description}. {len(duplicates)} bloques duplicados en {affected_files} archivos."
    
    def analyze_repository_files(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza duplicación en archivos de un repositorio.
        
        Args:
            files_content: Diccionario con contenido de archivos.
            
        Returns:
            Dict: Análisis completo de duplicación.
        """
        try:
            return self.find_duplicates(files_content)
        except Exception as e:
            logger.error(f"Error en análisis de duplicación: {e}")
            return {
                'porcentaje_global': 0,
                'bloques_encontrados': 0,
                'total_ocurrencias': 0,
                'lineas_duplicadas': 0,
                'archivos_afectados': [],
                'total_archivos': len(files_content),
                'mayor_duplicacion': None,
                'duplicates_details': {},
                'summary': "Error en el análisis de duplicación",
                'error': str(e)
            }