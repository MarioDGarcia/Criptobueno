
# Proeycto de Blockchain rudimentario

Este proyecto es una aplicación de prueba de concepto para la utilizacion de un blockchain enfocado a las selecciones para la FEU, 
## Guía de Instalación y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

### 1. Clonar el Repositorio

Abre tu terminal o línea de comandos y clona el proyecto desde GitHub:

git clone [https://github.com/MarioDGarcia/Criptobueno/](https://github.com/MarioDGarcia/Criptobueno/)
cd Criptobueno

**1. Crear un Entorno Virtual**
Es una buena práctica aislar las dependencias de tu proyecto del resto de tu sistema. Crea y activa un entorno virtual:

Crear el entorno virtual (se llamará venv):


python -m venv venv <br>
**2. Activar el entorno virtual:**

Windows (Command Prompt):


venv\Scripts\activate
Windows (PowerShell):

.\venv\Scripts\Activate.ps1
macOS/Linux:

source venv/bin/activate<br>
**3. Instalar Dependencias**
Con el entorno virtual activado, instala todas las librerías necesarias listadas en requirements.txt:


pip install -r requirements.txt<br>
**4. Ejecutar el Proyecto**
Una vez instaladas las dependencias, ejecuta el archivo principal:


python principal.py
