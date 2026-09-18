import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import sys
import subprocess

# =============================================================================
# REV 1 - IMPROVED PYTHON SOLVER
# Features: Pinned Supports, Beta Angles, Local/Global Axes, DOF
# =============================================================================

# =============================================================================
# 1. CREATE NODES FOR A 6m x 6m x 6m CUBE
# =============================================================================
nodes = np.array([
    [0.0, 0.0, 0.0],   # node 0 (bottom, supported)
    [6.0, 0.0, 0.0],   # node 1 (bottom, supported)
    [6.0, 6.0, 0.0],   # node 2 (bottom, supported)
    [0.0, 6.0, 0.0],   # node 3 (bottom, supported)
    [0.0, 0.0, 6.0],   # node 4 (top)
    [6.0, 0.0, 6.0],   # node 5 (top)
    [6.0, 6.0, 6.0],   # node 6 (top)
    [0.0, 6.0, 6.0]    # node 7 (top)
])

# =============================================================================
# 2. CREATE MEMBER INCIDENCES (i = start, j = end)
# =============================================================================
members = [
    # bottom face (z=0)
    (0, 1), (1, 2), (2, 3), (3, 0),
    # top face (z=6)
    (4, 5), (5, 6), (6, 7), (7, 4),
    # vertical edges
    (0, 4), (1, 5), (2, 6), (3, 7)
]

members_array = np.array(members)

# =============================================================================
# 3. ADD SUPPORT CONDITIONS (Pinned Supports at Bottom Nodes)
# =============================================================================
# Pinned support: Restrains translations in X, Y, Z (DOF 1, 2, 3)
# Free rotations: RX, RY, RZ (DOF 4, 5, 6)
# Node indices 0, 1, 2, 3 are at the bottom (Y=0)

supports = {}
for node_id in [0, 1, 2, 3]:
    supports[node_id] = {
        'type': 'Pinned',
        'restraints': [True, True, True, False, False, False],  # DX, DY, DZ, RX, RY, RZ
        'symbol': '🔺'
    }

# =============================================================================
# 4. ADD BETA ANGLE (Rotation about local x-axis)
# =============================================================================
# Beta angle is the roll angle of the member's local axes about its local x-axis
# For this example, we'll assign a beta angle to each member (default 0)
# In a real solver, this would be used to transform local to global stiffness

beta_angles = {}
for idx in range(len(members)):
    beta_angles[idx] = 0.0  # Default beta angle in degrees

# Example: Assign a 30-degree beta angle to member 8 (first vertical member)
beta_angles[8] = 30.0

# =============================================================================
# 5. ADD LOCAL AND GLOBAL AXES
# =============================================================================
# Global axes: X, Y, Z (Y is vertical)
# Local axes for each member: 
#   Local x: along member axis (from i to j)
#   Local y: perpendicular to local x (in the plane of the member)
#   Local z: perpendicular to both local x and local y (right-hand rule)

def compute_local_axes(node_i, node_j, beta_deg=0.0):
    """
    Compute local axes for a member from node i to node j.
    Returns local x, y, z unit vectors in global coordinates.
    Beta angle rotates the local y and z axes about the local x axis.
    """
    # Vector along member (local x)
    vec = node_j - node_i
    L = np.linalg.norm(vec)
    if L < 1e-12:
        raise ValueError("Zero-length member")
    local_x = vec / L

    # Choose a reference vector not parallel to local_x
    # Use global Y (vertical) as reference if member is not vertical
    if abs(local_x[1]) < 0.99:  # Not vertical
        ref = np.array([0.0, 1.0, 0.0])  # Global Y
    else:
        ref = np.array([1.0, 0.0, 0.0])  # Global X if member is vertical

    # Local z (perpendicular to local_x and ref)
    local_z = np.cross(local_x, ref)
    local_z = local_z / np.linalg.norm(local_z)

    # Local y (perpendicular to local_x and local_z)
    local_y = np.cross(local_z, local_x)
    local_y = local_y / np.linalg.norm(local_y)

    # Apply beta angle rotation about local x
    beta_rad = np.radians(beta_deg)
    cos_b = np.cos(beta_rad)
    sin_b = np.sin(beta_rad)

    # Rotate local_y and local_z about local_x
    local_y_rot = cos_b * local_y + sin_b * local_z
    local_z_rot = -sin_b * local_y + cos_b * local_z

    return local_x, local_y_rot, local_z_rot

# Compute local axes for all members
local_axes = {}
for idx, (i, j) in enumerate(members):
    local_axes[idx] = compute_local_axes(nodes[i], nodes[j], beta_angles[idx])

