from fmiopendata.wfs import download_stored_query
import datetime as dt
import pyodbc
import numpy as np

# Retrieve the latest hour of data from a bounding box
end_time = dt.datetime.utcnow()
start_time = end_time - dt.timedelta(hours=1)
# Convert times to properly formatted strings
start_time = start_time.isoformat(timespec="seconds") + "Z"
# -> 2020-07-07T12:00:00Z
end_time = end_time.isoformat(timespec="seconds") + "Z"
# -> 2020-07-07T13:00:00Z

START_TIME = dt.datetime(2023,1,1,0,0,0)
END_TIME = dt.datetime(2023,12,31,0,0,0)
ARGS =["place=Lappeenranta",
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

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes'
connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()

# Etsi viimeisin aikasäde
latest_tstep = max(obs.data.keys())

# Luo tietokantataulu, jos se ei ole vielä olemassa
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'säädata')
    BEGIN
        CREATE TABLE säädata (
            asema NVARCHAR(255),
            aika NVARCHAR(255),
            tuulen_nopeus FLOAT,
            ilmanlämpötila FLOAT,
            pilvisyys INT,
            ilmankosteus FLOAT,
            lumensyvyys FLOAT
        )
    END
''')
connection.commit()

# Lisää tiedot tietokantaan
wind_speed_values = []
air_temperature_values = []
cloud_amount_values = []
relative_humidity_values = []
snow_depth_values = []

for time, data in obs.data.items():
    for station, value in data.items():
        wind_speed = float(value.get("Wind speed", {}).get("value", 0.0))
        air_temperature = float(value.get("Air temperature", {}).get("value", 0.0))
        cloud_amount = int(value.get("Cloud amount", {}).get("value", 0))
        relative_humidity = float(value.get("Relative humidity", {}).get("value", 0.0))
        snow_depth = float(value.get("Snow depth", {}).get("value", 0.0))

        # Append values to lists
        wind_speed_values.append(wind_speed)
        air_temperature_values.append(air_temperature)
        cloud_amount_values.append(cloud_amount)
        relative_humidity_values.append(relative_humidity)
        snow_depth_values.append(snow_depth)

    # Käsittele 'nan'-arvot ennen lisäämistä tietokantaan
    wind_speed = wind_speed if not np.isnan(wind_speed) else 0.0
    air_temperature = air_temperature if not np.isnan(air_temperature) else 0.0
    snow_depth = snow_depth if not np.isnan(snow_depth) else 0.0

    try:
        print(
            f"Values before inserting for station {station}: {wind_speed}, {air_temperature}, {cloud_amount}, {relative_humidity}, {snow_depth}")

        cursor.execute('''
            INSERT INTO säädata (asema, aika, tuulen_nopeus, ilmanlämpötila, pilvisyys, ilmankosteus, lumensyvyys)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (station, time.strftime('%Y-%m-%d %H:%M:%S'), wind_speed, air_temperature, cloud_amount,
              relative_humidity, snow_depth))

    except Exception as e:
        print(f"Virhe lisättäessä tietoja asemalle {station}: {e}")

connection.commit()

# Sulje yhteys
connection.close()