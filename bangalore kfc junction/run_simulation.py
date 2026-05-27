import os
import sys

# 1. SUMO aur Python ko jodne wali library
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

# 2. SUMO Config file ka naam
sumoCmd = ["sumo-gui", "-c", "osm.sumocfg"]

def start_simulation():
    # Ye line code ke through aapka SUMO map open karegi
    traci.start(sumoCmd)
    print("Python se SUMO GUI open ho gaya!")

    step = 0
    # Simulation Loop
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep() # Ek second aage badhana
        
        # Har 100 step par console mein print karna
        if step % 100 == 0:
            print(f"Simulation Step: {step}")
            
        step += 1
        
        # 3600 steps (1 ghanta) ke baad rok dena
        if step > 3600:
            break

    traci.close()
    print("Simulation Khatam.")

if __name__ == "__main__":
    start_simulation()