# =============================================================================
# 6. ADD DEGREES OF FREEDOM (DOF) FOR EACH NODE
# =============================================================================
# Each node has 6 DOF: DX, DY, DZ (translations), RX, RY, RZ (rotations)
# DOF numbering: Node n has DOF 6n+0 to 6n+5

dof_labels = ['DX', 'DY', 'DZ', 'RX', 'RY', 'RZ']

# Build DOF table
dof_data = []
for node_id in range(len(nodes)):
    for dof_idx, dof_name in enumerate(dof_labels):
        restrained = False
        if node_id in supports:
            restrained = supports[node_id]['restraints'][dof_idx]
        dof_data.append({
            'Node': node_id,
            'DOF': dof_name,
            'Global DOF #': 6 * node_id + dof_idx,
            'Restrained': 'Yes' if restrained else 'No'
        })

df_dof = pd.DataFrame(dof_data)

# =============================================================================
# 7. CREATE EXCEL FILE WITH MULTIPLE TABS
# =============================================================================
# Tab 1: Nodes
df_nodes = pd.DataFrame(nodes, columns=['X (m)', 'Y (m)', 'Z (m)'])
df_nodes.index.name = 'Node ID'

# Tab 2: Members (incidences) with beta angle
df_members = pd.DataFrame(members_array, columns=['i (start node)', 'j (end node)'])
df_members.index.name = 'Member ID'
df_members['Beta Angle (deg)'] = [beta_angles[i] for i in range(len(members))]
df_members['Connection'] = df_members.apply(
    lambda row: f"Node {int(row['i (start node)'])} → Node {int(row['j (end node)'])}", 
    axis=1
)

# Tab 3: Supports
support_data = []
for node_id, support in supports.items():
    support_data.append({
        'Node': node_id,
        'Support Type': support['type'],
        'DX': 'Restrained' if support['restraints'][0] else 'Free',
        'DY': 'Restrained' if support['restraints'][1] else 'Free',
        'DZ': 'Restrained' if support['restraints'][2] else 'Free',
        'RX': 'Restrained' if support['restraints'][3] else 'Free',
        'RY': 'Restrained' if support['restraints'][4] else 'Free',
        'RZ': 'Restrained' if support['restraints'][5] else 'Free',
    })
df_supports = pd.DataFrame(support_data)
df_supports.index.name = 'Support ID'

# Tab 4: Degrees of Freedom
df_dof_sheet = df_dof.copy()
df_dof_sheet.index.name = 'DOF ID'

# Tab 5: Local Axes
local_axes_data = []
for idx, (lx, ly, lz) in local_axes.items():
    local_axes_data.append({
        'Member': idx,
        'Local x (X)': lx[0], 'Local x (Y)': lx[1], 'Local x (Z)': lx[2],
        'Local y (X)': ly[0], 'Local y (Y)': ly[1], 'Local y (Z)': ly[2],
        'Local z (X)': lz[0], 'Local z (Y)': lz[1], 'Local z (Z)': lz[2],
        'Beta Angle (deg)': beta_angles[idx]
    })
df_local_axes = pd.DataFrame(local_axes_data)
df_local_axes.index.name = 'Member ID'

# Write to Excel file
excel_filename = 'cube_6m_rev1.xlsx'
with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
    df_nodes.to_excel(writer, sheet_name='Nodes')
    df_members.to_excel(writer, sheet_name='Members (Incidences)')
    df_supports.to_excel(writer, sheet_name='Supports')
    df_dof_sheet.to_excel(writer, sheet_name='Degrees of Freedom')
    df_local_axes.to_excel(writer, sheet_name='Local Axes')

print(f"✅ Excel file '{excel_filename}' created successfully.")
print("  - Sheet 'Nodes': Node coordinates")
print("  - Sheet 'Members (Incidences)': Member i, j, beta angles")
print("  - Sheet 'Supports': Pinned support conditions")
print("  - Sheet 'Degrees of Freedom': DOF for each node")
print("  - Sheet 'Local Axes': Local axes vectors for each member")

# =============================================================================
# 8. AUTOMATICALLY OPEN THE EXCEL FILE
# =============================================================================
def open_excel_file(filename):
    try:
        if sys.platform == 'win32':
            os.startfile(filename)
        elif sys.platform == 'darwin':
            subprocess.run(['open', filename])
        else:
            subprocess.run(['xdg-open', filename])
        print(f"📂 Opening '{filename}' in Excel...")
        return True
    except Exception as e:
        print(f"⚠️ Could not automatically open Excel file: {e}")
        print(f"   Please open '{filename}' manually.")
        return False

