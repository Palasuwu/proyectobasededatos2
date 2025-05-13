# Gestion de hotel
Este proyecto es una API desarrollada en **Python** con el framework **Flask**, que utiliza **PostgreSQL** como base de datos relacional.

---

## 🛠 Tecnologías utilizadas

- Python  
- Flask  
- Visual Studio Code  
- Postman  
- flask_sqlalchemy  
- psycopg2-binary  

---

## ✅ Requisitos para probar la API localmente

- Python 3.8 o superior instalado  
- PostgreSQL instalado  
- Un editor de código como **Visual Studio Code** (opcional)  
- **Postman** para probar los endpoints  

---

## 🧩 Pasos para la configuración

### 1. Instalar PostgreSQL

Descarga e instala PostgreSQL desde el sitio oficial:  
👉 [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

---

### 2. Instalar librerías necesarias

#### En macOS o Linux:

```bash
pip3 install flask flask_sqlalchemy psycopg2-binary       

```
## ❗ Posible error en macOS con psycopg2-binary:

Si aparece un error como:

```pgsql
pg_config executable not found.
```

# Busca pg_config

```find / -name pg_config 2>/dev/null```

# Ejemplo de ruta encontrada:
```/Library/PostgreSQL/17/bin/pg_config```

# Agrega la ruta temporalmente al entorno
```export PATH="/Library/PostgreSQL/17/bin:$PATH"```

# Intenta instalar de nuevo
```pip install psycopg2-binary```
###En Windows
```pip install flask flask_sqlalchemy psycopg2-binary```

### para generar pdf excel y csv
```pip install reportlab```
```pip install pandas openpyxl```





