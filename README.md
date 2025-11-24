# Hand-Eye Calibration System

Una aplicación web full-stack para simplificar el proceso de calibración Hand-Eye en sistemas cámara-robot.

## 📋 Descripción

Este proyecto proporciona una interfaz web intuitiva que permite a usuarios sin conocimientos avanzados en robótica obtener la matriz de transformación necesaria para calibración Hand-Eye. El sistema utiliza el algoritmo Tsai-Lenz (AX=XB) e incluye gestión de usuarios con roles, historial de calibraciones y visualización de resultados.

## Arquitectura

- **Frontend**: Reflex (Python)
- **Backend**: FastAPI (Python)
- **Base de Datos**: SQLite con modo WAL
- **Algoritmo**: Tsai-Lenz (AX=XB)

##  Roles de Usuario

1. **Técnico de Mantenimiento**: Cargar datos, ejecutar calibraciones, ver/exportar resultados
2. **Ingeniero de Robótica/Visión Artificial**: Todos los permisos anteriores + configurar parámetros del algoritmo
3. **Supervisor/Gerente**: Solo lectura (historial y reportes)

## Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio (o descargar el proyecto)

```bash
git clone <repository-url>
cd CODIGO
```

### 2. Crear y activar entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y editarlo según sea necesario:

```bash
cp .env.example .env
```

**Importante**: Cambiar el `SECRET_KEY` en producción:

```bash
# En Linux/Mac, puedes generar una clave aleatoria con:
openssl rand -hex 32

# En Windows PowerShell:
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Inicializar la base de datos

```bash
python scripts/init_db.py
```

Este comando:
- Crea todas las tablas necesarias en SQLite
- Crea usuarios por defecto para cada rol
- Configura parámetros del algoritmo por defecto

**Credenciales por defecto**:
- **Ingeniero**: `admin` / `admin123`
- **Técnico**: `tech1` / `tech123`
- **Supervisor**: `supervisor1` / `super123`

 **ADVERTENCIA**: Cambiar estas contraseñas en producción.

##  Ejecución

### Iniciar el servidor backend

```bash
# Desarrollo (con auto-reload)
uvicorn backend.main:app --reload

# Producción
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

- Documentación interactiva (Swagger UI): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

## Estructura del Proyecto

```
CODIGO/
├── backend/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Esquemas Pydantic (Fase 2)
│   ├── api/             # Endpoints REST (Fase 4)
│   ├── auth/            # Autenticación JWT (Fase 2)
│   ├── calibration/     # Motor de calibración (Fase 3)
│   ├── config.py        # Configuración
│   ├── database.py      # Configuración de BD (con WAL)
│   └── main.py          # Aplicación FastAPI
├── frontend/            # Aplicación Reflex (Fase 5)
├── scripts/
│   └── init_db.py       # Script de inicialización de BD
├── .env                 # Variables de entorno (crear desde .env.example)
├── .env.example         # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt     # Dependencias Python
└── README.md
```

## 🗄️ Modelos de Datos

- **User**: Usuarios del sistema con roles (técnico, ingeniero, supervisor)
- **CalibrationRun**: Ejecuciones de calibración con resultados
- **RobotPose**: Poses del robot (matriz de rotación y vector de traslación)
- **CameraPose**: Poses de la cámara (matriz de rotación y vector de traslación)
- **AlgorithmParameters**: Parámetros configurables del algoritmo

## 🔧 Estado del Desarrollo

### ✅ Fase 1: Configuración y Modelos (Completada)
- [x] Estructura de directorios
- [x] Configuración del entorno
- [x] Modelos de datos SQLAlchemy
- [x] Script de inicialización de BD
- [x] Modo WAL activado en SQLite

### 🔜 Próximas Fases
- [ ] Fase 2: Autenticación y gestión de usuarios
- [ ] Fase 3: Motor de calibración (algoritmo Tsai-Lenz)
- [ ] Fase 4: API REST con control de roles
- [ ] Fase 5: Frontend con Reflex
- [ ] Fase 6: Visualización y exportación
