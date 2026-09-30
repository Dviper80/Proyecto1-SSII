import mysql.connector
import hashlib

def conectar():
    """Establece la conexión a XAMPP (MySQL local)."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="banco_db"
    )

def login(usuario, password):
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Encriptamos la contraseña introducida para compararla con la base de datos
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    # Usamos %s en lugar de ? para MySQL
    cursor.execute("SELECT saldo FROM cuentas WHERE nombre = %s AND password_hash = %s", (usuario, pwd_hash))
    resultado = cursor.fetchone()
    
    cursor.close()
    conexion.close()

    if resultado:
        return True, resultado[0]
    return False, 0

def modificar_saldo(usuario, cantidad):
    conexion = conectar()
    cursor = conexion.cursor()

    # Modificamos el saldo
    cursor.execute("UPDATE cuentas SET saldo = saldo + %s WHERE nombre = %s", (cantidad, usuario))
    conexion.commit()

    # Recuperamos el nuevo saldo
    cursor.execute("SELECT saldo FROM cuentas WHERE nombre = %s", (usuario,))
    nuevo_saldo = cursor.fetchone()[0]
    
    cursor.close()
    conexion.close()

    return nuevo_saldo


