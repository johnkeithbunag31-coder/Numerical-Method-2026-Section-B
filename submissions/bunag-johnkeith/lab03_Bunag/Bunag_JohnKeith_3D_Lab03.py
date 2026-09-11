# ====================================================================
# Lab 03: Real-World Data Linear Regression
# Numerical Methods - Section 3D
# Name: Bunag, John Keith
# File: Bunag_JohnKeith_3D_Lab03.py
# ====================================================================

import numpy as np
import matplotlib.pyplot as plt

# ====================================================================
# 1. DATA INPUT
# ====================================================================
# Annual average CO2 concentration (ppm) from Mauna Loa Observatory
# Using years since 2000 to improve numerical stability
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 
                  2018, 2019, 2020, 2021, 2022, 2023, 2024])
co2 = np.array([389.85, 391.61, 393.88, 396.44, 398.58, 400.83, 
                404.24, 406.55, 408.54, 411.43, 414.24, 416.41, 
                418.56, 421.08, 424.61])

# Center the x variable for numerical stability (x = year - 2000)
x = years - 2000

n = len(x)  # number of data points

print("=" * 60)
print("LINEAR REGRESSION ANALYSIS")
print("Numerical Methods - Section 3D")
print("Bunag, John Keith")
print("=" * 60)
print(f"\nNumber of observations: {n}")
print("\nData (x = Year - 2000):")
print("Year   x     CO2 (ppm)")
print("-" * 30)
for i in range(n):
    print(f"{years[i]:4d}   {x[i]:2d}       {co2[i]:8.2f}")

# ====================================================================
# 2. LEAST SQUARES FORMULAS
# ====================================================================
# Calculate summations needed for least squares
sum_x = np.sum(x)
sum_y = np.sum(co2)
sum_xy = np.sum(x * co2)
sum_x2 = np.sum(x ** 2)
sum_y2 = np.sum(co2 ** 2)

# Compute mean values
x_bar = sum_x / n
y_bar = sum_y / n

# Compute slope (a1) and intercept (a0)
# a1 = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - (sum_x)^2)
a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

# a0 = y_bar - a1 * x_bar (this is intercept for centered x)
a0_centered = y_bar - a1 * x_bar

# For original equation y = A0 + A1*year
# Since x = year - 2000, y = a0 + a1*(year - 2000) = (a0 - 2000*a1) + a1*year
A0 = a0_centered - 2000 * a1
A1 = a1

# ====================================================================
# 3. STATISTICAL MEASURES
# ====================================================================
# Predicted y values using the regression model
y_pred = a0_centered + a1 * x

# Residuals (errors)
residuals = co2 - y_pred

# Sum of Squared Errors (SSE) / Sr
SSE = np.sum(residuals ** 2)

# Total Sum of Squares (SSt)
y_mean = np.mean(co2)
SSt = np.sum((co2 - y_mean) ** 2)

# Coefficient of determination (r^2)
r_squared = 1 - (SSE / SSt)

# Standard error of the estimate (s_y/x)
std_error = np.sqrt(SSE / (n - 2))

# ====================================================================
# 4. DISPLAY RESULTS
# ====================================================================
print("\n" + "=" * 60)
print("REGRESSION RESULTS")
print("=" * 60)
print(f"\nRegression Equation (centered): y = {a0_centered:.4f} + {a1:.4f}(Year-2000)")
print(f"Regression Equation (original): y = {A0:.4f} + {A1:.4f}Year")
print(f"\nSlope (a1):     {a1:.4f} ppm/year")
print(f"Intercept (a0): {A0:.4f} ppm")
print(f"\nSum of Squared Errors (SSE / Sr): {SSE:.4f}")
print(f"Coefficient of Determination (r²): {r_squared:.6f}")
print(f"Standard Error (s_y/x):           {std_error:.4f} ppm")

print("\n" + "=" * 60)
print("DETAILED STATISTICS")
print("=" * 60)
print(f"Sum of x (Year-2000):   {sum_x:.2f}")
print(f"Sum of y:               {sum_y:.2f}")
print(f"Sum of xy:              {sum_xy:.2f}")
print(f"Sum of x²:              {sum_x2:.2f}")
print(f"Sum of y²:              {sum_y2:.2f}")
print(f"Mean of x:              {x_bar:.2f}")
print(f"Mean of y:              {y_bar:.2f}")
print(f"n:                      {n}")

