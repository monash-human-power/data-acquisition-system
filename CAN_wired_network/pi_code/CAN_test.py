import can
import time
def send_msg(bus):
    value = 0x1234567844445555
    msg = can.Message(
        arbitration_id=0x123,
        data=value.to_bytes(8,byteorder="litle"),
        is_extended_id=False,
    )
    while True:
        try:
            try:
                bus.send(msg)
                print(f"Sent: {msg}")
                time.sleep(2)
            except can.CanError as e:
                print(f"Send failed {e}")
        except KeyboardInterrupt:
            print("stop sending messages")
            break

def recv_msg(bus):
    print("Listening on can0...")
    while True:
        try:
            msg=bus.recv(timeout=5.0)
            if msg is None:
                print("No message received in 5 seconds")
            else:
                id = msg.arbitration_id
                dlc = int(msg.dlc)
                payload = int.from_bytes(msg.data,'little')
                print(
                    f"ID=0x{id:03X}, "
                    f"DLC = {dlc}"
                    f"Data = {hex(payload).upper()}"
                )
        except KeyboardInterrupt:
            print("\nStopped.")
            break

def main():
    bus = can.interface.Bus(channel="can0", bustype="socketcan", bitrate=500000, samplepoint=0.75)
    while True:
        try:
            mode = int(input("Enter mode 1(send) or 2(receive): "))
            if mode == 1:
                send_msg(bus)
            elif mode == 2:
                recv_msg(bus)
            else:
                print("Invalid input, enter 1 or 2")
                continue
        except KeyboardInterrupt:
            print("Exiting program")
            bus.shutdown()
            break

if __name__ == "__main__":
    main()