#!/bin/bash
# Script de inicio para Code Empathizer
# Autor: https://github.com/686f6c61
# Repositorio: https://github.com/686f6c61/Code-Empathizer
# Licencia: MIT

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║               CODE EMPATHIZER v2.2.2                      ║
║                                                           ║
║     Análisis de alineación entre código empresa           ║
║              y código de candidatos                       ║
║                                                           ║
║   Autor: https://github.com/686f6c61                      ║
║   Repo: https://github.com/686f6c61/Code-Empathizer       ║
║   Licencia: MIT                                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${BLUE}[INFO]${NC} Directorio del proyecto: $PROJECT_DIR"
echo ""

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 no está instalado"
    echo "Instala Python 3.8+ antes de continuar"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}[OK]${NC} Python detectado: $PYTHON_VERSION"
echo ""

# Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[SETUP]${NC} Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[OK]${NC} Entorno virtual creado"
else
    echo -e "${GREEN}[OK]${NC} Entorno virtual ya existe"
fi
echo ""

# Activar entorno virtual
echo -e "${BLUE}[INFO]${NC} Activando entorno virtual..."
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}[OK]${NC} Entorno virtual activado"
echo ""

# Actualizar pip
echo -e "${BLUE}[INFO]${NC} Actualizando pip..."
pip install --upgrade pip -q
echo -e "${GREEN}[OK]${NC} pip actualizado"
echo ""

# Menú de instalación de dependencias
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║        ¿Qué dependencias deseas instalar?                 ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}1) Solo producción${NC} - Para usar la herramienta"
echo -e "     Instala: radon, lizard, pylint, numpy, matplotlib,"
echo -e "              PyGithub, python-dotenv, jinja2, PyYAML, pytz"
echo ""
echo -e "  ${GREEN}2) Producción + Desarrollo${NC} - Para contribuir al proyecto"
echo -e "     Instala producción + pytest, black, isort, flake8,"
echo -e "              mypy, pre-commit hooks"
echo ""
echo -e "  ${GREEN}3) Saltar instalación${NC} - Ya tienes las dependencias"
echo ""
read -p "$(echo -e ${BLUE}Selecciona una opción [1-3]:${NC} )" option

case $option in
    1)
        echo -e "${BLUE}[INFO]${NC} Instalando dependencias de producción..."
        pip install -r "$PROJECT_DIR/requirements.txt"
        echo -e "${GREEN}[OK]${NC} Dependencias de producción instaladas"
        ;;
    2)
        echo -e "${BLUE}[INFO]${NC} Instalando producción + desarrollo..."
        pip install -r "$PROJECT_DIR/requirements.txt" -r "$PROJECT_DIR/requirements-dev.txt"
        echo -e "${GREEN}[OK]${NC} Dependencias de producción y desarrollo instaladas"
        ;;
    3)
        echo -e "${YELLOW}[INFO]${NC} Saltando instalación de dependencias"
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Opción inválida"
        exit 1
        ;;
esac
echo ""

# Verificar .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}[AVISO]${NC} Archivo .env no encontrado"
    echo -e "${BLUE}[INFO]${NC} Creando .env desde .env.example..."
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${YELLOW}[ACCIÓN REQUERIDA]${NC} Edita .env y agrega tu GITHUB_TOKEN"
    else
        echo -e "${RED}[ERROR]${NC} .env.example no encontrado"
    fi
else
    # Verificar que el token esté configurado
    if grep -q "your_github_token_here" "$PROJECT_DIR/.env" 2>/dev/null; then
        echo -e "${YELLOW}[AVISO]${NC} Token de GitHub no configurado en .env"
        echo -e "${YELLOW}[ACCIÓN REQUERIDA]${NC} Edita .env y agrega tu GITHUB_TOKEN"
    else
        echo -e "${GREEN}[OK]${NC} Token de GitHub configurado"
    fi
fi
echo ""

# Verificar estructura del proyecto
echo -e "${BLUE}[INFO]${NC} Verificando estructura del proyecto..."
REQUIRED_DIRS=("src" "tests" "scripts" "examples")
ALL_OK=true

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_DIR/$dir" ]; then
        echo -e "${GREEN}  ✓${NC} $dir/"
    else
        echo -e "${RED}  ✗${NC} $dir/ (falta)"
        ALL_OK=false
    fi
