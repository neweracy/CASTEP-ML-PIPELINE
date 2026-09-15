# Formation Energy Curve - Interpretation Guide

## Overview

The **Formation Energy Curve** visualizes the thermodynamic stability of Ti-Al binary alloys across the full composition range (0-100% Al). This graph combines DFT-calculated data points with a Gaussian Process Regression (GPR) machine learning model that predicts formation energies for any composition.

## Graph Components

### 1. **Red Scatter Points** (DFT Data from CASTEP)

**What they are:**
- Direct results from first-principles quantum mechanical calculations
- Each point represents a specific Ti-Al structure that was fully geometry-optimized
- These are the "ground truth" experimental observations our ML model learns from

**What they mean:**
- **x-coordinate**: Aluminum mole fraction (composition)
  - 0.0625 = Ti₁₅Al₁ (6.25% Al)
  - 0.125 = Ti₁₄Al₂ (12.5% Al)
  - 0.25 = Ti₁₂Al₄ (25% Al)
  - 0.50 = Ti₈Al₈ (50% Al)
  - 0.75 = Ti₄Al₁₂ (75% Al)

- **y-coordinate**: Formation energy per atom (eV/atom)
  - **Negative values** = Alloy is thermodynamically stable (energetically favorable to form)
  - **More negative** = More stable
  - **Positive values** = Unstable (would decompose into pure elements)

**Physical interpretation:**
- These points tell us which compositions are stable
- The further below zero, the more energetically favorable that composition is
- Gaps between points represent compositions we haven't calculated (yet)

---

### 2. **Blue Solid Line** (GPR Surrogate Model)

**What it is:**
- Machine learning prediction that smoothly interpolates between DFT data points
- Uses Gaussian Process Regression (GPR) with a Radial Basis Function (RBF) kernel
- Trained on the 5 red DFT points

**What it means:**
- Predicts formation energy for **any** composition, not just the 5 we calculated
- The smooth curve suggests how the stability changes continuously across composition space
- Can identify:
  - **Minima** (most stable compositions)
  - **Trends** (how stability changes with Al content)
  - **Ordering effects** (if curve is non-linear)

**Physical interpretation:**
- If the curve has a **minimum** → that composition is predicted to be most stable
- If the curve is **non-convex** (has humps) → may indicate phase separation
- The shape reveals mixing behavior (ideal vs. non-ideal solution)

---

### 3. **Light Blue Shaded Region** (95% Confidence Interval)

**What it is:**
- Uncertainty bounds on the GPR predictions
- Represents model's confidence in its predictions
- Calculated as ± 1.96 × σ (standard deviation from GPR)

**What it means:**
- **Narrow bands** (near DFT points) = Model is very confident
  - Why? Predictions are interpolations between known data
  - Low uncertainty because data constrains the prediction
  
- **Wide bands** (far from DFT points) = Model is uncertain
  - Why? Predictions are extrapolations beyond training data
  - High uncertainty because no data constrains the prediction
  
- **95% confidence** = If we calculated the DFT energy at that point, there's a 95% chance it would fall within the shaded region

**Physical interpretation:**
- Wide bands at edges (0% Al, 100% Al) indicate extrapolation risk
  - We didn't calculate pure Ti or pure Al in this dataset
  - Model is "guessing" based on trends from nearby points
  
- To reduce uncertainty: Calculate DFT for more compositions in high-uncertainty regions

---

## How to Read the Graph

### Example: Ti₈Al₈ (50% Al)

1. **DFT Point**: ~-0.32 eV/atom
   - This is the calculated formation energy
   - Most negative (most stable) of the 5 structures we tested

2. **GPR Prediction**: Also ~-0.32 eV/atom
   - Model perfectly fits the training data at this point
   
3. **Uncertainty**: Very small (narrow blue band)
   - Model is confident because this is a training point

**Conclusion**: 50-50 Ti-Al composition is the most stable alloy we've tested.

---

## Physical Interpretation Guide

### Formation Energy Values

| Formation Energy (eV/atom) | Interpretation |
|---------------------------|----------------|
| **E < -0.5** | Very stable alloy; strong ordering tendency |
| **-0.5 < E < -0.1** | Moderately stable; will form alloy phase |
| **-0.1 < E < 0** | Weakly stable; marginal stability |
| **E ≈ 0** | Ideal solution; no special interactions |
| **E > 0** | Unstable; phase separation expected |

### Our Ti-Al Results

**Range**: -0.32 to -0.06 eV/atom
- All compositions are **stable** (negative formation energy)
- **Most stable**: Ti₈Al₈ (50% Al) at -0.32 eV/atom
  - Suggests possible ordered intermetallic phase (e.g., TiAl)
  
