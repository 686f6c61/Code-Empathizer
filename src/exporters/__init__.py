#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Paquete de Exportadores - Code Empathizer
=============================================================================

Este paquete contiene los exportadores de resultados para múltiples formatos:
TXT, JSON, HTML, Dashboard y PNG.

ARQUITECTURA DEL PAQUETE:
------------------------
exporters/
├── __init__.py          # Este archivo (clase Exporter unificada)
├── base.py              # Clase base y utilidades
├── txt_exporter.py      # Exportador TXT
├── json_exporter.py     # Exportador JSON
├── html_exporter.py     # Exportador HTML/Dashboard
├── charts.py            # Generador de gráficas HTML
└── png_exporter.py      # Exportador PNG ZIP

USO:
---
    # Forma recomendada (igual que antes)
    from exporters import Exporter

    exporter = Exporter()
    exporter.exportar_txt(metricas, timestamp)
    exporter.exportar_json(metricas, timestamp)
    exporter.exportar_html(metricas, timestamp)
    exporter.exportar_graficas_zip(metricas, timestamp)
    exporter.exportar_equipo(resultados, timestamp)

COMPATIBILIDAD:
--------------
Este paquete mantiene 100% compatibilidad con el API anterior.
La clase Exporter se comporta exactamente igual que antes.

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

from typing import Dict, Any

from .base import BaseExporter
from .txt_exporter import TxtExporter
from .json_exporter import JsonExporter
from .html_exporter import HtmlExporter
from .charts import ChartGenerator
from .png_exporter import PngExporter


class Exporter(BaseExporter):
    """
    Clase principal de exportación - Mantiene compatibilidad con API anterior.

    Esta clase unifica todos los exportadores especializados y proporciona
    la misma interfaz que el exportador original.
    """

    def __init__(self):
        """Inicializa todos los exportadores especializados."""
        super().__init__()
        self._txt_exporter = TxtExporter()
        self._json_exporter = JsonExporter()
        self._html_exporter = HtmlExporter()
        self._chart_generator = ChartGenerator()
        self._png_exporter = PngExporter()

    def exportar_txt(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta los resultados a archivo de texto plano.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo generado.
        """
        return self._txt_exporter.exportar(metricas, timestamp)

    def exportar_json(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta los resultados a formato JSON.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo generado.
        """
        return self._json_exporter.exportar(metricas, timestamp)

    def exportar_html(self, metricas: Dict[str, Any], timestamp: str, dashboard: bool = False) -> str:
        """
        Exporta los resultados a formato HTML.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.
            dashboard: Si True, genera dashboard interactivo.

        Returns:
            str: Ruta al archivo generado.
        """
        return self._html_exporter.exportar(metricas, timestamp, dashboard)

    def exportar_equipo(self, resultados_equipo: Dict[str, Any], timestamp: str) -> None:
        """
        Genera un reporte especial para análisis de equipo.

        Args:
            resultados_equipo: Datos del análisis de equipo.
            timestamp: Marca de tiempo para el nombre del archivo.
        """
        return self._html_exporter.exportar_equipo(resultados_equipo, timestamp)

    def exportar_graficas_zip(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta todas las gráficas en un archivo ZIP.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo ZIP generado.
        """
        return self._png_exporter.exportar(metricas, timestamp)

    # =========================================================================
    # Métodos de generación de gráficas HTML (para compatibilidad)
    # =========================================================================

    def _generar_grafica_radar(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica radar interactiva."""
        return self._chart_generator.generar_radar(metricas, timestamp)

    def _generar_grafica_barras(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de barras comparativa."""
        return self._chart_generator.generar_barras(metricas, timestamp)

    def _generar_grafica_categorias(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de líneas por categorías."""
        return self._chart_generator.generar_categorias(metricas, timestamp)

    def _generar_grafica_distribucion(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de distribución."""
        return self._chart_generator.generar_distribucion(metricas, timestamp)

    def _generar_grafica_equipo(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica comparativa de equipo."""
        return self._chart_generator.generar_equipo(metricas, timestamp)

    def _generar_grafica_heatmap(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con mapa de calor comparativo."""
        return self._chart_generator.generar_heatmap(metricas, timestamp)

    def _generar_readme_graficas(self, timestamp: str) -> str:
        """Genera README para el ZIP de gráficas."""
        return self._png_exporter.generar_readme(timestamp)


# Exportaciones públicas
__all__ = [
    'Exporter',
    'BaseExporter',
    'TxtExporter',
    'JsonExporter',
    'HtmlExporter',
    'ChartGenerator',
    'PngExporter'
]
