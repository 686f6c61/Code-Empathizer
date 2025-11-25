#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Clase Base para Analizadores de Lenguaje - Template Method Pattern
=============================================================================

Este módulo define la clase base abstracta LanguageAnalyzer que implementa
el patrón Template Method para crear analizadores específicos de cada
lenguaje de programación soportado.

PATRÓN DE DISEÑO: TEMPLATE METHOD
---------------------------------
La clase base define el esqueleto del algoritmo de análisis, delegando
algunos pasos a las subclases:

    LanguageAnalyzer (abstracto)
           │
    ┌──────┴──────┬──────────────┬───────────────┐
    ▼             ▼              ▼               ▼
  Python      JavaScript     Java            ...más
  Analyzer    Analyzer       Analyzer        analizadores

MÉTODOS ABSTRACTOS (deben implementarse):
----------------------------------------
- get_file_extensions(): Extensiones de archivo soportadas
- get_language_name(): Nombre del lenguaje
- analyze_file(): Análisis de un archivo individual

MÉTODOS CONCRETOS (heredados):
-----------------------------
- analyze_files(): Analiza múltiples archivos
- aggregate_metrics(): Agrega métricas de archivos individuales
- calculate_empathy_score(): Calcula puntuación de empatía
- get_summary(): Obtiene resumen del análisis

INTEGRACIÓN CON ANALIZADORES AVANZADOS:
--------------------------------------
La clase base integra automáticamente los análisis avanzados:
- DuplicationAnalyzer: Código duplicado
- DependencyAnalyzer: Dependencias e imports
- PatternAnalyzer: Patrones de diseño
- PerformanceAnalyzer: Métricas de rendimiento
- CommentAnalyzer: Comentarios y TODOs

ESTRUCTURA DE MÉTRICAS:
----------------------
{
    'nombres': {'descriptividad': 0.0},
    'documentacion': {'cobertura_docstrings': 0.0},
    'modularidad': {'funciones_por_archivo': 0.0},
    'complejidad': {'complejidad_ciclomatica': 0.0},
    'manejo_errores': {'cobertura_manejo_errores': 0.0},
    'pruebas': {'cobertura_pruebas': 0.0},
    'seguridad': {'validacion_entradas': 0.0},
    'consistencia_estilo': {'consistencia_nombres': 0.0}
}

EJEMPLO DE IMPLEMENTACIÓN:
-------------------------
    class MyLanguageAnalyzer(LanguageAnalyzer):
        def get_file_extensions(self):
            return ['.mylang']

        def get_language_name(self):
            return 'MyLanguage'

        def analyze_file(self, file_path, content):
            # Implementar análisis específico
            return {'nombres': {'descriptividad': 0.8}, ...}

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
from abc import ABC, abstractmethod              # Clases abstractas
from typing import Dict, List, Any, Optional, Tuple  # Type hints
import os                                         # Operaciones del sistema
import sys                                        # Interacción con el sistema

# Añadir directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Analizadores avanzados integrados
from duplication_analyzer import DuplicationAnalyzer    # Análisis de duplicación
from dependency_analyzer import DependencyAnalyzer      # Análisis de dependencias
from pattern_analyzer import PatternAnalyzer            # Patrones de diseño
from performance_analyzer import PerformanceAnalyzer    # Análisis de rendimiento
from comment_analyzer import CommentAnalyzer            # Análisis de comentarios


