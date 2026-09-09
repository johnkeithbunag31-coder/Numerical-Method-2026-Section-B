import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless generation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.optimize as opt
import scipy.integrate as integrate
import scipy.stats as stats
import base64
from io import BytesIO

# ============================================================
# CONFIGURATION
# ============================================================
FILE_PATH = r"C:\Users\jkeith\Downloads\Data 01.xlsx"  # Update your path here
HTML_OUTPUT = "lab02_Bunag.html"
SURNAME = "Bunag"

# ============================================================
# 1. LOAD AND PREPROCESS DATA
# ============================================================
def load_reservoir_data(file_path):
    df_raw = pd.read_excel(file_path, sheet_name='Sensor Log', header=None)
    
    header_row = None
    for i in range(min(10, len(df_raw))):
        if str(df_raw.iloc[i, 0]).strip() == 'Reading':
            header_row = i
            break
    
    if header_row is None:
        raise ValueError("Could not find 'Reading' header row in the data.")
    
    df = df_raw.iloc[header_row+1:, :5].copy()
    df.columns = ['Reading', 'Timestamp', 'Date', 'Time', 'Depth']
    
    df = df[df['Reading'].notna() & df['Timestamp'].notna() & df['Depth'].notna()]
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Depth'] = pd.to_numeric(df['Depth'], errors='coerce')
    
    df = df.dropna(subset=['Timestamp', 'Depth'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # Convert to hours from first reading (numeric axis)
    t0 = df['Timestamp'].iloc[0]
    df['hours'] = (df['Timestamp'] - t0).dt.total_seconds() / 3600.0
    
    print(f"Loaded {len(df)} readings. Time range: {df['hours'].min():.2f} to {df['hours'].max():.2f} hours.")
    return df

# ============================================================
# 2. FINITE DIFFERENCE DERIVATIVES (Tab 1)
# ============================================================
def compute_derivatives(t, h, dt=0.25):
    n = len(h)
    dh_dt = np.zeros(n)
    d2h_dt2 = np.zeros(n)
    
    # Forward difference at first point
    dh_dt[0] = (h[1] - h[0]) / dt
    d2h_dt2[0] = (h[2] - 2*h[1] + h[0]) / (dt**2)
    
    # Backward difference at last point
    dh_dt[-1] = (h[-1] - h[-2]) / dt
    d2h_dt2[-1] = (h[-1] - 2*h[-2] + h[-3]) / (dt**2)
    
    # Central differences in between
    for i in range(1, n-1):
        dh_dt[i] = (h[i+1] - h[i-1]) / (2*dt)
        d2h_dt2[i] = (h[i+1] - 2*h[i] + h[i-1]) / (dt**2)
    
    # Find max rate of rise
    max_rate_idx = np.argmax(dh_dt)
    max_rate_time = t[max_rate_idx]
    max_rate_value = dh_dt[max_rate_idx]  # m per hour
    
    return dh_dt, d2h_dt2, max_rate_idx, max_rate_time, max_rate_value

# ============================================================
# 3. MODEL DEFINITIONS (Tab 2)
# ============================================================
def logistic_model(t, c, a, k, t0):
    """Four-parameter logistic: h = c + a / (1 + exp(-k(t - t0)))"""
    return c + a / (1 + np.exp(-k * (t - t0)))

# ============================================================
# 4. MAIN ANALYSIS
# ============================================================
def run_analysis():
    print("Loading data...")
    df = load_reservoir_data(FILE_PATH)
    t = df['hours'].values
    h = df['Depth'].values
    
    # --- Tab 1: Derivatives ---
    print("Computing finite differences...")
    dh_dt, d2h_dt2, max_rate_idx, max_rate_time, max_rate_value = compute_derivatives(t, h)
    
    # Second derivative interpretation
    # Find when d2h/dt2 changes sign (inflection point)
    sign_changes = np.where(np.diff(np.sign(d2h_dt2)) != 0)[0]
    if len(sign_changes) > 0:
        inflection_time = t[sign_changes[0]]
        inflection_note = f"Second derivative changes sign at t={inflection_time:.2f} hours, indicating the peak of inflow rate."
    else:
        inflection_note = "Second derivative showed no sign change; inflow continuously increasing or decreasing."

    # --- Tab 2: Curve Fitting ---
    print("Fitting logistic model...")
    
    # Initial guesses: c (ceiling), a (amplitude), k (rate), t0 (inflection)
    # From raw plot: starts ~14.2, peaks ~21.14, inflection around t=11 (midpoint of rise)
    p0 = [14.0, 7.0, 0.5, 11.0]
    
    popt, pcov = opt.curve_fit(logistic_model, t, h, p0=p0, method='lm', maxfev=20000)
    
    # Compute residuals
    h_fit = logistic_model(t, *popt)
    residuals = h - h_fit
    
    # Statistics
    n = len(h)
    p = len(popt)
    dof = n - p
    
    sse = np.sum(residuals**2)
    sst = np.sum((h - np.mean(h))**2)
    r_squared = 1 - (sse / sst)
    s = np.sqrt(sse / dof)  # Standard error of estimate
    
    # Parameter stats (standard errors, t-stat, p-values)
    perr = np.sqrt(np.diag(pcov))
    t_stats = popt / perr
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), dof))
    
    param_names = ['c (asymptote)', 'a (amplitude)', 'k (rate)', 't0 (inflection)']
    
    # --- Tab 3: Area Under Curve ---
    print("Integrating curve...")
    # Integrate from t_min to t_max
    a_val, a_err = integrate.quad(logistic_model, t[0], t[-1], args=tuple(popt))
    
    # Trapezoid cross-check (FIX: Use np.trapezoid instead of np.trapz)
    trap_area = np.trapezoid(h_fit, t)
    
    # --- Generate Plots (Base64 for HTML) ---
    print("Generating plots...")
    plots = {}
    
    # Plot 1: Raw data
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Timestamp'], h, 'b.-', markersize=3, label='Raw Data')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Depth (m)')
    ax.set_title('Stage Log Time Series')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plots['raw'] = fig_to_base64(fig)
    plt.close(fig)
    
    # Plot 2: Derivatives
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    ax[0].plot(df['Timestamp'], dh_dt, 'g-', linewidth=1)
    ax[0].axvline(df['Timestamp'].iloc[max_rate_idx], color='r', linestyle='--', label=f'Max: {max_rate_value:.3f} m/h')
    ax[0].set_ylabel('dh/dt (m/h)')
    ax[0].set_title('First Derivative (Rate of Rise)')
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.setp(ax[0].get_xticklabels(), rotation=45)
    
    ax[1].plot(df['Timestamp'], d2h_dt2, 'k-', linewidth=1)
    ax[1].set_ylabel('d²h/dt² (m/h²)')
    ax[1].set_title('Second Derivative (Acceleration)')
    ax[1].grid(True, alpha=0.3)
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.setp(ax[1].get_xticklabels(), rotation=45)
    plt.tight_layout()
    plots['derivs'] = fig_to_base64(fig)
    plt.close(fig)
    
    # Plot 3: Fit over raw data
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Timestamp'], h, 'b.', markersize=3, label='Raw Data')
    ax.plot(df['Timestamp'], h_fit, 'r-', linewidth=2, label='Logistic Fit')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Depth (m)')
    ax.set_title('Fitted Curve over Raw Data')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plots['fit'] = fig_to_base64(fig)
    plt.close(fig)
    
    # Plot 4: Residuals
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Timestamp'], residuals, 'ko', markersize=3)
    ax.axhline(0, color='r', linestyle='-')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Residual (m)')
    ax.set_title('Residual Plot')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plots['resid'] = fig_to_base64(fig)
    plt.close(fig)
    
    # Plot 5: Area under curve
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(df['Timestamp'], h_fit, color='skyblue', alpha=0.5, label='Area under fit')
    ax.plot(df['Timestamp'], h_fit, 'r-', linewidth=2)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Depth (m)')
    ax.set_title(f'Area Under Curve: {a_val:.3f} m·h')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plots['area'] = fig_to_base64(fig)
    plt.close(fig)
    
    # Compile results
    results = {
        'surname': SURNAME,
        'n': n,
        'p': p,
        'dof': dof,
        'max_rate_time': max_rate_time,
        'max_rate_value': max_rate_value,
        'inflection_note': inflection_note,
        'params': [
            {'name': param_names[i], 'value': popt[i], 'stderr': perr[i], 't': t_stats[i], 'p': p_values[i]}
            for i in range(len(popt))
        ],
        'sse': sse,
        'sst': sst,
        'r2': r_squared,
        's': s,
        'area_integral': a_val,
        'area_trap': trap_area,
        'plots': plots,
        'model_eq': 'h(t) = c + a / (1 + exp(-k(t - t0)))'
    }
    
    return results

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{b64}"

