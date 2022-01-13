import serial
import csv
import re
import os
from datetime import datetime


"""
CHANGE INFO ACCORDING TO YOUR PENDULUM LOCATION
"""
puertoExp = "/dev/ttyS0" # serial port RPI
dist = 10 # distance (CFG dist samples)
samples = 10 # samples per obscervation
country = "CO" # country code ISO
city = "BOG"
lat = "4°36'N"
long = "74°3'W"
alt = "2500"
univ = "Uniandes"
lenght = 2.8155 #m
cte_lenght = 0.000016 #m/m°C
t_measured=18.97 #°C

filename_v= "resultados_uniandes.csv"




def openConn(puertoExp):
    conn=False
    try:
        serial_port = serial.Serial(port = puertoExp, baudrate=115200)
    except:
        pass
    else:
        conn=True
    return conn, serial_port

def testExp(serial_port):
    test=False
    pic_message = serial_port.read_until(b'\r')
    pic_message = pic_message.decode(encoding='ascii')
    pic_message = pic_message.strip()
    print(" ->",pic_message)
    if(re.search(r"^(IDS)\s(?P<exp_name>[^ \t]+)\s(?P<exp_state>[^ \t]+)$",pic_message)):
        test=True
    return test

def initExp(serial_port,dist,samples):
    cmd ="cfg\t"+str(dist)+"\t"+str(samples)+"\r"
    cmd = cmd.encode(encoding="ascii")
    serial_port.reset_input_buffer()
    serial_port.write(cmd)

    intentoPorSiError=0

    while True :
        pic_message = serial_port.read_until(b'\r')
        print(" ->",pic_message.decode(encoding='ascii'))

        if "CFG" in pic_message.decode(encoding='ascii') :
            break
        elif intentoPorSiError < 3:
            cmd ="cfg\t"+str(dist)+"\t"+str(samples)+"\r"
            cmd = cmd.encode(encoding="ascii")
            serial_port.reset_input_buffer()
            serial_port.write(cmd)
            print(" -> WARNING: TRYING CFG AGAIN",intentoPorSiError)
            intentoPorSiError +=1
        else:
            return False
        
    
    status_confirmation = serial_port.read_until(b'\r')
    status_confirmation = status_confirmation.decode(encoding='ascii')
    print(" ->",status_confirmation)
    if "CFGOK" in status_confirmation:
        return True

def start(serial_port) :
    cmd = "str\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        print(" ->",pic_message.decode(encoding='ascii'))
        if "STROK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(STOPED|CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None:
            return False

def receiveData(serial_port,country,city,lat,long,alt,univ):
    pic_message = serial_port.read_until(b'\r')
    pic_message = pic_message.decode(encoding='ascii')
    print(" ->",pic_message)
    if "DAT" in pic_message:
        return "DATA_START"
    elif "END" in pic_message:
        return "DATA_END"
    else:
        try:
            pic_message = pic_message.strip()
            pic_message = pic_message.split("\t")
            pic_data={"sample":str(pic_message[0]),"datetime":str(datetime.now()),"period":str(pic_message[1]),"gravity":str(pic_message[2]),"velocity":str(pic_message[3]),"temperature":str(pic_message[4]),"country":country,"city":city,"university":univ,"lat":str(lat),"long":str(long),"alt":str(alt)}
            return pic_data
        except:
            return "ERROR"

def temperatureCorrection(data):
    t_fin=data[-1]["temperature"]
    t_ini=data[0]["temperature"]
    t=[]
    correccion=False

    for row in data:
        t.append(float(row["temperature"]))
    t_prom=sum(t)/len(t)
    var=0

    for t_u in t:
        var+=(t_u-t_prom)^2
    var=var^(1/2)

    if var>2 or abs(t_fin-t_ini)>2:
        t_new=sum(t[0:5])/5
        correccion=True
    
    for row in data:
        row["correction"]=correccion
        if(correccion):
            row["temp_corr"]=t_new
            row["length_corr"]=lenght+lenght*cte_lenght*(t_new-t_measured)
            row["g_corr"]=2*3.1415926*row["lenght_corr"]
        else:
            row["temp_corr"]=row["temperature"]
            row["length_corr"]=0
            row["g_corr"]=row["gravity"]




def saveObservationCSV(filename,data,datetime,backup_directory="backup-data"):


    if len(data)>0:
        escribirHead=False
        if(os.path.exists(filename)): 
            filesize = os.path.getsize(filename)
            if not filesize>0:
                escribirHead=True
        else:
            escribirHead=True

        f = open(filename, 'a')
        writer = csv.writer(f)
        if escribirHead:
            writer.writerow(list(data[0].keys()))
        for row in data:
            
            writer.writerow(list(row.values()))
        f.close()  
    
    os.mkdir(backup_directory)

    f = open(backup_directory+"/"+"data"+str(datetime)+".csv", 'a')
    writer = csv.writer(f)
    if escribirHead:
        writer.writerow(list(data[0].keys()))
    for row in data:
        writer.writerow(list(row.values()))
    f.close()  




# PRINCIPAL METHOD
def execute():
    allTest=False
    hour="XXX"
    executionOk=True
    try:
        
        print("TRYING CONNECTION ...")
        res,serial_port=openConn(puertoExp)
        if(res):
            print(" -> CONN SUCCESS ...")
            print("TEST EXPERIMENT ...")
            if(testExp(serial_port)):
                print(" -> TEST SUCCESS ...")
                print("CONFIGURE OBS...")
                if(initExp(serial_port,dist,samples)):
                    print(" -> CONF SUCCESS ...")
                    print("STARTING EXPERIMENT...")
                    if(start(serial_port)):
                        hour=str(datetime.now()).replace(" ","_").replace(":","_")
                        print(" -> EXP STARTED ...")
                        allTest=True
        
        if not allTest:
            print(" -> FAILED!!!")
        
        allObs=[]

        if allTest:
            pararCiclo=False
            while not pararCiclo:
                data=receiveData(serial_port,country,city,lat,long,alt,univ)
                if(data=="ERROR"):
                    print(" -> ERROR_EN_OBS")
                    pararCiclo=True
                elif(data=="DATA_END"):
                    pararCiclo=True
                elif(data=="DATA_START"):
                    pass
                else:
                    allObs.append(data)
            temperatureCorrection(allObs)
            saveObservationCSV(filename_v,allObs,hour)
            

    except Exception as e:
        executionOk = False
        print(" -> EXECUTION FAILED!!!\n",str(e))
    
    return (allTest and executionOk)

    
execute()






    

    

    