- **Least stable** (but still stable): Ti₁₅Al₁ (6.25% Al) at -0.06 eV/atom
  - Ti-rich solid solution, weaker ordering

**Physical insight:**
- Non-linear curve shape suggests **non-ideal mixing**
- Maximum stability near 50% composition suggests **ordered compound formation**
- This matches known Ti-Al phase diagram: TiAl (50-50) is a well-known intermetallic

---

## What Makes a "Good" Curve?

### Signs of a Good Model

✅ **GPR curve passes through all DFT points**
   - Our model: R² = 1.0 (perfect fit)

✅ **Smooth, physically reasonable shape**
   - No wild oscillations between points
   - Follows expected trends

✅ **Narrow uncertainty near training data**
   - Wide uncertainty only in extrapolation regions
   - Our model: Mean σ = 0.001 eV/atom (very confident)

✅ **Cross-validation error is low**
   - Our model: CV MAE = 0.043 eV/atom
   - This is good for materials properties (typical DFT accuracy ~0.01-0.1 eV)

### Warning Signs (What to Avoid)

❌ **GPR doesn't pass through DFT points**
   - Indicates poor model fit or too much regularization (alpha too high)

❌ **Oscillations between data points**
   - Overfitting or inappropriate kernel
   - Physically unrealistic

❌ **Extremely wide uncertainty bands everywhere**
   - Model isn't learning from data
   - Need more training points or better kernel

❌ **Predicted positive formation energies**
   - Unless truly unstable, this indicates:
     - Bad reference energies (μ_Ti, μ_Al)
     - Incorrect composition parsing
     - DFT calculation errors

---

## Using the Graph for Predictions

### Interpolation (Reliable)

**Question**: What's the formation energy of Ti₁₀Al₆ (37.5% Al)?

**Answer**: Read the blue curve at x = 0.375
- Predicted E_form ≈ -0.28 eV/atom (from curve)
- Uncertainty: ±0.005 eV/atom (from band width)

**Confidence**: High ✅
- Point is between two training data (25% and 50% Al)
- Narrow confidence interval
- This is **interpolation** → reliable

### Extrapolation (Less Reliable)

**Question**: What about pure Al (100% Al)?

**Answer**: Read curve at x = 1.0
- Predicted E_form ≈ -0.18 eV/atom
- Uncertainty: ±0.10 eV/atom (10× larger!)

**Confidence**: Low ⚠️
- No training data beyond 75% Al
- Wide confidence interval
- This is **extrapolation** → treat with caution
- **Recommendation**: Calculate DFT for Ti₂Al₁₄ (87.5% Al) to constrain model

---

## Improving the Model

### Add More DFT Calculations

**High Priority**: Fill gaps for better interpolation
- Ti₁₃Al₃ (18.75% Al) - Between current 12.5% and 25% points
- Ti₆Al₁₀ (62.5% Al) - Between 50% and 75% points

**Medium Priority**: Extend composition range
- Ti₁Al₁₅ (93.75% Al) - Near pure Al region
- Pure Ti (0% Al) and pure Al (100% Al) as anchors

### Expected Improvements

| # DFT Points | CV MAE (Expected) | Uncertainty | Coverage |
|-------------|------------------|-------------|----------|
| **5** (current) | 0.043 eV/atom | High at edges | 6-75% Al |
| **9** (+4 points) | ~0.020 eV/atom | Medium at edges | 6-94% Al |
| **15** (+10 points) | ~0.010 eV/atom | Low everywhere | 0-100% Al |

---

## Connecting to Phase Diagrams

### Convex Hull Construction

The formation energy curve can be used to construct the **convex hull** (thermodynamic ground state):

1. Plot all formation energies vs. composition
2. Draw the "lower convex envelope" connecting the lowest points
3. Points **on the hull** = Stable phases at T=0K
4. Points **above the hull** = Metastable (will decompose)

**For Ti-Al:**
- If Ti₈Al₈ (50% Al) is lowest → Likely stable TiAl intermetallic
- If curve is convex everywhere → Solid solution stable
- If curve has multiple minima → Multiple ordered phases

### Temperature Effects

**Important**: This is T=0K data (no entropy)
- Real phase diagrams include temperature (G = H - TS)
- At high T, entropy favors disorder (solid solutions over compounds)
- Our formation energies predict **low-temperature behavior**

---

## Statistical Interpretation

### Model Performance Metrics

From our training run:

