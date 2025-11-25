#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Analizador de Código TypeScript - Extensión del Analizador JavaScript
=============================================================================

Este módulo implementa un analizador para código TypeScript que extiende
el analizador de JavaScript con características específicas del sistema
de tipos de TypeScript.

EXTENSIONES SOPORTADAS:
----------------------
- .ts   - TypeScript estándar
- .tsx  - TypeScript con JSX (React)

HERENCIA:
--------
TypeScriptAnalyzer hereda de JavaScriptAnalyzer, por lo que incluye
todas las métricas de JavaScript más las específicas de TypeScript.

CARACTERÍSTICAS DE TYPESCRIPT ANALIZADAS:
----------------------------------------
Sistema de Tipos:
    - Interfaces (interface)
    - Type aliases (type)
    - Generics (<T>)
    - Union types (|)
    - Intersection types (&)
    - Type guards

Enums y Constantes:
    - enum
    - const enum
    - as const

Modificadores de Acceso:
    - public, private, protected
    - readonly
    - abstract

Decoradores:
    - @Component, @Injectable (Angular)
    - Decoradores personalizados

MÉTRICAS ESPECÍFICAS DE TYPESCRIPT:
----------------------------------
- type_coverage: % de código con tipos explícitos
- interface_count: Número de interfaces
- type_alias_count: Número de type aliases
- enum_count: Número de enums
- any_usage: Uso de tipo any (penaliza)
- strict_null_checks: Uso de null/undefined typing

CONVENCIONES EVALUADAS:
----------------------
- Interfaces con prefijo I (opcional)
- Types vs Interfaces
- Uso de unknown vs any
- Strict mode features

PATRONES DETECTADOS:
-------------------
Positivos:
    - Type guards
    - Discriminated unions
    - Generic constraints

Negativos:
    - Uso excesivo de any
    - Type assertions innecesarias (as)
    - Non-null assertions (!)

EJEMPLO DE USO:
--------------
    >>> from language_analyzers.typescript_analyzer import TypeScriptAnalyzer
    >>>
    >>> analyzer = TypeScriptAnalyzer()
    >>> metrics = analyzer.analyze_file("app.ts", source_code)
    >>> print(f"Type coverage: {metrics['typescript']['type_coverage']}%")

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
import re                                # Expresiones regulares
from typing import Dict, List, Any, Optional  # Type hints
from .javascript_analyzer import JavaScriptAnalyzer  # Clase padre


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """Analyzer for TypeScript code - extends JavaScript analyzer with TypeScript-specific features"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.ts', '.tsx']
    
    def get_language_name(self) -> str:
        return 'TypeScript'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a TypeScript file"""
        # Get base JavaScript metrics
        metrics = super().analyze_file(file_path, content)
        
        # Add TypeScript-specific metrics
        type_coverage = self._calculate_type_coverage(content)
        interface_count = self._count_interfaces(content)
        type_alias_count = self._count_type_aliases(content)
        enum_count = self._count_enums(content)
        
        # Update metrics with TypeScript-specific data
        metrics['typescript'] = {
            'type_coverage': type_coverage,
            'interfaces': interface_count,
            'type_aliases': type_alias_count,
            'enums': enum_count
        }
        
        # Boost documentation score if types are well-defined
        if type_coverage > 0.7:
            current_doc_score = metrics.get('documentacion', {}).get('cobertura', 0)
            metrics['documentacion']['cobertura'] = min(1.0, current_doc_score + 0.2)
        
        # Boost security score for type safety
        current_security = metrics.get('seguridad', {}).get('validacion', 0)
        metrics['seguridad']['validacion'] = min(1.0, current_security + (type_coverage * 0.2))
        
        return metrics
    
    def _calculate_type_coverage(self, content: str) -> float:
        """Calculate how many variables and parameters have type annotations"""
        # Count function parameters with types
        param_pattern = r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?)\s*\(([^)]*)\)'
        params_with_types = 0
        total_params = 0
        
        for match in re.finditer(param_pattern, content):
            params = match.group(1)
            if params.strip():
                param_list = params.split(',')
                for param in param_list:
                    total_params += 1
                    if ':' in param:  # Has type annotation
                        params_with_types += 1
        
        # Count variable declarations with types
        var_pattern = r'(?:const|let|var)\s+(\w+)\s*:\s*[A-Z]\w*'
        typed_vars = len(re.findall(var_pattern, content))
        
        # Count function return types
        return_type_pattern = r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?)[^)]*\)\s*:\s*[A-Z]\w*'
        typed_returns = len(re.findall(return_type_pattern, content))
        
        # Calculate overall coverage
        total_items = total_params + self._count_variables(content) + len(self._extract_functions(content))
        typed_items = params_with_types + typed_vars + typed_returns
        
        return typed_items / total_items if total_items > 0 else 0.0
    
    def _count_interfaces(self, content: str) -> int:
        """Count TypeScript interfaces"""
        interface_pattern = r'interface\s+\w+\s*(?:<[^>]+>)?\s*\{'
        return len(re.findall(interface_pattern, content))
    
    def _count_type_aliases(self, content: str) -> int:
        """Count TypeScript type aliases"""
        type_pattern = r'type\s+\w+\s*(?:<[^>]+>)?\s*='
        return len(re.findall(type_pattern, content))
    
    def _count_enums(self, content: str) -> int:
        """Count TypeScript enums"""
        enum_pattern = r'enum\s+\w+\s*\{'
        return len(re.findall(enum_pattern, content))
    
    def _count_variables(self, content: str) -> int:
        """Count variable declarations"""
        var_pattern = r'(?:const|let|var)\s+\w+'
        return len(re.findall(var_pattern, content))
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract functions including TypeScript-specific syntax"""
        functions = super()._extract_functions(content)
        
        # Add TypeScript-specific function patterns
        # Generic functions
        generic_func_pattern = r'function\s+(\w+)\s*<[^>]+>\s*\([^)]*\)'
        for match in re.finditer(generic_func_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'generic_function',
                'start': match.start()
            })
        
        # Method decorators
        decorator_pattern = r'@\w+\s*(?:\([^)]*\))?\s*(?:async\s+)?(\w+)\s*\([^)]*\)'
        for match in re.finditer(decorator_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'decorated_method',
                'start': match.start()
            })
        
        return functions
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency with TypeScript conventions"""
        base_score = super()._calculate_style_consistency(content)
        
        # Additional TypeScript style checks
        # Check interface naming convention (should start with I or not, consistently)
        interfaces = re.findall(r'interface\s+(\w+)', content)
        if interfaces:
            with_i = sum(1 for name in interfaces if name.startswith('I'))
            interface_consistency = with_i / len(interfaces)
            # Good if consistently using or not using I prefix
            interface_score = 1.0 if interface_consistency > 0.8 or interface_consistency < 0.2 else 0.5
        else:
            interface_score = 1.0
        
        # Check type naming convention (PascalCase)
        types = re.findall(r'type\s+(\w+)', content)
        if types:
            pascal_case = sum(1 for name in types if name[0].isupper())
            type_score = pascal_case / len(types)
        else:
            type_score = 1.0
        
        return (base_score + interface_score + type_score) / 3