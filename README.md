# Instrucciones:
### Requerimientos
- Para instalar todas las librerías necesarias, una vez en el directorio del proyecto, usar `pip install -r requirements.txt`
- Para la base de datos, abrir el archivo [SGDB_script.sql](/SGDB_script.sql) en MySQL Workbench, y luego darle al rayo.
  - La contraseña de todos los usuarios de ejemplo es `ola123`
  - Todos los usuarios de ejemplo tienen permisos normales excepto `12.345.678-9`, que tiene permisos de bibliotecario
### Cómo correr la página de forma local
- Usar `python -m flask run` para echar a correr flask
### Cómo ingresar las credenciales de la base de datos
1. Crea un archivo llamado `.env` en la carpeta raíz, es decir, en la misma donde se encuentra el archivo `app.py`
2. Escribir los datos de conexión de esta forma:<br>
```sql
DB_HOST={host}
DB_USER={usuario}
DB_PASS={contraseña}
DB_NAME={nombre de la base de datos}
```

**Imagen de ejemplo:**<br>
![database_connection](/database.PNG)
