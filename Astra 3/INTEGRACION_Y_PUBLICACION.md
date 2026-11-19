# ASTRA — Integración de archivos del equipo y publicación

## Qué se integró
- Se conservó `app.py` de la versión de interfaz más reciente, incluido su rango de ángulos de -60° a 60°, el chatbot y la visualización.
- Se conservaron los archivos de física, simulación y control existentes: la versión de los compañeros no incluye cambios nuevos en los módulos de IA.
- Se incorporaron los `__init__.py` de los módulos y el documento de transferencia `ASTRA_Project_Handoff.md`.
- Se incorporó `validation/check_integracion.py` para comprobar estructura, sintaxis y dependencias declaradas sin modificar modelos.
- Se conservaron los modelos `.joblib` y los CSV originales sin reentrenarlos.

## Publicación en Streamlit Community Cloud
1. Subir el contenido de la carpeta `Astra/` al repositorio de GitHub que utiliza la página (no subir la carpeta externa `ASTRA_integrado_para_pagina`).
2. Mantener `app.py` como archivo principal de la aplicación.
3. Confirmar que el despliegue instala las dependencias de `requirements.txt`.
4. Revisar los logs de la app después del despliegue y probar el chatbot, los controles y las gráficas.
5. No reemplazar la versión publicada sin guardar una copia o hacer un commit previo.

## Pendientes para los compañeros
- **IA**: el modelo actual no ha sido validado para todo el rango de ángulos que permite la interfaz. La versión compartida por el equipo trae el mismo código de IA y los mismos modelos que el proyecto de partida. Se requiere una evaluación independiente y una solución verificada antes de afirmar que funciona para todos los ángulos.
- **Control LS**: revisar y documentar por qué algunas configuraciones no mejoran los resultados. No se han cambiado sus ecuaciones ni parámetros en esta integración.
- **Validación**: acordar casos de prueba, métricas y criterios de aceptación; ejecutar la batería completa antes de presentar conclusiones.
- **Despliegue**: verificar versiones compatibles de paquetes en el entorno de Streamlit y confirmar el funcionamiento en la URL pública.

## Responsabilidad de interfaz
La interfaz y su diseño pueden editarse en `app.py`. Los demás módulos se mantienen separados para que los compañeros trabajen en ellos sin sobrescribir la página.

## Comprobación rápida
Desde la carpeta `Astra/`:
`python3 -m validation.check_integracion`

Esta comprobación es estructural, **no** prueba el desempeño de la IA ni garantiza que el sitio se haya publicado.