class LanguageAnalyzer(ABC):
    """
    Clase base abstracta para analizadores específicos de lenguaje.
    
    Define la interfaz y comportamiento común para todos los analizadores.
    Las subclases deben implementar los métodos abstractos para cada
    lenguaje específico.
    
    Attributes:
        metrics: Diccionario con las métricas analizadas.
        total_files: Número total de archivos analizados.
        total_lines: Número total de líneas procesadas.
    """
    
    def __init__(self):
        self.metrics = {
            'nombres': {},
            'documentacion': {},
            'modularidad': {},
            'complejidad': {},
            'manejo_errores': {},
            'pruebas': {},
            'seguridad': {},
            'consistencia_estilo': {}
        }
        self.total_files = 0
        self.total_lines = 0
        
    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """
        Retorna las extensiones de archivo que maneja este analizador.
        
        Returns:
            List[str]: Lista de extensiones (ej: ['.py', '.pyw']).
        """
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """Return the name of the language"""
        pass
    
    @abstractmethod
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a single file and return metrics"""
        pass
    
    def analyze_files(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza múltiples archivos y agrega los resultados.
        
        Procesa cada archivo individualmente y luego combina las métricas
        para obtener valores promedio o totales según corresponda.
        
        Args:
            files: Diccionario {ruta: contenido} de archivos a analizar.
        
        Returns:
            Dict[str, Any]: Métricas agregadas de todos los archivos.
        """
        file_metrics = []
        
        for file_path, content in files.items():
            if self.should_analyze_file(file_path):
                try:
                    metrics = self.analyze_file(file_path, content)
                    file_metrics.append(metrics)
                    self.total_files += 1
                    self.total_lines += content.count('\n')
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
        
        if file_metrics:
            self.aggregate_metrics(file_metrics)
        
        return self.metrics
    
    def should_analyze_file(self, file_path: str) -> bool:
        """Check if file should be analyzed based on extension"""
        return any(file_path.endswith(ext) for ext in self.get_file_extensions())
    
    def aggregate_metrics(self, file_metrics: List[Dict[str, Any]]) -> None:
        """Aggregate metrics from individual files"""
        # Default implementation - can be overridden by subclasses
        if not file_metrics:
            return
            
        # Nombres
        descriptividad_scores = [m.get('nombres', {}).get('descriptividad', 0) for m in file_metrics if m.get('nombres')]
        if descriptividad_scores:
            self.metrics['nombres']['descriptividad'] = sum(descriptividad_scores) / len(descriptividad_scores)
        
        # Documentación
        doc_scores = [m.get('documentacion', {}).get('cobertura', 0) for m in file_metrics if m.get('documentacion')]
        if doc_scores:
            self.metrics['documentacion']['cobertura_docstrings'] = sum(doc_scores) / len(doc_scores)
        
        # Complejidad
        complexity_scores = [m.get('complejidad', {}).get('ciclomatica', 0) for m in file_metrics if m.get('complejidad')]
        if complexity_scores:
            self.metrics['complejidad']['complejidad_ciclomatica'] = sum(complexity_scores) / len(complexity_scores)
        
        # Modularidad
        functions_per_file = [m.get('modularidad', {}).get('funciones', 0) for m in file_metrics if m.get('modularidad')]
        if functions_per_file:
            self.metrics['modularidad']['funciones_por_archivo'] = sum(functions_per_file) / len(functions_per_file)
        
        # Manejo de errores
        error_handling = [m.get('manejo_errores', {}).get('cobertura', 0) for m in file_metrics if m.get('manejo_errores')]
        if error_handling:
            self.metrics['manejo_errores']['cobertura_manejo_errores'] = sum(error_handling) / len(error_handling)
        
        # Pruebas
        test_coverage = [m.get('pruebas', {}).get('cobertura', 0) for m in file_metrics if m.get('pruebas')]
        if test_coverage:
            self.metrics['pruebas']['cobertura_pruebas'] = sum(test_coverage) / len(test_coverage)
        
        # Seguridad
        security_scores = [m.get('seguridad', {}).get('validacion', 0) for m in file_metrics if m.get('seguridad')]
        if security_scores:
            self.metrics['seguridad']['validacion_entradas'] = sum(security_scores) / len(security_scores)
        
        # Consistencia
        style_scores = [m.get('consistencia_estilo', {}).get('consistencia', 0) for m in file_metrics if m.get('consistencia_estilo')]
        if style_scores:
            self.metrics['consistencia_estilo']['consistencia_nombres'] = sum(style_scores) / len(style_scores)
    
    def calculate_empathy_score(self) -> float:
        """Calculate overall empathy score based on all metrics"""
        scores = []
        weights = {
            'nombres': 0.15,
            'documentacion': 0.15,
            'modularidad': 0.15,
            'complejidad': 0.15,
            'manejo_errores': 0.10,
            'pruebas': 0.10,
            'seguridad': 0.10,
            'consistencia_estilo': 0.10
        }
        
        for category, weight in weights.items():
            category_metrics = self.metrics.get(category, {})
            if category_metrics:
                # Get average of all metrics in category
                values = [v for v in category_metrics.values() if isinstance(v, (int, float))]
                if values:
                    avg = sum(values) / len(values)
                    scores.append(avg * weight)
        
        return sum(scores) if scores else 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de los resultados del análisis.
        
        Returns:
            Dict[str, Any]: Resumen con lenguaje, archivos, líneas,
                           métricas y puntuación de empatía.
        """
        return {
            'language': self.get_language_name(),
            'total_files': self.total_files,
            'total_lines': self.total_lines,
            'metrics': self.metrics,
            'empathy_score': self.calculate_empathy_score()
        }
    
    def analyze_duplication(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza duplicación de código en los archivos.
        
        Args:
            files_content: Diccionario con el contenido de archivos.
            
        Returns:
            Dict[str, Any]: Análisis de duplicación.
        """
        analyzer = DuplicationAnalyzer(min_block_size=5, ignore_whitespace=True)
        return analyzer.analyze_repository_files(files_content)
    
    def analyze_dependencies(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza las dependencias en los archivos.
        
        Args:
            files_content: Diccionario con el contenido de archivos.
            
        Returns:
            Dict[str, Any]: Análisis de dependencias.
        """
        analyzer = DependencyAnalyzer()
        return analyzer.analyze_dependencies(files_content)
    
    def analyze_patterns(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza patrones de diseño y anti-patrones.
        
        Args:
            files_content: Diccionario con el contenido de archivos.
            
        Returns:
            Dict[str, Any]: Análisis de patrones.
        """
        analyzer = PatternAnalyzer()
        return analyzer.analyze_patterns(files_content)
    
    def analyze_performance(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza métricas de rendimiento.
        
        Args:
            files_content: Diccionario con el contenido de archivos.
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento.
        """
        analyzer = PerformanceAnalyzer()
        return analyzer.analyze_performance(files_content)
    
    def analyze_comments(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza comentarios y TODOs.
        
        Args:
            files_content: Diccionario con el contenido de archivos.
            
        Returns:
            Dict[str, Any]: Análisis de comentarios.
        """
        analyzer = CommentAnalyzer()
        return analyzer.analyze_comments(files_content)