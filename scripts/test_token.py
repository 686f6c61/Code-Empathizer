#!/usr/bin/env python3
"""
Script para verificar que el token de GitHub funciona correctamente.

Este módulo es parte de Code Empathizer, una herramienta para medir la alineación
entre el código de una empresa y sus candidatos.

Autor: https://github.com/686f6c61
Repositorio: https://github.com/686f6c61/Code-Empathizer
Fecha: Noviembre 2025
Licencia: MIT
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from github import Github, GithubException

def test_github_token():
    """Verifica que el token de GitHub funcione correctamente."""

    print("=" * 70)
    print("TEST DE TOKEN DE GITHUB")
    print("=" * 70)
    print()

    # Cargar .env
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print("❌ ERROR: Archivo .env no encontrado")
        print(f"   Ubicación esperada: {env_path}")
        print()
        print("Crea el archivo .env con:")
        print("  GITHUB_TOKEN=tu_token_aqui")
        return False

    load_dotenv(env_path)
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        print("❌ ERROR: GITHUB_TOKEN no encontrado en .env")
        return False

    if token == 'your_github_token_here':
        print("❌ ERROR: Token no configurado (usando valor por defecto)")
        print()
        print("Edita .env y reemplaza 'your_github_token_here' con tu token real")
        return False

    print(f"✓ Token encontrado: {token[:10]}...{token[-4:]}")
    print()

    # Intentar conectar con GitHub
    print("Conectando con GitHub API...")
    try:
        g = Github(token)

        # Obtener información del usuario autenticado
        user = g.get_user()
        print(f"✓ Autenticado como: {user.login}")
        print(f"✓ Nombre: {user.name or 'N/A'}")
        print(f"✓ Tipo de cuenta: {user.type}")
        print()

        # Verificar rate limit
        try:
            rate_limit = g.get_rate_limit()
            if hasattr(rate_limit, 'core'):
                core = rate_limit.core
                print(f"Rate Limit:")
                print(f"  • Límite: {core.limit} requests/hora")
                print(f"  • Restantes: {core.remaining}")
                print(f"  • Reset: {core.reset.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"Rate Limit:")
                print(f"  • Límite: {rate_limit.rate.limit} requests/hora")
                print(f"  • Restantes: {rate_limit.rate.remaining}")
            print()
        except Exception as e:
            print(f"⚠ No se pudo verificar rate limit: {e}")
            print()

        # Intentar acceder a un repositorio público popular
        print("Probando acceso a repositorio público...")
        try:
            repo = g.get_repo("torvalds/linux")
            print(f"✓ Acceso exitoso a: {repo.full_name}")
            print(f"  • Estrellas: {repo.stargazers_count:,}")
            print(f"  • Lenguaje principal: {repo.language}")
            print()
        except GithubException as e:
            print(f"❌ Error accediendo a repositorio: {e.status} - {e.data.get('message', 'Unknown error')}")
            return False

        # Verificar scopes del token
        print("Verificando permisos del token...")
        scopes = g.oauth_scopes
        if scopes:
            print(f"✓ Scopes configurados: {', '.join(scopes)}")

            required_scopes = ['public_repo', 'read:user']
            missing_scopes = [s for s in required_scopes if s not in scopes and 'repo' not in scopes]

            if missing_scopes:
                print(f"⚠ Scopes faltantes recomendados: {', '.join(missing_scopes)}")
            else:
                print("✓ Todos los scopes recomendados presentes")
        else:
            print("⚠ No se pudieron verificar los scopes")
        print()

        print("=" * 70)
        print("✅ TOKEN DE GITHUB FUNCIONANDO CORRECTAMENTE")
        print("=" * 70)
        print()
        print("El token está listo para usar con Code Empathizer")
        return True

    except GithubException as e:
        print()
        print("=" * 70)
        print("❌ ERROR DE AUTENTICACIÓN")
        print("=" * 70)
        print()
        print(f"Status: {e.status}")
        print(f"Mensaje: {e.data.get('message', 'Unknown error')}")
        print()

        if e.status == 401:
            print("El token es inválido o ha expirado.")
            print()
            print("Solución:")
            print("1. Ve a https://github.com/settings/tokens")
            print("2. Genera un nuevo token con permisos: public_repo, read:user")
            print("3. Actualiza el token en .env")
        elif e.status == 403:
            print("El token no tiene permisos suficientes.")
            print()
            print("Solución:")
            print("1. Ve a https://github.com/settings/tokens")
            print("2. Verifica que el token tenga: public_repo, read:user")
            print("3. Si es necesario, genera un nuevo token")

        return False

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR INESPERADO")
        print("=" * 70)
        print()
        print(f"Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_github_token()
    sys.exit(0 if success else 1)
