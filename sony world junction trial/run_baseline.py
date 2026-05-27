import os
import sys
import traci
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd

# SUMO path setup
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: SUMO_HOME environment variable set nahi hai.")

def run_simulation():
    print("🚦 Starting Simulation WITHOUT RL (Baseline)... Please wait.")
    
    # SUMO ko bina GUI ke run kar rahe hain taaki fast ho, aur output files generate ho
    sumo_cmd = [
        "sumo", # Agar aapko chalte hue dekhna hai toh "sumo-gui" likh dein
        "-c", "osm.sumocfg",
        "--tripinfo-output", "baseline_tripinfo.xml",
        "--summary-output", "baseline_summary.xml",
        "--device.emissions.probability", "1.0" # CO2 measure karne ke liye zaroori
    ]
    
    traci.start(sumo_cmd)
    
    step = 0
    while step < 3600: # 1 Ghante ka simulation
        traci.simulationStep()
        
        # Har 500 step par progress print karega
        if step % 500 == 0:
            print(f"Simulation Progress: {step}/3600 seconds...")
            
        step += 1
        
    traci.close()
    print("✅ Simulation Complete! Data saved to XML files.\n")

def generate_graphs():
    print("📊 Generating Graphs...")
    
    tripinfo_file = 'baseline_tripinfo.xml'
    summary_file = 'baseline_summary.xml'
    
    if not os.path.exists(tripinfo_file) or not os.path.exists(summary_file):
        print("Error: Output files nahi mili.")
        return

    # 1. Parsing Tripinfo (Waiting Time & CO2)
    tree = ET.parse(tripinfo_file)
    root = tree.getroot()
    
    data = []
    for trip in root.findall('tripinfo'):
        vType = trip.get('vType')
        waitingTime = float(trip.get('waitingTime'))
        
        emissions = trip.find('emissions')
        co2_kg = float(emissions.get('CO2_abs')) / 1000000 if emissions is not None else 0.0
        
        data.append({'vType': vType, 'waitingTime': waitingTime, 'CO2_kg': co2_kg})
        
    df = pd.DataFrame(data)

    # 2. Parsing Summary Data (Queue Length)
    sum_tree = ET.parse(summary_file)
    sum_root = sum_tree.getroot()
    
    time_steps = []
    queue_length = []
    for step in sum_root.findall('step'):
        time_steps.append(float(step.get('time')))
        queue_length.append(int(step.get('halting'))) # Halting = ruki hui gaadiyan (Jam)

    # --- GRAPH 1: Average Waiting Time ---
    plt.figure(figsize=(10, 6))
    avg_wait = df.groupby('vType')['waitingTime'].mean()
    avg_wait.plot(kind='bar', color=['red', 'orange', 'blue', 'green', 'grey'])
    plt.title('Average Waiting Time by Vehicle Type (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Average Waiting Time (seconds)')
    plt.xlabel('Vehicle Type')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('baseline_waiting_time.png', dpi=300)
    plt.close()

    # --- GRAPH 2: CO2 Emissions ---
    plt.figure(figsize=(10, 6))
    total_co2 = df.groupby('vType')['CO2_kg'].sum()
    total_co2.plot(kind='bar', color='darkgray', edgecolor='black')
    plt.title('Total CO2 Emissions by Vehicle Type (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Total CO2 Emission (kg)')
    plt.xlabel('Vehicle Type')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('baseline_co2_emission.png', dpi=300)
    plt.close()

    # --- GRAPH 3: Queue Length (Jam) ---
    plt.figure(figsize=(12, 6))
    plt.plot(time_steps, queue_length, color='purple', linewidth=2)
    plt.fill_between(time_steps, queue_length, color='purple', alpha=0.2)
    plt.title('Traffic Queue Length Over Time (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Halting Vehicles')
    plt.xlabel('Simulation Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('baseline_queue_length.png', dpi=300)
    plt.close()

    print("🎉 Success! 3 High-Quality Graphs saved in your folder:")
    print(" 1. baseline_waiting_time.png")
    print(" 2. baseline_co2_emission.png")
    print(" 3. baseline_queue_length.png")

if __name__ == "__main__":
    run_simulation()
    generate_graphs()