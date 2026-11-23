# 05 - Firmware: test the board, flash the game

## Arduino setup (what we use)

- **Arduino IDE 2**, **ESP32 board package (core 3.3.x)**
- Board: **ESP32 Dev Module**
- Libraries: **GFX Library for Arduino** (moononournation) and **XPT2046_Touchscreen** (Paul Stoffregen)
- Partition scheme for the full game: **Minimal SPIFFS (1.9 MB APP with OTA)**. The CYD has only 4 MB of flash.

## Upload quirk (CYD)

On our boards the upload only starts if you help it: press **Upload**, **hold BOOT** until the log shows "Writing at ...", then let go and press **RST** when it finishes. With the case closed, use a pin through the BOOT / RST slot on the back (marked B and R).

## Step 1: hardware test sketch

Open `firmware/cyd_hardware_test/cyd_hardware_test.ino`. It checks the screen colours, touch (yellow dots), the RGB LED (green while touched) and the battery meter on IO35.

Expected: red, green, blue, white bars left to right. If the colours look inverted, the `invertDisplay(true)` line matters. If touch is mirrored, swap the map ranges.

> **Honest note:** the sketch was written from our confirmed pin settings but was not compiled by the author of this guide. If a library call has changed, it is a one-line fix.

## Step 2: the game

The game itself (Scrappies) lives in its own repository: **CodySDEV/skrappies**. It runs in the Minimal SPIFFS partition scheme and supports over-the-air updates from files hosted online.

Hardware facts the firmware relies on:

| What | Pin |
|---|---|
| Display | HSPI: DC 2, CS 15, SCK 14, MOSI 13, MISO 12, rotation 1 |
| Touch | VSPI: CLK 25, MISO 39, MOSI 32, CS 33, IRQ 36 |
| Backlight | 21 |
| RGB LED | 4 / 16 / 17, LOW = on |
| Battery meter | 35 (two 100 k resistors, volts = reading x 2) |

## Battery percentage

Read IO35 16 times, average, double it, then use a LiPo discharge curve. While USB is plugged in the reading is too high (charging voltage). Show the percentage only after unplugging, or add a "charging" note in software. There is no hardware signal for "USB present" in this build.

Next: [06 Troubleshooting](06_troubleshooting.md)
