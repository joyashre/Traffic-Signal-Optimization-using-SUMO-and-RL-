import pandas as pd
import os

# 1. Dataset Read Karna (Ensure karein ki dataset aapke folder mein ho)
try:
    df = pd.read_csv('Koramangala_Sony_World_Junction.csv')
    # Aap jis area ka map le rahe hain, uska data filter karein (e.g., Koramangala)
    area_data = df[df['Area Name'].str.contains('Koramangala', case=False, na=False)]
    
    if area_data.empty:
        print("Data nahi mila! Default volume use kar rahe hain.")
        hourly_volume = 3000
    else:
        # Ek road ka average nikal kar use poore map ke hisab se scale karna
        # (Kyunki ek road pe 1700 thi, toh poore map mein kam se kam 5-6 main roads hongi)
        avg_one_road = int(area_data['Traffic Volume'].mean() / 24)
        hourly_volume = avg_one_road * 5 # Map ko bharne ke liye multiplier
        print(f"Dataset se calculated Total Hourly Volume: {hourly_volume}")

except FileNotFoundError:
    print("CSV file nahi mili! Default 5000 volume use kar rahe hain.")
    hourly_volume = 5000

# 2. Interval Calculate Karna
simulation_time = 3600 # 1 ghanta (seconds mein)
interval = simulation_time / hourly_volume
print(f"Har {interval:.2f} seconds mein ek gaadi enter karegi poore map mein kahin se.")

# 3. SUMO HOME Path aur randomTrips tool nikalna
sumo_home = os.environ.get('SUMO_HOME')
if not sumo_home:
    sumo_home = r'C:\Program Files (x86)\Eclipse\Sumo' # Default Windows path check karein

randomTrips = os.path.join(sumo_home, 'tools', 'randomTrips.py')

# 4. randomTrips Command Run Karna
# -n: map file | -e: end time | -p: interval | -r: output route file | --additional-files: vTypes link karne ke liye
cmd = f'python "{randomTrips}" -n osm.net.xml.gz -e {simulation_time} -p {interval:.2f} -r full_map_traffic.rou.xml --trip-attributes "type=\'mixedTraffic\'" --additional-files vehicles.add.xml'

print("\nGaadiyon ko poore map par distribute kiya ja raha hai... Please wait.")
exit_code = os.system(cmd)

if exit_code == 0:
    print("\nSuccess! 'full_map_traffic.rou.xml' file ban gayi hai. Isme saari gaadiyan hain!")
else:
    print("\nError: Kuch issue aaya. Ensure karein ki SUMO_HOME environment variable set hai.")