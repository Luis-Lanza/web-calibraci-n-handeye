# Hand-Eye Calibration System

## Guía de Ejecución Rápida

Sigue estos pasos para levantar el proyecto completo (Backend + Frontend) en tu entorno local.

### 1. Prerrequisitos
*   Python 3.11 o superior.
*   Git.

### 2. Configuración del Entorno

1.  **Clonar/Abrir el proyecto** en tu terminal.
2.  **Crear y activar un entorno virtual**:

    ```powershell
    # Windows
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Instalar dependencias**:

    ```powershell
    pip install -r requirements.txt
    ```

### 3. Ejecutar el Backend (API)

El backend debe correr en el puerto **8001** para no chocar con el frontend.

1.  Abre una terminal, activa el entorno virtual y ejecuta:

    ```powershell
    uvicorn backend.main:app --reload --port 8001
    ```

    *Verás logs indicando que el servidor corre en `http://0.0.0.0:8001`.*

### 4. Ejecutar el Frontend (Reflex)

1.  Abre **otra** terminal nueva.
2.  Activa el entorno virtual (`.\.venv\Scripts\Activate.ps1`).
3.  Navega a la carpeta `frontend`:

    ```powershell
    cd frontend
    ```

4.  Inicia la aplicación:

    ```powershell
    reflex run
    ```

### 5. Acceder a la Aplicación

*   Abre tu navegador en: **http://localhost:3000**
*   Login por defecto (si ya creaste usuario): `admin` / `password` (o el que hayas registrado).

---

### Notas Adicionales
*   **Base de Datos**: Se crea automáticamente (`handeye_calibration.db`) en la raíz.
*   **Seguridad**: El sistema implementa MFA, Rate Limiting y Encriptación. Si te bloqueas por intentos fallidos, espera 1 minuto.
