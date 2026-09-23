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

def iniciar_cliente():
    print("--- CONECTANDO A BASE DE DATOS MYSQL ---")
    sesion_activa = None

    while True:
        if not sesion_activa:
            print("\n[--- INICIO DE SESIÓN ---]")
            user = input("Usuario: ")
            pwd = input("Contraseña: ")
            
            exito, saldo = login(user, pwd)
            if exito:
                print(f"\n[+] Login exitoso. Saldo actual: {saldo:.2f}€")
                sesion_activa = user
            else:
                print("\n[-] Credenciales incorrectas. Inténtalo de nuevo.")
                
        else:
            entrada = input(f"\n({sesion_activa}) > ").strip().split()
            if not entrada:
                continue

            comando = entrada[0].lower()

            if comando == 'logout':
                print("[-] Sesión cerrada.")
                sesion_activa = None

            elif comando == 'ingresar' and len(entrada) == 2:
                try:
                    cantidad = float(entrada[1])
                    if cantidad > 0:
                        nuevo_saldo = modificar_saldo(sesion_activa, cantidad)
                        print(f"[+] Has ingresado {cantidad:.2f}€. Nuevo saldo: {nuevo_saldo:.2f}€")
                    else:
                        print("[-] La cantidad debe ser positiva.")
                except ValueError:
                    print("[-] Error: Introduce un valor numérico.")

            elif comando == 'retirar' and len(entrada) == 2:
                try:
                    cantidad = float(entrada[1])
                    if cantidad > 0:
                        # Verificamos los fondos antes de retirar
                        conexion = conectar()
                        cursor = conexion.cursor()
                        cursor.execute("SELECT saldo FROM cuentas WHERE nombre = %s", (sesion_activa,))
                        saldo_actual = cursor.fetchone()[0]
                        cursor.close()
                        conexion.close()

                        if saldo_actual >= cantidad:
                            nuevo_saldo = modificar_saldo(sesion_activa, -cantidad)
                            print(f"[+] Has retirado {cantidad:.2f}€. Nuevo saldo: {nuevo_saldo:.2f}€")
                        else:
                            print("[-] Error: Fondos insuficientes.")
                    else:
                        print("[-] La cantidad debe ser positiva.")
                except ValueError:
                    print("[-] Error: Introduce un valor numérico.")
                    
            else:
                print("[-] Comandos válidos: ingresar <monto> | retirar <monto> | logout")

if __name__ == '__main__':
    iniciar_cliente()