""" SOFTWARE DE SEGUIMIENTO VIDEO BASADO EN OPENCV Y RFID.
SISTEMA PARA EL SEGUIMIENTO DE ANIMALES DE LABORATORIO MEDIANTE VISION
COMPUTACIONAL Y EL APOYO DE UN SISTEMA IDENTIFICACION MEDIANTE RADIOFRECUENCIA.

AUTOR: ELIO VALENZUELA SEGURA
TUTOR: ANTONIO DIAZ GARCIA

TRABAJO FIN DE GRADO UNIVERSIDAD DE GRANADA

TITULACION: INGENIERIA DE TECNOLOGIAS DE TELECOMUNICACION"""


import cv2
import numpy as np
import math
import time
import datetime
import os
import shutil
import plotly.plotly as py
import smtplib
import serial
import threading

from email.mime.text import MIMEText
from plotly.graph_objs import *
py.sign_in('elio', 'qtox15phuk')


#Funcion que no hace nada, solo para que el trackbar funcione
def nothing(x):
    pass


"""Definicion de los objetos mediante los cuales vamos a hacer el seguimiento
de los objetivos"""
class Target:

    def __init__(self):
        self.trayect = []
        self.unk = []
        self.name = 0
        self.areas = []
        self.mean = 0
        self.active = 1
        self.id = 1

    def setActive(self, a):
        self.active = a

    def getActive(self):
        return self.active

    def setName(self, n):
        self.name = n

    def getName(self):
        return self.name

    def setPos(self, x, y, time):
        self.trayect.append([x, y, time])

    def getPos(self):
        (x, y, t) = self.trayect[-1]
        return (x, y)

    def setUnk(self, x, y, time):
        self.unk.append([x, y, time])

    def resetUnk(self):
        self.unk=[]

    def getUnkPos(self):
        (x, y, t) = self.unk[-1]
        return (x, y)

    def getUnkTime(self):
        (x, y, t) = self.unk[-1]
        return (t)

    def getUnk(self):
        return self.unk

    def getTrayect(self):
        return self.trayect

    def getAreas(self):
        return self.areas

    def setArea(self, cnt):
        a = cv2.contourArea(cnt)
        self.areas.append(a)

    def getId(self):
        return self.id

    def setId(self,i):
        self.id=i

    def setMean(self, m):
        self.mean = m

    def getMean(self):
        return self.mean

    def getTime(self):
        (x, y, tim, iden) = self.trayect[-1]
        return str(tim)

    def updateTrayect(self, u):
        self.trayect= self.trayect + u

    def checkAnt(self, a):
        valor =0
        if a==self.name:
            valor=1
        return valor


class Unknow:

    def __init__(self):
        self.trayect = []
        self.active = 1

    def setActive(self, a):
        self.active = a

    def getActive(self):
        return self.active

    def setPos(self, x, y, time):
        self.trayect.append([x, y, time])

    def getPos(self):
        (x, y, t) = self.trayect[-1]
        return (x, y)

    def resetUnk(self):
        self.trayect=[]
        self.active = 0

    def getTrayect(self):
        return self.trayect





"""Dibuja la trayectoria que ha seguido el objeto. Para cada trayectoria coge
un color diferente. ATENCION!!    LA GAMA DE COLORES LIMITA A  10 OBJETOS """
def drawTrayect(tr, fr):
    for i in range(0, len(tr)):
        if (tr[i].getActive() == 1):
            if tr[i].getId()==1:
                t = tr[i].getTrayect()
                color = (0, 25 * i, 25 * i)
            if tr[i].getId()==0:
                t = tr[i].getUnk()
                color = (50, 0, 200)
            if(len(t) < 30):
                for j in range(0, len(t)):
                    tt = t[j]
                    x = tt[0]
                    y = tt[1]
                    cv2.circle(fr, (int(x), int(y)), 1, color, 2)
            if(len(t) > 30):
                for j in range((len(t) - 30), len(t)):
                #for j in range(0, len(t)):
                    tt = t[j]
                    x = tt[0]
                    y = tt[1]
                    cv2.circle(fr, (int(x), int(y)), 1, color, 2)
    if (len(doubleclick) > 0):
        point = doubleclick [-1]
        cv2.circle(fr,(point[0], point[1]), 3, (0, 0, 255), 3)


