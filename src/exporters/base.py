#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Módulo Base de Exportación - Clase Base y Utilidades
=============================================================================

Este módulo contiene la clase base y utilidades compartidas por todos los
exportadores de Code Empathizer.

CONTENIDO:
---------
- BaseExporter: Clase base con métodos comunes
- Filtros Jinja2 para formateo de fechas
- Constantes compartidas (categorías, rutas)

USO:
---
    from exporters.base import BaseExporter, CATEGORIAS

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import os
import logging
from datetime import datetime
from typing import Any

# Configurar logger
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES
# =============================================================================

CATEGORIAS = [
    "nombres", "documentacion", "modularidad", "complejidad",
    "manejo_errores", "pruebas", "consistencia_estilo", "seguridad"
]

CATEGORIAS_LABELS = [
    'NOMBRES', 'DOCUMENTACIÓN', 'MODULARIDAD', 'COMPLEJIDAD',
    'MANEJO ERRORES', 'PRUEBAS', 'SEGURIDAD', 'CONSISTENCIA'
]

EXPORT_DIR = 'export'


# =============================================================================
# CLASE BASE
# =============================================================================

class BaseExporter:
    """
    Clase base para todos los exportadores.

    Proporciona métodos comunes como formateo de fechas y
    creación del directorio de exportación.
    """

    def __init__(self):
        """Inicializa el exportador base."""
        self._ensure_export_dir()

    def _ensure_export_dir(self) -> None:
        """Crea el directorio de exportación si no existe."""
        os.makedirs(EXPORT_DIR, exist_ok=True)

    @staticmethod
    def format_date(value: Any) -> str:
        """
        Filtro Jinja2 para formatear fechas.

        Args:
            value: Fecha en formato ISO string o datetime object.

        Returns:
            str: Fecha formateada como DD/MM/YYYY HH:MM:SS.
        """
        try:
            if isinstance(value, str):
                date = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                date = value
            return date.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return str(value)

    @staticmethod
    def get_output_path(prefix: str, timestamp: str, extension: str) -> str:
        """
        Genera la ruta del archivo de salida.

        Args:
            prefix: Prefijo del archivo (ej: 'reporte', 'dashboard')
            timestamp: Marca de tiempo
            extension: Extensión del archivo (ej: 'txt', 'html')

        Returns:
            str: Ruta completa del archivo
        """
        return f'{EXPORT_DIR}/{prefix}_{timestamp}.{extension}'
