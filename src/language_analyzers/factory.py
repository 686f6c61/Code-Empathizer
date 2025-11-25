#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Factory para Analizadores de Lenguaje - Factory Pattern
=============================================================================

Este módulo implementa el patrón Factory para crear instancias de analizadores
específicos de lenguaje según la extensión de archivo o nombre del lenguaje.

PATRÓN DE DISEÑO: FACTORY
-------------------------
El Factory Pattern permite crear objetos sin especificar la clase exacta,
delegando la decisión a métodos de fábrica:

    Cliente
       │
       ▼
    AnalyzerFactory.get_analyzer("python")
       │
       ▼
    PythonAnalyzer()

LENGUAJES SOPORTADOS (12):
-------------------------
Lenguajes de programación:
    - Python (.py)
    - JavaScript (.js, .jsx, .mjs)
    - TypeScript (.ts, .tsx)
    - Java (.java)
    - Go (.go)
    - C# (.cs)
    - C++ (.cpp, .cc, .cxx, .hpp, .h, .hh)
    - PHP (.php, .php3-5, .phtml)
    - Ruby (.rb, .rake, .gemspec)
    - Swift (.swift)

Lenguajes web:
    - HTML (.html, .htm, .xhtml)
    - CSS (.css, .scss, .sass, .less)

MÉTODOS DE LA FACTORY:
---------------------
- get_analyzer(language): Obtiene analizador por nombre de lenguaje
- get_analyzer_for_file(path): Obtiene analizador por extensión de archivo
- get_supported_extensions(): Lista todas las extensiones soportadas
- get_supported_languages(): Lista todos los lenguajes soportados
- detect_primary_language(files): Detecta lenguaje principal del proyecto
- analyze_multi_language_project(files): Analiza proyecto multi-lenguaje
- register_analyzer(language, class): Registra nuevo analizador

EXTENSIÓN DEL SISTEMA:
---------------------
Para añadir soporte para un nuevo lenguaje:

    1. Crear nueva clase que herede de LanguageAnalyzer
    2. Implementar métodos abstractos
    3. Registrar en el factory:

    AnalyzerFactory.register_analyzer('mylang', MyLangAnalyzer)

EJEMPLO DE USO:
--------------
    >>> from language_analyzers.factory import AnalyzerFactory
    >>>
    >>> # Por lenguaje
    >>> analyzer = AnalyzerFactory.get_analyzer('python')
    >>>
    >>> # Por archivo
    >>> analyzer = AnalyzerFactory.get_analyzer_for_file('main.py')
    >>>
    >>> # Proyecto multi-lenguaje
    >>> files = {'app.py': '...', 'index.js': '...'}
    >>> results = AnalyzerFactory.analyze_multi_language_project(files)

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
import os                                        # Operaciones del sistema
from typing import Optional, Dict, List, Type, Any  # Type hints

# Clase base y analizadores específicos
from .base import LanguageAnalyzer               # Clase abstracta base
from .python_analyzer import PythonAnalyzer      # Analizador Python
from .javascript_analyzer import JavaScriptAnalyzer  # Analizador JavaScript
from .typescript_analyzer import TypeScriptAnalyzer  # Analizador TypeScript
from .java_analyzer import JavaAnalyzer          # Analizador Java
from .go_analyzer import GoAnalyzer              # Analizador Go
from .csharp_analyzer import CSharpAnalyzer      # Analizador C#
from .cpp_analyzer import CppAnalyzer            # Analizador C++
from .php_analyzer import PHPAnalyzer            # Analizador PHP
from .ruby_analyzer import RubyAnalyzer          # Analizador Ruby
from .swift_analyzer import SwiftAnalyzer        # Analizador Swift
from .html_analyzer import HTMLAnalyzer          # Analizador HTML
from .css_analyzer import CSSAnalyzer            # Analizador CSS


