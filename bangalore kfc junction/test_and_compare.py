import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment
import traci

# SUMO Path Setup
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

# 1. Wahi purana Reward Function (AI ko yaad dilane ke liye)
def ultimate_smart_reward(traffic_signal):
    total_penalty = 0
    current_time = traci.simulation.getTime()
    is_raining = current_time > 1000 
    lanes = traffic_signal.lanes 

    for lane in lanes:
        vehicles = traci.lane.getLastStepVehicleIDs(lane)
        for v in vehicles:
            try:
                v_type = traci.vehicle.getTypeID(v)
                speed = traci.vehicle.getSpeed(v)
                co2_emission = traci.vehicle.getCO2Emission(v) / 1000.0 

                if is_raining:
                    traci.vehicle.setSignals(v, 1)
                    traci.vehicle.setMaxSpeed(v, 8.0)

                if "ambulance" in v_type:
                    if speed < 2.0: 
                        total_penalty -= 2000 
                else:
                    if speed < 2.0: 
                        total_penalty -= 1 
                    total_penalty -= (co2_emission * 0.5)
            except:
                pass
    return total_penalty

def test_model_and_generate_graphs():
    print("🚀 Trained AI Model Load ho raha hai...")
    
    # 2. Environment Setup (is baar use_gui=True for Video Recording!)
    env = SumoEnvironment(
        net_file='osm.net.xml.gz',
        route_file='custom_traffic.rou.xml',
        out_csv_name='test_rl',
        use_gui=True,   # 🌟 GUI ON for Presentation
        num_seconds=3600,
        reward_fn=ultimate_smart_reward,
        additional_sumo_cmd="--additional-files vehicle_types.xml",
        single_agent=True
    )

    # 3. Model Load karna (Jo abhi train hua hai)
    model = PPO.load("ppo_ultimate_thesis_model")
    obs, info = env.reset()
    
    done = False
    rl_data = []

    print("🚦 Simulation Start! Aap Video Record kar sakte hain...")
    
    # 4. Simulation Loop (AI Action le raha hai)
    while not done:
        # AI decide karega light red karni hai ya green
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        current_time = traci.simulation.getTime()
        
        # Data Collect karna (har 10 second mein)
        if int(current_time) % 10 == 0:
            try:
                vehicles = traci.vehicle.getIDList()
                total_wait = 0
                amb_wait = 0
                total_co2 = 0
                queue_length = 0
                
                for v in vehicles:
                    v_type = traci.vehicle.getTypeID(v)
                    v_wait = traci.vehicle.getWaitingTime(v)
                    v_speed = traci.vehicle.getSpeed(v)
                    
                    total_wait += v_wait
                    if "ambulance" in v_type:
                        amb_wait += v_wait
                    total_co2 += traci.vehicle.getCO2Emission(v) / 1000
                    if v_speed < 0.1:
                        queue_length += 1
                        
                rl_data.append({
                    "Time": current_time, 
                    "Total_Wait": total_wait, 
                    "Ambulance_Wait": amb_wait,
                    "CO2": total_co2,
                    "Queue": queue_length
                })
            except:
                pass

    env.close()

    # 5. Save Data aur Compare karna
    print("📊 Data Collect ho gaya. Ab Graphs ban rahe hain...")
    df_rl = pd.DataFrame(rl_data)
    df_rl.to_csv("detailed_rl_results.csv", index=False)

    try:
        df_base = pd.read_csv("detailed_baseline.csv")
        
        plt.figure(figsize=(15, 10))

        # Wait Time Compare
        plt.subplot(2, 2, 1)
        plt.plot(df_base["Step"], df_base["Total_Wait"], color='red', label='Without RL', alpha=0.6)
        plt.plot(df_rl["Time"], df_rl["Total_Wait"], color='green', label='With SOTA RL', linewidth=2)
        plt.title("Total Waiting Time Reduction")
        plt.legend()

        # Ambulance Delay Compare
        plt.subplot(2, 2, 2)
        plt.plot(df_base["Step"], df_base["Ambulance_Wait"], color='red', label='Without RL', alpha=0.6)
        plt.plot(df_rl["Time"], df_rl["Ambulance_Wait"], color='blue', label='With SOTA RL (Priority)', linewidth=2)
        plt.title("Ambulance Delay (Emergency Preemption)")
        plt.legend()

        # CO2 Compare
        plt.subplot(2, 2, 3)
        plt.plot(df_base["Step"], df_base["CO2"], color='red', label='Without RL', alpha=0.6)
        plt.plot(df_rl["Time"], df_rl["CO2"], color='green', label='With SOTA RL', linewidth=2)
        plt.title("CO2 Emissions (Eco-Routing)")
        plt.legend()

        # Queue Compare
        plt.subplot(2, 2, 4)
        plt.plot(df_base["Step"], df_base["Queue"], color='red', label='Without RL', alpha=0.6)
        plt.plot(df_rl["Time"], df_rl["Queue"], color='green', label='With SOTA RL', linewidth=2)
        plt.title("Intersection Queue Length")
        plt.legend()

        plt.tight_layout()
        plt.savefig("FINAL_THESIS_COMPARISON.png")
        print("✅ SUCCESS! 'FINAL_THESIS_COMPARISON.png' ban gaya hai. Aapka project complete hua!")
    except Exception as e:
        print(f"Graph banane mein error (Baseline file missing hogi): {e}")

if __name__ == "__main__":
    test_model_and_generate_graphs()