open_excel_file(excel_filename)

# =============================================================================
# 9. PLOT USING MATPLOTLIB
# =============================================================================
fig = plt.figure(figsize=(14, 11))
ax = fig.add_subplot(111, projection='3d')

# Plot members as lines with local axes
for idx, (i, j) in enumerate(members):
    x = [nodes[i, 0], nodes[j, 0]]
    y = [nodes[i, 1], nodes[j, 1]]
    z = [nodes[i, 2], nodes[j, 2]]
    
    # Color members differently if they have non-zero beta angle
    color = 'orange' if beta_angles[idx] != 0 else 'blue'
    ax.plot(x, y, z, color=color, linewidth=2)
    
    # Member label at midpoint
    mid = (nodes[i] + nodes[j]) / 2
    ax.text(mid[0], mid[1], mid[2], f'M{idx}', size=8, color='green',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# Plot nodes
ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], 
           color='red', s=80, label='Nodes', zorder=5)

# Add node labels
for idx, (x, y, z) in enumerate(nodes):
    ax.text(x, y, z, f'N{idx}', size=11, color='black',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.8))

# -----------------------------------------------------------------------------
# PLOT SUPPORTS (Pinned Symbols)
# -----------------------------------------------------------------------------
for node_id, support in supports.items():
    x, y, z = nodes[node_id]
    # Draw a triangle (pinned support symbol) below the node
    tri_size = 0.5
    tri_verts = np.array([
        [x, y - tri_size, z],
        [x - tri_size*0.866, y - tri_size*1.5, z],
        [x + tri_size*0.866, y - tri_size*1.5, z],
        [x, y - tri_size, z]  # close the triangle
    ])
    ax.plot(tri_verts[:, 0], tri_verts[:, 1], tri_verts[:, 2], 
            color='darkgreen', linewidth=2)
    # Add a small line below the triangle
    ax.plot([x, x], [y - tri_size*1.5, y - tri_size*2.0], 
            color='darkgreen', linewidth=2)
    # Label
    ax.text(x, y - tri_size*2.5, z, f'Pinned', size=8, color='darkgreen',
            ha='center', fontweight='bold')

# -----------------------------------------------------------------------------
# PLOT LOCAL AXES (for selected members to avoid clutter)
# -----------------------------------------------------------------------------
# Plot local axes for member 8 (vertical member with beta=30°) and member 0
members_to_show_axes = [0, 8]
axis_scale = 1.5

for member_idx in members_to_show_axes:
    i, j = members[member_idx]
    mid = (nodes[i] + nodes[j]) / 2
    lx, ly, lz = local_axes[member_idx]
    
    # Local x (red)
    ax.quiver(mid[0], mid[1], mid[2], lx[0], lx[1], lx[2], 
              length=axis_scale, color='red', arrow_length_ratio=0.2, linewidth=2)
    # Local y (green)
    ax.quiver(mid[0], mid[1], mid[2], ly[0], ly[1], ly[2], 
              length=axis_scale, color='green', arrow_length_ratio=0.2, linewidth=2)
    # Local z (blue)
    ax.quiver(mid[0], mid[1], mid[2], lz[0], lz[1], lz[2], 
              length=axis_scale, color='blue', arrow_length_ratio=0.2, linewidth=2)
    
    ax.text(mid[0] + lx[0]*axis_scale, mid[1] + lx[1]*axis_scale, mid[2] + lx[2]*axis_scale,
            'Local x', color='red', size=8)
    ax.text(mid[0] + ly[0]*axis_scale, mid[1] + ly[1]*axis_scale, mid[2] + ly[2]*axis_scale,
            'Local y', color='green', size=8)
    ax.text(mid[0] + lz[0]*axis_scale, mid[1] + lz[1]*axis_scale, mid[2] + lz[2]*axis_scale,
            'Local z', color='blue', size=8)

# -----------------------------------------------------------------------------
# PLOT GLOBAL AXES at origin
# -----------------------------------------------------------------------------
global_axis_scale = 2.0
ax.quiver(0, 0, 0, global_axis_scale, 0, 0, color='darkred', 
          arrow_length_ratio=0.15, linewidth=2)
ax.quiver(0, 0, 0, 0, global_axis_scale, 0, color='darkgreen', 
          arrow_length_ratio=0.15, linewidth=2)
ax.quiver(0, 0, 0, 0, 0, global_axis_scale, color='darkblue', 
          arrow_length_ratio=0.15, linewidth=2)
ax.text(global_axis_scale, 0, 0, 'Global X', color='darkred', size=9, fontweight='bold')
ax.text(0, global_axis_scale, 0, 'Global Y', color='darkgreen', size=9, fontweight='bold')
ax.text(0, 0, global_axis_scale, 'Global Z', color='darkblue', size=9, fontweight='bold')