class AnalyzerFactory:
    """Factory class for creating appropriate language analyzers"""
    
    # Registry of available analyzers
    _analyzers: Dict[str, Type[LanguageAnalyzer]] = {
        'python': PythonAnalyzer,
        'javascript': JavaScriptAnalyzer,
        'typescript': TypeScriptAnalyzer,
        'java': JavaAnalyzer,
        'go': GoAnalyzer,
        'c#': CSharpAnalyzer,
        'csharp': CSharpAnalyzer,
        'c++': CppAnalyzer,
        'cpp': CppAnalyzer,
        'php': PHPAnalyzer,
        'ruby': RubyAnalyzer,
        'swift': SwiftAnalyzer,
        'html': HTMLAnalyzer,
        'css': CSSAnalyzer
    }
    
    # Extension to language mapping
    _extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.mjs': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.h': 'cpp',
        '.hh': 'cpp',
        '.php': 'php',
        '.php3': 'php',
        '.php4': 'php',
        '.php5': 'php',
        '.phtml': 'php',
        '.rb': 'ruby',
        '.rake': 'ruby',
        '.gemspec': 'ruby',
        '.swift': 'swift',
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.css': 'css',
        '.scss': 'css',
        '.sass': 'css',
        '.less': 'css'
    }
    
    @classmethod
    def register_analyzer(cls, language: str, analyzer_class: Type[LanguageAnalyzer]) -> None:
        """Register a new analyzer for a language"""
        cls._analyzers[language.lower()] = analyzer_class
    
    @classmethod
    def get_analyzer(cls, language: str) -> Optional[LanguageAnalyzer]:
        """Get an analyzer instance for a specific language"""
        analyzer_class = cls._analyzers.get(language.lower())
        if analyzer_class:
            return analyzer_class()
        return None
    
    @classmethod
    def get_analyzer_for_file(cls, file_path: str) -> Optional[LanguageAnalyzer]:
        """Get an analyzer instance based on file extension"""
        _, ext = os.path.splitext(file_path)
        language = cls._extension_map.get(ext.lower())
        
        if language:
            return cls.get_analyzer(language)
        return None
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of all supported file extensions"""
        return list(cls._extension_map.keys())
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of all supported languages"""
        return list(cls._analyzers.keys())
    
    @classmethod
    def detect_primary_language(cls, files: Dict[str, str]) -> Optional[str]:
        """Detect the primary language in a set of files"""
        language_counts = {}
        
        for file_path in files:
            _, ext = os.path.splitext(file_path)
            language = cls._extension_map.get(ext.lower())
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        
        if language_counts:
            # Return the most common language
            return max(language_counts, key=language_counts.get)
        return None
    
    @classmethod
    def analyze_multi_language_project(cls, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a project with multiple languages"""
        results = {
            'languages': {},
            'total_metrics': {},
            'primary_language': None
        }
        
        # Group files by language
        language_files = {}
        for file_path, content in files.items():
            analyzer = cls.get_analyzer_for_file(file_path)
            if analyzer:
                language = analyzer.get_language_name()
                if language not in language_files:
                    language_files[language] = {}
                language_files[language][file_path] = content
        
        # Analyze each language separately
        for language, lang_files in language_files.items():
            print(f"      📝 Analizando {language}: {len(lang_files)} archivos", flush=True)
            analyzer = cls.get_analyzer(language.lower())
            if analyzer:
                print(f"         • Métricas básicas...", flush=True)
                metrics = analyzer.analyze_files(lang_files)
                print(f"         • Duplicación...", flush=True)
                duplication = analyzer.analyze_duplication(lang_files)
                print(f"         • Dependencias...", flush=True)
                dependencies = analyzer.analyze_dependencies(lang_files)
                print(f"         • Patrones...", flush=True)
                patterns = analyzer.analyze_patterns(lang_files)
                print(f"         • Rendimiento...", flush=True)
                performance = analyzer.analyze_performance(lang_files)
                print(f"         • Comentarios...", flush=True)
                comments = analyzer.analyze_comments(lang_files)
                print(f"         ✅ {language} completado", flush=True)
                results['languages'][language] = {
                    'metrics': metrics,
                    'summary': analyzer.get_summary(),
                    'duplication': duplication,
                    'dependencies': dependencies,
                    'patterns': patterns,
                    'performance': performance,
                    'comments': comments,
                    'file_count': len(lang_files)
                }
        
        # Determine primary language
        if language_files:
            primary = max(language_files, key=lambda x: len(language_files[x]))
            results['primary_language'] = primary
        
        # Calculate aggregate metrics
        results['total_metrics'] = cls._calculate_aggregate_metrics(results['languages'])
        
        return results
    
    @classmethod
    def _calculate_aggregate_metrics(cls, language_results: Dict) -> Dict[str, Any]:
        """Calculate aggregate metrics across all languages"""
        if not language_results:
            return {}
        
        total_files = sum(lang['file_count'] for lang in language_results.values())
        total_lines = sum(lang['summary']['total_lines'] for lang in language_results.values())
        
        # Weight metrics by file count
        weighted_scores = {}
        for lang_name, lang_data in language_results.items():
            weight = lang_data['file_count'] / total_files
            empathy_score = lang_data['summary']['empathy_score']
            
            if 'weighted_empathy' not in weighted_scores:
                weighted_scores['weighted_empathy'] = 0
            weighted_scores['weighted_empathy'] += empathy_score * weight
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'languages_analyzed': list(language_results.keys()),
            'overall_empathy_score': weighted_scores.get('weighted_empathy', 0)
        }