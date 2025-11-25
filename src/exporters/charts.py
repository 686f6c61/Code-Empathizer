#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Generador de Gráficas HTML - Charts con Chart.js
=============================================================================

Este módulo genera gráficas HTML interactivas usando Chart.js para
visualización de métricas de código.

TIPOS DE GRÁFICAS:
-----------------
1. Radar - Comparación general por categorías
2. Barras - Comparación detallada lado a lado
3. Líneas - Evolución de métricas
4. Distribución (Doughnut) - Vista general de calidad
5. Heatmap - Mapa de calor comparativo
6. Equipo - Ranking de candidatos

CARACTERÍSTICAS:
---------------
- Gráficas interactivas con Chart.js
- Diseño responsive
- Tooltips informativos
- Colores profesionales

USO:
---
    from exporters.charts import ChartGenerator

    generator = ChartGenerator()
    html = generator.generar_radar(metricas, timestamp)

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

from .base import BaseExporter, CATEGORIAS, CATEGORIAS_LABELS


class ChartGenerator(BaseExporter):
    """Generador de gráficas HTML con Chart.js."""

    def _get_scores(self, metricas: Dict[str, Any]) -> Tuple[List[float], List[float]]:
        """
        Extrae las puntuaciones de empresa y candidato.

        Args:
            metricas: Diccionario con métricas.

        Returns:
            Tuple con listas de scores de empresa y candidato.
        """
        empresa_data = metricas.get('repos', {}).get('empresa', {})
        candidato_data = metricas.get('repos', {}).get('candidato', {})

        empresa_scores = []
        candidato_scores = []

        for cat in CATEGORIAS:
            emp_score = empresa_data.get(cat, {}).get('score', 0)
            cand_score = candidato_data.get(cat, {}).get('score', 0)
            empresa_scores.append(round(emp_score * 100, 2) if emp_score else 0)
            candidato_scores.append(round(cand_score * 100, 2) if cand_score else 0)

        return empresa_scores, candidato_scores

    def generar_radar(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica radar interactiva."""
        empresa_scores, candidato_scores = self._get_scores(metricas)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRÁFICA RADAR - ANÁLISIS DE EMPATÍA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 900px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .chart-container {{ position: relative; height: 500px; margin: 20px 0; }}
        .info {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }}
        .info h3 {{ color: #667eea; margin-bottom: 10px; font-size: 16px; }}
        .info p {{ color: #666; font-size: 14px; line-height: 1.6; }}
        .footer {{ text-align: center; color: white; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GRÁFICA RADAR - ANÁLISIS DE EMPATÍA</h1>
        <p class="subtitle">COMPARACIÓN DE MÉTRICAS ENTRE EMPRESA Y CANDIDATO</p>
        <div class="chart-container">
            <canvas id="radarChart"></canvas>
        </div>
        <div class="info">
            <h3>Cómo interpretar esta gráfica</h3>
            <p>
                La gráfica radar muestra la comparación de 8 categorías de análisis de código.
                Cuanto más cerca del borde exterior, mejor es la puntuación (máximo 100).
                <br><br>
                <strong>• Línea azul:</strong> Repositorio de la Empresa (Master)<br>
                <strong>• Línea naranja:</strong> Repositorio del Candidato<br>
                <br>
                Una mayor superposición entre ambas líneas indica mayor empatía de código.
            </p>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
    <script>
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(CATEGORIAS_LABELS)},
                datasets: [
                    {{
                        label: 'Empresa (Master)',
                        data: {json.dumps(empresa_scores)},
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: 'Candidato',
                        data: {json.dumps(candidato_scores)},
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(255, 159, 64, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(255, 159, 64, 1)',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top', labels: {{ padding: 20, font: {{ size: 14 }} }} }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 13 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.r.toFixed(2) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 20,
                            callback: function(value) {{ return value + '%'; }},
                            font: {{ size: 12 }}
                        }},
                        pointLabels: {{ font: {{ size: 13 }}, color: '#333' }},
                        grid: {{ color: 'rgba(0, 0, 0, 0.1)' }},
                        angleLines: {{ color: 'rgba(0, 0, 0, 0.1)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    def generar_barras(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de barras comparativa."""
        empresa_scores, candidato_scores = self._get_scores(metricas)

        promedio_empresa = round(sum(empresa_scores) / len(empresa_scores), 1) if empresa_scores else 0
        promedio_candidato = round(sum(candidato_scores) / len(candidato_scores), 1) if candidato_scores else 0
        diferencia = abs(promedio_empresa - promedio_candidato)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRÁFICA DE BARRAS - ANÁLISIS DE EMPATÍA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 1000px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .chart-container {{ position: relative; height: 500px; margin: 20px 0; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }}
        .stat-card h3 {{ font-size: 14px; margin-bottom: 5px; opacity: 0.9; }}
        .stat-card .value {{ font-size: 24px; font-weight: bold; }}
        .footer {{ text-align: center; color: white; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GRÁFICA DE BARRAS COMPARATIVA</h1>
        <p class="subtitle">ANÁLISIS DETALLADO POR CATEGORÍA</p>
        <div class="chart-container">
            <canvas id="barChart"></canvas>
        </div>
        <div class="stats">
            <div class="stat-card">
                <h3>Promedio Empresa</h3>
                <div class="value">{promedio_empresa}%</div>
            </div>
            <div class="stat-card">
                <h3>Promedio Candidato</h3>
                <div class="value">{promedio_candidato}%</div>
            </div>
            <div class="stat-card">
                <h3>Diferencia Media</h3>
                <div class="value">{diferencia}%</div>
            </div>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
    <script>
        const ctx = document.getElementById('barChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(CATEGORIAS_LABELS)},
                datasets: [
                    {{
                        label: 'Empresa (Master)',
                        data: {json.dumps(empresa_scores)},
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        borderRadius: 5
                    }},
                    {{
                        label: 'Candidato',
                        data: {json.dumps(candidato_scores)},
                        backgroundColor: 'rgba(255, 159, 64, 0.8)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 2,
                        borderRadius: 5
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top', labels: {{ padding: 20, font: {{ size: 14 }} }} }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 13 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 10,
                            callback: function(value) {{ return value + '%'; }},
                            font: {{ size: 12 }}
                        }},
                        grid: {{ color: 'rgba(0, 0, 0, 0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ font: {{ size: 12 }} }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    def generar_categorias(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de líneas por categorías."""
        empresa_scores, candidato_scores = self._get_scores(metricas)
        diferencias = [abs(e - c) for e, c in zip(empresa_scores, candidato_scores)]

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANÁLISIS POR CATEGORÍAS</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 1100px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .chart-container {{ position: relative; height: 450px; margin: 20px 0; }}
        .footer {{ text-align: center; color: white; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ANÁLISIS DETALLADO POR CATEGORÍAS</h1>
        <p class="subtitle">EVOLUCIÓN DE MÉTRICAS Y DIFERENCIAS</p>
        <div class="chart-container">
            <canvas id="lineChart"></canvas>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
    <script>
        const ctx = document.getElementById('lineChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(CATEGORIAS_LABELS)},
                datasets: [
                    {{
                        label: 'Empresa',
                        data: {json.dumps(empresa_scores)},
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }},
                    {{
                        label: 'Candidato',
                        data: {json.dumps(candidato_scores)},
                        borderColor: 'rgba(255, 159, 64, 1)',
                        backgroundColor: 'rgba(255, 159, 64, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }},
                    {{
                        label: 'Diferencia',
                        data: {json.dumps(diferencias)},
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top', labels: {{ padding: 20, font: {{ size: 14 }} }} }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 13 }},
                        padding: 12
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{ callback: function(value) {{ return value + '%'; }} }}
                    }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    def generar_distribucion(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica de distribución de puntuaciones."""
        empresa_data = metricas.get('repos', {}).get('empresa', {})
        candidato_data = metricas.get('repos', {}).get('candidato', {})
        empathy_score = metricas.get('empathy_analysis', {}).get('overall_score', 0)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DISTRIBUCIÓN DE PUNTUACIONES</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 900px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .chart-container {{ position: relative; height: 400px; margin: 20px 0; }}
        .empathy-score {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-top: 20px;
        }}
        .empathy-score h2 {{ font-size: 18px; margin-bottom: 10px; }}
        .empathy-score .score {{ font-size: 48px; font-weight: bold; }}
        .footer {{ text-align: center; color: #333; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>DISTRIBUCIÓN DE PUNTUACIONES</h1>
        <p class="subtitle">VISTA GENERAL DE CALIDAD DE CÓDIGO</p>
        <div class="chart-container">
            <canvas id="doughnutChart"></canvas>
        </div>
        <div class="empathy-score">
            <h2>SCORE DE EMPATÍA GLOBAL</h2>
            <div class="score">{round(empathy_score, 1)}%</div>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
    <script>
        const ctx = document.getElementById('doughnutChart').getContext('2d');
        const categorias = ['nombres', 'documentacion', 'modularidad', 'complejidad', 'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo'];
        const scores = [];
        const empresaData = {json.dumps(empresa_data)};
        const candidatoData = {json.dumps(candidato_data)};

        categorias.forEach(cat => {{
            const empScore = (empresaData[cat] && empresaData[cat].score) || 0;
            const candScore = (candidatoData[cat] && candidatoData[cat].score) || 0;
            scores.push(empScore * 100);
            scores.push(candScore * 100);
        }});

        let excelente = 0, bueno = 0, aceptable = 0, mejorar = 0;
        scores.forEach(score => {{
            if (score >= 80) excelente++;
            else if (score >= 60) bueno++;
            else if (score >= 40) aceptable++;
            else mejorar++;
        }});

        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Excelente (80-100%)', 'Bueno (60-79%)', 'Aceptable (40-59%)', 'Necesita Mejorar (<40%)'],
                datasets: [{{
                    data: [excelente, bueno, aceptable, mejorar],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ padding: 15, font: {{ size: 13 }} }} }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 13 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    def generar_equipo(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con gráfica comparativa de equipo."""
        if 'candidatos' not in metricas:
            return ""

        candidatos = metricas['candidatos']
        nombres = list(candidatos.keys())[:10]
        scores = [candidatos[n]['empathy_score'] for n in nombres]

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COMPARATIVA DE EQUIPO</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 1200px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .chart-container {{ position: relative; height: 500px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #333; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>COMPARATIVA DE CANDIDATOS</h1>
        <p class="subtitle">RANKING POR SCORE DE EMPATÍA</p>
        <div class="chart-container">
            <canvas id="teamChart"></canvas>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
    <script>
        const ctx = document.getElementById('teamChart').getContext('2d');
        const scores = {json.dumps(scores)};
        const backgroundColors = scores.map(score => {{
            if (score >= 80) return 'rgba(75, 192, 192, 0.8)';
            if (score >= 60) return 'rgba(54, 162, 235, 0.8)';
            if (score >= 40) return 'rgba(255, 206, 86, 0.8)';
            return 'rgba(255, 99, 132, 0.8)';
        }});

        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(nombres)},
                datasets: [{{
                    label: 'Score de Empatía (%)',
                    data: scores,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(c => c.replace('0.8', '1')),
                    borderWidth: 2,
                    borderRadius: 5
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 13 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                let label = 'Score: ' + context.parsed.x.toFixed(2) + '%';
                                if (context.parsed.x >= 80) label += ' (Excelente)';
                                else if (context.parsed.x >= 60) label += ' (Bueno)';
                                else if (context.parsed.x >= 40) label += ' (Aceptable)';
                                else label += ' (Necesita mejorar)';
                                return label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
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

    def generar_heatmap(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """Genera HTML con mapa de calor comparativo."""
        empresa_data = metricas.get('repos', {}).get('empresa', {})
        candidato_data = metricas.get('repos', {}).get('candidato', {})

        categorias_map = [
            ('nombres', 'NOMBRES'),
            ('documentacion', 'DOCUMENTACIÓN'),
            ('modularidad', 'MODULARIDAD'),
            ('complejidad', 'COMPLEJIDAD'),
            ('manejo_errores', 'MANEJO ERRORES'),
            ('pruebas', 'PRUEBAS'),
            ('seguridad', 'SEGURIDAD'),
            ('consistencia_estilo', 'CONSISTENCIA')
        ]

        def get_color(value):
            if value >= 90:
                return '#2ecc71'
            if value >= 75:
                return '#58d68d'
            if value >= 60:
                return '#f39c12'
            if value >= 45:
                return '#e67e22'
            return '#e74c3c'

        filas_html = ""
        for cat_key, cat_label in categorias_map:
            emp_score = empresa_data.get(cat_key, {}).get('score', 0)
            cand_score = candidato_data.get(cat_key, {}).get('score', 0)
            emp_pct = round(emp_score * 100, 1) if emp_score else 0
            cand_pct = round(cand_score * 100, 1) if cand_score else 0
            diferencia = abs(emp_pct - cand_pct)

            filas_html += f"""
            <tr>
                <td class="category-label">{cat_label}</td>
                <td style="background-color: {get_color(emp_pct)}" title="Empresa: {emp_pct}%">{emp_pct}%</td>
                <td style="background-color: {get_color(cand_pct)}" title="Candidato: {cand_pct}%">{cand_pct}%</td>
                <td class="diff-column" title="Diferencia absoluta">{diferencia:.1f}%</td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAPA DE CALOR - ANÁLISIS DE EMPATÍA</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 900px;
            width: 100%;
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 28px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
        .heatmap-container {{ overflow-x: auto; margin: 20px 0; }}
        .heatmap-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 2px;
        }}
        .heatmap-table th {{
            background: #34495e;
            color: white;
            padding: 15px;
            font-weight: 600;
            text-align: center;
            font-size: 14px;
        }}
        .heatmap-table td {{
            padding: 18px;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            color: white;
            border-radius: 4px;
            transition: all 0.3s ease;
        }}
        .heatmap-table td:not(.category-label):not(.diff-column):hover {{
            transform: scale(1.08);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
            z-index: 10;
            position: relative;
        }}
        .category-label {{
            background: #ecf0f1;
            color: #2c3e50;
            font-weight: 600;
            text-align: left;
            padding-left: 20px;
        }}
        .diff-column {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-weight: bold;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .legend-color {{ width: 30px; height: 20px; border-radius: 4px; }}
        .legend-label {{ font-size: 13px; color: #666; }}
        .info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .info h3 {{ color: #2c3e50; margin-bottom: 10px; font-size: 16px; }}
        .info p {{ color: #555; line-height: 1.6; font-size: 14px; }}
        .footer {{ text-align: center; color: white; margin-top: 20px; font-size: 12px; }}
        @media (max-width: 768px) {{
            .heatmap-table th, .heatmap-table td {{ padding: 10px 5px; font-size: 12px; }}
            h1 {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MAPA DE CALOR - ANÁLISIS DE EMPATÍA</h1>
        <p class="subtitle">COMPARACIÓN VISUAL DE TODAS LAS CATEGORÍAS</p>
        <div class="heatmap-container">
            <table class="heatmap-table">
                <thead>
                    <tr>
                        <th>CATEGORÍA</th>
                        <th>EMPRESA</th>
                        <th>CANDIDATO</th>
                        <th>DIFERENCIA</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #2ecc71"></div>
                <span class="legend-label">Excelente (90-100%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #58d68d"></div>
                <span class="legend-label">Bueno (75-89%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f39c12"></div>
                <span class="legend-label">Aceptable (60-74%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e67e22"></div>
                <span class="legend-label">Regular (45-59%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e74c3c"></div>
                <span class="legend-label">Deficiente (0-44%)</span>
            </div>
        </div>
        <div class="info">
            <h3>Cómo interpretar este mapa de calor</h3>
            <p>
                Este mapa de calor muestra visualmente el rendimiento en cada categoría de análisis.
                Los colores más verdes indican mejor calidad de código, mientras que los rojos señalan
                áreas que requieren mejora. La columna "Diferencia" muestra la brecha entre empresa
                y candidato, siendo útil para identificar las áreas prioritarias de capacitación.
                <br><br>
                <strong>Tip:</strong> Pasa el cursor sobre cada celda para ver detalles adicionales.
            </p>
        </div>
    </div>
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Code Empathizer v2.2.2
    </div>
</body>
</html>
"""
