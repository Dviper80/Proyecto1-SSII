import socket
import threading
import json
import banco

HOST = "0.0.0.0"

PORT = 5000


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
    
        





