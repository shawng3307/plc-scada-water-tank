
import os
import time

from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# OpenPLC configuration
PLC_HOST = "127.0.0.1"
PLC_PORT = 1502
PLC_DEVICE_ID = 1

# InfluxDB configuration
INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_ORG = "ics-lab"
INFLUX_BUCKET = "water_tank"
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN")

if not INFLUX_TOKEN:
    raise SystemExit("INFLUX_TOKEN environment variable is missing")

plc = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

if not plc.connect():
    raise SystemExit("Could not connect to OpenPLC")

influx = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
)

write_api = influx.write_api(write_options=SYNCHRONOUS)

print("Connected to OpenPLC")
print("Starting InfluxDB collector...")

try:
    while True:
        try:
            tank = plc.read_holding_registers(
                address=1024,
                count=1,
                device_id=PLC_DEVICE_ID,
            )

            pump = plc.read_coils(
                address=0,
                count=1,
                device_id=PLC_DEVICE_ID,
            )

            if tank.isError() or pump.isError():
                print("Modbus read error")
                time.sleep(1)
                continue

            tank_level = tank.registers[0]
            pump_on = pump.bits[0]

            point = (
                Point("water_tank")
                .tag("device", "openplc")
                .field("tank_level", int(tank_level))
                .field("pump_on", bool(pump_on))
            )

            write_api.write(
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG,
                record=point,
            )

            print(
                f"Tank: {tank_level}% | "
                f"Pump: {'ON' if pump_on else 'OFF'} | "
                "InfluxDB: written"
            )

        except Exception as error:
            print(f"Collection error: {error}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping collector")

finally:
    plc.close()
    influx.close()
