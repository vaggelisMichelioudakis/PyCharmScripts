import os, glob, re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

FOLDER = r"Digitzed_SS_CSV"  # <-- ΒΑΛΕ ΕΔΩ ΤΟ PATH ΣΟΥ
WL_MIN, WL_MAX, STEP = 200, 2501, 5
grid = np.arange(WL_MIN, WL_MAX + STEP, STEP)


def load_curve_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.iloc[:, :2].copy()
    df.columns = ["wl", "T"]
    df["wl"] = pd.to_numeric(df["wl"], errors="coerce")
    df["T"] = pd.to_numeric(df["T"], errors="coerce")
    df = df.dropna().sort_values("wl")
    return df


def to_percent(df: pd.DataFrame) -> pd.DataFrame:
    mx = df["T"].max()
    if mx <= 1.2:
        df = df.copy()
        df["T"] *= 100.0
    return df


def get_base_name(filename_no_ext: str):
    # Extracts the system name by removing "_STATIC"
    name_u = filename_no_ext.upper()
    if "_STATIC" in name_u:
        return re.split(r"_STATIC", filename_no_ext, flags=re.IGNORECASE)[0]
    # Fallback just in case the file doesn't have the _STATIC suffix
    return filename_no_ext


def interp_to_grid(df: pd.DataFrame, grid_nm: np.ndarray) -> np.ndarray:
    wl = df["wl"].to_numpy()
    T = df["T"].to_numpy()
    return np.interp(grid_nm, wl, T, left=np.nan, right=np.nan)


# === Load + interpolate ===
systems = {}  # Simply {base_name: array_of_transmittance}
for path in sorted(glob.glob(os.path.join(FOLDER, "*.csv"))):
    fname = os.path.splitext(os.path.basename(path))[0]
    base = get_base_name(fname)

    df = to_percent(load_curve_csv(path))
    df = df[(df["wl"] >= WL_MIN) & (df["wl"] <= WL_MAX)]
    if df.empty:
        continue

    # Store directly since there's only one state
    systems[base] = interp_to_grid(df, grid)

keys = sorted(systems.keys())
print(f"Loaded {len(keys)} STATIC systems.")
if not keys:
    raise RuntimeError("Δεν βρέθηκαν αρχεία STATIC. Έλεγξε ονόματα αρχείων και φάκελο.")

# === Colors (one per system) ===
palette = px.colors.qualitative.Dark24


def color_for(i): return palette[i % len(palette)]


# === Build interactive figure ===
fig = go.Figure()

for i, k in enumerate(keys):
    col = color_for(i)
    T_arr = systems[k]

    # Filter out NaN values for plotting
    mask = ~np.isnan(T_arr)

    label = k.replace("SS_", "")

    # Single trace per system
    fig.add_trace(go.Scatter(
        x=grid[mask], y=T_arr[mask],
        mode="lines",
        name=label,
        line=dict(color=col, width=2, dash="solid"),
        hovertemplate="System: %{fullData.name}<br>State: STATIC<br>λ=%{x} nm<br>T=%{y:.2f}%<extra></extra>"
    ))

fig.update_layout(
    title="Transmittance spectra per system (STATIC)",
    xaxis_title="Wavelength (nm)",
    yaxis_title="Transmittance (%)",
    hovermode="x unified",
    legend_title="Click text to edit / Click box to toggle",
    template="plotly_white",
    width=1200, height=650
)

# Configuration enabling editable legends and titles
interactive_config = {
    'editable': True,
    'edits': {
        'legendText': True,
        'titleText': True,
        'axisTitleText': True
    }
}

# 1) Ανοίγει σε browser από Python:
fig.show(config=interactive_config)

# 2) Αν θες να το έχεις ως αρχείο (offline):
# fig.write_html("spectra_interactive_static.html", include_plotlyjs="cdn", config=interactive_config)