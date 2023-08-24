from machine import SDCard , Pin, PWM, reset,SoftI2C,TouchPad, reset
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import time
import os

pasoY=Pin(25,Pin.OUT)   
pasoX=Pin(26,Pin.OUT)
enables=Pin(2,Pin.OUT)
direccionx=Pin(33,Pin.OUT)
direcciony=Pin(04,Pin.OUT)
servo= PWM(Pin(32),freq=50,duty=0)
btn1Pin=12
btn2Pin=13
btn3Pin=14

servo.duty(0)
enables.value(1)
def sd():
    return(os.listdir("/sd/cnc"))

class menu:#
    def iconos(self):            
        arrows=bytearray([0x04,0x0E,0x15,0x04,0x04,0x15,0x0E,0x04])
        sdIcon=bytearray([0x00,0x0F,0x15,0x1D,0x1F,0x1F,0x1F,0x00])
        self.lcd.custom_char(0, arrows)
        self.lcd.custom_char(1,sdIcon)

    def __init__(self):
        I2C_ADDR = 0x27
        i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)     #initializing the I2C method for ESP32
        enables.value(1)
        self.lcd = I2cLcd(i2c, I2C_ADDR, 2,16)
        self.ObjetoDibujo=Dibujar(4,-4.7,self.lcd)
        self.iconos()
        self.botones()
        try:
            os.mount(SDCard(slot=2, width=1, sck=18, cs=5, miso=19, mosi=23), "/sd")
        except:
            self.lcd.clear()
            self.lcd.putstr("insert an SDcard " )
            self.lcd.move_to(0,1)
            self.lcd.putstr("and reset   "+ chr(1))
            while reset!=True:
                if self.touch3.read()< 150:
                    print("try reset")
                    reset()
        self.files=sd()
        self.elementos=sd()
        print(self.elementos,self.files,"elementos y files antes del append")
        self.elementos.insert(0,"SET HOME")
        print(self.elementos)
        print("Files and directories in /sd")
        print(self.files)
        self.seleccionar()
        
    def botones(self):
        self.touch1 = TouchPad(Pin(btn1Pin, mode=Pin.IN))
        self.touch2 = TouchPad(Pin(btn2Pin, mode=Pin.IN))
        self.touch3 = TouchPad(Pin(btn3Pin, mode=Pin.IN))
        print("botones definidos")

        
    def seleccionar(self):
        if self.touch1.read()< 150:
            boton1A=1
        else:
            boton1A=0
        if self.touch2.read()< 150:
            boton2A=1
        else:
            boton2A=0
        if self.touch3.read()< 150:
            boton3A=1
        else:
            boton3A=0
        seleccionado=False
        indice=0
        indiceA=0
        self.lcd.clear()
        print(str(self.elementos[indice]))
        
        
        self.lcd.putstr("select File: ")
        self.lcd.move_to(15,0)
        self.lcd.putstr(chr(0))
        self.lcd.move_to(0,1)
        self.lcd.putstr(str(self.elementos[indice]))

        while seleccionado==False:
            try:
                if indice!=indiceA:
                    self.lcd.clear()
                    self.lcd.putstr("select file:")
                    self.lcd.move_to(15,0)
                    self.lcd.putstr(chr(0))
                    self.lcd.move_to(0,1)
                    self.lcd.putstr(str(self.elementos[indice]))
                    indiceA=indice
                
                if self.touch1.read()< 100:
                    boton1=1
                else:
                    boton1=0
                if self.touch2.read()< 100:
                    boton2=1
                else:
                    boton2=0
                if self.touch3.read()< 100:
                    boton3=1
                else:
                    boton3=0
                
                time.sleep(.1)
                if boton1!=boton1A:
                    if boton1==1:
                        indice+=1
                        if indice >= len(self.elementos):
                            indice=(len(self.elementos))-1
                    boton1A=boton1
                if boton2!=boton2A:
                    if boton2==1:
                        indice-=1
                        if indice<0:
                            indice=0
                    boton2A=boton2

                if boton3!=boton3A:
                    if boton3==1:
                        if self.elementos[indice] in self.files:
                            print("el elemento esta en los archivos")
                            self.lcd.clear()
                            self.lcd.putstr(str(self.elementos[indice]))
                            self.lcd.move_to(0,1)
                            self.lcd.putstr("initiating...")
                            
                            print(str(self.elementos[indice]),"seleccionado")
                            
                            file=str(self.elementos[indice])
                            print(file)
                            self.ObjetoDibujo.dibujar(file)
                            self.lcd.clear()
                            self.lcd.putstr("done in   "+str(round(self.ObjetoDibujo.tiempoDeDibujo,2))+" s")
                            self.lcd.move_to(0,1)
                            self.lcd.putstr("continue:     "+chr(0))
                        elif self.elementos[indice] =="SET HOME":
                            self.ObjetoDibujo.home()
                            self.lcd.clear()
                            self.lcd.putstr("home has ben set")
                            self.lcd.move_to(0,1)
                            self.lcd.putstr("continue:     "+chr(0))
                            enables.value(1)
                            
                    boton3A=boton3
                        
            except ValueError:
                self.lcd.putstr("Texto en el codigo G")
                print("Texto en el godigo G")
                continue
                