# ====================================================================
# 5. PLOTS
# ====================================================================
# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# ---- Plot 1: Data with fitted line ----
ax1.scatter(years, co2, color='blue', s=60, label='Observed Data', 
            zorder=5, edgecolors='darkblue', linewidth=1.5)
ax1.plot(years, y_pred, color='red', linewidth=2.5, 
         label=f'Fitted Line: y = {A0:.2f} + {A1:.2f}x')

# Add equation text box
ax1.text(0.05, 0.95, f'y = {A0:.2f} + {A1:.2f}x\nr² = {r_squared:.4f}', 
         transform=ax1.transAxes, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('CO₂ Concentration (ppm)', fontsize=12, fontweight='bold')
ax1.set_title('Atmospheric CO₂ Concentration vs. Year', fontsize=14, 
              fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower right', fontsize=11)
ax1.set_xlim(2009, 2025)
ax1.set_ylim(380, 430)

# ---- Plot 2: Residual plot ----
ax2.scatter(years, residuals, color='green', s=60, zorder=5, 
            edgecolors='darkgreen', linewidth=1.5)
ax2.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax2.plot(years, residuals, 'green', linewidth=1.5, alpha=0.5)

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Residuals (ppm)', fontsize=12, fontweight='bold')
ax2.set_title('Residual Plot', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(2009, 2025)

# Add horizontal line for zero
ax2.text(0.05, 0.95, 'Zero residual line', transform=ax2.transAxes, 
         verticalalignment='top', color='red')

plt.tight_layout()
plt.savefig('Bunag_JohnKeith_3D_Lab03_Plots.png', dpi=300, bbox_inches='tight')
plt.show()

# ====================================================================
# 6. PREDICTION
# ====================================================================
# Predict CO2 for the year 2026 (not in dataset)
year_predict = 2026
co2_pred = A0 + A1 * year_predict

print("\n" + "=" * 60)
print("PREDICTION")
print("=" * 60)
print(f"\nPredicted CO₂ concentration for {year_predict}:")
print(f"y = {A0:.4f} + {A1:.4f}({year_predict})")
print(f"y = {co2_pred:.2f} ppm")

# ====================================================================
# 7. INTERPRETATION SUMMARY
# ====================================================================
print("\n" + "=" * 60)
print("INTERPRETATION SUMMARY")
print("=" * 60)
print(f"""
1. SLOPE: The slope of {a1:.4f} ppm/year indicates that CO₂ 
   concentration increases by approximately {a1:.2f} ppm each year.

2. INTERCEPT: The intercept of {A0:.2f} ppm is the theoretical CO₂ 
   level at year 0 (not meaningful in practical terms).

3. FIT QUALITY: 
   - r² = {r_squared:.6f} means {r_squared*100:.1f}% of the variation in CO₂ 
     concentration is explained by the year.
   - Standard error = {std_error:.4f} ppm, meaning typical predictions 
     are within ±{std_error:.4f} ppm of actual values.

4. RESIDUALS: The residual plot shows random scatter around zero
   with no clear pattern, suggesting a linear model is appropriate.
   Residuals are small (mostly within ±1 ppm), indicating good fit.

5. PREDICTION: For {year_predict}, the predicted CO₂ is {co2_pred:.2f} ppm, which 
   is meaningful for climate change monitoring and policy planning.
""")

# ====================================================================
# 8. RESIDUAL TABLE
# ====================================================================
print("\n" + "=" * 60)
print("RESIDUAL ANALYSIS TABLE")
print("=" * 60)
print("Year   Observed   Predicted   Residual")
print("-" * 45)
for i in range(n):
    print(f"{years[i]:4d}   {co2[i]:8.2f}   {y_pred[i]:8.2f}   {residuals[i]:8.3f}")

print("\n" + "=" * 60)
print("END OF ANALYSIS")
print("=" * 60)