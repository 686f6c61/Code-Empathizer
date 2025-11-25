#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Paquete de Analizadores de Lenguaje - Code Empathizer
=============================================================================

Este paquete contiene los analizadores específicos para cada lenguaje de
programación soportado por Code Empathizer.

ARQUITECTURA DEL PAQUETE:
------------------------
language_analyzers/
├── __init__.py          # Este archivo (exportaciones públicas)
├── base.py              # Clase abstracta base (Template Method)
├── factory.py           # Factory para crear analizadores
├── python_analyzer.py   # Analizador Python (AST)
├── javascript_analyzer.py # Analizador JavaScript (Regex)
├── typescript_analyzer.py # Analizador TypeScript (hereda JS)
├── java_analyzer.py     # Analizador Java
├── go_analyzer.py       # Analizador Go
├── csharp_analyzer.py   # Analizador C#
├── cpp_analyzer.py      # Analizador C++
├── php_analyzer.py      # Analizador PHP
├── ruby_analyzer.py     # Analizador Ruby
├── swift_analyzer.py    # Analizador Swift
├── html_analyzer.py     # Analizador HTML
└── css_analyzer.py      # Analizador CSS

EXPORTACIONES PÚBLICAS:
----------------------
- LanguageAnalyzer: Clase base abstracta para crear analizadores
- AnalyzerFactory: Factory para obtener analizadores por lenguaje

USO DEL PAQUETE:
---------------
    # Importar el factory (forma recomendada)
    from language_analyzers import AnalyzerFactory

    # Obtener analizador
    analyzer = AnalyzerFactory.get_analyzer('python')

    # Analizar archivos
    metrics = analyzer.analyze_files({'main.py': source_code})

    # O usar el análisis multi-lenguaje directamente
    results = AnalyzerFactory.analyze_multi_language_project(files)

EXTENSIBILIDAD:
--------------
Para añadir un nuevo lenguaje:
    1. Crear nueva clase en este paquete
    2. Heredar de LanguageAnalyzer
    3. Implementar métodos abstractos
    4. Registrar en AnalyzerFactory

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

# =============================================================================
# EXPORTACIONES PÚBLICAS
# =============================================================================
from .base import LanguageAnalyzer     # Clase base abstracta
from .factory import AnalyzerFactory   # Factory de analizadores

# Lista de símbolos exportados por "from language_analyzers import *"
__all__ = ['LanguageAnalyzer', 'AnalyzerFactory']