from fmiopendata.wfs import download_stored_query
import datetime as dt
import pyodbc
import numpy as np

START_TIME = dt.datetime(2023, 12, 1, 0, 0, 0)
END_TIME = dt.datetime(2023, 12, 30, 0, 0, 0)
ARGS = ["place=Lappeenranta",
        "starttime=" + START_TIME.isoformat(timespec="auto"),
        "endtime=" + END_TIME.isoformat(timespec="auto")]

obs = download_stored_query("fmi::observations::weather::daily::multipointcoverage",
                            args=ARGS)

# Uusi for-loop kaikkien havaintoasemien viimeisimpien tietojen tulostamiseksi
for time, data in obs.data.items():
    print(f"\nTime: {time}")
    for variable, value in data.items():
        print(f"{variable}: {value}")

# Yhdistä SQL Server -tietokantaan
server = ' '
database = 'tietokanta'
username = 'DESKTOP-368NHB7\\sampp'
password = ''
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = (f'DRIVER={driver};SERVER={server};DATABASE={database};'
                     f'Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes')
connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()

# Etsi viimeisin aikasäde
#latest_tstep = max(obs.data.keys())

# Luo tietokantataulu, jos se ei ole vielä olemassa
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'December2023')
    BEGIN
        CREATE TABLE December2023 (
            Station NVARCHAR(255),
            Time NVARCHAR(255),
            Max_temperature FLOAT,
            Min_temperature FLOAT,
            Avg_temperature FLOAT,
            Precipitation FLOAT,
            Snow_depth FLOAT
        )
    END
''')
connection.commit()

air_temperature_values = []
max_temp_values = []
min_temp_values = []
precipitation_values = []
snow_depth_values = []

# Lisää tiedot tietokantaan
for time, data in obs.data.items():
    for station, value in data.items():
        air_temperature = float(value.get("Air temperature", {}).get("value", 0.0))
        max_temp = float(value.get("Maximum temperature", {}).get("value", 0.0))
        min_temp = float(value.get("Minimum temperature", {}).get("value", 0.0))
        precipitation = float(value.get("Precipitation amount", {}).get("value", 0.0))
        snow_depth = float(value.get("Snow depth", {}).get("value", 0.0))

    air_temperature_values.append(air_temperature)
    max_temp_values.append(max_temp)
    min_temp_values.append(min_temp)
    precipitation_values.append(precipitation)
    snow_depth_values.append(snow_depth)

    try:
        print(
            f"Values before inserting for station {station}: {air_temperature}, {max_temp}, {min_temp},"
            f" {precipitation}, {snow_depth}")

        cursor.execute('''
            INSERT INTO December2023 (Station, Time, Avg_temperature, Max_temperature, Min_temperature, Precipitation, 
            Snow_depth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (station, time.strftime('%Y-%m-%d'), air_temperature, max_temp, min_temp,
              precipitation, snow_depth))

    except Exception as e:
        print(f"Virhe lisättäessä tietoja asemalle {station}: {e}")

connection.commit()

# Sulje yhteys
connection.close()