# 🚦 AI-Driven Intelligent Traffic Signal Control 

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![SUMO](https://img.shields.io/badge/Eclipse_SUMO-Simulation-success)
![RL](https://img.shields.io/badge/Reinforcement_Learning-PPO-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**M.Tech Thesis Project in Artificial Intelligence** **Author:** Joyashree Mandal  
**Guide:** Arnab Chatterjee  

## 📑 Project Overview
Rapid urbanization in cities like Bangalore leads to severe traffic congestion, increasing travel time, fuel consumption, and greenhouse gas emissions. Traditional traffic lights operate on fixed timers and fail to adapt to real-time, dynamic traffic fluctuations (e.g., peak hours, emergency situations). 

This project introduces a **Deep Reinforcement Learning (DRL)** approach using the **Proximal Policy Optimization (PPO)** algorithm to dynamically control traffic signal phases. Validated via the **Eclipse SUMO** microscopic simulator, the AI agent optimizes traffic flow, prioritizes emergency vehicles (ambulances), and minimizes environmental impact (CO2 & PM2.5 emissions).



https://github.com/user-attachments/assets/21dfda2d-8ea9-4cbb-b30d-53699c61283d   https://github.com/user-attachments/assets/8481cdf6-9c72-4842-afae-ebf79a909f53





## ✨ Key Features
- **🧠 Advanced AI Agent (PPO):** Utilizes Stable Baselines3's PPO algorithm over traditional DQN to prevent "Catastrophic Forgetting" and ensure stable, monotonic policy improvements via Trust Region clipping.
- **🚑 Emergency Preemption:** Strict algorithmic priority for ambulances, ensuring rapid clearance without causing network-wide gridlocks.
- **🍃 Eco-Routing (HBEFA3):** Integrates real-time emission tracking to penalize high-acceleration stop-and-go waves, drastically reducing vehicular pollution.
- **📊 Macro-to-Micro Pipeline:** Uses real-world Bangalore traffic volume data (from Kaggle) scaled down into microscopic spawn probabilities for highly realistic SUMO simulations.

## 🧮 The Multi-Objective Reward Function
To prevent "Reward Hacking" (where the AI keeps one lane green indefinitely), a custom **Time-Accumulated Penalty** function was engineered:

`Rt = - Σ(W_normal) - Σ(W_ambulance × 100) - (CO2_HBEFA3 × 0.5)`

* The agent is penalized exponentially as wait time increases.
* A **100x multiplier** is applied to ambulance wait times, forcing an immediate green wave.

## 📈 Real-World Case Studies & Results

### Case Study 1: Indiranagar (KFC Junction)
A standard urban intersection with moderate cross-traffic density.
* **Queue Length MSE Reduction:** 48.2% drop (from 1049.9 to 543.5)
* **Overall Waiting Time Drop:** 18.8% reduction
* **Ambulance Delay Reduction:** 38.1% faster clearance

### Case Study 2: Koramangala (Sony World Junction)
An extreme congestion stress test on a highly asymmetric, severely bottlenecked network.
* **Queue Length MSE Reduction:** 70.5% drop
* **Overall Waiting Time:** 77.4% reduction (Dropped from 789s to 177s)
* **Ambulance Clearance:** 57.3% faster response
* **CO2 Emissions:** 85.5% reduction (Dropped from 2760 kg to just 398 kg)

## 🎥 Simulation Demo

*(Add your SUMO simulation video links or GIFs here)*


- [Watch KFC Junction AI Simulation (With RL vs Without RL)] https://github.com/user-attachments/assets/28624ac7-9cb9-4f71-aebf-de055b09c2b9

- [Watch Sony World Junction Extreme Congestion Solving](link_to_your_video_or_gif_here)

## 🛠️ Tech Stack & Requirements
* **Python 3.8+**
* **Eclipse SUMO** (Simulation of Urban MObility)
* **TraCI** (Traffic Control Interface)
* **Stable Baselines3** (For PPO Implementation)
* **Pandas / NumPy** (For Kaggle dataset preprocessing)

## 🚀 How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/Traffic-Signal-AI.git](https://github.com/yourusername/Traffic-Signal-AI.git)
   cd Traffic-Signal-AI