class Dibujar:
    def init(self,ppmmx,ppmmy):
        self.Z=10
        self.Za=self.Z
        self.decimalx,self.decimaly=0,0
        self.ppmmy=ppmmy
        self.ppmmx=ppmmx
        print("los ppmm estan definidas",self.ppmmx,self.ppmmy)
        
        self.home()
        time.sleep()
        self.decimal_acumuladoX,self.decimal_acumuladoY=0,0
        
    
    def __init__(self,Ppmmx, Ppmmy,screen):#ppmm se usara para calcular la cantidad de pasos que deve de dar por medida
        self.init(Ppmmx,Ppmmy)
        self.screen=screen
        self.FrecPasos=0.003
        
    def home(self):
        self.x,self.y,self.z=0,0,0#aqui se define la pocicion inicial de la herramienta
        self.xa,self.ya,self.za=self.x,self.y,self.z
        self.puntoX,self.puntoXa,self.puntoY,self.puntoYa=0,0,0,0
        print("coordenadas iniciales definidas")

    def girarMotorX(self,pasos):
        if pasos<0:
            Direccion=0

        else:
            Direccion=1
        direccionx.value(Direccion)
        for i in range(abs(pasos)):#ES EXTRAÑO QUE ESTO EXISTA PORQUE JAMAS VA A MOVER MAS DE 1 (PUEDE SER UTIL PARA EL SICLO HOME?)
            #print("X")        
            time.sleep(self.FrecPasos)
            pasoX.value(1)
            time.sleep(self.FrecPasos)
            pasoX.value(0)
        #
    def girarMotorY(self,pasos):
        if pasos<0:
            Direccion=0
        else:
            Direccion=1
        direcciony.value(Direccion)
        for i in range(abs(pasos)):
            #print("Y")
            time.sleep(self.FrecPasos)
            pasoY.value(1)
            time.sleep(self.FrecPasos)
            pasoY.value(0)
        #
    def zeta(self,zeta):
        self.Z=zeta
        if self.Z!=self.Za:
            if self.Z<0:
                servo.duty(3)
                #led.(duty_cycle)
                time.sleep(.5)
                servo.duty(0)
            elif self.Z>0:
                servo.duty(7)
                time.sleep(.5)
                servo.duty(0)
                #levanta
        self.Za=self.Z
        
        
    
    def bresenham(self,x0,y0,x1,y1):#uno introduce los parametros cada que se llama a la funcion, esta se llama cada lectura de gcode
#        self.puntos=[]
        #los parametros de entrada de la funcion son decimales, tienen que ser enteros, pero sin redondear
        #si 
        dx=x1-x0
        dy=y1-y0
        if dy<0:
            dy=-dy
            stepy=-1
        else:
            stepy=1
        if dx<0:
            dx=-dx
            stepx=-1
        else:
            stepx=1
        x=x0
        y=y0
        #print(x,y,"or")
 #       self.puntos.append([x,y])
        self.puntoX=x
        self.puntoY=y
        self.girarMotorY(self.puntoY-self.puntoYa)
        self.girarMotorX(self.puntoX-self.puntoXa)
        #print(self.puntoX-self.puntoXa,self.puntoY-self.puntoYa)
        self.puntoXa=self.puntoX
        self.puntoYa=self.puntoY
        if dx>dy:
            p=dy-dx
            incE=2*dy
            incNE=2*(dy-dx)
            while x!= x1:
                x=x+stepx
                if p<0:
                    p=p+incE
                else:
                    y=y+stepy
                    p=p+incNE
                #print(x,y,"or")
                self.puntoX=x
                self.puntoY=y
                self.girarMotorY(self.puntoY-self.puntoYa)
                self.girarMotorX(self.puntoX-self.puntoXa)
                #print(self.puntoX-self.puntoXa,self.puntoY-self.puntoYa)
                self.puntoXa=self.puntoX
                self.puntoYa=self.puntoY
        else:
            p=2*(dx-dy)
            incE=2*dx
            incNE=2*(dx-dy)
            while y!=y1:
                y=y+stepy
                if p<0:
                    p=p+incE
                else:
                    x=x+stepx
                    p=p+incNE
                #print(x,y,"or")
                self.puntoX=x
                self.puntoY=y
                self.girarMotorY(self.puntoY-self.puntoYa)
                self.girarMotorX(self.puntoX-self.puntoXa)
                #print(self.puntoX-self.puntoXa,self.puntoY-self.puntoYa)
                self.puntoXa=self.puntoX
                self.puntoYa=self.puntoY
