#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";

//***Set server***
const char* mqttServer = "broker.hivemq.com"; 
int port = 1883;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>
#include <ESP32Servo.h>

// Define các PIN
#define TRIG_PIN 13
#define ECHO_PIN 12
#define BUTTON_PIN 14
#define SERVO_PIN 11
#define MAX_LOG_COUNT 100  // lưu tối đa 100 lần cho ăn gần nhất

struct FoodLog {
  String datetime;
  float level;
};

FoodLog foodLogs[MAX_LOG_COUNT];
int logCount = 0;
// Các biến cần thiết cho chức năng đo lượng thức ăn bằng cảm biến khoảng cách
unsigned long lastMeasureTime = 0;
int max_distance = 130;
int distance = 0;

// Mạch thời gian thực
RTC_DS1307 rtc;
char daysOfTheWeek[7][12] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};

// Màn hình LCD
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Servo
Servo feederServo;

// Biến dùng để ghi nhận có đang có ăn không
bool feeding = false;
bool alreadyFed = false;

int readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  int distance = duration * 0.034 / 2;
  return distance;
}

float readFoodLevelPercent() {
  int d = readDistance();
  d = min(d, max_distance);
  float level = (1.0 - (float(d) / max_distance)) * 100;
  return level;
}

void feedCat(int hour, int minute, int second, int duration = 1) {
  lcd.setCursor(0, 2);
  lcd.print("Feeding...         ");
  feederServo.write(90);
  delay(duration * 1000);
  feederServo.write(0);
  lcd.setCursor(0, 2);
  lcd.printf("Last feed: %02d:%02d:%02d", hour, minute, second);
  char buffer[10];
  sprintf(buffer, "%02d:%02d:%02d", hour, minute, second);
  mqttClient.publish("/23127138/LastFeed", buffer);
}

// Define giờ cho ăn (Dành cho chức năng cho ăn tự động)
struct FeedTime {
  int hour;
  int minute;
  int duration;
};

#define MAX_FEED_COUNT 10
FeedTime FeedSchedule[MAX_FEED_COUNT];
int feedCount = 0;
int lastMinute = -1;

// Gửi danh sách lịch trình cho ăn tới web
void publishFeedSchedule() {
  String payload = "[";
  for (int i = 0; i < feedCount; i++) {
    payload += "{";
    payload += "\"hour\":" + String(FeedSchedule[i].hour) + ",";
    payload += "\"minute\":" + String(FeedSchedule[i].minute) + ",";
    payload += "\"duration\":" + String(FeedSchedule[i].duration);
    payload += "}";

    if (i < feedCount - 1) payload += ",";
  }
  payload += "]";

  mqttClient.publish("/23127138/ScheduleList", payload.c_str());
  Serial.println("Đã gửi FeedSchedule");
}

// Thêm lịch cho ăn vào danh sách
void addFeedTime(int hour, int minute, int duration) {
  if (feedCount >= MAX_FEED_COUNT) {
    Serial.println("Lịch đầy, không thể thêm.");
    return;
  }
  FeedSchedule[feedCount].hour = hour;
  FeedSchedule[feedCount].minute = minute;
  FeedSchedule[feedCount].duration = duration;
  feedCount++;
  Serial.printf("Đã thêm: %02d:%02d vào lịch trình\n", hour, minute);
  publishFeedSchedule();
}

// Xoá lịch cho ăn khỏi danh sách
void removeFeedTime(int hour, int minute) {
  bool found = false;
  for (int i = 0; i < feedCount; i++) {
    if (FeedSchedule[i].hour == hour && FeedSchedule[i].minute == minute) {
      found = true;
      // Dịch các phần tử phía sau lên
      for (int j = i; j < feedCount - 1; j++) {
        FeedSchedule[j] = FeedSchedule[j + 1];
      }
      feedCount--; // giảm số lượng lịch
      Serial.printf("Đã xoá lịch %02d:%02d\n", hour, minute);
      break;
    }
  }

  if (!found) {
    Serial.printf("Không tìm thấy lịch %02d:%02d để xoá\n", hour, minute);
  }

  publishFeedSchedule();
}

