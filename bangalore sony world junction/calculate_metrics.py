import xml.etree.ElementTree as ET
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
        return []
    tree = ET.parse(file_path)
    queues = []
    for step in tree.getroot().findall('step'):
        queues.append(int(step.get('halting')))
    return np.array(queues)

def calculate_percentage(old_val, new_val):
    if old_val == 0: return 0.0
    return ((old_val - new_val) / old_val) * 100

def generate_report():
    print("📊 Calculating Performance Metrics...\n")
    
    # 1. Data Load Karna
    df_base = parse_tripinfo('baseline_tripinfo.xml')
    df_rl = parse_tripinfo('with_rl_tripinfo.xml')
    
    q_base = parse_summary('baseline_summary.xml')
    q_rl = parse_summary('with_rl_summary.xml')
    
    if df_base.empty or df_rl.empty or len(q_base)==0 or len(q_rl)==0:
        print("Error: Files nahi mili! Ensure dono (baseline aur rl) run complete ho gaye hain.")
        return

    # 2. Calculations
    # Queue Length & MSE (Assuming ideal queue is 0, MSE = mean of squared queues)
    avg_q_base = np.mean(q_base)
    avg_q_rl = np.mean(q_rl)
    
    mse_base = np.mean(q_base ** 2)
    mse_rl = np.mean(q_rl ** 2)
    
    # Waiting Time
    wait_base = df_base['waitingTime'].mean()
    wait_rl = df_rl['waitingTime'].mean()
    
    # Ambulance Waiting Time
    amb_base = df_base[df_base['vType'].str.contains('ambulance', case=False)]['waitingTime'].mean()
    amb_rl = df_rl[df_rl['vType'].str.contains('ambulance', case=False)]['waitingTime'].mean()
    if pd.isna(amb_base): amb_base = 0
    if pd.isna(amb_rl): amb_rl = 0
    
    # CO2 Emission
    co2_base = df_base['CO2_kg'].sum()
    co2_rl = df_rl['CO2_kg'].sum()

    # 3. Generating Report String
    report = f"""
=========================================================
      🚦 AI TRAFFIC OPTIMIZATION RESULTS (SONY WORLD)
=========================================================

1. QUEUE LENGTH (Traffic Jam)
   - Without AI : {avg_q_base:.2f} vehicles (Average)
   - With PPO AI: {avg_q_rl:.2f} vehicles (Average)
   => IMPROVEMENT : {calculate_percentage(avg_q_base, avg_q_rl):.2f}% Reduce hua!

2. QUEUE MSE (Mean Squared Error - Penalizing large jams)
   - Without AI : {mse_base:.2f}
   - With PPO AI: {mse_rl:.2f}
   => MSE REDUCTION : {calculate_percentage(mse_base, mse_rl):.2f}% Reduce hua!

3. AVERAGE WAITING TIME (Sabhi gaadiyon ka)
   - Without AI : {wait_base:.2f} Seconds
   - With PPO AI: {wait_rl:.2f} Seconds
   => IMPROVEMENT : {calculate_percentage(wait_base, wait_rl):.2f}% Time bacha!

4. AMBULANCE WAITING TIME (Emergency Priority)
   - Without AI : {amb_base:.2f} Seconds
   - With PPO AI: {amb_rl:.2f} Seconds
   => IMPROVEMENT : {calculate_percentage(amb_base, amb_rl):.2f}% Faster Clearance!

5. TOTAL CO2 EMISSIONS (Pollution)
   - Without AI : {co2_base:.2f} kg
   - With PPO AI: {co2_rl:.2f} kg
   => IMPROVEMENT : {calculate_percentage(co2_base, co2_rl):.2f}% Pollution kam hua!

=========================================================
    """
    
    # Print to Terminal
    print(report)
    
    # Save to Text File
    with open('results_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("✅ Result perfectly calculated! 'results_report.txt' file save ho gayi hai.")

if __name__ == "__main__":
    generate_report()