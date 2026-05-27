import kagglehub
import pandas as pd
import os

print("Dataset download ho raha hai... Please wait.")

# 1. Aapka code: Download the dataset via Kagglehub
path = kagglehub.dataset_download("preethamgouda/banglore-city-traffic-dataset")
print(f"Dataset downloaded successfully at: {path}")

# 2. Folder ke andar se CSV file dhoondhna
csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]

if not csv_files:
    print("Error: Koi CSV file nahi mili folder mein!")
else:
    # Pehli CSV file ka pura path banana
    csv_path = os.path.join(path, csv_files[0])
    print(f"Reading file: {csv_path}\n")
    
    # 3. Pandas se Data Read Karna
    df = pd.read_csv(csv_path)
    
    # Dataset ke columns print karke check karna (Aapki understanding ke liye)
    print("Dataset ke Columns:", df.columns.tolist())
    
    
    # 4. Indiranagar ka data filter karna (Note: Column name check kar lena)
    # Agar column ka naam 'Area Name' hai, toh us hisab se likhein.
    # Main assume kar raha hu column ka naam 'Area Name' hai.
    try:
        indiranagar_data = df[df['Area Name'] == 'Indiranagar']
        
        if indiranagar_data.empty:
            print("Indiranagar ka data nahi mila. Shayad spelling alag hai.")
        else:
            # Hum original count ko 10 ya 20 se divide kar rahe hain taaki simulation realistic lage
            total_vehicles = int(indiranagar_data['Traffic Volume'].max() / 20)
            print(f"Indiranagar mein Peak Traffic: {total_vehicles} vehicles/hour")
            
            # 5. SUMO Route File Generate Karna
            with open("custom_traffic.rou.xml", "w") as f:
                f.write('<routes>\n')
                # flow id, begin time (0s), end time (3600s), aur total count
                f.write(f'  <flow id="flow_1" begin="0" end="3600" number="{total_vehicles}" from="input_edge" to="output_edge"/>\n')
                f.write('</routes>\n')
            print("Success! SUMO ke liye 'custom_traffic.rou.xml' file ban gayi hai.")
            
    except KeyError as e:
        print(f"Column name error: Dataset mein {e} naam ka column nahi hai. Upar print hue columns check karein.")