import socket
import threading
import json
import banco

HOST = "0.0.0.0"

PORT = 5000


MAX_CONNECTIONS = 1
semaforo = threading.Semaphore(MAX_CONNECTIONS)


def procesar_peticion(pet):
    accion = pet.get("accion")

    if accion == "login":
        usuario = pet.get("usuario")
        contraseña = pet.get("password")

        exito, saldo = banco.login(usuario, contraseña)
        if exito:
            return {"status":"ok","mensaje":"Login con exito","saldo":float(saldo)}
        else:
            return {"status":"error","mensaje":"Credenciales incorrectas"}
        
    elif accion == "ingresar":
        usuario = pet.get("usuario")
        cantidad = float(pet.get("cantidad",0))
        if cantidad <= 0:
            return {"status":"error","mensaje":"La cantidad a ingresar debe ser positiva y mayor que 0"}
        saldo_nuevo = banco.modificar_saldo(usuario,cantidad)
        return {"status":"ok","mensaje":"La cantidad ha sido transferida con exito", "saldo":float(saldo_nuevo)}

    elif accion == "retirar":
        usuario = pet.get("usuario")
        cantidad = float(pet.get("cantidad",0))
        if cantidad <= 0:
                    return {"status":"error","mensaje":"La cantidad a retirar debe ser positiva y mayor que 0"}

        try:
            conexion = banco.conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT saldo FROM cuentas WHERE nombre = %s", (usuario,))
            saldo_actual = cursor.fetchone()
            cursor.close()
            conexion.close()

            if saldo_actual and saldo_actual[0] >= cantidad:
                 saldo_nuevo = banco.modificar_saldo(usuario, -cantidad)
                 return {"status":"ok","mensaje":"La cantidad ha sido retirada con exito", "saldo":float(saldo_nuevo)}

            else:
                 return {"status":"error","mensaje":"Fondos insuficientes"}
            
        except Exception as e:
             return {"status":"error","mensaje":f"Error procesando retiro de fondos: {str(e)}"}

    return {"status":"error","mensaje":"Accion desconocida"}

def atiende_cliente(con, addr):
     print(f"[+] Cliente conectado desde {addr}")

     try:
          while True:
               datos = con.recv(1024).decode("utf-8")
               if not datos:
                    break
               peticion = json.loads(datos)
               respuesta = procesar_peticion(peticion)
               con.sendall(json.dumps(respuesta).encode("utf-8"))

     except Exception as e:
          print(f"[-] Error conectando con {addr}: {e}")

     finally:
          con.close()
          semaforo.release()
          print(f"[-] Conexion cerrada con {addr}")


def inicia_servidor():
     servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     servidor.bind((HOST,PORT))
     servidor.listen()
     print(f"[*] Servidor banco escuchando en {HOST}:{PORT}...")

     while True:
          con, addr = servidor.accept()
          if semaforo.acquire(blocking=False):
               hilo = threading.Thread(target=atiende_cliente, args=(con,addr))
               hilo.daemon = True
               hilo.start()
          else:
               print(f"[!] Conexión rechazada desde {addr}: Límite alcanzado")
               resp_err = {"status": "error", "mensaje": "Servidor lleno. Limite de conexiones alcanzado"}
               try:
                    con.sendall(json.dumps(resp_err).encode("utf-8"))
               except Exception:
                    pass
               con.close()

if __name__ == '__main__':
     inicia_servidor()