void wifiConnect() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connected!");
}

void mqttConnect() {
  while(!mqttClient.connected()) {
    Serial.println("Attemping MQTT connection...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);
    if(mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");

      //***Subscribe all topic you need***
      mqttClient.subscribe("/23127138/DropFood");
      mqttClient.subscribe("/23127138/Schedule");
      mqttClient.subscribe("/23127138/ScheduleGet");
     
    }
    else {
      Serial.print(mqttClient.state());
      Serial.println("try again in 5 seconds");
      delay(5000);
    }
  }
}

void addFoodLog(float level) {
  DateTime now = rtc.now();
  
  String dt = "";
  dt += String(now.day()) + "/";
  dt += String(now.month()) + "/";
  dt += String(now.year()) + " ";
  dt += String(now.hour()) + ":";
  dt += String(now.minute());

  if (logCount >= MAX_LOG_COUNT) {
    // Dịch mảng sang trái để xoá phần tử cũ nhất
    for (int i = 0; i < MAX_LOG_COUNT - 1; i++) {
      foodLogs[i] = foodLogs[i + 1];
    }
    logCount = MAX_LOG_COUNT - 1;
  }

  foodLogs[logCount].datetime = dt;
  foodLogs[logCount].level = level;
  logCount++;
}

void sendFoodLevelToChartHistory() {
  StaticJsonDocument<2048> doc;  // Chỉnh dung lượng tùy số lượng log

  JsonArray arr = doc.to<JsonArray>();

  for (int i = 0; i < logCount; i++) {
    JsonObject obj = arr.createNestedObject();
    obj["payload"] = foodLogs[i].level;
    obj["topic"] = "FoodLevel";
    obj["datetime"] = foodLogs[i].datetime;  // đã là chuỗi "dd/mm/yyyy HH:MM"
  }

  char jsonBuffer[2048];
  serializeJson(doc, jsonBuffer);

  mqttClient.publish("/23127138/FoodLevelChart", jsonBuffer);
  Serial.print("Gửi log đồ ăn (mảng): ");
  Serial.println(jsonBuffer);
}


void sendFoodLevelToChart(float level) {
  DateTime now = rtc.now();

  // Tạo JSON object
  StaticJsonDocument<128> doc;
  doc["payload"] = level;
  doc["topic"] = "FoodLevel";

  // Định dạng datetime thành chuỗi "dd/mm/yyyy HH:MM"
  char datetime[20];
  snprintf(datetime, sizeof(datetime),
           "%02d/%02d/%04d %02d:%02d",
           now.day(), now.month(), now.year(),
           now.hour(), now.minute());
  doc["datetime"] = datetime;

  // Chuyển sang chuỗi JSON và publish
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);

  mqttClient.publish("/23127138/FoodLevelChart", jsonBuffer);

  Serial.print("Đã gửi dữ liệu chart: ");
  Serial.println(jsonBuffer);
}



