# osm on krne k liye cmd par python "%SUMO_HOME%\tools\osmWebWizard.py"
import pandas as pd
import numpy as np

def calculate_thesis_metrics():
    print("\n" + "="*50)
    print("🎓 M.TECH THESIS RESULTS CALCULATOR 🎓")
    print("="*50)

    try:
        # Dono files load karna
        base_df = pd.read_csv("detailed_baseline.csv")
        rl_df = pd.read_csv("detailed_rl_results.csv")

        # 1. Total Waiting Time Analysis
        base_wait_mean = base_df["Total_Wait"].mean()
        rl_wait_mean = rl_df["Total_Wait"].mean()
        wait_improvement = ((base_wait_mean - rl_wait_mean) / base_wait_mean) * 100

        # 2. Ambulance Delay Analysis (SOTA Feature)
        base_amb_mean = base_df["Ambulance_Wait"].mean()
        rl_amb_mean = rl_df["Ambulance_Wait"].mean()
        # Handle divide by zero if baseline was somehow 0
        amb_improvement = 0 if base_amb_mean == 0 else ((base_amb_mean - rl_amb_mean) / base_amb_mean) * 100

        # 3. CO2 Emission Analysis
        base_co2_mean = base_df["CO2"].mean()
        rl_co2_mean = rl_df["CO2"].mean()
        co2_improvement = ((base_co2_mean - rl_co2_mean) / base_co2_mean) * 100

        # 4. Queue Length (MSE Logic - Ideal Queue is 0)
        # MSE from ideal state (0 queue)
        base_queue_mse = np.mean(np.square(base_df["Queue"] - 0))
        rl_queue_mse = np.mean(np.square(rl_df["Queue"] - 0))

        # Printing Results for Thesis Table
        print("\n📊 1. OVERALL WAITING TIME")
        print(f"   - Without RL (Baseline): {base_wait_mean:.2f} seconds")
        print(f"   - With RL Model:       {rl_wait_mean:.2f} seconds")
        print(f"   ✅ Improvement:        {wait_improvement:.2f}% reduction in traffic delay")

        print("\n🚑 2. EMERGENCY VEHICLE (AMBULANCE) DELAY")
        print(f"   - Without RL (Baseline): {base_amb_mean:.2f} seconds")
        print(f"   - With RL Model:       {rl_amb_mean:.2f} seconds")
        print(f"   ✅ Improvement:        {amb_improvement:.2f}% faster emergency response")

        print("\n🍃 3. CO2 EMISSIONS (Eco-Routing)")
        print(f"   - Without RL (Baseline): {base_co2_mean:.2f} grams")
        print(f"   - With RL Model:       {rl_co2_mean:.2f} grams")
        print(f"   ✅ Improvement:        {co2_improvement:.2f}% reduction in pollution")

        print("\n📉 4. QUEUE LENGTH (MSE from Ideal State = 0)")
        print(f"   - Baseline MSE: {base_queue_mse:.2f}")
        print(f"   - RL Model MSE: {rl_queue_mse:.2f}")
        print("   (Lower MSE means the queue is closer to zero, which is better!)")
        
        print("\n" + "="*50)
        

    except FileNotFoundError:
        print("Error: CSV files nahi milin. Kya aapne test_and_compare.py aur run_baseline_data.py chalaya hai?")

if __name__ == "__main__":
    calculate_thesis_metrics()