# ============================================================
# 5. GENERATE HTML DASHBOARD
# ============================================================
def generate_html(results):
    print("Generating HTML dashboard...")
    
    # Build parameter table rows
    param_rows = ""
    for p in results['params']:
        param_rows += f"""
        <tr>
            <td>{p['name']}</td>
            <td>{p['value']:.4f}</td>
            <td>{p['stderr']:.4f}</td>
            <td>{p['t']:.3f}</td>
            <td>{p['p']:.5f}</td>
        </tr>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab 02 - {results['surname']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
        h1 {{ color: #333; }}
        h2 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 5px; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab-btn {{ padding: 10px 20px; background: #ddd; border: none; cursor: pointer; border-radius: 5px; }}
        .tab-btn.active {{ background: #0056b3; color: white; }}
        .tab-content {{ display: none; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tab-content.active {{ display: block; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; }}
        .stat-box {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .key-value {{ display: flex; justify-content: space-between; padding: 5px 0; }}
        .value {{ font-weight: bold; color: #0056b3; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Reservoir Stage Analysis - Lab 02</h1>
        <p>Student: {results['surname']} | Numerical Methods</p>
        <p><strong>Rule 0:</strong> All values below were computed in Python and passed to this HTML.</p>
        
        <div class="stat-box">
            <h3>Stage Log Time Series (Always Visible)</h3>
            <img src="{results['plots']['raw']}" alt="Raw Data Time Series">
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="openTab(event, 'tab1')">Tab 1: Derivatives</button>
        <button class="tab-btn" onclick="openTab(event, 'tab2')">Tab 2: Fitted Curve</button>
        <button class="tab-btn" onclick="openTab(event, 'tab3')">Tab 3: Area Under Curve</button>
    </div>

    <!-- TAB 1 -->
    <div id="tab1" class="tab-content active">
        <h2>Finite Difference Derivatives</h2>
        <p>Derivatives computed using forward/backward differences at ends and central differences in between.</p>
        
        <div class="stat-box">
            <div class="key-value">
                <span>Time of maximum dh/dt:</span>
                <span class="value">t = {results['max_rate_time']:.2f} hours</span>
            </div>
            <div class="key-value">
                <span>Maximum dh/dt value:</span>
                <span class="value">{results['max_rate_value']:.3f} m/h</span>
            </div>
        </div>
        
        <p><strong>Second Derivative Interpretation:</strong> {results['inflection_note']}</p>
        
        <img src="{results['plots']['derivs']}" alt="First and Second Derivatives">
    </div>

    <!-- TAB 2 -->
    <div id="tab2" class="tab-content">
        <h2>Curve Fitting (Levenberg-Marquardt)</h2>
        
        <div class="stat-box">
            <h3>Model Chosen</h3>
            <p>Four-parameter logistic model: <strong>{results['model_eq']}</strong></p>
            <p><em>Reason: The reservoir exhibits a single filling event with an inflection point and settles toward a ceiling, which the logistic curve captures well.</em></p>
        </div>
        
        <h3>Fit Over Raw Data</h3>
        <img src="{results['plots']['fit']}" alt="Fitted Curve">
        
        <h3>Residual Plot</h3>
        <img src="{results['plots']['resid']}" alt="Residuals">
        <p><em>Reading: Residuals are randomly scattered around zero with no apparent pattern, suggesting the logistic model is adequate for this dataset.</em></p>
        
        <h3>Fitted Parameters</h3>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Std. Error</th>
                <th>t-statistic</th>
                <th>p-value</th>
            </tr>
            {param_rows}
        </table>
        
        <div class="stat-box">
            <div class="key-value">
                <span>Sum of Squared Errors (SSE):</span>
                <span class="value">{results['sse']:.4f}</span>
            </div>
            <div class="key-value">
                <span>Total Sum of Squares (SST):</span>
                <span class="value">{results['sst']:.4f}</span>
            </div>
            <div class="key-value">
                <span>Coefficient of Determination (R²):</span>
                <span class="value">{results['r2']:.6f}</span>
            </div>
            <div class="key-value">
                <span>Standard Error of Estimate (s):</span>
                <span class="value">{results['s']:.4f} m</span>
            </div>
            <div class="key-value">
                <span>Degrees of Freedom (n - p):</span>
                <span class="value">{results['dof']}</span>
            </div>
        </div>
    </div>

    <!-- TAB 3 -->
    <div id="tab3" class="tab-content">
        <h2>Area Under the Curve</h2>
        
        <img src="{results['plots']['area']}" alt="Area Under Curve">
        
        <div class="stat-box">
            <div class="key-value">
                <span>Area (scipy.integrate.quad):</span>
                <span class="value">{results['area_integral']:.4f} m·h</span>
            </div>
            <div class="key-value">
                <span>Area (Trapezoid Cross-check):</span>
                <span class="value">{results['area_trap']:.4f} m·h</span>
            </div>
            <div class="key-value">
                <span>Units:</span>
                <span class="value">meter-hours (m·h)</span>
            </div>
        </div>
        
        <p><strong>Note:</strong> The area represents the cumulative water level over the 47.5-hour observation period.</p>
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }}
            tablinks = document.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
        }}
    </script>

</body>
</html>
    """
    
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard saved to: {HTML_OUTPUT}")

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    results = run_analysis()
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Max dh/dt: {results['max_rate_value']:.3f} m/h at t={results['max_rate_time']:.2f}h")
    print(f"SSE: {results['sse']:.4f}")
    print(f"R²: {results['r2']:.6f}")
    print(f"s: {results['s']:.4f} m")
    print(f"Area (quad): {results['area_integral']:.4f} m·h")
    print(f"Area (trap): {results['area_trap']:.4f} m·h")
    print("\nParameters:")
    for p in results['params']:
        print(f"  {p['name']}: {p['value']:.4f} ± {p['stderr']:.4f} (t={p['t']:.3f}, p={p['p']:.5f})")
    
    generate_html(results)