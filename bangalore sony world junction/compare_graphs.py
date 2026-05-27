import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def parse_tripinfo(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    tree = ET.parse(file_path)
    data = []
    for trip in tree.getroot().findall('tripinfo'):
        vType = trip.get('vType')
        wait_time = float(trip.get('waitingTime'))
        co2 = float(trip.find('emissions').get('CO2_abs')) / 1000000 if trip.find('emissions') is not None else 0.0
        data.append({'vType': vType, 'waitingTime': wait_time, 'CO2_kg': co2})
    return pd.DataFrame(data)

def parse_summary(file_path):
    if not os.path.exists(file_path):
        return [], []
    tree = ET.parse(file_path)
    times, queues = [], []
    for step in tree.getroot().findall('step'):
        times.append(float(step.get('time')))
        queues.append(int(step.get('halting')))
    return times, queues

def generate_comparison():
    print("Reading Data for Comparison...")
    
    df_base = parse_tripinfo('baseline_tripinfo.xml')
    df_rl = parse_tripinfo('with_rl_tripinfo.xml')
    
    time_base, q_base = parse_summary('baseline_summary.xml')
    time_rl, q_rl = parse_summary('with_rl_summary.xml')
    
    if df_base.empty or df_rl.empty:
        print("Error: Files nahi mili! Ensure karein ki dono simulations poore ho gaye hain.")
        return

    # 1. Queue Length Comparison (Jam kitna kam hua)
    plt.figure(figsize=(12, 6))
    plt.plot(time_base, q_base, label='Without AI (Baseline)', color='red', alpha=0.7)
    plt.plot(time_rl, q_rl, label='With PPO-AI', color='green', linewidth=2)
    plt.title('Traffic Queue Length Comparison (Jam Reduction)', fontsize=14, fontweight='bold')
    plt.xlabel('Simulation Time (seconds)')
    plt.ylabel('Number of Halting Vehicles')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('Compare_Queue_Length.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Average Waiting Time Comparison
    base_wait = df_base.groupby('vType')['waitingTime'].mean()
    rl_wait = df_rl.groupby('vType')['waitingTime'].mean()
    
    x = np.arange(len(base_wait.index))
    width = 0.35
    
    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, base_wait.values, width, label='Without AI', color='salmon')
    plt.bar(x + width/2, rl_wait.values, width, label='With PPO-AI', color='lightgreen')
    plt.title('Average Waiting Time Comparison', fontsize=14, fontweight='bold')
    plt.ylabel('Waiting Time (seconds)')
    plt.xticks(x, base_wait.index, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig('Compare_Waiting_Time.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. CO2 Emission Comparison
    base_co2 = df_base.groupby('vType')['CO2_kg'].sum()
    rl_co2 = df_rl.groupby('vType')['CO2_kg'].sum()
    
    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, base_co2.values, width, label='Without AI', color='grey')
    plt.bar(x + width/2, rl_co2.values, width, label='With PPO-AI', color='skyblue')
    plt.title('CO2 Emissions Comparison (Pollution Reduction)', fontsize=14, fontweight='bold')
    plt.ylabel('Total CO2 Emitted (kg)')
    plt.xticks(x, base_co2.index, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig('Compare_CO2_Emissions.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Ambulance Priority check
    base_amb = df_base[df_base['vType'].str.contains('ambulance', case=False)]['waitingTime'].mean()
    rl_amb = df_rl[df_rl['vType'].str.contains('ambulance', case=False)]['waitingTime'].mean()
    
    plt.figure(figsize=(6, 6))
    plt.bar(['Without AI', 'With PPO-AI'], [base_amb, rl_amb], color=['red', 'green'])
    plt.title('Ambulance Average Waiting Time', fontsize=14, fontweight='bold')
    plt.ylabel('Waiting Time (seconds)')
    for i, v in enumerate([base_amb, rl_amb]):
        plt.text(i, v + 0.5, f"{v:.1f}s", ha='center', fontweight='bold')
    plt.savefig('Compare_Ambulance.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("🎉 BOOM! 4 Comparison Graphs generated successfully! Project is ready to show.")

if __name__ == "__main__":
    generate_comparison()