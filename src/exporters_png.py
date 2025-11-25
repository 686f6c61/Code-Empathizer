#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Generador de Gráficas PNG - Visualizaciones de Alta Resolución
=============================================================================

Este módulo genera gráficas PNG de alta resolución (300 DPI) para visualizar
los resultados de análisis de Code Empathizer.

GRÁFICAS GENERADAS:
------------------
1. RADAR (Spider Chart)
   - Comparación visual de todas las categorías
   - Empresa vs Candidato en un solo gráfico
   - Ideal para ver fortalezas/debilidades relativas

2. BARRAS (Bar Chart)
   - Comparación lado a lado por categoría
   - Fácil de leer para presentaciones
   - Incluye valores numéricos

3. CATEGORÍAS (Line Chart)
   - Evolución de puntuaciones por categoría
   - Muestra tendencias de similitud

4. DISTRIBUCIÓN (Pie Charts)
   - Distribución de puntuaciones
   - Gráficos separados para empresa y candidato

5. HEATMAP
   - Mapa de calor de métricas
   - Intensidad de color por puntuación
   - Vista matricial de resultados

ESPECIFICACIONES TÉCNICAS:
-------------------------
- Formato: PNG (RGBA, 8 bits por canal)
- Resolución: 300 DPI (alta calidad para impresión)
- Dimensiones típicas: ~2879×2369 px
- Tamaño archivo: 245-519 KB por gráfica
- Backend: Agg (sin GUI, apto para servidores)

USO DEL MÓDULO:
--------------
    >>> from exporters_png import (
    ...     generar_grafica_radar_png,
    ...     generar_grafica_barras_png,
    ...     generar_grafica_heatmap_png
    ... )
    >>>
    >>> # Generar gráfica radar
    >>> png_bytes = generar_grafica_radar_png(metricas, timestamp)
    >>>
    >>> # Guardar a archivo
    >>> with open("radar.png", "wb") as f:
    ...     f.write(png_bytes)

INTEGRACIÓN CON EXPORTERS:
-------------------------
Este módulo es utilizado por exporters.py para generar el archivo ZIP
de gráficas. Las funciones retornan bytes que pueden ser guardados
directamente o agregados a un archivo ZIP.

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
from typing import Dict, Any        # Type hints
import matplotlib                   # Librería de gráficas
matplotlib.use('Agg')               # Backend sin GUI (necesario para servidores)
import matplotlib.pyplot as plt     # API de pyplot
import numpy as np                  # Cálculos numéricos
from io import BytesIO              # Buffer de bytes en memoria
from datetime import datetime       # Timestamps


def generar_grafica_radar_png(metricas: Dict[str, Any], timestamp: str) -> bytes:
    """Genera gráfica radar en formato PNG"""
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))

    # Extraer datos de repos
    if 'repos' not in metricas or 'empresa' not in metricas['repos'] or 'candidato' not in metricas['repos']:
        plt.close(fig)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        return buffer.getvalue()

    # Categorías de análisis
    categories = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                  'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']

    empresa_data = metricas['repos']['empresa']
    candidato_data = metricas['repos']['candidato']

    empresa_scores = []
    candidato_scores = []

    # Extraer scores de cada categoría
    for cat in categories:
        # Obtener el primer valor numérico de cada categoría
        emp_val = empresa_data.get(cat, {})
        can_val = candidato_data.get(cat, {})

        # Extraer valores numéricos
        if isinstance(emp_val, dict):
            emp_score = list(emp_val.values())[0] if emp_val.values() else 0
            emp_score = emp_score * 100 if isinstance(emp_score, float) and emp_score <= 1 else emp_score
        else:
            emp_score = 0

        if isinstance(can_val, dict):
            can_score = list(can_val.values())[0] if can_val.values() else 0
            can_score = can_score * 100 if isinstance(can_score, float) and can_score <= 1 else can_score
        else:
            can_score = 0

        empresa_scores.append(emp_score if isinstance(emp_score, (int, float)) else 0)
        candidato_scores.append(can_score if isinstance(can_score, (int, float)) else 0)

    # Configurar ángulos
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    empresa_scores += empresa_scores[:1]
    candidato_scores += candidato_scores[:1]
    angles += angles[:1]

    # Plotear
    ax.plot(angles, empresa_scores, 'o-', linewidth=2, label='Empresa', color='#3498db')
    ax.fill(angles, empresa_scores, alpha=0.25, color='#3498db')
    ax.plot(angles, candidato_scores, 'o-', linewidth=2, label='Candidato', color='#e74c3c')
    ax.fill(angles, candidato_scores, alpha=0.25, color='#e74c3c')

    # Configurar etiquetas
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], size=10)
    ax.set_ylim(0, 100)
    ax.set_title('Comparación de Métricas (Gráfica Radar)', size=14, weight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)

    # Guardar en buffer
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()


