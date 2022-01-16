import csv
import os

filename_read = "resultados_uniandes.csv"
filename_write = "averaged_resultados_uniandes.csv"
sample_number = 64

def readFile(filename,sample_number):
    final_data = []
    with open(filename,"r") as file:
        csv_reader = csv.DictReader(file)

        count=1

        t_sum=[]
        g_sum=[]
        vel_sum=[]
        per_sum=[]

        initial_time = ""
        end_time = ""

        for row in csv_reader:
            if(int(row["sample"])==1):
                initial_time=row["datetime (utc)"]
            t_sum.append(float(row["temp_corr (c)"]))
            g_sum.append(float(row["g_corr (m/s2)"]))
            vel_sum.append(float(row["velocity (m/s)"]))
            per_sum.append(float(row["period (s)"]))

            if count%sample_number==0:
                
                if int(row["sample"])==sample_number:
                    end_time=row["datetime (utc)"]
                    t_aver=sum(t_sum)/len(t_sum)
                    g_aver=sum(g_sum)/len(g_sum)
                    vel_aver=sum(vel_sum)/len(vel_sum)
                    per_aver=sum(per_sum)/len(per_sum)

                    final_data.append({"temperature_average (c)":t_aver,"gravity_average (m/s2)":g_aver,\
                        "velocity_average (m/s)":vel_aver,"period_average (s)":per_aver,"samples":len(g_sum),\
                        "datetime_start (utc)":initial_time,"datetime_end (utc)":end_time,"data_t_corrected":row["correction"],\
                        "country":row["country"],"city":row["city"],"university":row["university"],"lat":row["lat"],"long":row["long"],"alt":row["alt"]})

                    count=0

                    t_sum=[]
                    g_sum=[]
                    vel_sum=[]
                    per_sum=[]
                    
                else:
                    raise Exception("Number of lines not matching sample number")
                
                
            count+=1
    return final_data

def writeCSV(filename,data):
    try:
        if len(data)>0:
            f = open(filename, 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(list(data[0].keys()))
            for row in data:
                
                writer.writerow(list(row.values()))
            f.close()  
    except:
         raise Exception("Error al guardar datos")

def execute(filename_read,filename_write,sample_number):
    data = readFile(filename_read,sample_number)
    writeCSV(filename_write,data)

execute(filename_read,filename_write,sample_number)