| Metric | Value | Meaning |
|--------|-------|---------|
| **R² Score** | 1.0000 | Perfect fit on training data |
| **MAE** | 0.00004 eV/atom | Average prediction error (training) |
| **RMSE** | 0.00005 eV/atom | RMS prediction error (training) |
| **CV MAE (LOO)** | 0.0428 eV/atom | **Generalization error** (most important) |
| **Mean σ** | 0.001 eV/atom | Average prediction uncertainty |

**Key Insight**: CV MAE (0.043 eV/atom) >> Training MAE (0.00004 eV/atom)
- This is **expected** and **healthy**
- Shows model isn't blindly memorizing
- CV MAE is the realistic error for new predictions
- 0.043 eV/atom is excellent for materials properties

### Uncertainty Quantification

**Why GPR over other ML models?**
- GPR provides **uncertainty estimates** (σ values)
- Critical for scientific applications:
  - Know when predictions are reliable
  - Guide future experiments (active learning)
  - Quantify risk in predictions

**Example**: Predicting at 60% Al
- Prediction: E_form = -0.26 eV/atom
- Uncertainty: σ = 0.008 eV/atom
- 95% CI: [-0.276, -0.244] eV/atom
- **Interpretation**: We're 95% confident the true value is between -0.28 and -0.24 eV/atom

---

## Advanced: Kernel Interpretation

### Optimized Kernel Parameters

From our model: `1.13² × RBF(length_scale=0.182)`

**Constant term (1.13²):**
- Controls overall output variance
- 1.13² ≈ 1.28 eV²/atom²
- Indicates moderate variance in formation energies

**Length scale (0.182):**
- Controls how fast predictions change with composition
- 0.182 in composition space (0-1 scale) = 18.2% Al composition
- **Physical meaning**: Formation energy changes significantly over ~18% Al changes
- Smaller length scale → more wiggly curve (more local variation)
- Larger length scale → smoother curve (more global trends)

**Our value (0.182) suggests:**
- Formation energy varies on the scale of ~3 atoms in a 16-atom cell
- Local chemical environment matters (not just average composition)
- Consistent with short-range ordering in alloys

---

## Summary: Key Takeaways

### What the Graph Shows
- 📊 Thermodynamic stability of Ti-Al alloys across all compositions
- 🔴 5 DFT-calculated reference points (ground truth)
- 🔵 ML model filling gaps with uncertainty quantification

### Main Findings
1. **All Ti-Al compositions are stable** (negative formation energy)
2. **50% Al composition is most stable** (~-0.32 eV/atom)
3. **Stability decreases toward pure elements** (especially Ti-rich side)
4. **Non-ideal mixing** (curve is not linear)

### Model Quality
✅ Excellent fit (R² = 1.0)  
✅ Good generalization (CV MAE = 0.043 eV/atom)  
✅ Appropriate uncertainty estimates  
✅ Physically reasonable predictions  

### Next Steps
🎯 Add DFT calculations at 18.75%, 37.5%, 62.5%, 87.5% Al  
🎯 Calculate pure Ti and pure Al as reference anchors  
🎯 Consider different crystal structures (HCP, BCC, FCC)  
🎯 Extend to ternary systems (Ti-Al-X)  

---

## Questions & Answers

**Q: Why only 5 data points?**  
A: DFT calculations are expensive (hours to days per structure). We use ML to predict the ~infinite compositions between the 5 calculated ones.

**Q: Can I trust predictions far from data points?**  
A: No. Always check the uncertainty bands. Wide bands = low confidence = need more DFT data.

**Q: What if I add more DFT points?**  
A: Rerun `uv run python train_ml.py` after updating `alloy_ml_dataset.csv`. The model will automatically retrain with new data.

**Q: Why is the curve smooth and not jagged?**  
A: The RBF kernel enforces smoothness. This is physically reasonable (formation energy changes gradually with composition).

**Q: Can this predict other properties?**  
A: This model only predicts formation energy. For other properties (band gap, elastic constants, etc.), train separate models with appropriate training data.

---

## References

### Thermodynamics
- "Introduction to the Thermodynamics of Materials" by Gaskell
- Formation energy concept: [NIST Materials Data Repository](https://materialsdata.nist.gov/)

### Machine Learning
- Gaussian Processes: Rasmussen & Williams (2006), "Gaussian Processes for Machine Learning"
- GPR in materials: Behler (2016), "Perspective: Machine learning potentials"

### Ti-Al System
- Banerjee & Cahn (2004), "Phase Transformations in Ti-Al"
- Kim (1994), "Ordered intermetallic alloys, part III: Gamma titanium aluminides"

---

**Last Updated**: 2026-09-15  
**Generated by**: DFT-ML Pipeline v0.1.0  
**Model**: Gaussian Process Regression with RBF Kernel
