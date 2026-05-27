import os
import sys
import traci
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

# SUMO Path Setup
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: SUMO_HOME set nahi hai.")

class SumoFullMapEnv(gym.Env):
    """Custom Environment jo poore map ke traffic lights ko PPO se connect karega"""
    def __init__(self):
        super(SumoFullMapEnv, self).__init__()
        
        # SUMO run command (Without GUI for fast training)
        self.sumo_cmd = [
            "sumo", "-c", "osm.sumocfg",
            "--tripinfo-output", "with_rl_tripinfo.xml",
            "--summary-output", "with_rl_summary.xml",
            "--device.emissions.probability", "1.0"
        ]
        
        # Ek baar start karke signals ki details le lete hain
        traci.start(self.sumo_cmd)
        self.tls_ids = traci.trafficlight.getIDList()
        self.num_lights = len(self.tls_ids)
        traci.close()
        
        print(f"🌍 Found {self.num_lights} Traffic Signals in the Map!")

        # Action Space: AI har traffic light ke liye 1 phase choose karega (assume max 4 phases per signal)
        self.action_space = spaces.MultiDiscrete([4] * self.num_lights)
        
        # Observation Space: Har signal par ruki hui gaadiyon ka total number (Queue)
        self.observation_space = spaces.Box(low=0, high=1000, shape=(self.num_lights,), dtype=np.float32)
        
        self.step_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        try:
            traci.close()
        except:
            pass
        
        traci.start(self.sumo_cmd)
        self.step_count = 0
        return self._get_obs(), {}

    def _get_obs(self):
        """AI ko batata hai ki har signal par kitni bheed hai"""
        obs = []
        for tls in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls)
            queue = sum([traci.lane.getLastStepHaltingNumber(lane) for lane in set(lanes)])
            obs.append(queue)
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        """AI ka decision apply karna aur Custom Reward calculate karna"""
        
        # 1. AI ne jo action diya, usko traffic lights par apply karna
        for i, tls in enumerate(self.tls_ids):
            # Error se bachne ke liye safe phase calculate karna
            num_phases = len(traci.trafficlight.getCompleteRedYellowGreenDefinition(tls)[0].phases)
            safe_action = action[i] % num_phases
            traci.trafficlight.setPhase(tls, safe_action)
            
        # 2. Simulation ko 10 second aage badhana (AI har 10 sec mein sochega)
        for _ in range(10):
            traci.simulationStep()
            self.step_count += 1
            
        # 3. Naya State (Observation)
        obs = self._get_obs()
        
        # 4. CUSTOM REWARD CALCULATION (Aapki Requirement!)
        reward = 0
        for tls in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls)
            for lane in set(lanes):
                # Penalty 1: Queue kam karo
                reward -= traci.lane.getLastStepHaltingNumber(lane) * 0.5 
                
                # Penalty 2: CO2 Emission kam karo
                reward -= (traci.lane.getCO2Emission(lane) / 100000) 
                
                # Penalty 3: Emergency Vehicle Priority (V.IMP)
                for veh in traci.lane.getLastStepVehicleIDs(lane):
                    if traci.vehicle.getVehicleClass(veh) == "emergency" and traci.vehicle.getSpeed(veh) < 1.0:
                        reward -= 100  # Ambulance ruki hui hai, HUGE Penalty!

        # 5. Check if simulation is done (1 hour = 3600 seconds)
        done = self.step_count >= 3600
        truncated = False
        
        return obs, float(reward), done, truncated, {}

    def close(self):
        traci.close()

if __name__ == "__main__":
    print("🚀 Initializing Custom SUMO Environment for PPO...")
    env = SumoFullMapEnv()
    
    print("🧠 Building PPO Model...")
    # PPO model setup with Multi-Layer Perceptron (MlpPolicy)
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)
    
    print("⏳ Training AI Model (This will take a few minutes)...")
    # Training for 10,000 timesteps (Aap isko 50000+ kar sakti hain final result ke liye)
    model.learn(total_timesteps=10000)
    
    print("💾 Saving Trained Model...")
    model.save("ppo_sumo_model")
    
    env.close()
    print("✅ Training Complete! 'with_rl_tripinfo.xml' aur 'with_rl_summary.xml' save ho gaye hain.")