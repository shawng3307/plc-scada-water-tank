import time
from pymodbus.client import ModbusTcpClient

HOST = "127.0.0.1"
PORT = 1502

client = ModbusTcpClient(HOST, port=PORT)

if not client.connect():
    print("Could not connect to OpenPLC")
    raise SystemExit(1)

print("Connected to OpenPLC")

try:
    while True:
        tank_result = client.read_holding_registers(
            address=1024,
            count=1,
            device_id=1,
        )

        pump_result = client.read_coils(
            address=0,
            count=1,
            device_id=1,
        )

        if not tank_result.isError() and not pump_result.isError():
            tank_level = tank_result.registers[0]
            pump_on = pump_result.bits[0]

            print(f"Tank level: {tank_level} | Pump on: {pump_on}")
        else:
            print("Modbus read error")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping poller")

finally:
    client.close()
