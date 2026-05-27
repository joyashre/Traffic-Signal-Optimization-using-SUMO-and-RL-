import traci
from stable_baselines3 import PPO
from train_ppo import SumoFullMapEnv # Aapki purani env class load kar rahe hain

def test_model():
    print("🚦 SUMO GUI shuru ho raha hai... AI model load ho raha hai.")
    
    # Environment initialize karna (is baar GUI ke sath)
    env = SumoFullMapEnv()
    # PPO script mein sumo-gui enable karne ke liye manually start karte hain
    traci.start(["sumo-gui", "-c", "osm.sumocfg", "--start"])
    
    # Trained model load karna
    model = PPO.load("ppo_sumo_model")
    
    obs, _ = env.reset()
    done = False
    
    while not done:
        # AI se action poochna
        action, _states = model.predict(obs, deterministic=True)
        
        # Action apply karna
        obs, reward, done, truncated, info = env.step(action)
        
        # Speed control (taki aap aaram se dekh sakein)
        traci.simulation.setDeltaT(0.1) 
        
    print("Simulation khatam!")
    env.close()

if __name__ == "__main__":
    test_model()