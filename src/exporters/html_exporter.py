#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Exportador HTML - Generación de Reportes HTML y Dashboard
=============================================================================

Este módulo gestiona la exportación de resultados a formato HTML,
incluyendo reportes estáticos y dashboards interactivos.

FORMATOS SOPORTADOS:
-------------------
1. HTML Estático - Visualización básica
2. Dashboard Bootstrap - Interfaz interactiva con Chart.js
3. Reporte de Equipo - Comparación de múltiples candidatos

PLANTILLAS:
----------
Las plantillas Jinja2 se cargan desde el directorio templates/:
- informe_template.html
- dashboard_bootstrap.html

USO:
---
    from exporters.html_exporter import HtmlExporter

    exporter = HtmlExporter()
    path = exporter.exportar(metricas, timestamp)
    path = exporter.exportar_equipo(resultados, timestamp)

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import os
import json
import logging
from typing import Dict, Any, List

from jinja2 import Environment, FileSystemLoader

from .base import BaseExporter, CATEGORIAS

logger = logging.getLogger(__name__)


class HtmlExporter(BaseExporter):
    """Exportador de reportes en formato HTML."""

    def __init__(self):
        """Inicializa el exportador HTML con el entorno Jinja2."""
        super().__init__()
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_dir = os.path.join(root_dir, "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters['date'] = self.format_date
        self.env.filters['format_date'] = self.format_date

    def exportar(self, metricas: Dict[str, Any], timestamp: str, dashboard: bool = False) -> str:
        """
        Exporta los resultados a formato HTML.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.
            dashboard: Si True, genera dashboard interactivo.

        Returns:
            str: Ruta al archivo generado.

        Raises:
            IOError: Si no se puede escribir el archivo.
            TemplateNotFound: Si no encuentra las plantillas HTML.
        """
        try:
            # Verificar formato de métricas
            if 'empresa' not in metricas.get('repos', {}) and 'A' not in metricas.get('repos', {}):
                logger.error("Formato de métricas no reconocido")

            # Seleccionar plantilla
            if dashboard or 'empathy_analysis' in metricas:
                template = self.env.get_template('dashboard_bootstrap.html')
            else:
                template = self.env.get_template('informe_template.html')

            datos_template = {
                "titulo": "Análisis de Empatía de Código",
                "fecha_generacion": timestamp,
                "timestamp": timestamp,
                "metricas": metricas,
                "categorias": CATEGORIAS
            }

            html_content = template.render(**datos_template)

            output_path = self.get_output_path('reporte', timestamp, 'html')

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return output_path
        except Exception as e:
            logger.error(f"Error generando reporte HTML: {str(e)}")
            raise

    def exportar_equipo(self, resultados_equipo: Dict[str, Any], timestamp: str) -> None:
        """
        Genera un reporte especial para análisis de equipo.

        Args:
            resultados_equipo: Datos del análisis de equipo con empresa y candidatos.
            timestamp: Marca de tiempo para el nombre del archivo.
        """
        try:
            archivo_salida = os.path.join('export', f"equipo_{timestamp}.html")

            # Preparar datos para el template
            candidatos_ordenados = sorted(
                resultados_equipo['candidatos'].items(),
                key=lambda x: x[1]['empathy_score'],
                reverse=True
            )

            # Crear resumen comparativo
            comparacion = []
            for nombre, datos in candidatos_ordenados:
                comparacion.append({
                    'nombre': nombre,
                    'score': datos['empathy_score'],
                    'nivel': datos['empathy_analysis']['interpretation']['level'],
                    'color': datos['empathy_analysis']['interpretation']['color'],
                    'recomendacion': datos['empathy_analysis']['interpretation']['recommendation'],
                    'fortalezas': [s for s in datos['empathy_analysis']['detailed_analysis']['strengths'] if s['score'] >= 80],
                    'debilidades': [s for s in datos['empathy_analysis']['detailed_analysis']['weaknesses'] if s['score'] < 60],
                    'lenguajes': datos['analisis']['metadata'].get('lenguajes_analizados', []),
                    'category_scores': datos['empathy_analysis']['category_scores'],
                    'duplicacion': datos['analisis'].get('duplicacion', {}),
                    'dependencias': datos['analisis'].get('dependencias', {}),
                    'patrones': datos['analisis'].get('patrones', {}),
                    'rendimiento': datos['analisis'].get('rendimiento', {}),
                    'comentarios': datos['analisis'].get('comentarios', {}),
                    'metadata': datos['analisis']['metadata']
                })

            # Generar HTML personalizado
            html_content = self._generar_html_equipo(
                resultados_equipo['empresa'],
                comparacion,
                timestamp
            )

            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Generar JSON adicional
            json_file = os.path.join('export', f"equipo_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(resultados_equipo, f, ensure_ascii=False, indent=2)

            logger.info(f"Reporte de equipo generado: {archivo_salida}")

        except Exception as e:
            logger.error(f"Error generando reporte de equipo: {str(e)}")
            raise

    def _generar_html_equipo(self, empresa_data: Dict, candidatos: List[Dict], timestamp: str) -> str:
        """Genera HTML personalizado para reporte de equipo."""
        categorias = ['nombres', 'documentacion', 'modularidad', 'complejidad',
                      'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']
        categorias_labels = [cat.replace('_', ' ').title() for cat in categorias]

        html = self._get_team_html_header(timestamp, empresa_data)
        html += self._get_team_chart_section(categorias_labels, candidatos)
        html += self._get_team_table(categorias, candidatos)
        html += self._get_team_candidates_detail(candidatos)
        html += self._get_team_footer()
        html += self._get_team_script(categorias_labels, categorias, candidatos)

        return html

    def _get_team_html_header(self, timestamp: str, empresa_data: Dict) -> str:
        """Genera el encabezado HTML del reporte de equipo."""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANÁLISIS DE EQUIPO - CODE EMPATHIZER</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: #000000;
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .empresa-info {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        .empresa-info h2 {{ color: #333; margin-bottom: 20px; }}
        .chart-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        .chart-container {{ position: relative; height: 400px; margin: 20px 0; }}
        .candidato-card {{
            background: #f8f9fa;
            padding: 30px;
            margin: 20px 0;
            border-radius: 10px;
            border-left: 5px solid #333;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        .candidato-card.top {{ border-left-color: #000; background: #f0f0f0; }}
        .candidato-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .candidato-nombre {{ font-size: 1.5em; font-weight: bold; }}
        .candidato-score {{ font-size: 2.5em; font-weight: bold; }}
        .metricas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metrica-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        .metrica-label {{ font-size: 0.9em; color: #666; margin-bottom: 5px; text-transform: uppercase; }}
        .metrica-value {{ font-size: 1.8em; font-weight: bold; color: #333; }}
        .fortalezas-debilidades {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .lista-items {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        .lista-items h4 {{ color: #333; margin-bottom: 15px; font-size: 1.1em; }}
        .lista-items ul {{ list-style: none; padding: 0; }}
        .lista-items li {{ padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
        .lista-items li:last-child {{ border-bottom: none; }}
        .score-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
            background: #e0e0e0;
            color: #333;
        }}
        .lenguajes {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
        .lenguaje-tag {{ background: #e0e0e0; padding: 6px 15px; border-radius: 20px; font-size: 0.9em; }}
        .posicion {{
            display: inline-block;
            width: 50px;
            height: 50px;
            background: #333;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 50px;
            font-weight: bold;
            font-size: 1.2em;
            margin-right: 15px;
        }}
        .posicion.gold {{ background: #FFD700; color: #333; }}
        .posicion.silver {{ background: #C0C0C0; color: #333; }}
        .posicion.bronze {{ background: #CD7F32; color: white; }}
        .info-adicional {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        .info-card h5 {{ color: #666; margin-bottom: 10px; font-size: 1em; text-transform: uppercase; }}
        .info-card p {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .comparacion-tabla {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .footer {{ text-align: center; padding: 30px 0; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ANÁLISIS DE EQUIPO</h1>
            <p>EVALUACIÓN COMPARATIVA DE CANDIDATOS</p>
            <p style="margin-top: 10px; opacity: 0.8;">Generado el {self.format_date(timestamp)}</p>
        </div>

        <div class="empresa-info">
            <h2>Empresa de Referencia</h2>
            <p><strong>Repositorio:</strong> {empresa_data['metadata']['nombre']}</p>
            <p><strong>URL:</strong> <a href="{empresa_data['metadata']['url']}" target="_blank">{empresa_data['metadata']['url']}</a></p>
            <p><strong>Lenguaje Principal:</strong> {empresa_data['metadata']['lenguaje_principal']}</p>
            <p><strong>Archivos Analizados:</strong> {empresa_data['metadata']['archivos_analizados']}</p>
            <p><strong>Tamaño:</strong> {empresa_data['metadata']['tamano_kb']} KB</p>
        </div>
"""

    def _get_team_chart_section(self, categorias_labels: List[str], candidatos: List[Dict]) -> str:
        """Genera la sección del gráfico comparativo."""
        return """
        <div class="chart-section">
            <h2>Comparación Visual de Candidatos</h2>
            <div class="chart-container">
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>
"""

    def _get_team_table(self, categorias: List[str], candidatos: List[Dict]) -> str:
        """Genera la tabla comparativa."""
        html = """
        <div class="comparacion-tabla">
            <h2>Tabla Comparativa Detallada</h2>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
"""
        for candidato in candidatos:
            html += f"<th>{candidato['nombre']}</th>"

        html += """
                    </tr>
                </thead>
                <tbody>
"""
        for categoria in categorias:
            html += f"<tr><td><strong>{categoria.replace('_', ' ').title()}</strong></td>"
            for candidato in candidatos:
                score = candidato['category_scores'].get(categoria, 0)
                html += f"<td>{score:.1f}%</td>"
            html += "</tr>"

        # Métricas adicionales
        html += self._get_additional_metrics_rows(candidatos)

        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _get_additional_metrics_rows(self, candidatos: List[Dict]) -> str:
        """Genera filas de métricas adicionales para la tabla."""
        html = ""

        # Duplicación
        html += "<tr><td><strong>Duplicación de Código</strong></td>"
        for candidato in candidatos:
            dup = candidato.get('duplicacion', {})
            porcentaje = dup.get('porcentaje_global', 'N/A')
            html += f"<td>{porcentaje}%</td>" if porcentaje != 'N/A' else "<td>N/A</td>"
        html += "</tr>"

        # Dependencias
        html += "<tr><td><strong>Dependencias Totales</strong></td>"
        for candidato in candidatos:
            deps = candidato.get('dependencias', {})
            total = deps.get('total_dependencies', 'N/A')
            html += f"<td>{total}</td>"
        html += "</tr>"

        # Score de Patrones
        html += "<tr><td><strong>Score de Patrones</strong></td>"
        for candidato in candidatos:
            patrones = candidato.get('patrones', {})
            score = patrones.get('pattern_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        html += "</tr>"

        # Score de Rendimiento
        html += "<tr><td><strong>Score de Rendimiento</strong></td>"
        for candidato in candidatos:
            perf = candidato.get('rendimiento', {})
            score = perf.get('performance_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        html += "</tr>"

        # Score de Comentarios
        html += "<tr><td><strong>Score de Comentarios</strong></td>"
        for candidato in candidatos:
            comments = candidato.get('comentarios', {})
            score = comments.get('comment_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        html += "</tr>"

        # Archivos Analizados
        html += "<tr><td><strong>Archivos Analizados</strong></td>"
        for candidato in candidatos:
            archivos = candidato['metadata'].get('archivos_analizados', 'N/A')
            html += f"<td>{archivos}</td>"
        html += "</tr>"

        return html

    def _get_team_candidates_detail(self, candidatos: List[Dict]) -> str:
        """Genera el detalle de cada candidato."""
        html = """
        <h2 style="text-align: center; margin: 30px 0;">Análisis Detallado por Candidato</h2>
"""
        for i, candidato in enumerate(candidatos):
            posicion_class = 'gold' if i == 0 else 'silver' if i == 1 else 'bronze' if i == 2 else ''
            card_class = 'candidato-card top' if i == 0 else 'candidato-card'

            html += f"""
            <div class="{card_class}">
                <div class="candidato-header">
                    <div>
                        <span class="posicion {posicion_class}">{i + 1}</span>
                        <span class="candidato-nombre">{candidato['nombre']}</span>
                    </div>
                    <div class="candidato-score" style="color: {candidato['color']}">
                        {candidato['score']:.1f}%
                    </div>
                </div>

                <p><strong>Nivel:</strong> {candidato['nivel']}</p>
                <p><strong>Recomendación:</strong> {candidato['recomendacion']}</p>
                <p><strong>URL:</strong> <a href="{candidato['metadata']['url']}" target="_blank">{candidato['metadata']['url']}</a></p>

                <div class="metricas-grid">
                    <div class="metrica-item">
                        <div class="metrica-label">Documentación</div>
                        <div class="metrica-value">{candidato['category_scores']['documentacion']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Pruebas</div>
                        <div class="metrica-value">{candidato['category_scores']['pruebas']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Complejidad</div>
                        <div class="metrica-value">{candidato['category_scores']['complejidad']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Seguridad</div>
                        <div class="metrica-value">{candidato['category_scores']['seguridad']:.1f}%</div>
                    </div>
                </div>

                <div class="fortalezas-debilidades">
                    <div class="lista-items">
                        <h4>Fortalezas ({len(candidato["fortalezas"])})</h4>
                        <ul>
"""
            for fortaleza in candidato['fortalezas'][:5]:
                html += f"""
                            <li>
                                {fortaleza['category'].replace('_', ' ').title()}
                                <span class="score-badge">{fortaleza['score']:.1f}%</span>
                            </li>
"""
            html += """
                        </ul>
                    </div>
                    <div class="lista-items">
                        <h4>Áreas de Mejora ({len(candidato["debilidades"])})</h4>
                        <ul>
"""
            for debilidad in candidato['debilidades'][:5]:
                html += f"""
                            <li>
                                {debilidad['category'].replace('_', ' ').title()}
                                <span class="score-badge">{debilidad['score']:.1f}%</span>
                            </li>
"""
            html += """
                        </ul>
                    </div>
                </div>

                <div class="info-adicional">
"""
            if candidato.get('duplicacion'):
                dup = candidato['duplicacion']
                html += f"""
                    <div class="info-card">
                        <h5>Duplicación de Código</h5>
                        <p>{dup.get('porcentaje_global', 'N/A')}%</p>
                        <small>{dup.get('bloques_encontrados', 0)} bloques duplicados</small>
                    </div>
"""
            if candidato.get('dependencias'):
                deps = candidato['dependencias']
                html += f"""
                    <div class="info-card">
                        <h5>Dependencias</h5>
                        <p>{deps.get('total_dependencies', 0)}</p>
                        <small>{deps.get('external_dependencies', 0)} externas</small>
                    </div>
"""
            html += f"""
                    <div class="info-card">
                        <h5>Archivos Analizados</h5>
                        <p>{candidato['metadata']['archivos_analizados']}</p>
                        <small>{candidato['metadata']['tamano_kb']} KB total</small>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <strong>Lenguajes:</strong>
                    <div class="lenguajes">
                        {''.join([f'<span class="lenguaje-tag">{lang}</span>' for lang in candidato['lenguajes']])}
                    </div>
                </div>
            </div>
"""
        return html

    def _get_team_footer(self) -> str:
        """Genera el pie de página del reporte de equipo."""
        return """
        <div class="footer">
            <p>Generado por Code Empathizer v2.2.2 - R. Benítez |
            <a href="https://github.com/686f6c61/Repo-Code-Empathizer">GitHub</a></p>
        </div>
    </div>
"""

    def _get_team_script(self, categorias_labels: List[str], categorias: List[str], candidatos: List[Dict]) -> str:
        """Genera el script JavaScript para los gráficos."""
        colors = ['rgba(0, 0, 0, 0.8)', 'rgba(100, 100, 100, 0.8)',
                  'rgba(150, 150, 150, 0.8)', 'rgba(200, 200, 200, 0.8)']

        datasets = []
        for idx, candidato in enumerate(candidatos):
            scores = [candidato['category_scores'].get(cat, 0) for cat in categorias]
            datasets.append({
                'label': candidato['nombre'],
                'data': scores,
                'backgroundColor': colors[idx % len(colors)],
                'borderColor': colors[idx % len(colors)],
                'borderWidth': 2
            })

        return f"""
    <script>
        const ctx = document.getElementById('comparisonChart').getContext('2d');

        const data = {{
            labels: {json.dumps(categorias_labels)},
            datasets: {json.dumps(datasets)}
        }};

        new Chart(ctx, {{
            type: 'bar',
            data: data,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }},
                    title: {{ display: true, text: 'Comparación de Métricas por Categoría' }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{ callback: function(value) {{ return value + '%'; }} }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
