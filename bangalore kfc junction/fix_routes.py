import os

# 1. Total gaadiyan jo humne kaggle dataset se scale down ki thi (approx 3081)
total_vehicles = 3081
simulation_time = 3600 # 1 ghanta

# 2. Har kitne second mein 1 gaadi aani chahiye? (Interval)
interval = simulation_time / total_vehicles

# 3. SUMO_HOME path nikalna
sumo_home = os.environ.get('SUMO_HOME')
if not sumo_home:
    sumo_home = r'C:\Program Files (x86)\Eclipse\Sumo' # Default Windows path

randomTrips = os.path.join(sumo_home, 'tools', 'randomTrips.py')

# 4. SUMO ke algorithm se Real map par Valid Routes generate karna
# -n: map file, -e: end time, -p: interval, -r: final route file
cmd = f'python "{randomTrips}" -n osm.net.xml.gz -e {simulation_time} -p {interval:.2f} -r custom_traffic.rou.xml --trip-attributes "type=\'mixedTraffic\'"'

print("Mapping realistic traffic to Indiranagar roads... Please wait 5-10 seconds.")
exit_code = os.system(cmd)

if exit_code == 0:
    print("Success! 'custom_traffic.rou.xml' ab valid map roads ke sath update ho gayi hai.")
else:
    print("Kuch issue aaya. Path check kijiye.")