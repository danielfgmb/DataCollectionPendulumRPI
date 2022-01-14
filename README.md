# DataCollectionPendulumRPI

## Requirements

### Python packages

- serial
- csv
- re
- os
- pytz
- datetime

### Installation

```
pip install serial
pip install pytz
pip install regex
pip install csv
```


## Configuration

Edit lines 8 to 24 with the specifications for the location and configuration of the pendulum.
```
"""
CHANGE INFO ACCORDING TO YOUR PENDULUM LOCATION
"""
puertoExp = "/dev/ttyS0" # serial port RPI
dist = 15 # distance (CFG dist samples)
samples = 64 # samples per obscervation
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
```

## Chron Job

Enter this command to set a new chron job

```
crontab -e
```

Add a new line in the chron tab file to run the script every 12 minutes


```
*/12 * * * * /usr/bin/python3 ~/DataCollectionPendulumRPI/script.py

```

#### Based on https://github.com/e-lab-FREE/RPi_Proxy/tree/main/pic_interface
