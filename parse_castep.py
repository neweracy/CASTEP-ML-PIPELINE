import os
import re
import pandas as pd

# --- 1. Define Your Reference Energies (eV/atom) ---
MU_TI = -1593.839175
MU_AL = -110.897059

def parse_castep_files(directory_path):
    data_records = []
    
    # Regex patterns to find specific lines in the text files
    # Looks for: "LBFGS: Final Enthalpy     = -2.55014268E+004 eV"
    energy_pattern = re.compile(r"LBFGS:\s+Final Enthalpy\s+=\s+([-.\dE+]+)\s+eV")
    
    # Looks for: "Total number of ions in cell =   16"
    total_atoms_pattern = re.compile(r"Total number of ions in cell\s*=\s*(\d+)")

    for filename in os.listdir(directory_path):
        if filename.endswith(".castep"):
            filepath = os.path.join(directory_path, filename)
            
            # --- 2. Extract Composition from Filename ---
            # Assuming you name files like "Ti14Al2.castep"
            ti_match = re.search(r"Ti(\d+)", filename)
            al_match = re.search(r"Al(\d+)", filename)
            
            # If no number is found, assume 0 for that element
            n_ti = int(ti_match.group(1)) if ti_match else 0
            n_al = int(al_match.group(1)) if al_match else 0
            
            final_energy = None
            total_atoms = None

            # --- 3. Parse the .castep File ---
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
                # Find all energy matches and take the last one (the fully relaxed state)
                energy_matches = energy_pattern.findall(content)
                if energy_matches:
                    final_energy = float(energy_matches[-1])
                
                # Find total atoms
                atoms_match = total_atoms_pattern.search(content)
                if atoms_match:
                    total_atoms = int(atoms_match.group(1))

            # --- 4. Calculate Formation Energy ---
            if final_energy is not None and total_atoms is not None:
                # Ensure the filename composition matches the box size
                if (n_ti + n_al) == total_atoms:
                    
                    e_form = (final_energy - (n_ti * MU_TI + n_al * MU_AL)) / total_atoms
                    atomic_fraction_al = n_al / total_atoms
                    
                    data_records.append({
                        "Structure": filename.replace(".castep", ""),
                        "Total_Atoms": total_atoms,
                        "n_Ti": n_ti,
                        "n_Al": n_al,
                        "Atomic_Fraction_Al": atomic_fraction_al,
                        "Total_Energy_eV": final_energy,
                        "Formation_Energy_eV_per_atom": e_form
                    })
                else:
                    print(f"Warning: {filename} composition ({n_ti}+{n_al}) does not match N ({total_atoms}).")

    # --- 5. Export to DataFrame and CSV ---
    df = pd.DataFrame(data_records)
    # Sort by Aluminum concentration
    df = df.sort_values(by="Atomic_Fraction_Al").reset_index(drop=True)
    return df

# Run the parser
if __name__ == "__main__":
    # Point this to the folder containing all your completed CASTEP batch runs
    folder_path = "./ML_Data"

    dataset = parse_castep_files(folder_path)
    print(dataset)

    # Save the clean data for your ML model
    output_path = "./alloy_ml_dataset.csv"
    dataset.to_csv(output_path, index=False)
    print(f"\nDataset successfully saved to {output_path}!")