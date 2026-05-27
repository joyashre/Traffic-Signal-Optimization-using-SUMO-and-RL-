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

class SmartFullMapEnv(gym.Env):
    """Full Map PPO Environment with Advanced Wait-Time & Emergency Logic"""
    def __init__(self):
        super(SmartFullMapEnv, self).__init__()
        
        self.sumo_cmd = [
            "sumo", "-c", "osm.sumocfg",
            "--tripinfo-output", "with_rl_tripinfo.xml",
            "--summary-output", "with_rl_summary.xml",
            "--device.emissions.probability", "1.0"
        ]
        
        traci.start(self.sumo_cmd)
        self.tls_ids = traci.trafficlight.getIDList()
        self.num_lights = len(self.tls_ids)
        traci.close()
        
        print(f"🌍 Initiating Smart Control for {self.num_lights} Signals across the Map!")

        # Action Space: AI choosing phases for ALL traffic lights
        self.action_space = spaces.MultiDiscrete([4] * self.num_lights)
        
        # Observation Space: Har signal ke liye 2 cheezein (Queue Length, Max Wait Time)
        self.observation_space = spaces.Box(
            low=0, high=2000, shape=(self.num_lights * 2,), dtype=np.float32
        )
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
        """AI ko bheed aur wait time dono batana zaroori hai"""
        obs = []
        for tls in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls)
            queue = 0
            max_wait_time = 0
            
            for lane in set(lanes):
                queue += traci.lane.getLastStepHaltingNumber(lane)
                
                # Us intersection par sabse zyada der se ruki gaadi ka wait time nikalna
                vehicles = traci.lane.getLastStepVehicleIDs(lane)
                for v in vehicles:
                    wt = traci.vehicle.getWaitingTime(v)
                    if wt > max_wait_time:
                        max_wait_time = wt
                        
            obs.extend([queue, max_wait_time])
            
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        # 1. Apply Actions safely
        for i, tls in enumerate(self.tls_ids):
            num_phases = len(traci.trafficlight.getCompleteRedYellowGreenDefinition(tls)[0].phases)
            safe_action = action[i] % num_phases
            traci.trafficlight.setPhase(tls, safe_action)
            
        # 2. Advance Simulation
        for _ in range(10):
            traci.simulationStep()
            self.step_count += 1
            
        # 3. Get New State
        obs = self._get_obs()
        
        # 4. 🌟 ULTIMATE SMART REWARD FOR FULL MAP 🌟
        reward = 0
        current_time = traci.simulation.getTime()
        is_raining = current_time > 1000 
        
        for tls in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls)
            for lane in set(lanes):
                vehicles = traci.lane.getLastStepVehicleIDs(lane)
                for v in vehicles:
                    try:
                        wait_time = traci.vehicle.getWaitingTime(v)
                        co2_emission = traci.vehicle.getCO2Emission(v) / 1000.0
                        v_class = traci.vehicle.getVehicleClass(v)

                        # Dynamic Weather Effect
                        if is_raining:
                            traci.vehicle.setSignals(v, 1)
                            traci.vehicle.setMaxSpeed(v, 8.0)

                        # Exponential Ambulance Priority
                        if v_class == "emergency":
                            if wait_time > 0:
                                reward -= (wait_time * 100) 
                        # Normal Traffic Wait Time & Emissions
                        else:
                            if wait_time > 0:
                                reward -= wait_time
                            reward -= (co2_emission * 0.5)
                    except Exception:
                        pass

        done = self.step_count >= 3600
        truncated = False
        return obs, float(reward), done, truncated, {}

    def close(self):
        traci.close()

if __name__ == "__main__":
    env = SmartFullMapEnv()
    
    # Advanced PPO setup adapted from your second model
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, ent_coef=0.05, batch_size=256, n_steps=1024)
    
    print("⏳ Training Ultimate Full Map Agent...")
    # Training for a longer duration is required for full map complexity
    model.learn(total_timesteps=50000) 
    
    model.save("ppo_fullmap_ultimate_model")
    env.close()
    print("✅ Training Complete!")