#                self.puntos.append([x,y])
 #       self.moverLinea(self.puntos)

        
    """def zeta(self,zeta):
        
        self.Z=zeta
        if self.Z!=self.Za:
            #print("zeta",zeta)
            if self.Z <=0:
                #bobina.value(0)#el selenoide.
                time.sleep(.3)
            elif self.Z>0:
                #bobina.value(1)#el selenoide.
                time.sleep(.5)#creo que puede ser nucho mas rapido que esto, pero eso ya depende del hardware
                #levanta
        self.Za=self.Z
    """
    def toolChange(self,ToNum):
        duty=self.tools[ToNum]
        self.Z=5
        self.zata(self.Z)
        servomotor.duty(duty)
        time.sleep(.5)#puedo hacer que se adapte al que tan distante es el color multiplicandolo por la diferencia entre ToNum anterior y actual,
        
        
    def tamañof(self,archivo):
        self.tamaño=0
        for tmañodelineas in archivo:
            self.tamaño+=1
        print(self.tamaño,"el tamaño")
        
    def dibujar(self,nombre):
        
        enables.value(0)
        self.nombre=nombre
        print(self.nombre,"NOMBRE")
        ruta="/gcode/"+self.nombre
        print(ruta)
        archivo=open("/sd/cnc/"+self.nombre,mode="r")
        con=0
        self.tamañof(open("/sd/cnc/"+self.nombre,mode="r"))
        print("comienza")
        start=time.time()
        self.screen.move_to(0,1)
        self.screen.putstr("drawing... ")
        for line in archivo:
        #mienras=["G00 X 10.5 Y 10.5","G00 X 10.5 Y 10.5"]
        #for line in mienras:
            con+=1
            
            l=line[0:3]
            if l== "M06":
                c=0
                print ("tool change")
                for i in line:
                   c+=1
                   if i=="T" or i=="t":
                       self.tool=int(line[c+1:c+3])
                       print(self.tool)
                       
                
            if l == "G00"or l =="G01":
                c=0
                #print(line)
                for i in line:#extrae los valores de x e y actuales
                    c+=1
                    if i =="Z" or i =="z":
                        self.z=float(line[c+1:c+4])
                        self.zeta(self.z)
                        #print("z",self.z)

                    if i =="Y" or i =="y":
                        self.y=float(line[c+1:c+6])
                        #pprint("y",self.y)
                    if i =="X" or i=="x":
                        self.x=float(line[c+1:c+6])
 #                       pprint("x",self.x)
            #desde aqui indica para moverse
 
            # por aqui se deverian de multiplicar las coordenadas por los ppmm antes de pasarselas a bresenham
            #self.xa=self.xa*self.ppmm
            #self.ya=self.ya*self.ppmm
            #self.x=self.x*self.ppmm
            
                #primero con una variable
#                print("self.Y: ",self.y*self.ppmm)
                
                resy= self.y*self.ppmmy+self.decimaly
                self.decimaly= resy-int(resy)
                BresY=int(resy)
                #print(BresY)
                
                resx= self.x*self.ppmmx+self.decimalx
                self.decimalx= resx-int(resx)
                #print(self.x,self.ppmm,self.x*self.ppmm,"ppmm")
                
                BresX=int(resx)
                #print(BresX)
                
                #ahora las cordenadas anteriores y las actuales son decimales,
                #self.screen.move_to(0,1)
                #self.screen.putstr("drawing... ")
                #self.screen.move_to(11,1)
                #self.screen.putstr(str(round(con/(self.tamaño/100),1))+"%   ")

                self.bresenham(self.xa,self.ya,BresX,BresY)# aqui no se le pueden dar redondeados.
                self.xa=BresX
                self.ya=BresY
                self.za=self.z
        enables.value(1)
        self.tiempoDeDibujo=time.ticks_diff(time.time(), start) 
        #print(delta)
        print(self.xa,self.ya)
        self.bresenham(self.xa,self.ya,0,0)
        self.init(self.ppmmy,self.ppmmx)


Menu=menu()
#dibujo=Dibujar(4,-4.7)
print("las clases estan definidas")
#315
