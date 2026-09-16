import MaterialsScript as MS

project = MS.Project

# 1. Target the folder containing your alloy models
try:
    batch_folder = project.Folders("Structures")
except:
    print("Error: Could not find a folder named 'Structures'.")
    import sys
    sys.exit()

# 2. Configure CASTEP with our verified baseline settings
castep = MS.CASTEP()
castep.Task = "GeometryOptimization"
castep.Functional = "PBE"
castep.CutoffEnergy = 420.0
castep.TreatAsMetal = True
castep.OptimizeCell = True  # Allows the box size to shrink/expand

print("Starting CASTEP Batch Automation...")

# 3. Loop through the folder and run CASTEP sequentially
for item in batch_folder.Items:
    if item.Type == "StructureDocument":
        print("Running Geometry Optimization for: " + item.Name)
        
        # Launch the job using your local CPU
        job = castep.Run(item)
        
        # CRITICAL: Wait for this job to finish before launching the next one
        # This prevents your CPU from crashing by running 10 jobs at once
        job.WaitToCompletion()
        
        print("Successfully finished: " + item.Name)

print("All batch calculations completed successfully!")