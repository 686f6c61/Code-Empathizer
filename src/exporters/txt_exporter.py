#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Exportador TXT - Generación de Reportes en Texto Plano
=============================================================================

Este módulo gestiona la exportación de resultados a formato de texto plano
con tablas ASCII formateadas.

CARACTERÍSTICAS:
---------------
- Tablas ASCII con bordes Unicode
- Resumen de repositorios
- Métricas por categoría
- Análisis de empatía
- Recomendaciones

USO:
---
    from exporters.txt_exporter import TxtExporter

    exporter = TxtExporter()
    path = exporter.exportar(metricas, timestamp)

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT

Copyright (c) 2025 - Code Empathizer
=============================================================================
"""

import logging
from datetime import datetime
from typing import Dict, Any

from .base import BaseExporter, CATEGORIAS

logger = logging.getLogger(__name__)


class TxtExporter(BaseExporter):
    """Exportador de reportes en formato texto plano."""

    def exportar(self, metricas: Dict[str, Any], timestamp: str) -> str:
        """
        Exporta los resultados a archivo de texto plano.

        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.

        Returns:
            str: Ruta al archivo generado.

        Raises:
            IOError: Si no se puede escribir el archivo.
        """
        try:
            output_path = self.get_output_path('reporte', timestamp, 'txt')

            with open(output_path, 'w', encoding='utf-8') as f:
                self._write_header(f)
                self._write_repos_summary(f, metricas)
                self._write_empathy_analysis(f, metricas)
                self._write_detailed_metrics(f, metricas)
                self._write_advanced_analysis(f, metricas)
                self._write_conclusion(f, metricas)

            return output_path
        except Exception as e:
            logger.error(f"Error generando reporte TXT: {str(e)}")
            raise

    def _write_header(self, f) -> None:
        """Escribe el encabezado del reporte."""
        f.write("=" * 80 + "\n")
        f.write("ANÁLISIS DE EMPATÍA EMPRESA-CANDIDATO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

    def _write_repos_summary(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el resumen de repositorios."""
        if not metricas or 'repos' not in metricas:
            f.write("ERROR: No hay datos para analizar\n")
            return

        f.write("-" * 80 + "\n")
        f.write("RESUMEN DE REPOSITORIOS\n")
        f.write("-" * 80 + "\n\n")

        for repo_tipo, repo_data in metricas['repos'].items():
            if not repo_data:
                continue

            label = "EMPRESA (Master)" if repo_tipo == "empresa" else "CANDIDATO"
            f.write(f"{label}\n")
            f.write("=" * 50 + "\n")

            meta = repo_data.get('metadata', {})
            if meta:
                f.write(f"• Repositorio: {meta.get('nombre', 'N/A')}\n")
                f.write(f"• URL: {meta.get('url', 'N/A')}\n")
                f.write(f"• Descripción: {meta.get('descripcion', 'N/A')}\n")
                f.write(f"• Lenguaje principal: {meta.get('lenguaje_principal', 'N/A')}\n")
                if 'lenguajes_analizados' in meta:
                    f.write(f"• Lenguajes analizados: {', '.join(meta['lenguajes_analizados'])}\n")
                f.write(f"• Archivos analizados: {meta.get('archivos_analizados', 0)}\n")
                f.write(f"• Tamaño: {meta.get('tamano_kb', 0)} KB\n\n")

    def _write_empathy_analysis(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el análisis de empatía."""
        if 'empathy_analysis' not in metricas:
            return

        analysis = metricas['empathy_analysis']
        f.write("\n" + "=" * 80 + "\n")
        f.write("RESULTADO DEL ANÁLISIS DE EMPATÍA\n")
        f.write("=" * 80 + "\n\n")

        score = analysis['empathy_score']
        interpretation = analysis['interpretation']
        f.write(f"PUNTUACIÓN DE EMPATÍA: {score}%\n")
        f.write(f"   Nivel: {interpretation['level']}\n")
        f.write(f"   {interpretation['description']}\n")
        f.write(f"   Recomendación: {interpretation['recommendation']}\n\n")

        f.write("Puntuaciones por Categoría:\n")
        f.write("-" * 40 + "\n")
        for categoria, score in analysis['category_scores'].items():
            indicador = "[EXCELENTE]" if score >= 80 else "[BUENO]" if score >= 60 else "[MEJORAR]"
            f.write(f"  • {categoria.replace('_', ' ').title()}: {score:.1f}% {indicador}\n")

        lang_overlap = analysis['language_overlap']
        f.write(f"\nCoincidencia de Lenguajes: {lang_overlap['score']:.1f}%\n")
        if lang_overlap['missing']:
            f.write(f"  ADVERTENCIA: Lenguajes faltantes del candidato: {', '.join(lang_overlap['missing'])}\n")

        if analysis['recommendations']:
            f.write("\nRecomendaciones para el Candidato:\n")
            f.write("-" * 40 + "\n")
            for i, rec in enumerate(analysis['recommendations'], 1):
                f.write(f"\n{i}. {rec['title']}\n")
                f.write(f"   {rec['description']}\n")
                if 'tips' in rec:
                    for tip in rec['tips']:
                        f.write(f"   - {tip}\n")

    def _write_detailed_metrics(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe las métricas detalladas por categoría."""
        f.write("\n" + "=" * 80 + "\n")
        f.write("MÉTRICAS DETALLADAS POR CATEGORÍA\n")
        f.write("=" * 80 + "\n\n")

        for categoria in CATEGORIAS:
            f.write(f"\n{categoria.upper()}\n")
            f.write("-" * len(categoria) + "\n\n")

            f.write("┌" + "─" * 30 + "┬" + "─" * 15 + "┬" + "─" * 15 + "┐\n")
            f.write("│ Métrica" + " " * 23 + "│ Empresa" + " " * 7 + "│ Candidato" + " " * 5 + "│\n")
            f.write("├" + "─" * 30 + "┼" + "─" * 15 + "┼" + "─" * 15 + "┤\n")

            empresa_data = metricas['repos'].get('empresa', {}).get(categoria, {})
            candidato_data = metricas['repos'].get('candidato', {}).get(categoria, {})

            all_metrics = set(empresa_data.keys()) | set(candidato_data.keys())

            for metrica in sorted(all_metrics):
                empresa_val = f"{empresa_data.get(metrica, 0):.3f}"
                candidato_val = f"{candidato_data.get(metrica, 0):.3f}"
                metrica_name = metrica.replace('_', ' ').title()

                f.write(f"│ {metrica_name:<30}")
                f.write(f"│ {empresa_val:>15}")
                f.write(f"│ {candidato_val:>15}│\n")

            f.write("└" + "─" * 30 + "┴" + "─" * 15 + "┴" + "─" * 15 + "┘\n")

            if 'diferencias' in metricas and categoria in metricas['diferencias']:
                f.write("\nDiferencias:\n")
                for metrica, diff in metricas['diferencias'][categoria].items():
                    signo = "+" if diff > 0 else ""
                    f.write(f"• {metrica.replace('_', ' ').title()}: {signo}{diff:.3f}\n")
            f.write("\n")

    def _write_advanced_analysis(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el análisis avanzado (patrones, rendimiento, comentarios)."""
        f.write("\n" + "=" * 80 + "\n")
        f.write("ANÁLISIS AVANZADO\n")
        f.write("=" * 80 + "\n\n")

        self._write_patterns_analysis(f, metricas)
        self._write_performance_analysis(f, metricas)
        self._write_comments_analysis(f, metricas)

    def _write_patterns_analysis(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el análisis de patrones de diseño."""
        empresa_patterns = metricas['repos'].get('empresa', {}).get('patrones', {})
        candidato_patterns = metricas['repos'].get('candidato', {}).get('patrones', {})

        if not empresa_patterns and not candidato_patterns:
            return

        f.write("PATRONES DE DISEÑO Y ANTI-PATRONES\n")
        f.write("-" * 35 + "\n\n")

        f.write("Patrones de Diseño Detectados:\n")
        all_patterns = set()
        if empresa_patterns:
            all_patterns.update(empresa_patterns.get('design_patterns', {}).keys())
        if candidato_patterns:
            all_patterns.update(candidato_patterns.get('design_patterns', {}).keys())

        for pattern in sorted(all_patterns):
            emp_count = len(empresa_patterns.get('design_patterns', {}).get(pattern, []))
            cand_count = len(candidato_patterns.get('design_patterns', {}).get(pattern, []))
            f.write(f"  • {pattern.title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")

        f.write("\nAnti-patrones Detectados:\n")
        all_antipatterns = set()
        if empresa_patterns:
            all_antipatterns.update(empresa_patterns.get('anti_patterns', {}).keys())
        if candidato_patterns:
            all_antipatterns.update(candidato_patterns.get('anti_patterns', {}).keys())

        for antipattern in sorted(all_antipatterns):
            emp_count = len(empresa_patterns.get('anti_patterns', {}).get(antipattern, []))
            cand_count = len(candidato_patterns.get('anti_patterns', {}).get(antipattern, []))
            f.write(f"  • {antipattern.replace('_', ' ').title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")

        emp_score = empresa_patterns.get('pattern_score', 0) if empresa_patterns else 0
        cand_score = candidato_patterns.get('pattern_score', 0) if candidato_patterns else 0
        f.write(f"\nScore de Patrones: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")

    def _write_performance_analysis(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el análisis de rendimiento."""
        empresa_perf = metricas['repos'].get('empresa', {}).get('rendimiento', {})
        candidato_perf = metricas['repos'].get('candidato', {}).get('rendimiento', {})

        if not empresa_perf and not candidato_perf:
            return

        f.write("ANÁLISIS DE RENDIMIENTO\n")
        f.write("-" * 22 + "\n\n")

        f.write("Problemas de Rendimiento Detectados:\n")
        all_issues = set()
        if empresa_perf:
            all_issues.update(empresa_perf.get('performance_issues', {}).keys())
        if candidato_perf:
            all_issues.update(candidato_perf.get('performance_issues', {}).keys())

        for issue in sorted(all_issues):
            emp_count = len(empresa_perf.get('performance_issues', {}).get(issue, []))
            cand_count = len(candidato_perf.get('performance_issues', {}).get(issue, []))
            f.write(f"  • {issue.replace('_', ' ').title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")

        emp_score = empresa_perf.get('performance_score', 0) if empresa_perf else 0
        cand_score = candidato_perf.get('performance_score', 0) if candidato_perf else 0
        f.write(f"\nScore de Rendimiento: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")

    def _write_comments_analysis(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe el análisis de comentarios."""
        empresa_comments = metricas['repos'].get('empresa', {}).get('comentarios', {})
        candidato_comments = metricas['repos'].get('candidato', {}).get('comentarios', {})

        if not empresa_comments and not candidato_comments:
            return

        f.write("ANÁLISIS DE COMENTARIOS Y DOCUMENTACIÓN\n")
        f.write("-" * 38 + "\n\n")

        f.write("Métricas de Comentarios:\n")
        emp_metrics = empresa_comments.get('comment_metrics', {}) if empresa_comments else {}
        cand_metrics = candidato_comments.get('comment_metrics', {}) if candidato_comments else {}

        f.write(f"  • Ratio de comentarios: Empresa: {emp_metrics.get('comment_ratio', 0):.1f}%, "
                f"Candidato: {cand_metrics.get('comment_ratio', 0):.1f}%\n")
        f.write(f"  • Cobertura de documentación: Empresa: {emp_metrics.get('documentation_coverage', 0):.1f}%, "
                f"Candidato: {cand_metrics.get('documentation_coverage', 0):.1f}%\n")

        f.write("\nMarcadores Encontrados:\n")
        all_markers = set()
        if empresa_comments:
            all_markers.update(empresa_comments.get('markers', {}).keys())
        if candidato_comments:
            all_markers.update(candidato_comments.get('markers', {}).keys())

        for marker in sorted(all_markers):
            emp_count = len(empresa_comments.get('markers', {}).get(marker, []))
            cand_count = len(candidato_comments.get('markers', {}).get(marker, []))
            f.write(f"  • {marker.upper()}: Empresa: {emp_count}, Candidato: {cand_count}\n")

        emp_score = empresa_comments.get('comment_score', 0) if empresa_comments else 0
        cand_score = candidato_comments.get('comment_score', 0) if candidato_comments else 0
        f.write(f"\nScore de Comentarios: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")

    def _write_conclusion(self, f, metricas: Dict[str, Any]) -> None:
        """Escribe la conclusión del reporte."""
        if 'empathy_analysis' not in metricas:
            return

        f.write("\n" + "=" * 80 + "\n")
        f.write("CONCLUSIÓN Y DECISIÓN DE CONTRATACIÓN\n")
        f.write("=" * 80 + "\n\n")

        analysis = metricas['empathy_analysis']
        score = analysis['empathy_score']
        interpretation = analysis['interpretation']

        f.write(f"Puntuación Final de Empatía: {score}%\n")
        f.write(f"Nivel: {interpretation['level']}\n")
        f.write(f"Evaluación: {interpretation['description']}\n")
        f.write(f"Decisión: {interpretation['recommendation']}\n\n")

        if 'detailed_analysis' in analysis:
            detailed = analysis['detailed_analysis']

            if detailed.get('strengths'):
                f.write("FORTALEZAS DEL CANDIDATO:\n")
                for strength in detailed['strengths']:
                    f.write(f"  • {strength['category'].replace('_', ' ').title()}: {strength['score']:.1f}%\n")
                f.write("\n")

            if detailed.get('weaknesses'):
                f.write("ÁREAS DE MEJORA:\n")
                for weakness in detailed['weaknesses']:
                    f.write(f"  • {weakness['category'].replace('_', ' ').title()}: {weakness['score']:.1f}%\n")
                f.write("\n")
