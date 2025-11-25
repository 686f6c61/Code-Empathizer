#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Exportador PNG - Generación de Gráficas de Alta Resolución
=============================================================================

Este módulo gestiona la exportación de gráficas en formato PNG de alta
resolución, empaquetadas en un archivo ZIP.

CARACTERÍSTICAS:
---------------
- Resolución 300 DPI sin pérdida
- Múltiples tipos de gráficas
- Archivo ZIP con todas las imágenes
- README descriptivo incluido

GRÁFICAS INCLUIDAS:
------------------
1. Radar - Comparación por categorías
2. Barras - Comparación lado a lado
3. Categorías - Evolución de métricas
4. Distribución - Vista de calidad
5. Heatmap - Mapa de calor

USO:
---
    from exporters.png_exporter import PngExporter

    exporter = PngExporter()
    zip_path = exporter.exportar(metricas, timestamp)

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import logging
import zipfile
from datetime import datetime
from typing import Dict, Any

import sys
import os

# Añadir directorio src al path para importar exporters_png
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from .base import BaseExporter

# Importar generadores de PNG desde exporters_png
from exporters_png import (
    generar_grafica_radar_png,
    generar_grafica_barras_png,
    generar_grafica_categorias_png,
    generar_grafica_distribucion_png,
    generar_grafica_heatmap_png,
    generar_readme_graficas_png
)

logger = logging.getLogger(__name__)


class PngExporter(BaseExporter):
    """Exportador de gráficas PNG en archivo ZIP."""

    def exportar(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta todas las gráficas generadas en un archivo ZIP.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo ZIP generado.

        Raises:
            IOError: Si no se puede escribir el archivo ZIP.
        """
        try:
            zip_path = self.get_output_path('graficas', timestamp, 'zip')

            logger.info(f"Generando ZIP de gráficas PNG: {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Gráfica radar
                png_radar = generar_grafica_radar_png(metricas, timestamp)
                zipf.writestr(f'grafica_radar_{timestamp}.png', png_radar)
                logger.debug("Gráfica radar agregada al ZIP")

                # Gráfica de barras
                png_barras = generar_grafica_barras_png(metricas, timestamp)
                zipf.writestr(f'grafica_barras_{timestamp}.png', png_barras)
                logger.debug("Gráfica de barras agregada al ZIP")

                # Gráfica de categorías
                png_categorias = generar_grafica_categorias_png(metricas, timestamp)
                zipf.writestr(f'grafica_categorias_{timestamp}.png', png_categorias)
                logger.debug("Gráfica de categorías agregada al ZIP")

                # Gráfica de distribución
                png_distribucion = generar_grafica_distribucion_png(metricas, timestamp)
                zipf.writestr(f'grafica_distribucion_{timestamp}.png', png_distribucion)
                logger.debug("Gráfica de distribución agregada al ZIP")

                # Gráfica de heatmap
                png_heatmap = generar_grafica_heatmap_png(metricas, timestamp)
                zipf.writestr(f'grafica_heatmap_{timestamp}.png', png_heatmap)
                logger.debug("Gráfica de mapa de calor agregada al ZIP")

                # README
                readme_content = generar_readme_graficas_png(timestamp)
                zipf.writestr('README.txt', readme_content)
                logger.debug("README agregado al ZIP")

            logger.info(f"ZIP de gráficas generado exitosamente: {zip_path}")
            print(f"\nGráficas exportadas a: {zip_path}")

            return zip_path

        except Exception as e:
            logger.error(f"Error generando ZIP de gráficas: {str(e)}")
            raise

    def generar_readme(self, timestamp: str) -> str:
        """
        Genera contenido del README para el ZIP de gráficas.

        Args:
            timestamp: Marca de tiempo del análisis.

        Returns:
            str: Contenido del README.
        """
        return f"""╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              GRÁFICAS DE ANÁLISIS DE EMPATÍA DE CÓDIGO              ║
║                      Code Empathizer v2.2.2                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

CONTENIDO DEL ARCHIVO

Este archivo ZIP contiene todas las gráficas generadas del análisis de
empatía de código entre repositorios.

ARCHIVOS INCLUIDOS:

1. grafica_radar_{timestamp}.png
   └─ Gráfica tipo radar que muestra la comparación general entre
      empresa y candidato en todas las categorías

2. grafica_barras_{timestamp}.png
   └─ Gráfica de barras comparativas por categoría individual

3. grafica_categorias_{timestamp}.png
   └─ Gráfica detallada de distribución por categorías

4. grafica_distribucion_{timestamp}.png
   └─ Gráfica de distribución de puntuaciones

5. grafica_heatmap_{timestamp}.png
   └─ Mapa de calor con comparación visual de todas las categorías

6. README.txt
   └─ Este archivo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÓMO USAR LAS GRÁFICAS

1. Extraer el contenido del ZIP a una carpeta
2. Abrir cualquier archivo .png en tu visor de imágenes
3. Las gráficas son de alta resolución (300 DPI)
4. Ideales para presentaciones e informes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INFORMACIÓN

Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Timestamp: {timestamp}
Herramienta: Code Empathizer v2.2.2
Autor: R. Benítez

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MÁS INFORMACIÓN

Repositorio: https://github.com/686f6c61/Repo-Code-Empathizer
Documentación: Ver README.md en el repositorio principal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¡Gracias por usar Code Empathizer!
"""
