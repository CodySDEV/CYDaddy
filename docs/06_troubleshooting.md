# 06 - Troubleshooting and known quirks

| Symptom | Cause / fix |
|---|---|
| CYD dies the moment the boost is connected | Boost was not set to 5.0 V first. Over-voltage on VIN killed one of our boards (21.5 V). Always set and re-check the boost off-board. |
| VIN to GND beeps on a meter | Short. Do not power. The board is damaged. |
| Screen colours inverted | Missing `invertDisplay(true)`. |
| Upload will not start | Hold BOOT until "Writing at...", then press RST. |
| CYD cuts out when the slide switch moves, slow to start | Bad switch. Replace it (our first one was bad). |
| Battery percentage jumps up while charging | Expected. It reads charging voltage. Unplug and wait a minute. |
| Unit keeps running with the switch off | Expected when USB is plugged in; the switch only cuts the battery path. |
| Battery plug does not match | These packs use non-standard polarity. Meter it first. |
| Charger tab snaps | Use the reinforced tab (7 Final), and do not over-tighten the M2.5 screw. |
| M3 hole too tight in the back shell | Clear with a 3.5 mm drill. |
| Switch screw pokes through the top | Screw too long. Use M2 x 4. |
| Stylus too loose or too tight | Try the other body (A, B or C). |
| No microSD opening | By design. Open the case to reach the card. |
| Slicer says floating regions on the stylus | Fixed in 7 Final (flange touches the bed). |

Next: [07 Changelog](07_changelog.md)
