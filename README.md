# Proyecto de API de Vulnerabilidades

Este proyecto contiene una API desarrollada con Django Rest Framework para obtener y gestionar vulnerabilidades del NIST.

## Requisitos

- Docker
- Docker Compose

## Instrucciones para iniciar el contenedor

1. Clona este repositorio en tu máquina local:
    ```bash
    git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/gabriellopera/challenge_python_security.git)
    cd tu-repositorio
    ```

2. Asegúrate de tener Docker y Docker Compose instalados en tu sistema.

3. Construye y levanta los contenedores con el siguiente comando:
    ```bash
    docker compose up
    ```

4. La API estará disponible en `http://localhost:5173` (o en el puerto configurado en tu archivo `docker-compose.yml`).

## Notas

- Las URL o IP:Puerto pueden variar según el entorno en el que se despliegue la API.
- Para detener los contenedores, usa `Ctrl+C` en la terminal donde ejecutaste `docker compose up` o ejecuta:
    ```bash
    docker compose down
    ```