done
echo ""

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}[OK]${NC} Estructura del proyecto verificada"
else
    echo -e "${YELLOW}[AVISO]${NC} Algunos directorios faltan"
fi
echo ""

# Menú principal
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║              ¿Qué deseas hacer?                           ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}1) Ejecutar análisis principal${NC} (main.py)"
echo -e "     Análisis completo interactivo con todas las opciones"
echo ""
echo -e "  ${GREEN}2) Ejecutar tests${NC} (pytest)"
echo -e "     Suite completa de pruebas unitarias"
echo ""
echo -e "  ${GREEN}3) Verificar token de GitHub${NC}"
echo -e "     Comprueba que el token esté configurado correctamente"
echo ""
echo -e "  ${GREEN}4) Abrir documentación HTML${NC}"
echo ""
echo -e "  ${GREEN}5) Ver algoritmo de empatía${NC} (fundamentos técnicos)"
echo -e "     Explicación detallada de la fórmula y funcionamiento"
echo ""
echo -e "  ${GREEN}6) Solo activar entorno virtual${NC} (shell interactivo)"
echo ""
echo -e "  ${GREEN}7) Salir${NC}"
echo ""
read -p "$(echo -e ${BLUE}Selecciona una opción [1-7]:${NC} )" action

case $action in
    1)
        echo -e "${BLUE}[INFO]${NC} Ejecutando análisis principal..."
        echo ""
        cd "$PROJECT_DIR"
        python3 src/main.py
        ;;
    2)
        echo -e "${BLUE}[INFO]${NC} Ejecutando tests con pytest..."
        echo ""
        cd "$PROJECT_DIR"
        pytest tests/ -v
        ;;
    3)
        echo -e "${BLUE}[INFO]${NC} Verificando token de GitHub..."
        echo ""
        cd "$PROJECT_DIR"
        python3 scripts/test_token.py
        ;;
    4)
        echo -e "${BLUE}[INFO]${NC} Abriendo documentación..."
        if [ -f "$PROJECT_DIR/docs/index.html" ]; then
            xdg-open "$PROJECT_DIR/docs/index.html" 2>/dev/null || open "$PROJECT_DIR/docs/index.html" 2>/dev/null || echo -e "${YELLOW}[INFO]${NC} Abre manualmente: $PROJECT_DIR/docs/index.html"
        else
            echo -e "${RED}[ERROR]${NC} Documentación no encontrada en docs/index.html"
        fi
        ;;
    5)
        echo -e "${BLUE}[INFO]${NC} Abriendo documentación del algoritmo de empatía..."
        if [ -f "$PROJECT_DIR/docs/algoritmo.html" ]; then
            xdg-open "$PROJECT_DIR/docs/algoritmo.html" 2>/dev/null || open "$PROJECT_DIR/docs/algoritmo.html" 2>/dev/null || echo -e "${YELLOW}[INFO]${NC} Abre manualmente: $PROJECT_DIR/docs/algoritmo.html"
        else
            echo -e "${RED}[ERROR]${NC} Documentación del algoritmo no encontrada en docs/algoritmo.html"
        fi
        ;;
    6)
        echo -e "${GREEN}[INFO]${NC} Entorno virtual activado"
        echo -e "${BLUE}[INFO]${NC} Para desactivar: ${YELLOW}deactivate${NC}"
        echo -e "${BLUE}[INFO]${NC} Directorio: ${YELLOW}$PROJECT_DIR${NC}"
        echo ""
        exec bash --init-file <(echo "source '$VENV_DIR/bin/activate'; cd '$PROJECT_DIR'; PS1='(venv) \u@\h:\w\$ '")
        ;;
    7)
        echo -e "${GREEN}[INFO]${NC} Saliendo..."
        echo ""
        echo -e "${BLUE}Para usar Code Empathizer manualmente:${NC}"
        echo -e "  1. ${YELLOW}source venv/bin/activate${NC}"
        echo -e "  2. ${YELLOW}python3 src/main.py${NC}"
        echo ""
        exit 0
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Opción inválida"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   Proceso completado                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
