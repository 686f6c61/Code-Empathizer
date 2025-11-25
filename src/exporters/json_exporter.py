#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Exportador JSON - Generación de Datos Estructurados
=============================================================================

Este módulo gestiona la exportación de resultados a formato JSON para
procesamiento automatizado e integración con otras herramientas.

CARACTERÍSTICAS:
---------------
- Datos estructurados con indentación
- Codificación UTF-8 sin escape ASCII
- Timestamp incluido en metadata
- Compatible con APIs REST

USO:
---
    from exporters.json_exporter import JsonExporter

    exporter = JsonExporter()
    path = exporter.exportar(metricas, timestamp)

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import json
import logging
from typing import Dict, Any

from .base import BaseExporter

logger = logging.getLogger(__name__)


class JsonExporter(BaseExporter):
    """Exportador de reportes en formato JSON."""

    def exportar(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta los resultados a formato JSON.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo generado.

        Raises:
            IOError: Si no se puede escribir el archivo.
        """
        try:
            output_path = self.get_output_path('reporte', timestamp, 'json')

            datos_export = {
                "timestamp": timestamp,
                "metricas": metricas
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(datos_export, f, indent=2, ensure_ascii=False)

            return output_path
        except Exception as e:
            logger.error(f"Error generando reporte JSON: {str(e)}")
            raise
