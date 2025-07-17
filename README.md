# Test - AgroRed

Este repositorio contiene scripts de prueba para validar el funcionamiento de los microservicios y la interfaz web de AgroRed.

## 🧪 ¿Qué se prueba?

- Endpoints del backend (`Backend-main`)
- Autenticación de usuarios (`user_service`)
- CRUD de productos (`product_service`)
- Visualización y carga de componentes en el frontend

## 🚀 Cómo ejecutar las pruebas

```bash
# Backend
python BackEnd-Test.py

# Frontend
python FrontEnd-Test.py

# También puedes usar pytest si está configurado
pytest
```

> Asegúrate de tener los servicios correspondientes levantados antes de correr los tests.
