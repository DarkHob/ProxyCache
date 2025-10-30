# 🎵 Proxy de Caché - Demo estilo Bootstrap (PyQt6)

Este proyecto es una **demostración interactiva** del **patrón Proxy con caché**, implementado con **Python y PyQt6**.  
La interfaz gráfica simula la búsqueda de canciones, mostrando si el resultado proviene del servidor o de la caché local.  
Además, cuenta con un diseño visual inspirado en **Bootstrap 5**.

---

## 🧩 Características principales

- **Patrón Proxy**: encapsula el acceso al servicio real mediante un proxy con caché.  
- **Simulación de latencia**: las consultas al servidor incluyen una pequeña espera para imitar la red.  
- **Interfaz moderna**: diseño visual con estilos similares a Bootstrap.  
- **Multihilo (QThread)**: evita que la interfaz se congele durante las operaciones.  
- **Caché manual**: permite limpiar la caché con un botón.

---

## 🧰 Requisitos

- Python 3.10 o superior
- Instala las dependencias necesarias con  pip install -r requirements.txt