# -----------------------------------------------------------------------------
# AXIS LABELS AND TITLE
# -----------------------------------------------------------------------------
ax.set_xlabel('X (lateral) [m]')
ax.set_ylabel('Y (vertical) [m]')
ax.set_zlabel('Z (lateral) [m]')

max_range = 6.0
mid_x, mid_y, mid_z = 3.0, 3.0, 3.0
ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
ax.set_ylim(mid_y - max_range/2 - 1, mid_y + max_range/2)  # extra space for supports
ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)

ax.set_title('6m Cube - Rev 1\nPinned Supports | Beta Angles | Local & Global Axes | DOF', 
             fontsize=12, fontweight='bold')

# Custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='blue', lw=2, label='Member (beta=0°)'),
    Line2D([0], [0], color='orange', lw=2, label='Member (beta≠0°)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Node'),
    Line2D([0], [0], color='darkgreen', lw=2, label='Pinned Support'),
    Line2D([0], [0], color='red', lw=2, label='Local x-axis'),
    Line2D([0], [0], color='green', lw=2, label='Local y-axis'),
    Line2D([0], [0], color='blue', lw=2, label='Local z-axis'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=8)

plt.tight_layout()
plt.show()

# =============================================================================
# 10. PRINT SUMMARY
# =============================================================================
print("\n" + "="*70)
print("REV 1 - CUBE STRUCTURE SUMMARY WITH ENHANCED FEATURES")
print("="*70)

print("\n📌 NODES:")
print("-"*40)
for idx, (x, y, z) in enumerate(nodes):
    support_info = f" [PINNED]" if idx in supports else ""
    print(f"  Node {idx}: ({x:.1f}, {y:.1f}, {z:.1f}) m{support_info}")

print("\n📌 MEMBER INCIDENCES (i=start, j=end) + Beta Angles:")
print("-"*50)
for idx, (i, j) in enumerate(members):
    beta = beta_angles[idx]
    beta_str = f" | Beta = {beta:.1f}°" if beta != 0 else ""
    print(f"  Member {idx:2d}: Node {i} → Node {j}{beta_str}")

print("\n📌 SUPPORT CONDITIONS:")
print("-"*40)
for node_id, support in supports.items():
    r = support['restraints']
    restrained_dof = [dof_labels[i] for i, val in enumerate(r) if val]
    print(f"  Node {node_id}: {support['type']} - Restrained DOF: {', '.join(restrained_dof)}")

print("\n📌 DEGREES OF FREEDOM (per node):")
print("-"*40)
print(f"  Each node has 6 DOF: {', '.join(dof_labels)}")
print(f"  Total DOF in system: {len(nodes) * 6}")
print(f"  Restrained DOF: {sum(1 for d in df_dof['Restrained'] if d == 'Yes')}")
print(f"  Free DOF: {sum(1 for d in df_dof['Restrained'] if d == 'No')}")

print("\n📌 LOCAL AXES (for members with beta angles):")
print("-"*40)
for idx, beta in beta_angles.items():
    if beta != 0:
        lx, ly, lz = local_axes[idx]
        print(f"  Member {idx} (Beta = {beta}°):")
        print(f"    Local x: ({lx[0]:.3f}, {lx[1]:.3f}, {lx[2]:.3f})")
        print(f"    Local y: ({ly[0]:.3f}, {ly[1]:.3f}, {ly[2]:.3f})")
        print(f"    Local z: ({lz[0]:.3f}, {lz[1]:.3f}, {lz[2]:.3f})")

print("\n" + "="*70)
print(f"✅ Total nodes: {len(nodes)}")
print(f"✅ Total members: {len(members)}")
print(f"✅ Total DOF: {len(nodes) * 6}")
print(f"✅ Excel file: {excel_filename}")
print("="*70)

# =============================================================================
# 11. SAVE ADDITIONAL CSV FILES FOR QUICK REFERENCE
# =============================================================================
df_members.to_csv('member_incidences_rev1.csv')
df_dof.to_csv('degrees_of_freedom_rev1.csv', index=False)
df_supports.to_csv('supports_rev1.csv')
df_local_axes.to_csv('local_axes_rev1.csv')

print("\n📁 Additional CSV files created:")
print("   - member_incidences_rev1.csv")
print("   - degrees_of_freedom_rev1.csv")
print("   - supports_rev1.csv")
print("   - local_axes_rev1.csv")
print(f"\n📂 Current working directory: {os.getcwd()}")