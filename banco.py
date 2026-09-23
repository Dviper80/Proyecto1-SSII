import sqlite3
import hashlib


DB_NAME = 'banco.db'

def conectar():
    """Establece y devuelve la conexión a la base de datos."""
    return sqlite3.connect(DB_NAME)

def login(usuario, password):
    """Verifica las credenciales contra la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    "ESTOY ASUMIENDO QUE CODIFICAMOS CON SHA256, SIN SALT NI NA LUEGO HAY QUE CAMBIARLO"
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("SELECT saldo FROM cuentas WHERE nombre = ? AND password_hash = ?", (usuario, pwd_hash))
    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        return True, resultado[0]
    return False, 0

def modificar_saldo(usuario, cantidad):
    """Suma o resta dinero y devuelve el nuevo saldo."""
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("UPDATE cuentas SET saldo = saldo + ? WHERE nombre = ?", (cantidad, usuario))
    conexion.commit()

    cursor.execute("SELECT saldo FROM cuentas WHERE nombre = ?", (usuario,))
    nuevo_saldo = cursor.fetchone()[0]
    conexion.close()

    return nuevo_saldo

def iniciar_cliente():
    sesion_activa = None

    while True:
        # 1. Gestión de Login
        if not sesion_activa:
            print("\n[--- INICIO DE SESIÓN ---]")
            user = input("Usuario: ")
            pwd = input("Contraseña: ")
            
            exito, saldo = login(user, pwd)
            if exito:
                print(f"[+] Login exitoso. Saldo actual: {saldo:.2f}€")
                sesion_activa = user
            else:
                print("[-] Credenciales incorrectas. Inténtalo de nuevo.")
                
        # 2. Gestión de Eventos (Ingresar, Retirar, Logout)
        else:
            entrada = input(f"({sesion_activa}) > ").strip().split()
            if not entrada:
                continue

            comando = entrada[0].lower()

            if comando == 'logout':
                print(f"[-] Sesión cerrada.")
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
                        # Verificación rápida de fondos antes de restar
                        conexion = conectar()
                        saldo_actual = conexion.execute("SELECT saldo FROM cuentas WHERE nombre = ?", (sesion_activa,)).fetchone()[0]
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