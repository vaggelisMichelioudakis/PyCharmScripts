import os, glob, re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

FOLDER = r"Digitzed_EC_CSV"   # <-- ΒΑΛΕ ΕΔΩ ΤΟ PATH ΣΟΥ
WL_MIN, WL_MAX, STEP = 200, 2501, 5
grid = np.arange(WL_MIN, WL_MAX + STEP, STEP)

def load_curve_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.iloc[:, :2].copy()
    df.columns = ["wl", "T"]
    df["wl"] = pd.to_numeric(df["wl"], errors="coerce")
    df["T"]  = pd.to_numeric(df["T"],  errors="coerce")
    df = df.dropna().sort_values("wl")
    return df

def to_percent(df: pd.DataFrame) -> pd.DataFrame:
    mx = df["T"].max()
    if mx <= 1.2:
        df = df.copy()
        df["T"] *= 100.0
    return df

def parse_state_and_base(filename_no_ext: str):
    name_u = filename_no_ext.upper()
    if "_CLEAR" in name_u:
        return "CLEAR", re.split(r"_CLEAR", filename_no_ext, flags=re.IGNORECASE)[0]
    if "_TINTED" in name_u:
        return "TINTED", re.split(r"_TINTED", filename_no_ext, flags=re.IGNORECASE)[0]
    return None, None

def interp_to_grid(df: pd.DataFrame, grid_nm: np.ndarray) -> np.ndarray:
    wl = df["wl"].to_numpy()
    T  = df["T"].to_numpy()
    return np.interp(grid_nm, wl, T, left=np.nan, right=np.nan)

# === Load + interpolate ===
systems = {}  # {base: {"CLEAR": arr%, "TINTED": arr%}}
for path in sorted(glob.glob(os.path.join(FOLDER, "*.csv"))):
    fname = os.path.splitext(os.path.basename(path))[0]
    state, base = parse_state_and_base(fname)
    if state is None:
        continue

    df = to_percent(load_curve_csv(path))
    df = df[(df["wl"] >= WL_MIN) & (df["wl"] <= WL_MAX)]
    if df.empty:
        continue

    systems.setdefault(base, {})[state] = interp_to_grid(df, grid)

keys = sorted([k for k, v in systems.items() if "CLEAR" in v and "TINTED" in v])
print(len(keys))
if not keys:
    raise RuntimeError("Δεν βρέθηκαν ζευγάρια CLEAR/TINTED. Έλεγξε ονόματα αρχείων και φάκελο.")

# === Colors (one per system) ===
palette = px.colors.qualitative.Dark24  # 24 distinct colors
def color_for(i): return palette[i % len(palette)]

# === Build interactive figure ===
fig = go.Figure()

for i, k in enumerate(keys):
    col = color_for(i)

    cold = systems[k]["CLEAR"]
    hot  = systems[k]["TINTED"]

    mc = ~np.isnan(cold)
    mh = ~np.isnan(hot)

    label = k.replace("EC_", "")

    # COLD: solid
    fig.add_trace(go.Scatter(
        x=grid[mc], y=cold[mc],
        mode="lines",
        name=label,                 # legend entry (ONE per system)
        legendgroup=label,          # group cold+hot together
        line=dict(color=col, width=2, dash="solid"),
        hovertemplate="System: %{legendgroup}<br>State: CLEAR<br>λ=%{x} nm<br>T=%{y:.2f}%<extra></extra>"
    ))

    # HOT: dashed (same color) - hide from legend to avoid duplicate entry
    fig.add_trace(go.Scatter(
        x=grid[mh], y=hot[mh],
        mode="lines",
        name=label + " (TINTED)",
        legendgroup=label,
        showlegend=False,           # IMPORTANT: no duplicate legend
        line=dict(color=col, width=2, dash="dash"),
        hovertemplate="System: %{legendgroup}<br>State: TINTED<br>λ=%{x} nm<br>T=%{y:.2f}%<extra></extra>"
    ))

fig.update_layout(
    title="Transmittance spectra per system (CLEAR solid / TINTED dashed)",
    xaxis_title="Wavelength (nm)",
    yaxis_title="Transmittance (%)",
    hovermode="x unified",
    legend_title="Click to hide/show systems",
    template="plotly_white",
    width=1200, height=650
)

# 1) Ανοίγει σε browser από Python:
fig.show()

# 2) Αν θες να το έχεις ως αρχείο (offline):
# fig.write_html("spectra_interactive.html", include_plotlyjs="cdn")