"""Funcion para dibujar el nombre del objeto"""
def drawObject(tr, fr):
    global scale, height,lastRead
    for i in range(0, len(tr)):
        if(tr[i].getId() == 1):
            (x, y) = tr[i].getPos()
            cv2.putText(fr, str(tr[i].getName()), (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255))
        if(tr[i].getId() == 0):
            (x, y) = tr[i].getUnkPos()
            cv2.putText(fr, str(tr[i].getName()), (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255))
        else:
            (x, y) = tr[i].getPos()
            cv2.putText(fr, str(tr[i].getName()), (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0))
    cv2.line(fr,(0, 5), (int(10/scale), 5), (0, 0, 0), 1)
    cv2.putText(fr, "0", (0, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
    cv2.putText(fr, "10 cm", (int(10/scale), 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
    cv2.line(fr,((width/2),0),((width/2),height),(255,100,0),1)
    cv2.putText(fr, str(lastRead), (10, 430), cv2.FONT_HERSHEY_PLAIN, 3, (0,10,255))



def read_from_port(ser):
    global received
    while True:
        time.sleep(0.0001)
        if ser.inWaiting()>0:
            reading = ser.readline()
            received.append(int(reading))





def save_click(event,x,y,flags,param):
    global click,doubleclick,targets, on, frame, mousepos,lastmousepos
    lastmousepos = mousepos
    mousepos = (x,y)
    if event == cv2.EVENT_LBUTTONUP:
        click.append([x ,y])
    if event == cv2.EVENT_LBUTTONDBLCLK:
        doubleclick.append([x,y])
        t = str (datetime.datetime.now())
        targets[1].setPos(x, y, t, 1)
        targets[1].setActive(1)


def lookTag(a,tr,fr):
    area1=0
    area2=0
    antena=[]
    antena.append(-1)
    antena.append(-1)
    global veces,received
    global lastRead
    global width
    for i in range(0, len(tr)):
        if tr[i].getId()==0 and tr[i].getActive()==1:
            (x,y)=tr[i].getUnkPos()
            if (x<width/2):
                area2+=1
            if (x>width/2):
                area1+=1
    for i in range(0, len(tr)):
        if tr[i].getId()==1 and tr[i].getActive()==1:
            (x,y)=tr[i].getPos()
            if (x<width/2):
                area2+=2
            if (x>width/2):
                area1+=2
    if (area1==1 and veces==20 and lastRead==1):
        if (received.count(1) >0):
            antena[0]=1
            cv2.putText(fr, '1', (height/2+200, 200), cv2.FONT_HERSHEY_PLAIN, 9, (0, 255, 0))
        elif (received.count(2) >0):
            antena[0]=2
            cv2.putText(fr, '2', (height/2+200, 200), cv2.FONT_HERSHEY_PLAIN, 9, (0, 255, 0))
    elif (area2==1 and veces==10 and lastRead==2):
        if (received.count(1) >0):
            antena[1]=1
            cv2.putText(fr, '1', (height/2-200, 200), cv2.FONT_HERSHEY_PLAIN, 9, (0, 0, 255))
        elif (received.count(2) >0):
            antena[1]=2
            cv2.putText(fr, '2', (height/2-200, 200), cv2.FONT_HERSHEY_PLAIN, 9, (0, 0, 255))
    if veces==10 or veces==20:
        for i in range(0, len(tr)):
            if tr[i].getId()==0:
                (x,y)=tr[i].getUnkPos()
                if (x>width/2 and area1==1 ):
                    if (antena[0]==1 or antena[0]==2):
                        for j in range(0, len(tr)):
                            if tr[j].getName()== antena[0]:
                                tr[j].setName(tr[i].getName())
                        tr[i].setName(antena[0])
                        tr[i].updateTrayect(tr[i].getUnk())
                        tr[i].setId(1)
                        tr[i].setActive(1)
                        t = str (datetime.datetime.now())
                        tr[i].setPos(x,y,t)
                if (x<width/2 and area2==1):
                    if (antena[1]==1 or antena[1]==2):
                        for j in range(0, len(tr)):
                            if tr[j].getName()== antena[1]:
                                tr[j].setName(tr[i].getName())
                        tr[i].setName(antena[1])
                        tr[i].updateTrayect(tr[i].getUnk())
                        tr[i].setId(1)
                        tr[i].setActive(1)
                        t = str (datetime.datetime.now())
                        tr[i].setPos(x,y,t)



    if veces ==10:
        changeAnt(1)
        received=[]
        lastRead=1
    if veces == 20:
        changeAnt(2)
        lastRead=2
        received=[]
        veces=0
    veces+=1


def drawArea(cnt, fr):
    for i in range(0, len(cnt)):
        area = cv2.contourArea(cnt[i])
        (x, y), _ = cv2.minEnclosingCircle(cnt[i])
        cv2.putText(fr, str(area), (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255))


def meanArea (cnt,rounds):
    global means
    global mean
    for i in range(0, len(cnt)):
        a = cv2.contourArea(cnt[i])
        means.append(a)
        m = 0
    if (rounds == 19):
        for j in range(0,len(means)):
            m = m + means[j]
        m = m /len(means)
        mean = m


"""Funcion para filtrar los contornos que solo superen un tamano determinado
y asi eliminar posible ruido. Tambien limita el numero de contornos a seguir."""
def selectedCnt (cnt):
    i = len(cnt) - 1
    while(i >= 0):
        if cv2.contourArea(cnt[i]) < size:
            cnt.pop(i)
        i = i - 1
    if (len(cnt) > maxObjects):
        cnt = cnt[0:maxObjects]
    return cnt


"""Funcion que asigna cada contorno a su objetivo basando en la minima distancia
entre la ultima posicion del objetivo y el centro del contorno detectado"""
def dMin(cnt, tr):
    for k in range(0, len(tr)):
        tr[k].setActive(0)
    global mean
    pArea = mean
    i = 0
    while (i <= (len(cnt) - 1)):
        dmin = 20000
        dminfake = 20000
        (xc, yc), _ = cv2.minEnclosingCircle(cnt[i])
        area = cv2.contourArea(cnt[i])
        for j in range(0, len(tr)):
            if tr[j].getId()==1:
                (xt, yt) = tr[j].getPos()
            if tr[j].getId()==0:
                (xt, yt) = tr[j].getUnkPos()
            d = math.sqrt((xc-xt)*(xc-xt)+(yc-yt)*(yc-yt))
            if (d < dmin and area < (pArea + (pArea/2)) and tr[j].getActive() == 0):
                dmin = d
                indextr = j
            if (d < dmin and area > (pArea + (pArea/2)) and tr[j].getActive() == 0):
                dminfake = d
                indextr = j
                for p in range (0,(len(cnt))):
                    (xc, yc), _ = cv2.minEnclosingCircle(cnt[p])
                    d2 = math.sqrt((xc-xt)*(xc-xt)+(yc-yt)*(yc-yt))
                    if (d2 < dminfake):
                        dminfake=20000
        if (dmin < 20000 and tr[indextr].getActive() == 0 and tr[indextr].getId()==1):
            t = str (datetime.datetime.now())
            tr[indextr].setPos(xc, yc, t)
            tr[indextr].setId(1)
            tr[indextr].setActive(1)
            i += 1
        elif (dmin < 20000 and tr[indextr].getActive() == 0 and tr[indextr].getId()==0):
            t = str (datetime.datetime.now())
            tr[indextr].setActive(1)
            tr[indextr].setUnk(xc, yc, t)
            tr[indextr].setId(0)
            i += 1
        elif (dminfake < 20000 and tr[indextr].getActive() == 0 and tr[indextr].getId()==1):
            t = str (datetime.datetime.now())
            tr[indextr].setActive(1)
            tr[indextr].setId(0)
            tr[indextr].setUnk(xc, yc, t)
        elif (dminfake < 20000 and tr[indextr].getActive() == 0 and tr[indextr].getId()==0):
            t = str (datetime.datetime.now())
            tr[indextr].setActive(1)
            tr[indextr].setId(0)
            tr[indextr].resetUnk()
            tr[indextr].setUnk(xc, yc, t)
        else:
            i+=1



#Obtiene el valor de la escala en centimetros/pixel
def setScale ():
    global mousepos, click, scale, frame, width, height
    point1=click[1]
    if (len(click)== 2):
        cv2.line(frame,(point1[0],point1[1]),mousepos,(255,0,0),1)
    if (len(click)== 3):
        point2=click[2]
        s = math.sqrt((point1[0]-point2[0])*(point1[0]-point2[0])+ (point1[1]-point2[1])*(point1[1]-point2[1]))
        height, width = frame.shape[:2]
        scale = 10/s


def sendAlarm ():
    remitente = "<sistema@gmail.com>"
    destinatario = "<eliovalenzuela2@gmail.com>"
    # Construimos el mensaje simple
    mensaje = MIMEText("""Se ha detectado un evento en el sistema""")
    mensaje['From']="Sistema Monitorizacion <sistema@gmail.com>"
    mensaje['To']="Responsable laboratorio <eliovalenzuela2@gmail.com>"
    mensaje['Subject']="Alarma Sistema Monitorizacion"
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(remitente, destinatario, mensaje.as_string())
        print "Correo enviado"
    except:
        print """Error: el mensaje no pudo enviarse.
        Compruebe que sendmail se encuentra instalado en su sistema"""


"""Funcion que se ejecuta al arrancar el programa y crea los objetos
en funcion de los contornos detectados en ese momento"""
def first(cnt, tr):
    for i in range(0, len(cnt)):
        (xc, yc), _ = cv2.minEnclosingCircle(cnt[i])
        new = Target()
        new.setName(i+1)
        t = str (datetime.datetime.now())
        new.setPos(xc, yc, t)
        tr.append(new)
        #sendAlarm()


def log(tr):
    shutil.rmtree('trayects')
    os.mkdir('trayects')
    for j in range(0, len(tr)):
        path= 'trayects/'
        path += `j`
        f = open(path,"a")
        f.write(str(tr[j].getTrayect()))
        f.close()


def getGraphs():
    setScale()
    global vel,scale
    for j in range(0,len(targets)):
        path= 'trayects/'
        path += `j`
        f = open(path,"r")
        trayect = f.read()
        datos0=trayect.replace("[", " ")
        datos1=datos0.replace("]", " ")
        datos0=datos1.replace("'", " ")
        datos1=datos0.replace(")", " ")
        datos0=datos1.replace("(", " ")
        datos1=datos0.replace('"', " ")
        datos=datos1.split(",")
        x=[]
        y=[]
        tim=[]
        vel=[]
        while (len(datos)>4):
            a= datos.pop(0)
            b=datos.pop(0)
            t=datos.pop(0)
            t=t[2:-2]
            tim.append(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f"))
            x.append(int(float(a)))
            y.append(abs(int(float(b))-height))
            if len(x)>2:
                x1=x[-1]
                x2=x[-2]
                y1=y[-1]
                y2=y[-2]
                s = math.sqrt((x1-x2)*(x1-x2)+ (y1-y2)*(y1-y2))
                delta = (tim[-1]-tim[-2]).total_seconds()
                v=(s*scale)/(delta*10)
                if v>9:
                    vel.append(9)
                else :
                    vel.append(v)
        coordx.append(x)
        coordy.append(y)
        times.append(tim)
        veloc.append(vel)
        f.close()




def traceGraphs():
    trace=[]
    scat=[]
    vel=[]
    for i in range (0,len(coordx)):
        n= 'Target '
        n += `i`
        trace.append(Scatter(x=coordx[i],y= coordy[i],name= n))
        scat.append(Histogram2d(x=coordx[i],y=coordy[i], name=n))
        vel.append(Scatter(x=times[i],y=veloc[i], name=n))
    data2 = Data(scat)
    data3 = Data(vel)
    layout = Layout(title='Trayects',xaxis=XAxis(title='Pos X', showgrid=False,),yaxis=YAxis(title='Pos Y', showgrid=False,))
    data1 = Data(trace)
    fig = Figure(data=data1, layout=layout)
    plot_url = py.plot(fig, filename='Trayect')
    layout2 = Layout(title='Activity zones',xaxis=XAxis(title='Pos X', showgrid=False,),yaxis=YAxis(title='Pos Y', showgrid=False,))
    fig2 = Figure(data=data2, layout=layout2)
    plot_url = py.plot(fig2, filename='Activity zones')
    layout3 = Layout(title='Speed',xaxis=XAxis(title='Time',),yaxis=YAxis(title='Velocity',))
    fig3 = Figure(data=data3, layout=layout3)
    plot_url = py.plot(fig3, filename='Speed cm per sec')



def selectColor():
    global colorsHSV
    if (colorsHSV[0] == 0):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        point = click [-1]
        crop_img = hsv[point[1]:point[1]+10, point[0]:point[0]+10]
        col=cv2.mean(crop_img)
        colorsHSV=(col[0],col[1],col[2])


def printInstruc(i):
    if (i == 0):
        s = 'Haga click en el objeto a seguir para calibrar la mascara de color'
        cv2.putText(frame, s, (20,455), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
    if (i == 1 or i == 2):
        s = 'Ajuste el rango de la mascara hasta obtener una imagen clara'
        cv2.putText(frame, s, (20,455), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
        s = 'Escalado: haga click para seleccionar un objeto referencia de 10 cm'
        cv2.putText(frame, s, (20,470), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
    if (i == 3 and on ==0):
        s = 'Pulse barra espaciadora para comenzar el seguimiento'
        cv2.putText(frame, s, (20,455), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
    if (mean == 0 and on ==1):
        s = 'Calibrando...'
        cv2.putText(frame, s, (20,455), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
    if (i >= 3 and on ==1 and i <=5 and mean!=0):
        s = 'Seleccione haciendo click cada tag comenzando por el 1'
        cv2.putText(frame, s, (20,455), cv2.FONT_HERSHEY_PLAIN, 1, (255, 100, 0))
    elif (on == 1 and mean !=0 and i>5):
        s = 'Programa en ejecucion'
        cv2.putText(frame, s, (450,455), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

"""Funcion principal.Busca los contornos externos en una imagen y almacena los
puntos obtenidos de manera comprimida.Filtra los objetos menores que size
y dibuja los contornos de los objetos seleccionados por color.Finalmente
dibuja el nombre del objeto en su centro y almacena y dibuja la trayectoria
seguida."""
def trackObject(img, fr, tr, rounds, unk):
    global click
    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = selectedCnt(contours)
    meanArea(contours,rounds)
    if (rounds == 19):
        first(contours, tr)
    if (rounds >= 21):
        #drawArea(contours, fr)
        if (len(tr)+3 == len (click)):
            setTag()
        dMin(contours, tr)
        lookTag(2,tr,fr)
        #lk(fr,contours)
        drawObject(tr, fr)
        drawTrayect(tr, fr)


def lk(fr,cnt):
    global old_gray,p1,lk_params,good_new,good_old,mask2,targets,copy,p0
    if (rounds == 22):
        feature_params = dict( maxCorners = 50 ,qualityLevel = 0.1,minDistance = 2,blockSize = 10 )
        p0 = cv2.goodFeaturesToTrack(old_gray, mask = copy, **feature_params)
    p= np.zeros(shape=(len(targets),1,2))
    frame= fr.copy()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    for k in range (0,len(targets)):
        x=targets[k].getPos()[0]
        y= targets[k].getPos()[1]
        o=np.array([x, y],dtype='float')
        p[k]=np.array([o],dtype='float')
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    good_new = p1[st==1]
    good_old = p0[st==1]
    for i in range (0,len(good_new)):
        cv2.circle(frame,(good_new[i][0],good_new[i][1]),5,[255,0,0],-1)
        cv2.circle(frame,(good_old[i][0],good_old[i][1]),5,[255,0,255],-1)
        cv2.line(frame, (good_new[i][0],good_new[i][1]),(good_old[i][0],good_old[i][1]), [255,255,0], 2)
    cv2.imshow('Frameflow',frame)
    img = cv2.add(frame,mask2)
    p0 = good_new.reshape(-1,1,2)
    old_gray=frame_gray.copy()


def setTag():
    global targets
    for j in range(3, (len(click))):
        (xc,yc) = click [j]
        dmin=20000
        for k in range(0, len(targets)):
            (xt, yt) = targets[k].getPos()
            d = math.sqrt((xc-xt)*(xc-xt)+(yc-yt)*(yc-yt))
            if (d < dmin):
                dmin = d
                index=k
        targets[index].setName(j-2)
    click.append([0,0])


def changeAnt(a):
    """
    arduinoPort.flushInput()
    arduinoPort.flushOutput()
    arduinoPort.flush()"""
    try:
        arduinoPort.write(str (a))
    except:
        pass


"""Declaracion de variables"""

#Para rastrear mas objetos aumentar valor
maxObjects = 2
#Para objetos pequenos disminuir valor
size = 600
#Elementos estructurantes (de tipo rectangular) para las funciones erode y dilate
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6))





targets = []
unknow = []
cap = cv2.VideoCapture(0)


#cv2.namedWindow('Mask original',cv2.WINDOW_OPENGL)
#cv2.moveWindow('Mask original',0,600)
cv2.namedWindow('Mask original',cv2.WINDOW_NORMAL)
cv2.namedWindow('Filtered mask',cv2.WINDOW_NORMAL)
cv2.namedWindow('Frame',cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('Frame',save_click)
cv2.createTrackbar('Range', 'Filtered mask', 70, 100, nothing)
on = 0
mean = 0
means = []
rounds = 1
m = 0
click = (0,0)
copy=np.empty
frame = np.empty
old_gray = np.empty
click = []
doubleclick=[]
mousepos=(0,0)
lastmousepos = (0,0)
colorsHSV=(0,0,0)
scale = 0
coordx=[]
coordy=[]
good_old=[]
good_new=[]
times=[]
veloc=[]
width = 0
height = 0
lastRead=2
veces=0
received=[]

ret, old_frame = cap.read()
mask2 = np.zeros_like(old_frame)
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
lk_params = dict( winSize  = (15,15),maxLevel = 2,criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
feature_params = dict( maxCorners = 50 ,qualityLevel = 0.2,minDistance = 50,blockSize = 20 )
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
p1 = p0



print '\nDatos generales de la comunicacin serial establecida'
# Iniciando conexin serial
arduinoPort = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
# Reset manual del Arduino
arduinoPort.setDTR(False)
time.sleep(0.3)
# Se borra cualquier data que haya quedado en el buffer
arduinoPort.flushInput()
arduinoPort.setDTR()
time.sleep(2)
print '\nEstado del puerto: %s ' % (arduinoPort.isOpen())
print 'Nombre del dispositivo conectado: %s ' % (arduinoPort.name)
print 'Dump de la configuracin:\n %s ' % (arduinoPort)
print '\n###############################################\n'


thread = threading.Thread(target=read_from_port,args=(arduinoPort,))
thread.start()


"""Bucle principal del programa que obtiene los valores de HSV introducidos,
los aplica a la mascara. Realiza capturas de la camara y convierte formatos.
Muestra ventanas con las diferentes fases del filtrado.

PARA FIN DEL PROGRAMA PULSA ESC, Y PARA COMENZAR A RASTREAR OBJETIVOS UNA
VEZ CALIBRADA LA MASCARA PULSA ESPACIO
"""
while(1):

    # Obtiene el frame
    _, frame = cap.read()

    try:
        len(frame)
    except TypeError:
        break
    printInstruc(len(click))
    x = datetime.datetime.now()
    if (len(click) == 1) :
        selectColor()
    if (len(click) == 2 or len(click) == 3) :
        setScale()
    p = cv2.getTrackbarPos('Range', 'Filtered mask')

    Hmin = colorsHSV[0]-p
    Hmax = colorsHSV[0]+p
    Smin = colorsHSV[1]-p
    Smax = colorsHSV[1]+p
    Vmin = colorsHSV[2]-p
    Vmax = colorsHSV[2]+p

    # Convierte BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Defino el rango de color a filtrar y creo la mascara entre los rangos
    #obtenidos en HSV selection
    lower_color = np.array([Hmin, Smin, Vmin])
    upper_color = np.array([Hmax, Smax, Vmax])
    mask = cv2.inRange(hsv, lower_color, upper_color)

    #Erosiono y dilato la mascara para eliminar ruido y obtener solo los
    #objetivos de mayor tamano
    erosion = cv2.erode(mask, kernel, iterations=1)
    dilation = cv2.dilate(erosion, kernel2, iterations=5)
    erosion = cv2.erode(dilation, kernel, iterations=2)
    erosion2 = cv2.erode(dilation, kernel, iterations=1)
    copy = erosion
    if on == 1:
        trackObject(copy, frame, targets, rounds, unknow)
        rounds += 1
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask original', mask)
    cv2.imshow('Filtered mask', erosion2)
    cv2.moveWindow('Mask original',0,0)
    cv2.moveWindow('Filtered mask',0,350)
    cv2.moveWindow('Frame',480,0)
    #time.sleep(0.06)

    k = cv2.waitKey(5) & 0xFF
    if k == 32:
        on = 1
    if k==13:
        time.sleep(10)
    if k==9:
        changeAnt(2)
    if (k == 70 or k == 102):
        break
    if k == 27:
        break
sendAlarm()
log(targets)
getGraphs()
traceGraphs()
arduinoPort.close()
cv2.destroyAllWindows()