def generar_grafica_barras_png(metricas: Dict[str, Any], timestamp: str) -> bytes:
    """Genera gráfica de barras comparativas en formato PNG"""
    fig, ax = plt.subplots(figsize=(12, 8))

    if 'repos' not in metricas or 'empresa' not in metricas['repos'] or 'candidato' not in metricas['repos']:
        plt.close(fig)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        return buffer.getvalue()

    categories = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                  'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']

    empresa_data = metricas['repos']['empresa']
    candidato_data = metricas['repos']['candidato']

    empresa_scores = []
    candidato_scores = []

    for cat in categories:
        emp_val = empresa_data.get(cat, {})
        can_val = candidato_data.get(cat, {})

        if isinstance(emp_val, dict):
            emp_score = list(emp_val.values())[0] if emp_val.values() else 0
            emp_score = emp_score * 100 if isinstance(emp_score, float) and emp_score <= 1 else emp_score
        else:
            emp_score = 0

        if isinstance(can_val, dict):
            can_score = list(can_val.values())[0] if can_val.values() else 0
            can_score = can_score * 100 if isinstance(can_score, float) and can_score <= 1 else can_score
        else:
            can_score = 0

        empresa_scores.append(emp_score if isinstance(emp_score, (int, float)) else 0)
        candidato_scores.append(can_score if isinstance(can_score, (int, float)) else 0)

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax.bar(x - width/2, empresa_scores, width, label='Empresa', color='#3498db')
    bars2 = ax.bar(x + width/2, candidato_scores, width, label='Candidato', color='#e74c3c')

    ax.set_xlabel('Categorías', fontsize=12, weight='bold')
    ax.set_ylabel('Puntuación (%)', fontsize=12, weight='bold')
    ax.set_title('Comparación de Puntuaciones por Categoría', fontsize=14, weight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)

    # Agregar valores encima de las barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=8)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()


def generar_grafica_categorias_png(metricas: Dict[str, Any], timestamp: str) -> bytes:
    """Genera gráfica de líneas para evolución de categorías en formato PNG"""
    fig, ax = plt.subplots(figsize=(12, 6))

    if 'repos' not in metricas or 'empresa' not in metricas['repos'] or 'candidato' not in metricas['repos']:
        plt.close(fig)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        return buffer.getvalue()

    categories = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                  'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']

    empresa_data = metricas['repos']['empresa']
    candidato_data = metricas['repos']['candidato']

    empresa_scores = []
    candidato_scores = []
    diferencias = []

    for cat in categories:
        emp_val = empresa_data.get(cat, {})
        can_val = candidato_data.get(cat, {})

        if isinstance(emp_val, dict):
            emp = list(emp_val.values())[0] if emp_val.values() else 0
            emp = emp * 100 if isinstance(emp, float) and emp <= 1 else emp
        else:
            emp = 0

        if isinstance(can_val, dict):
            can = list(can_val.values())[0] if can_val.values() else 0
            can = can * 100 if isinstance(can, float) and can <= 1 else can
        else:
            can = 0

        empresa_scores.append(emp if isinstance(emp, (int, float)) else 0)
        candidato_scores.append(can if isinstance(can, (int, float)) else 0)
        diferencias.append(abs(emp - can) if isinstance(emp, (int, float)) and isinstance(can, (int, float)) else 0)

    x = range(len(categories))

    ax.plot(x, empresa_scores, marker='o', linewidth=2, markersize=8,
            label='Empresa', color='#3498db')
    ax.plot(x, candidato_scores, marker='s', linewidth=2, markersize=8,
            label='Candidato', color='#e74c3c')
    ax.plot(x, diferencias, marker='^', linewidth=2, markersize=8,
            label='Diferencia', color='#f39c12', linestyle='--')

    ax.set_xlabel('Categorías', fontsize=12, weight='bold')
    ax.set_ylabel('Puntuación (%)', fontsize=12, weight='bold')
    ax.set_title('Análisis Comparativo de Categorías', fontsize=14, weight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories],
                      rotation=45, ha='right')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 110)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()


