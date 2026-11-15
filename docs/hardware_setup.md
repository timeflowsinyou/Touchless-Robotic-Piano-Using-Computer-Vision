# Hardware setup

## Wiring

Connect the five servo signal inputs to the original pins:

| Servo | Signal pin |
| ---: | ---: |
| 1 | D4 |
| 2 | D5 |
| 3 | D6 |
| 4 | D7 |
| 5 | D8 |

The source code assumes this ordering. Changing it changes which tracked finger
controls each piano key.

## Power and grounding

Do not assume that an Arduino board's 5 V pin or USB connection can safely
power five moving servos. Servo current depends on supply voltage, mechanical
load, motion, and stall conditions. Select a regulated external supply using
the servo manufacturer's datasheet and measured system load, with appropriate
current margin and wiring protection.

Connect all grounds together:

- external servo-supply ground;
- Arduino ground; and
- all five servo grounds.

The shared ground provides the reference for the D4–D8 control signals. Connect
servo positive supply leads to the external regulated supply, not automatically
to the Arduino 5 V pin. Confirm polarity before applying power.

## Mechanical safety

1. Disconnect servo power while installing horns and linkages.
2. Verify that each linkage moves freely through its intended range.
3. The software commands angles from 0° through 150°. Confirm that both endpoints
   are mechanically safe before coupling a servo to a piano key.
4. Test one servo at a time with the mechanism unloaded where practical.
5. Be ready to remove servo power if a linkage binds or a servo stalls.

No current rating, supply voltage, or mechanical endpoint is prescribed here
because those values were not established by the supplied source files.

## Arduino firmware

`arduino/pyfirmata2.ino` is a minimal ServoFirmata-style sketch. It:

- includes the Arduino `Servo` and `Firmata` libraries;
- starts Firmata at 57,600 baud;
- attaches servos across supported digital pins, subject to `MAX_SERVOS`;
- handles Firmata analog messages by writing their value to a servo; and
- handles system reset by resetting its servo counter.

It is not a complete copy of StandardFirmata and does not register the full set
of StandardFirmata callbacks. Upload this exact sketch to reproduce the source
configuration, or evaluate StandardFirmata separately if broader Firmata
features are required. Do not assume the two are interchangeable without a
hardware test.

### Upload procedure

1. Install Arduino IDE.
2. Ensure the Firmata and Servo libraries required by the sketch are available.
3. Open `arduino/pyfirmata2.ino`.
4. Select the connected Arduino-compatible board and its serial port.
5. Compile and upload the sketch.
6. Close Arduino Serial Monitor before running Python so that it does not hold
   the serial port.

## Camera

The application defaults to USB webcam index `0`:

```powershell
python src/ArduinoHand.py
```

For an IP camera, supply its stream URL rather than a web control-page URL:

```powershell
python src/ArduinoHand.py --camera "http://192.168.1.50:8080/video"
```

Keep credentials out of committed command examples and documentation. Network
latency and dropped frames can affect control responsiveness.
