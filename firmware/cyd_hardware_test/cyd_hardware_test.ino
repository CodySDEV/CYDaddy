// CYDaddy hardware test for the CYD ESP32-2432S028 (ILI9341 + XPT2046).
// Written from the pin settings confirmed on our boards.
// NOTE: not compile-tested by the author of this guide. If a library call has changed, fix it and tell us.
// Libraries: "GFX Library for Arduino" (moononournation), "XPT2046_Touchscreen" (Paul Stoffregen)
// Board: ESP32 Dev Module. Hold BOOT while uploading until "Writing at..." shows, then press RST.
#include <Arduino_GFX_Library.h>
#include <SPI.h>
#include <XPT2046_Touchscreen.h>

#define TFT_BL 21
#define LED_R 4
#define LED_G 16
#define LED_B 17
#define BAT_PIN 35

Arduino_DataBus *bus = new Arduino_ESP32SPI(2 /*DC*/, 15 /*CS*/, 14 /*SCK*/, 13 /*MOSI*/, 12 /*MISO*/, HSPI);
Arduino_GFX *gfx = new Arduino_ILI9341(bus, GFX_NOT_DEFINED /*RST*/, 1 /*rotation*/);

SPIClass touchSPI(VSPI);
XPT2046_Touchscreen ts(33 /*CS*/, 36 /*IRQ*/);

void setup() {
  Serial.begin(115200);
  pinMode(LED_R, OUTPUT); pinMode(LED_G, OUTPUT); pinMode(LED_B, OUTPUT);
  digitalWrite(LED_R, HIGH); digitalWrite(LED_G, HIGH); digitalWrite(LED_B, HIGH); // LOW = on
  pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH);
  gfx->begin();
  gfx->invertDisplay(true);           // needed on our boards
  gfx->fillScreen(BLACK);
  touchSPI.begin(25 /*CLK*/, 39 /*MISO*/, 32 /*MOSI*/, 33 /*CS*/);
  ts.begin(touchSPI);
  ts.setRotation(1);
  // colour bars: should read red, green, blue, white left to right
  gfx->fillRect(0, 0, 80, 40, RED);
  gfx->fillRect(80, 0, 80, 40, GREEN);
  gfx->fillRect(160, 0, 80, 40, BLUE);
  gfx->fillRect(240, 0, 80, 40, WHITE);
  gfx->setTextColor(WHITE); gfx->setTextSize(2);
  gfx->setCursor(10, 60); gfx->print("CYD test: touch the screen");
}

void loop() {
  // battery on IO35 through two 100k resistors: volts = reading x 2
  static uint32_t t = 0;
  if (millis() - t > 1000) {
    t = millis();
    long sum = 0;
    for (int i = 0; i < 16; i++) sum += analogReadMilliVolts(BAT_PIN);
    float v = (sum / 16.0) * 2.0 / 1000.0;
    gfx->fillRect(0, 100, 320, 30, BLACK);
    gfx->setCursor(10, 105); gfx->printf("Battery: %.2f V", v);
    Serial.printf("battery %.2f V\n", v);
  }
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.x, 200, 3700, 0, 319);
    int y = map(p.y, 240, 3800, 0, 239);
    x = constrain(x, 0, 319); y = constrain(y, 0, 239);
    gfx->fillCircle(x, y, 4, YELLOW);
    digitalWrite(LED_G, LOW);
  } else {
    digitalWrite(LED_G, HIGH);
  }
}
