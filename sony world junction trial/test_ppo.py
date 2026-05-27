import traci
import time
from stable_baselines3 import PPO

# Aapki training file (train_ppo.py) se naya smart environment import kar rahe hain
from train_ppo import SmartFullMapEnv 

def test_model():
    print("🚦 SUMO GUI shuru ho raha hai... AI model load ho raha hai.")
    
    # 1. Environment initialize karna
    env = SmartFullMapEnv()
    
    # 2. 🌟 SMART TRICK: Env ke andar CLI ("sumo") ko GUI ("sumo-gui") se replace karna
    env.sumo_cmd = [
        "sumo-gui", "-c", "osm.sumocfg",
        "--start", # Automatically start ho jayega
        "--device.emissions.probability", "1.0"
    ]
    
    # 3. Naya Smart Model load karna
    print("🧠 Trained Ultimate Model load ho raha hai...")
    model = PPO.load("ppo_fullmap_ultimate_model")
    
    # 4. Environment reset karna (Yeh automatically sumo-gui ko start kar dega)
    obs, _ = env.reset()
    done = False
    
    print("🚗 Simulation chalu ho gaya hai! AI signals control kar raha hai...")
    
    while not done:
        # AI se action poochna (deterministic=True ka matlab AI best decision lega bina random soche)
        action, _states = model.predict(obs, deterministic=True)
        
        # Action apply karna map par
        obs, reward, done, truncated, info = env.step(action)
        
        # Speed control (taaki gaadiyan aaram se observe kar sakein)
        time.sleep(0.05) # Speed adjust karne ke liye isko 0.1 ya 0.2 kar sakti hain
        
    print("✅ Simulation khatam!")
    env.close()

if __name__ == "__main__":
    test_model()