def generar_grafica_distribucion_png(metricas: Dict[str, Any], timestamp: str) -> bytes:
    """Genera gráfica de distribución (pie chart) en formato PNG"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    if 'repos' not in metricas or 'empresa' not in metricas['repos'] or 'candidato' not in metricas['repos']:
        plt.close(fig)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        return buffer.getvalue()

    categories = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                  'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']

    empresa_data = metricas['repos']['empresa']
    candidato_data = metricas['repos']['candidato']

    empresa_scores = []
    candidato_scores = []

    for cat in categories:
        emp_val = empresa_data.get(cat, {})
        can_val = candidato_data.get(cat, {})

        if isinstance(emp_val, dict):
            emp_score = list(emp_val.values())[0] if emp_val.values() else 0
            emp_score = emp_score * 100 if isinstance(emp_score, float) and emp_score <= 1 else emp_score
        else:
            emp_score = 0

        if isinstance(can_val, dict):
            can_score = list(can_val.values())[0] if can_val.values() else 0
            can_score = can_score * 100 if isinstance(can_score, float) and can_score <= 1 else can_score
        else:
            can_score = 0

        empresa_scores.append(emp_score if isinstance(emp_score, (int, float)) else 0)
        candidato_scores.append(can_score if isinstance(can_score, (int, float)) else 0)

    colors = plt.cm.Set3(range(len(categories)))
    labels = [cat.replace('_', ' ').title() for cat in categories]

    # Empresa
    ax1.pie(empresa_scores, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Distribución - Empresa', fontsize=12, weight='bold')

    # Candidato
    ax2.pie(candidato_scores, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Distribución - Candidato', fontsize=12, weight='bold')

    plt.suptitle('Distribución de Puntuaciones por Categoría', fontsize=14, weight='bold')

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()


def generar_grafica_heatmap_png(metricas: Dict[str, Any], timestamp: str) -> bytes:
    """Genera mapa de calor en formato PNG"""
    fig, ax = plt.subplots(figsize=(10, 8))

    if 'repos' not in metricas or 'empresa' not in metricas['repos'] or 'candidato' not in metricas['repos']:
        plt.close(fig)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        return buffer.getvalue()

    categories = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                  'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']

    empresa_data = metricas['repos']['empresa']
    candidato_data = metricas['repos']['candidato']

    data = []

    for cat in categories:
        emp_val = empresa_data.get(cat, {})
        can_val = candidato_data.get(cat, {})

        if isinstance(emp_val, dict):
            empresa = list(emp_val.values())[0] if emp_val.values() else 0
            empresa = empresa * 100 if isinstance(empresa, float) and empresa <= 1 else empresa
        else:
            empresa = 0

        if isinstance(can_val, dict):
            candidato = list(can_val.values())[0] if can_val.values() else 0
            candidato = candidato * 100 if isinstance(candidato, float) and candidato <= 1 else candidato
        else:
            candidato = 0

        diferencia = abs(empresa - candidato) if isinstance(empresa, (int, float)) and isinstance(candidato, (int, float)) else 0
        data.append([empresa, candidato, diferencia])

    data = np.array(data)

    im = ax.imshow(data.T, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories],
                      rotation=45, ha='right')
    ax.set_yticklabels(['Empresa', 'Candidato', 'Diferencia'])

    # Agregar valores en las celdas
    for i in range(len(categories)):
        for j in range(3):
            text = ax.text(i, j, f'{data[i, j]:.1f}',
                         ha="center", va="center", color="black", fontsize=9)

    ax.set_title('Mapa de Calor - Comparación de Métricas', fontsize=14, weight='bold', pad=20)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Puntuación (%)', rotation=270, labelpad=20)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()


def generar_readme_graficas_png(timestamp: str) -> str:
    """Genera README para gráficas PNG"""
    return f"""╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              GRÁFICAS DE ANÁLISIS DE EMPATÍA DE CÓDIGO              ║
║                      Code Empathizer v2.2.2                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

CONTENIDO DEL ARCHIVO

Este archivo ZIP contiene todas las gráficas generadas del análisis de
empatía de código entre repositorios en formato PNG de alta calidad.

ARCHIVOS INCLUIDOS:

1. grafica_radar_{timestamp}.png
   └─ Gráfica tipo radar que muestra la comparación general entre
      empresa y candidato en todas las categorías

2. grafica_barras_{timestamp}.png
   └─ Gráfica de barras comparativas por categoría individual

3. grafica_categorias_{timestamp}.png
   └─ Gráfica de líneas mostrando evolución y diferencias

4. grafica_distribucion_{timestamp}.png
   └─ Gráficas circulares (pie charts) de distribución de puntuaciones

5. grafica_heatmap_{timestamp}.png
   └─ Mapa de calor mostrando intensidad de métricas

CÓMO USAR ESTAS GRÁFICAS:

• Abrir con cualquier visor de imágenes
• Insertar en presentaciones (PowerPoint, Google Slides, etc.)
• Incluir en documentos (Word, PDF, etc.)
• Compartir directamente por email o mensajería
• Publicar en documentación técnica

RESOLUCIÓN:

Todas las gráficas están generadas en alta resolución (300 DPI)
para garantizar calidad profesional en impresión y presentaciones.

INFORMACIÓN TÉCNICA:

• Formato: PNG
• Resolución: 300 DPI
• Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
• Herramienta: Code Empathizer v2.2.2

═══════════════════════════════════════════════════════════════════════

Para más información sobre Code Empathizer:
https://github.com/686f6c61/Code-Empathizer

Licencia: MIT
Autor: https://github.com/686f6c61
"""
