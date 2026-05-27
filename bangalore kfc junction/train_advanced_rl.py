import os
import sys
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment
import traci

# 1. SUMO Path Setup
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# =================================================================
# 🌟 UPDATED REWARD: BEATING 'REWARD HACKING' WITH WAIT-TIME 🌟
# =================================================================
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
                
                # 🌟 THE GAME CHANGER: Speed ki jagah hum 'Wait Time' check kar rahe hain
                wait_time = traci.vehicle.getWaitingTime(v) 
                co2_emission = traci.vehicle.getCO2Emission(v) / 1000.0 

                if is_raining:
                    traci.vehicle.setSignals(v, 1)
                    traci.vehicle.setMaxSpeed(v, 8.0)

                # --- AMBULANCE PRIORITY ---
                if "ambulance" in v_type:
                    # Agar ambulance ruki hai, toh har second penalty bhayankar badhegi!
                    if wait_time > 0:
                        total_penalty -= (wait_time * 100) # Exponential Panic for AI
                
                # --- NORMAL TRAFFIC ---
                else:
                    # Normal gaadiyon ka wait time bhi penalty badhayega (taaki light switch ho)
                    if wait_time > 0:
                        total_penalty -= wait_time 
                    
                    total_penalty -= (co2_emission * 0.5)

            except Exception as e:
                pass
            
    return total_penalty
# ==========================================
# TRAINING SETUP
# ==========================================
def train_ultimate_agent():
    print("🚀 ULTIMATE SOTA MODEL: Ambulance + Weather + CO2 Training Shuru!")
    
    env = SumoEnvironment(
        net_file='osm.net.xml.gz',
        route_file='custom_traffic.rou.xml',
        out_csv_name='ultimate_rl_results',
        use_gui=False,                      
        num_seconds=3600,                   
        reward_fn=ultimate_smart_reward,
        additional_sumo_cmd="--additional-files vehicle_types.xml",
        single_agent=True   
    )

  # ent_coef=0.05 AI ko majboor karega nayi lights try karne ke liye (Exploration)
    # batch_size=256 aur n_steps=1024 bade map ko jaldi seekhne mein madad karenge
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, ent_coef=0.05, batch_size=256, n_steps=1024)
    
    print("🚀 AI ab HARD TRAINING kar raha hai KFC Junction ke liye...")
    print("Isme kareeb 15-20 minute lagenge. Kripya wait karein...")
    
    # Timesteps ko 10,000 se badha kar 50,000 kar diya!
    model.learn(total_timesteps=50000) 
    

    model.save("ppo_ultimate_thesis_model")
    print("🎉 Ultimate Thesis Model Save ho gaya: 'ppo_ultimate_thesis_model.zip'")
    
    env.close()

if __name__ == "__main__":
    train_ultimate_agent()