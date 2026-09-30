import socket
import json
import seguridad # Lo usamos solo para generar el paquete de la "víctima"

# Cambia la IP si el servidor está en otra máquina
HOST = "10.21.215.140" 
PORT = 5000

print("--- SIMULACIÓN DE ROBO DE TRÁFICO ---")
# 1. Simulamos a la víctima generando un paquete válido
peticion_legitima = {"accion": "ingresar", "token": "token_falso", "cantidad": 50}
paquete_interceptado = seguridad.cifrar_peticion(peticion_legitima)

print(f"Paquete capturado en texto plano por el atacante:\n{paquete_interceptado.decode('utf-8')[:100]}...\n")

def inyectar_ataque(nombre_ataque, payload_bytes):
    print(f"[>] Ejecutando: {nombre_ataque}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        s.sendall(payload_bytes)
        
        # Esperamos a ver qué responde el servidor
        respuesta = s.recv(4096)
        if not respuesta:
            print("[+] ÉXITO DEFENSIVO: El servidor detectó el ataque y cortó la conexión silenciosamente.\n")
        else:
            print(f"[-] FALLO DEFENSIVO: El servidor respondió: {respuesta}\n")
    except Exception as e:
        print(f"[+] ÉXITO DEFENSIVO (Conexión rechazada/cerrada): {e}\n")
    finally:
        s.close()


# ==========================================
# PRUEBA 1: ATAQUE DE REPETICIÓN (REPLAY)
# ==========================================

# A) El atacante deja pasar el paquete original hacia el servidor (El servidor lo procesa y guarda el Nonce)
inyectar_ataque("Paso original (Víctima enviando petición)", paquete_interceptado)

# B) El atacante reenvía EXACTAMENTE la misma cadena de bytes 1 segundo después para duplicar el ingreso
inyectar_ataque("Replay Attack (Reenviando el mismo paquete interceptado)", paquete_interceptado)


# ==========================================
# PRUEBA 2: MAN IN THE MIDDLE (MANIPULACIÓN)
# ==========================================

# El atacante coge el paquete interceptado, lo abre como JSON y decide alterar
# el mensaje cifrado para intentar inyectar otro comando (ej. "retirar 1000")
diccionario_atacante = json.loads(paquete_interceptado.decode('utf-8'))

# Cambiamos un solo carácter del texto cifrado (cambiamos la última letra)
texto_cifrado = diccionario_atacante['mensaje_cifrado']
diccionario_atacante['mensaje_cifrado'] = texto_cifrado[:-1] + ('A' if texto_cifrado[-1] != 'A' else 'B')

# Reempaquetamos el JSON manipulado a bytes
paquete_manipulado = json.dumps(diccionario_atacante).encode('utf-8')

# El atacante envía el paquete alterado con la firma (MAC) original
inyectar_ataque("MitM Attack (Enviando paquete con ciphertext alterado)", paquete_manipulado)