//MQTT Receiver
void callback(char* topic, byte* message, unsigned int length) {
  Serial.println(topic);
  String msg;
  for(int i=0; i<length; i++) {
    msg += (char)message[i];
  }
  Serial.println(msg);

  //***Code here to process the received package***
  DateTime now = rtc.now();
  if (msg == "DropFood") {
    feedCat(now.hour(), now.minute(), now.second());
  }

  // Lấy danh sách lịch trình được gửi từ web
  if (String(topic) == "/23127138/ScheduleGet") {
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, msg);

    if (error) {
      Serial.print("Lỗi parse JSON: ");
      Serial.println(error.c_str());
      return;
    }

    feedCount = 0;  // reset lịch cũ
    for (JsonObject t : doc.as<JsonArray>()) {
      int h = t["hour"];
      int m = t["minute"];
      int d = t["duration"];
      addFeedTime(h, m, d);
    }

    Serial.println("Đã nạp lại FeedSchedule từ server.");
  }

  // Thêm/Xoá lịch trình
  if (msg.startsWith("Add")) {
    int hour, minute, duration;
    sscanf(msg.c_str(), "Add %d %d %d", &hour, &minute, &duration);
    addFeedTime(hour, minute, duration);
  }
  else if (msg.startsWith("Remove")) {
    int hour, minute;
    sscanf(msg.c_str(), "Remove %d %d", &hour, &minute);
    removeFeedTime(hour, minute);
  }

}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Serial.print("Connecting to WiFi");

  wifiConnect();
  mqttClient.setServer(mqttServer, port);
  mqttClient.setCallback(callback);
  mqttClient.setKeepAlive( 90 );
  
  lcd.init();
  lcd.backlight();
  
  rtc.begin();
  if (!rtc.isrunning()) {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); // set time from compiler
  }

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  feederServo.attach(SERVO_PIN);
  feederServo.write(0); // default position

  // addFeedTime(23, 12, 2);
  // addFeedTime(21, 13, 3);
  // addFeedTime(21, 14, 4);
  // addFeedTime(21, 15, 3);

  // publishFeedSchedule();
  mqttConnect();
  mqttClient.publish("/23127138/GetSchedule", "");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Reconnecting to WiFi");
    wifiConnect();
  }
  if(!mqttClient.connected()) {
    mqttConnect();
  }
  mqttClient.loop();

  DateTime now = rtc.now();

  // Hiển thị thời gian lên LCD
  lcd.setCursor(0, 0);
  lcd.printf("%02d/%02d, %s %02d:%02d:%02d",
              now.day(), now.month(), daysOfTheWeek[now.dayOfTheWeek()],
              now.hour(), now.minute(), now.second());

  // Hiển thị mức thức ăn
  if (millis() - lastMeasureTime >= 100) {
    distance = readDistance();
    distance = min(distance, max_distance);
    lastMeasureTime = millis();
  }
  float FoodLevel = (1.0 -  (float(distance) / max_distance)) * 100;
  char FoodLevelStr[10];
  dtostrf(FoodLevel, 4, 2, FoodLevelStr);
  mqttClient.publish("/23127138/FoodLevel", FoodLevelStr);
  lcd.setCursor(0, 1);
  lcd.print("Food Level: ");
  lcd.print(FoodLevel, 2); 
  lcd.print("% ");
  

  // Kiểm tra nút nhấn cho ăn
  if (digitalRead(BUTTON_PIN) == LOW && !feeding) {
    while (digitalRead(BUTTON_PIN) == LOW);  // chờ nhả nút
    feeding = true;

    float level = readFoodLevelPercent();
    if (level < 90.0) {
      feedCat(now.hour(), now.minute(), now.second());
      addFoodLog(level);             // thêm vào mảng log
      sendFoodLevelToChartHistory(); // gửi toàn bộ mảng lên topic
    } else {
      lcd.setCursor(0, 2);
      lcd.print("Đủ đồ ăn, không cho");
      Serial.println("Không cho ăn - Đồ ăn > 90%");
    }
  }


  // Reset lại biến khi sang phút mới
  if (now.minute() != lastMinute) {
    alreadyFed = false;
    lastMinute = now.minute();
  }

  // Kiểm tra lịch cho ăn tự động
  for (int i = 0; i < feedCount; i++) {
    if (now.hour() == FeedSchedule[i].hour &&
        now.minute() == FeedSchedule[i].minute &&
        !alreadyFed) {

      float level = readFoodLevelPercent();
      if (level < 90.0) {
        feeding = true;
        feedCat(now.hour(), now.minute(), now.second(), FeedSchedule[i].duration);
        addFoodLog(level);             // thêm vào mảng log
        sendFoodLevelToChart(level);  // chỉ gửi khi có cho ăn
      } else {
        lcd.setCursor(0, 2);
        lcd.print("Đủ đồ ăn, không cho");
        Serial.println("Không cho ăn (tự động) - Đồ ăn > 90%");
      }

      alreadyFed = true;
    }
  }


  // delay(500);
  feeding = false;
}




