import requests
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# CITY CONFIGURATION
# ==============================
CITY = "Thanjavur"

# ==============================
# PUBLIC WEATHER API (NO KEY)
# ==============================
url = f"https://wttr.in/{CITY}?format=j1"
response = requests.get(url)
data = response.json()

# ==============================
# DATA EXTRACTION
# ==============================
current = data["current_condition"][0]

temperature = float(current["temp_C"])
humidity = float(current["humidity"])
wind_speed = float(current["windspeedKmph"])

labels = ["Temperature (°C)", "Humidity (%)", "Wind Speed (km/h)"]
values = [temperature, humidity, wind_speed]

# ==============================
# DATA VISUALIZATION
# ==============================
sns.set(style="whitegrid")
plt.figure(figsize=(8, 5))

sns.barplot(x=labels, y=values)

plt.title(f"Weather Dashboard for {CITY}", fontsize=14)
plt.xlabel("Weather Parameters")
plt.ylabel("Values")

plt.tight_layout()

# SAVE GRAPH FOR SUBMISSION
plt.savefig("thanjavur_weather_dashboard.png")

# SHOW GRAPH
plt.show()
