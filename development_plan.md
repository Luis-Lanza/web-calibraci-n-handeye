# Plan de Desarrollo: Aplicación Web de Calibración Hand-Eye

Este documento describe el plan de desarrollo para la "Aplicación Web de Calibración Hand-Eye", basado en la monografía del proyecto. El objetivo es crear una guía clara y estructurada para el desarrollo, desde la configuración inicial hasta el despliegue de funcionalidades.

## 1. Resumen del Proyecto

El proyecto consiste en desarrollar una aplicación web full-stack que simplifique el proceso de calibración Hand-Eye para sistemas cámara-robot. La aplicación permitirá a usuarios sin conocimientos avanzados en robótica obtener la matriz de transformación necesaria, a través de una interfaz web intuitiva y un potente motor de cálculo en el backend.

## 2. Arquitectura y Tecnologías

La arquitectura será un modelo **Cliente-Servidor** utilizando un stack tecnológico basado completamente en **Python**, lo que facilita la integración y reduce la complejidad.

- **Frontend (Cliente)**:
  - **Framework**: `Reflex`
  - **Lenguaje**: Python
  - **Función**: Proporcionar la interfaz de usuario web para la carga de datos, visualización de resultados e interacción general.

- **Backend (Servidor)**:
  - **Framework**: `FastAPI`
  - **Lenguaje**: Python
  - **Función**: Exponer una API RESTful para gestionar la lógica de negocio, procesar los datos y realizar los cálculos de calibración.

- **Base de Datos**:
  - **Motor**: `SQLite`
  - **Tipo**: Relacional
  - **Función**: Almacenar el historial de calibraciones, parámetros, métricas y resultados para su posterior consulta y análisis.

- **Librerías Clave**:
  - **Autenticación**: `passlib[bcrypt]` (para hashing de contraseñas), `python-jose` (para JWT).
  - **Visión por Computadora**: `OpenCV` (para el procesamiento de imágenes si se extiende la funcionalidad).
  - **Cálculo Numérico**: `NumPy` y `SciPy` (para el álgebra lineal y la implementación de los algoritmos de calibración).
  - **Visualización**: `Plotly` y `Matplotlib` (para generar gráficos interactivos de los sistemas de coordenadas y los errores de calibración).
  - **Control de Versiones**: `Git` y `GitHub`.

## 3. Roles de Usuario

El sistema definirá tres roles con diferentes niveles de permiso:

- **Técnico de Mantenimiento**: El usuario principal. Puede cargar datos, ejecutar calibraciones y ver/exportar los resultados.
- **Ingeniero de Robótica / Visión Artificial**: Un rol técnico avanzado. Tiene todos los permisos del Técnico y, además, puede configurar los parámetros internos de los algoritmos de calibración.
- **Supervisor / Gerente**: Un rol de solo lectura. Puede ver el historial de calibraciones y los reportes de resultados para supervisión, pero no puede ejecutar ni modificar datos.

## 4. Fases y Módulos de Desarrollo

Se propone un desarrollo incremental dividido en las siguientes fases.

### Fase 1: Configuración del Entorno y Modelos de Datos

**Objetivo**: Establecer la base del proyecto, el servidor y los modelos de datos.

- **Módulo: `Configuración del Proyecto`**
  1. Crear la estructura de directorios.
  2. Configurar el entorno virtual de Python e instalar dependencias: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `passlib[bcrypt]`, `python-jose`.
  3. Inicializar el repositorio de `Git`.

- **Módulo: `Modelos de Datos (SQLAlchemy)`**
  1. Definir todos los modelos de la base de datos: `User`, `CalibrationRun`, `RobotPose`, `CameraPose`, y `AlgorithmParameters`. La tabla `User` debe incluir el rol.
  2. Crear una utilidad para inicializar la base de datos.

### Fase 2: Gestión de Usuarios y Autenticación

**Objetivo**: Implementar un sistema seguro de login y gestión de roles.

