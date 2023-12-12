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

snd = download_stored_query("fmi::observations::weather::sounding::multipointcoverage",
                            ["place=Sodankylä"])

sounding = snd.soundings[0]
sounding.name  # Name of the sounding station
sounding.id  # Station ID of the sounding station
sounding.nominal_time  # Nominal time of the sounding
sounding.start_time  # Actual start time of the sounding
sounding.end_time  # Actual end time of the sounding
sounding.lats  # Numpy array of the measurement location latitudes [degrees]
sounding.lons  # Numpy array of the measurement location longitudes [degrees]
sounding.altitudes  # Numpy array of the measurement location altitudes [m]
sounding.times  # Numpy array of the measurement times [datetime]
sounding.pressures  # Numpy array of measured pressures [hPa]
sounding.temperatures  # Numpy array of measured temperatures [°C]
sounding.dew_points  # Numpy array of measured dew points [°C]
sounding.wind_speeds  # Numpy array of measured wind speeds [m/s]
sounding.wind_directions  # Numpy array of measured wind directions [°]

# print(sounding.temperatures)
# print(sounding.name)


obs = download_stored_query("fmi::observations::weather::multipointcoverage",
                            args=["place=Lappeenranta"])
# Tulosta saatavilla olevat tiedot
print(sorted(obs.data.keys()))
# Etsi viimeisin aikasäde
latest_tstep = max(obs.data.keys())
print(sorted(obs.data[latest_tstep].keys()))
# Tulosta havaintoaseman tiedot
print(sorted(obs.data[latest_tstep]["Lappeenranta Lepola"].keys()))

# Tulosta tiettyjä sääparametreja Lappeenranta Lepola
print(obs.data[latest_tstep]["Lappeenranta Lepola"]["Wind speed"])
print(obs.data[latest_tstep]["Lappeenranta Lepola"]["Air temperature"])
print(obs.data[latest_tstep]["Lappeenranta Lepola"]["Cloud amount"])
print(obs.data[latest_tstep]["Lappeenranta Lepola"]["Relative humidity"])
print(obs.data[latest_tstep]["Lappeenranta Lepola"]["Snow depth"])

# Uusi for-loop kaikkien havaintoasemien viimeisimpien tietojen tulostamiseksi
for station, data in obs.data[latest_tstep].items():
    print(f"\nStation: {station}")
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
for station, data in obs.data[latest_tstep].items():
    wind_speed = float(data.get("Wind speed", {}).get("value", 0.0))
    air_temperature = float(data.get("Air temperature", {}).get("value", 0.0))
    cloud_amount = int(data.get("Cloud amount", {}).get("value", 0))
    relative_humidity = float(data.get("Relative humidity", {}).get("value", 0.0))
    snow_depth = float(data.get("Snow depth", {}).get("value", 0.0))

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
        ''', (station, latest_tstep.strftime('%Y-%m-%d %H:%M:%S'), wind_speed, air_temperature, cloud_amount,
              relative_humidity, snow_depth))

    except Exception as e:
        print(f"Virhe lisättäessä tietoja asemalle {station}: {e}")

connection.commit()

# Sulje yhteys
connection.close()