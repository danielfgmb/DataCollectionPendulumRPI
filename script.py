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
samples = 64 # samples per obscervation
country = "CO" # country code ISO
city = "BOG"
lat = "4°36'N"
long = "74°3'W"
alt = "2500"
univ = "Uniandes"

filename_v= "resultados_uniandes"




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
    print(pic_message)
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
        #print("MENSAGEM DO PIC DE CONFIGURACAO:\n")
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
    print(pic_message)
    if "DAT" in pic_message:
        return "DATA_START"
    elif "END" in pic_message:
        return "DATA_END"
    else:
        #1       3.1911812       9.7769165       21.2292843      25.72
        try:
            pic_message = pic_message.strip()
            pic_message = pic_message.split("\t")
            pic_data={"sample":str(pic_message[0]),"datetime":str(datetime.now()),"period":str(pic_message[1]),"gravity":str(pic_message[2]),"velocity":str(pic_message[3]),"temperature":str(pic_message[4]),"country":country,"city":city,"university":univ,"lat":str(lat),"long":str(long),"alt":str(alt)}
            return pic_data
        except:
            return "ERROR"


def saveObservationCSV(filename,data,datetime,backup_directory="backup-data"):
    if len(data)>0:
        if(os.path.exists(filename)):
            f = open(filename, 'w')
            writer = csv.writer(f)
            writer.writerow(list(data[0].keys()))
            f.close()
        

        f = open(filename, 'w')
        for row in data:
            writer = csv.writer(f)
            writer.writerow(list(data[0].values()))
        f.close()  
    pass



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
                else:
                    print(data)
                    allObs.append(data)
            
            saveObservationCSV(filename_v,data,hour)
            

    except:
        executionOk = False
        print(" -> EXECUTION FAILED!!!")
    
    return (allTest and executionOk)

    
execute()






    

    

    