- **Módulo: `Autenticación (Backend)`**
  1. Implementar la lógica para el hashing y verificación de contraseñas con `passlib`.
  2. Crear un endpoint `POST /api/v1/token` que genere un token JWT para el login (OAuth2 Password Flow).
  3. Implementar dependencias en FastAPI para proteger endpoints y verificar roles a partir del token JWT.

### Fase 3: Implementación del Motor de Calibración

**Objetivo**: Desarrollar la lógica central que resuelve el problema de calibración.

- **Módulo: `calibration_engine`**
  1. Crear el módulo `calibration/engine.py`.
  2. Implementar el algoritmo **Tsai-Lenz (AX=XB)** usando `NumPy`. La función aceptará las poses y los parámetros de configuración del algoritmo.
  3. La función debe devolver la matriz de transformación (`X`) y métricas de error.

### Fase 4: Desarrollo de la API Principal con Roles

**Objetivo**: Exponer la lógica de negocio a través de una API segura.

- **Módulo: `API Endpoints`**
  1. **`POST /api/v1/calibrate`**: Protegido para roles `Técnico` e `Ingeniero`.
  2. **`GET /api/v1/calibrations`**: Protegido para todos los roles autenticados.
  3. **`GET /api/v1/calibrations/{id}`**: Protegido para todos los roles autenticados.
  4. **`GET /api/v1/config` y `POST /api/v1/config`**: Endpoints para leer y actualizar los parámetros del algoritmo. Protegidos solo para el rol `Ingeniero`.

### Fase 5: Desarrollo del Frontend con Reflex y Roles

**Objetivo**: Construir una interfaz de usuario que se adapte al rol del usuario.

- **Módulo: `Frontend (Reflex)`**
  1. **Página de `Login`**: Para que los usuarios inicien sesión.
  2. **Gestión de Estado**: Manejar el estado de autenticación del usuario y su rol en el frontend.
  3. **Componentes condicionales**: Mostrar/ocultar elementos de la UI (ej. el botón de "Configuración") según el rol del usuario.
  4. **Páginas**: `CalibrationPage`, `HistoryPage` y `ParametersPage` (esta última solo visible para Ingenieros).

### Fase 6: Visualización y Funcionalidades Adicionales

**Objetivo**: Enriquecer la aplicación con visualizaciones y herramientas de exportación.

- **Módulo: `visualization_service`**
  1. En el backend, crear un servicio que genere figuras de `Plotly` para visualizar en 3D los sistemas de coordenadas.
- **Módulo: `Exportación y Reportes`**
  1. Implementar endpoints para descargar resultados en `JSON`, `CSV`, `TXT`.
  2. Investigar la generación de reportes en PDF (`ReportLab` o `PyFPDF`).

## 5. Consideraciones Adicionales

- **Testing**: Es crucial escribir pruebas unitarias para el motor de calibración (`calibration_engine`) y pruebas de integración para los endpoints de la API usando `pytest`.
- **Logging**: Implementar un sistema de logging estructurado para registrar eventos importantes (ej. inicios de sesión, ejecuciones de calibración, errores). Esto es vital para la depuración y para la trazabilidad que necesita el rol de `Supervisor`.

## 6. Por Dónde Empezar (Primeros Pasos)

1.  **Configurar el Entorno y Modelos**: Sigue la **Fase 1** al pie de la letra. Tener los modelos de datos bien definidos desde el principio es clave.
2.  **Implementar Autenticación**: Continúa con la **Fase 2**. Un sistema de autenticación funcional es prerrequisito para el resto de la API. Pruébalo con una herramienta como Postman o Insomnia.
3.  **Implementar el Algoritmo (Offline)**: Concéntrate en la **Fase 3**. Crea un script de prueba independiente para validar la lógica matemática antes de integrarla.
4.  **Construir la API**: Procede con la **Fase 4**, aplicando la seguridad de roles a cada endpoint a medida que lo creas.

Siguiendo este plan, podrás construir el proyecto de manera estructurada, asegurando que cada componente sea funcional antes de integrarlo en el sistema completo.
