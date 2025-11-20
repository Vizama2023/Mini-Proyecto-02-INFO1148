# Mini Proyecto #2 INFO1148: Generador Automático de Casos de Prueba (GLC)

## Descripción General
Este proyecto consiste en el desarrollo de un Generador Automático de Casos de Prueba para expresiones aritméticas. La herramienta utiliza una Gramática Libre de Contexto (GLC) como base para generar sistemáticamente casos de prueba de tres categorías: **Válidos, Inválidos y Extremos (Límite)**.

El objetivo es facilitar la verificación de compiladores o aplicaciones de procesamiento de expresiones, aplicando técnicas de derivación sintáctica y mutación controlada.

##  Requerimientos y Funcionalidades
La aplicación, implementada en Python con interfaz gráfica Tkinter, cumple con:

* **Generación de Casos (Válidos):** Derivación directa a partir de la gramática.
* **Generación de Casos (Inválidos):** Mutación controlada (eliminar, insertar, duplicar) sobre las cadenas válidas.
* **Generación de Casos (Extremos):** Restricciones agresivas de profundidad y longitud.
* **Métricas y Reporte:** Genera un reporte estadístico detallado sobre la distribución, conteo de operadores, y niveles de mutación.
* **Exportación:** Los resultados son exportables en formatos JSON y TXT.

## Estructura del Proyecto

* `interfaz.py`: Módulo principal que contiene la interfaz gráfica (Tkinter).
* `generador.py`: Clase `GeneradorCasosPrueba` con la lógica de derivación, mutación y análisis de métricas.
* `gramatica.txt`: Archivo de entrada con la Gramática Libre de Contexto.


## Instrucciones de Ejecución
1.  Asegúrese de tener Python instalado.
2.  Ejecute `python interfaz.py` en la terminal.
3.  Cargue el archivo `gramatica.txt` en la interfaz.
4.  Configure los parámetros y haga clic en "GENERAR CASOS".
## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado por:

| Nombre del Estudiante | Rol Sugerido / Contribución |
| :--- | :--- |
| **Debora Vizama** | Liderazgo, Diseño de Interfaz y Lógica del Generador |
| **Cristobal Pichara** | Desarrollo de la Lógica de Derivación y Mutación |
| **Cristobal Medel** | Análisis de Métricas y Documentación Técnica |
---
*Desarrollado para el curso INFO1148 - Teoría de la Computación.*