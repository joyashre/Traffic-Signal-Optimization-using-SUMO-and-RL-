import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import traci

# SUMO Path Setup
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

sumoCmd = ["sumo", "-c", "osm.sumocfg"]

def collect_full_baseline():
    traci.start(sumoCmd)
    data = []
    print("📊 Collecting Detailed Baseline (Wait, Queue, CO2, Ambulance)...")

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0 and step < 3600:
        traci.simulationStep()
        
        if step % 10 == 0:
            vehicles = traci.vehicle.getIDList()
            
            total_wait = 0
            amb_wait = 0
            total_co2 = 0
            queue_length = 0
            
            for v in vehicles:
                v_type = traci.vehicle.getTypeID(v)
                v_wait = traci.vehicle.getWaitingTime(v)
                v_speed = traci.vehicle.getSpeed(v)
                
                # 1. Total Wait Time
                total_wait += v_wait
                
                # 2. Ambulance Only Wait Time
                if "ambulance" in v_type:
                    amb_wait += v_wait
                
                # 3. CO2 Emissions (mg to grams)
                total_co2 += traci.vehicle.getCO2Emission(v) / 1000
                
                # 4. Queue Length (vehicles moving slower than 0.1 m/s)
                if v_speed < 0.1:
                    queue_length += 1
            
            data.append({
                "Step": step, 
                "Total_Wait": total_wait, 
                "Ambulance_Wait": amb_wait,
                "CO2": total_co2,
                "Queue": queue_length
            })
            
        step += 1

    traci.close()
    df = pd.DataFrame(data)
    df.to_csv("detailed_baseline.csv", index=False)
    
    # --- Professional Visualization for Thesis ---
    plt.figure(figsize=(15, 10))

    # Plot 1: Total Waiting Time
    plt.subplot(2, 2, 1)
    plt.plot(df["Total_Wait"], color='blue')
    plt.title("Baseline: Total Waiting Time (All Vehicles)")
    plt.ylabel("Seconds")

    # Plot 2: Ambulance Delay
    plt.subplot(2, 2, 2)
    plt.plot(df["Ambulance_Wait"], color='red', linewidth=2)
    plt.title("Baseline: Emergency Vehicle Delay")
    plt.ylabel("Seconds")

    # Plot 3: CO2 Emissions
    plt.subplot(2, 2, 3)
    plt.plot(df["CO2"], color='green')
    plt.title("Baseline: CO2 Emissions")
    plt.ylabel("Grams (g)")

    # Plot 4: Queue Length
    plt.subplot(2, 2, 4)
    plt.plot(df["Queue"], color='orange')
    plt.title("Baseline: Total Queue Length")
    plt.ylabel("Number of Vehicles")

    plt.tight_layout()
    plt.savefig("full_baseline_performance.png")
    print("✅ Success! 'full_baseline_performance.png' and 'detailed_baseline.csv' are ready.")

if __name__ == "__main__":
    collect_full_baseline()