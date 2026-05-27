import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd
import os

def generate_graphs():
    print("Reading SUMO Output files...")
    
    # 1. Parsing Tripinfo Data (Waiting Time & CO2)
    tripinfo_file = 'tripinfos.xml'
    summary_file = 'summary.xml'
    
    if not os.path.exists(tripinfo_file) or not os.path.exists(summary_file):
        print("Error: tripinfos.xml ya summary.xml nahi mili. Pehle simulation ko pura run hone dein.")
        return

    tree = ET.parse(tripinfo_file)
    root = tree.getroot()
    
    data = []
    for trip in root.findall('tripinfo'):
        vType = trip.get('vType')
        waitingTime = float(trip.get('waitingTime'))
        
        # CO2 data nikalna (mg se kg mein convert kar rahe hain)
        emissions = trip.find('emissions')
        co2 = float(emissions.get('CO2_abs')) / 1000000 if emissions is not None else 0.0
        
        data.append({'vType': vType, 'waitingTime': waitingTime, 'CO2_kg': co2})
        
    df = pd.DataFrame(data)

    # 2. Parsing Summary Data (Queue Length over time)
    sum_tree = ET.parse(summary_file)
    sum_root = sum_tree.getroot()
    
    time_steps = []
    queue_length = [] # Halting vehicles (ruki hui gadiyan)
    
    for step in sum_root.findall('step'):
        time_steps.append(float(step.get('time')))
        queue_length.append(int(step.get('halting')))

    print("Data processed. Generating Graphs...")

    # ==========================================
    # GRAPH 1: Average Waiting Time (All Vehicles)
    # ==========================================
    plt.figure(figsize=(10, 6))
    avg_wait = df.groupby('vType')['waitingTime'].mean()
    avg_wait.plot(kind='bar', color=['red', 'orange', 'blue', 'green', 'grey'])
    plt.title('Average Waiting Time by Vehicle Type (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Average Waiting Time (seconds)', fontsize=12)
    plt.xlabel('Vehicle Type', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('waiting_time_without_rl.png', dpi=300)
    plt.close()

    # ==========================================
    # GRAPH 2: Ambulance Waiting Time
    # ==========================================
    plt.figure(figsize=(6, 6))
    ambulance_data = df[df['vType'].str.contains('ambulance', case=False)]
    if not ambulance_data.empty:
        plt.boxplot(ambulance_data['waitingTime'], patch_artist=True, boxprops=dict(facecolor='red'))
        plt.title('Ambulance Waiting Time (Without RL)', fontsize=14, fontweight='bold')
        plt.ylabel('Waiting Time (seconds)', fontsize=12)
        plt.xticks([1], ['Ambulance'])
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('ambulance_waiting_time_without_rl.png', dpi=300)
    else:
        print("Ambulance data nahi mila.")
    plt.close()

    # ==========================================
    # GRAPH 3: Queue Length Over Time
    # ==========================================
    plt.figure(figsize=(12, 6))
    plt.plot(time_steps, queue_length, color='purple', linewidth=2)
    plt.title('Total Traffic Queue / Halting Vehicles Over Time (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Halting Vehicles', fontsize=12)
    plt.xlabel('Simulation Time (seconds)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.fill_between(time_steps, queue_length, color='purple', alpha=0.2)
    plt.tight_layout()
    plt.savefig('queue_length_without_rl.png', dpi=300)
    plt.close()

    # ==========================================
    # GRAPH 4: CO2 Emissions
    # ==========================================
    plt.figure(figsize=(10, 6))
    total_co2 = df.groupby('vType')['CO2_kg'].sum()
    total_co2.plot(kind='bar', color='darkgray', edgecolor='black')
    plt.title('Total CO2 Emissions by Vehicle Type (Without RL)', fontsize=14, fontweight='bold')
    plt.ylabel('Total CO2 Emission (Kilograms)', fontsize=12)
    plt.xlabel('Vehicle Type', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('co2_emission_without_rl.png', dpi=300)
    plt.close()

    print("Success! 4 Graphs successfully folder mein save ho gaye hain:")
    print(" 1. waiting_time_without_rl.png")
    print(" 2. ambulance_waiting_time_without_rl.png")
    print(" 3. queue_length_without_rl.png")
    print(" 4. co2_emission_without_rl.png")

if __name__ == "__main__":
    generate_graphs()