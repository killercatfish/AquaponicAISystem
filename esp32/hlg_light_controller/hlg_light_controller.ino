// ============================================================
// HLG-320H-48B PWM Light Controller
// ESP32 DevKit V1 — GPIO18 hardware PWM
// Board: EPLZON perfboard, soldered circuit
//
// MODES:
//   TEST_MODE true  = standalone test, cycles brightness on boot
//   TEST_MODE false = Pi serial control via USB
//
// SERIAL PROTOCOL (Pi → ESP32):
//   SET:75\n       → set brightness to 75%
//   GET\n          → returns current brightness as "BRIGHTNESS:75\n"
//   FADE:50:10\n   → fade to 50% over 10 seconds
//   TEST\n         → run test cycle once
//
// INVERTED LOGIC (HLG-320H-48B type B):
//   PWM duty 0%   = full brightness (transistor OFF, Dim+ floating)
//   PWM duty 100% = minimum brightness (transistor ON, Dim+ pulled to GND)
// ============================================================

#define TEST_MODE false        // true = standalone test, false = Pi serial mode

#define PWM_PIN       18       // GPIO18, hardware PWM
#define PWM_CHANNEL   0        // LEDC channel
#define PWM_FREQ      1000     // 1kHz — HLG spec minimum
#define PWM_RES       8        // 8-bit = 0-255

// ---- state ----
int currentBrightness = 100;  // 0-100% (human-readable)
bool fadingActive = false;
unsigned long fadeStart = 0;
int fadeFrom = 0;
int fadeTo = 0;
unsigned long fadeDuration = 0;

// ---- helpers ----

// Convert human brightness % to PWM duty (inverted)
// 100% bright = duty 0, 0% bright = duty 255
int brightnessToduty(int pct) {
  pct = constrain(pct, 0, 100);
  return map(pct, 0, 100, 255, 0);
}

void setBrightness(int pct) {
  pct = constrain(pct, 0, 100);
  currentBrightness = pct;
  ledcWrite(PWM_PIN, brightnessToduty(pct));
}

void startFade(int toPct, unsigned long durationMs) {
  fadeFrom = currentBrightness;
  fadeTo = constrain(toPct, 0, 100);
  fadeDuration = durationMs;
  fadeStart = millis();
  fadingActive = true;
}

void updateFade() {
  if (!fadingActive) return;
  unsigned long elapsed = millis() - fadeStart;
  if (elapsed >= fadeDuration) {
    setBrightness(fadeTo);
    fadingActive = false;
    return;
  }
  float progress = (float)elapsed / fadeDuration;
  int current = fadeFrom + (fadeTo - fadeFrom) * progress;
  setBrightness(current);
}

void runTestCycle() {
  Serial.println("TEST: starting cycle");

  Serial.println("TEST: full brightness");
  setBrightness(100);
  delay(2000);

  Serial.println("TEST: 75%");
  setBrightness(75);
  delay(2000);

  Serial.println("TEST: 50%");
  setBrightness(50);
  delay(2000);

  Serial.println("TEST: 25%");
  setBrightness(25);
  delay(2000);

  Serial.println("TEST: minimum (10%)");
  setBrightness(10);
  delay(2000);

  Serial.println("TEST: fade back to 100% over 5s");
  startFade(100, 5000);
  while (fadingActive) {
    updateFade();
    delay(50);
  }

  Serial.println("TEST: complete");
}

// ---- serial command parser ----
String inputBuffer = "";

void handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "GET") {
    Serial.print("BRIGHTNESS:");
    Serial.println(currentBrightness);
    return;
  }

  if (cmd == "TEST") {
    runTestCycle();
    return;
  }

  if (cmd.startsWith("SET:")) {
    int pct = cmd.substring(4).toInt();
    setBrightness(pct);
    Serial.print("OK:BRIGHTNESS:");
    Serial.println(currentBrightness);
    return;
  }

  // FADE:50:10  → fade to 50% over 10 seconds
  if (cmd.startsWith("FADE:")) {
    String args = cmd.substring(5);
    int colonIdx = args.indexOf(':');
    if (colonIdx > 0) {
      int toPct = args.substring(0, colonIdx).toInt();
      int secs = args.substring(colonIdx + 1).toInt();
      startFade(toPct, (unsigned long)secs * 1000);
      Serial.print("OK:FADING_TO:");
      Serial.print(toPct);
      Serial.print(":OVER:");
      Serial.print(secs);
      Serial.println("s");
    } else {
      Serial.println("ERR:FADE_FORMAT");
    }
    return;
  }

  Serial.print("ERR:UNKNOWN:");
  Serial.println(cmd);
}

// ---- setup ----
void setup() {
  Serial.begin(115200);
  delay(500);

  // Configure hardware PWM (ESP32 core 3.x LEDC API)
  ledcAttach(PWM_PIN, PWM_FREQ, PWM_RES);

  // Start at full brightness
  setBrightness(100);

  Serial.println("HLG LIGHT CONTROLLER READY");
  Serial.print("MODE: ");
  Serial.println(TEST_MODE ? "STANDALONE TEST" : "PI SERIAL");
  Serial.println("Commands: SET:0-100 | GET | FADE:pct:secs | TEST");

  if (TEST_MODE) {
    delay(1000);
    runTestCycle();
  }
}

// ---- loop ----
void loop() {
  // Update any active fade
  updateFade();

  // Read serial commands (Pi or Serial Monitor)
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (inputBuffer.length() > 0) {
        handleCommand(inputBuffer);
        inputBuffer = "";
      }
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }

  delay(20);
}
