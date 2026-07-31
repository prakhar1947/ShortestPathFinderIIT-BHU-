import os
from flask_cors import CORS
from collections import defaultdict
from heapq import heappush, heappop
from math import hypot
from flask import Flask, jsonify, abort

app = Flask(__name__, static_folder='../client/build', static_url_path='')

# Dynamic CORS configuration via FRONTEND_URL or ALLOWED_ORIGINS env variables
allowed_origins_env = os.environ.get("FRONTEND_URL") or os.environ.get("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    origins = [
        "https://shortest-path-finder-delta.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "*"
    ]

CORS(app, origins=origins)

# ---------------------------------------------------------------------------
# NODES: slug -> (Display Name, x, y)
#
# The (x, y) values are APPROXIMATE pixel coordinates read off the campus map
# image you uploaded (arbitrary units, not real-world meters/GPS). They are
# only used to derive relative distances between connected buildings via
# straight-line (Euclidean) distance * DIST_SCALE below.
#
# This means the "totalDis" the API returns is an ESTIMATE, not a surveyed
# distance. If you have real distances (measured, or GPS lat/lon) for any
# edge, replace the coordinates or hardcode that edge's weight instead.
# ---------------------------------------------------------------------------
NODES = {
    # --- Top compound ---
    "biomedical_dept": ("Biomedical Dept.", 1525, 110),
    "lt2": ("LT-2 (Mathematics & Comp. Office)", 1360, 235),
    "computer_science_dept": ("Computer Science Dept.", 1105, 340),
    "mathematics_comp_dept": ("Mathematics & Comp. Dept.", 1360, 345),
    "swatantrata_bhawan": ("Swatantrata Bhawan", 1780, 290),

    # --- Main engineering compound ---
    "rampur_lawn": ("Rampur Lawn", 1220, 510),
    "civil_dept_a": ("Civil Dept. (block A)", 940, 595),
    "civil_dept_b": ("Civil Dept. (block B)", 1010, 660),
    "mechanical_dept_a": ("Mechanical Dept. (block A)", 1220, 585),
    "electrical_dept": ("Electrical Dept.", 1350, 585),
    "exam_scholarship_section": ("Examination & Scholarship Section", 1490, 585),
    "sakha_office": ("Sakha Office", 1110, 675),
    "mechanical_dept_b": ("Mechanical Dept. (block B)", 1225, 650),
    "architecture_dept": ("Architecture Dept.", 1310, 650),
    "mechanical_dept_c": ("Mechanical Dept. (block C)", 1360, 660),
    "chemistry_dept": ("Chemistry Dept.", 1460, 685),
    "electronics_dept": ("Electronics Dept.", 940, 785),
    "main_workshop": ("Main Workshop", 1095, 785),
    "ncc_office_humanistic_dept": ("NCC Office & Humanistic Dept.", 1240, 785),
    "manufacturing_workshop": ("Manufacturing Workshop", 1380, 785),
    "cafeteria": ("Cafeteria", 1540, 795),
    "ncc_ground": ("NCC Ground", 1220, 870),
    "iwd": ("IWD", 1480, 860),
    "lt1": ("LT-1", 1560, 865),

    # --- Chemical / science compound ---
    "ecell_incubation_centre": ("Ecell Incubation Centre", 1715, 620),
    "chemical_dept": ("Chemical Dept.", 1830, 610),
    "biochemical_dept": ("Biochemical Dept.", 1990, 610),
    "proctor_office": ("Proctor Office", 1695, 735),
    "ceramic_dept": ("Ceramic Dept.", 1770, 735),
    "physics_dept": ("Physics Dept.", 1845, 735),
    "pharmaceutical_dept": ("Pharmaceutical Dept.", 1940, 735),
    "school_material_science_tech": ("School of Material Science & Technology", 1710, 845),
    "lt3": ("LT-3", 1845, 840),

    # --- Left column ---
    "metallurgy_dept": ("Metallurgy Dept.", 200, 590),
    "mining_dept": ("Mining Dept.", 200, 765),
    "central_library": ("Central Library", 495, 650),
    "botony_dept": ("Botony Dept.", 495, 830),
    "agriculture_dept": ("Agriculture Department", 680, 590),
    "shatabdi_bhawan": ("Shatabdi Bhawan", 680, 830),

    # --- Gate ---
    "iit_bhu_gate": ("IIT BHU Gate", 795, 925),

    # --- Row 3: temple / library / grounds ---
    "shops": ("Shops", 480, 1000),
    "vishwanath_temple": ("Vishwanath Temple (VT)", 480, 1110),
    "health_centre": ("Health Centre", 145, 1105),
    "lotus_pond": ("Lotus Pond", 885, 1000),
    "director_office": ("Director Office", 990, 1000),
    "iit_bhu_library": ("IIT(BHU) Library", 1105, 995),
    "tpc_office": ("TPC Office", 990, 1050),
    "reading_room": ("Reading Room", 1105, 1045),
    "ablt": ("ABLT 1-2-3-4", 895, 1090),
    "tlc_office_idapt_hub": ("TLC Office / IDAPT Hub", 1105, 1090),
    "sac": ("Student Activity Center (SAC)", 910, 1195),
    "rajputana_ground": ("Rajputana Ground", 1030, 1160),
    "gymkhana_ground": ("Gymkhana Ground", 1325, 1105),
    "gymkhana_building_dosa": ("Gymkhana Building & Dosa Office", 1485, 1090),
    "adv_ground": ("ADV Ground", 1795, 1105),
    "imc": ("IMC", 1980, 1025),

    # --- Corners ---
    "dg_corner": ("DG Corner", 795, 1235),
    "limbdi_corner": ("Limbdi Corner", 1215, 1235),

    # --- Hostel cluster 1 ---
    "dr_cv_raman_hostel": ("Dr. CV Raman Hostel (Boys)", 355, 1300),
    "morvi_hostel": ("Morvi Hostel (Boys)", 525, 1300),
    "dhanrajgiri_hostel": ("Dhanrajgiri Hostel (Boys)", 675, 1300),
    "pc_ray_hostel": ("PC Ray Hostel (Boys)", 500, 1400),
    "satish_dhawan_hostel": ("Satish Dhawan Hostel (Boys)", 620, 1400),
    "ramanujan_hostel": ("Ramanujan Hostel (Boys)", 725, 1400),
    "swimming_pool": ("Swimming Pool", 355, 1435),
    "aryabhatta_hostel": ("Aryabhatta 1 & 2 Hostel (Boys)", 570, 1505),
    "asn_bose_hostel": ("ASN Bose Hostel (Boys)", 720, 1505),

    # --- Hostel cluster 2 ---
    "rajputana_hostel": ("Rajputana Hostel (Boys)", 910, 1300),
    "limbdi_hostel": ("Limbdi Hostel (Girls)", 1100, 1300),
    "gsc_ext_hostel": ("GSC Ext. Hostel (Girls)", 1150, 1425),
    "visvesvaraya_hostel": ("Visvesvaraya Hostel (Boys)", 880, 1505),
    "nivedita_hostel": ("Nivedita Hostel (Girls)", 1035, 1505),
    "gsc_old_hostel": ("GSC Old Hostel (Girls)", 1140, 1505),

    # --- Hostel cluster 3 ---
    "sc_dey_hostel": ("SC Dey Hostel (Girls)", 1310, 1300),
    "vivekanand_hostel": ("Vivekanand Hostel (Boys)", 1530, 1300),
    "gtac_guest_house": ("GTAC IIT(BHU) Guest House", 1310, 1425),
    "faculty_apartments_1": ("Faculty Apartments (1)", 1495, 1400),
    "faculty_apartments_2": ("Faculty Apartments (2)", 1405, 1450),
    "vishwakarma_hostel": ("Vishwakarma Hostel (Boys)", 1545, 1450),
    "karman_veer_baba_temple": ("Karman Veer Baba Temple", 1700, 1555),

    # --- Bottom path ---
    "auto_stand": ("Auto Stand", 750, 1615),
    "mother_dairy": ("Mother Dairy", 835, 1615),
    "hyderabad_gate": ("Hyderabad Gate (HG)", 795, 1665),
}

# ---------------------------------------------------------------------------
# EDGES: which locations are directly connected by a walkable path/road,
# based on adjacency in the map image.
# ---------------------------------------------------------------------------
EDGES = [
    # Top compound
    ("biomedical_dept", "lt2"),
    ("lt2", "mathematics_comp_dept"),
    ("mathematics_comp_dept", "computer_science_dept"),
    ("computer_science_dept", "rampur_lawn"),
    ("biomedical_dept", "swatantrata_bhawan"),
    ("swatantrata_bhawan", "biochemical_dept"),

    # Main engineering compound
    ("rampur_lawn", "civil_dept_a"),
    ("civil_dept_a", "mechanical_dept_a"),
    ("mechanical_dept_a", "electrical_dept"),
    ("electrical_dept", "exam_scholarship_section"),
    ("civil_dept_a", "civil_dept_b"),
    ("civil_dept_b", "sakha_office"),
    ("sakha_office", "mechanical_dept_b"),
    ("mechanical_dept_b", "architecture_dept"),
    ("architecture_dept", "mechanical_dept_c"),
    ("mechanical_dept_c", "chemistry_dept"),
    ("civil_dept_b", "electronics_dept"),
    ("sakha_office", "main_workshop"),
    ("mechanical_dept_b", "ncc_office_humanistic_dept"),
    ("mechanical_dept_c", "manufacturing_workshop"),
    ("chemistry_dept", "cafeteria"),
    ("electronics_dept", "main_workshop"),
    ("main_workshop", "ncc_office_humanistic_dept"),
    ("ncc_office_humanistic_dept", "manufacturing_workshop"),
    ("manufacturing_workshop", "cafeteria"),
    ("electronics_dept", "ncc_ground"),
    ("main_workshop", "ncc_ground"),
    ("ncc_office_humanistic_dept", "ncc_ground"),
    ("manufacturing_workshop", "ncc_ground"),
    ("ncc_ground", "lt1"),
    ("lt1", "iwd"),
    ("iwd", "cafeteria"),
    ("ncc_ground", "iit_bhu_gate"),
    ("exam_scholarship_section", "ecell_incubation_centre"),
    ("cafeteria", "ecell_incubation_centre"),

    # Chemical / science compound
    ("ecell_incubation_centre", "chemical_dept"),
    ("chemical_dept", "biochemical_dept"),
    ("ecell_incubation_centre", "proctor_office"),
    ("chemical_dept", "ceramic_dept"),
    ("biochemical_dept", "pharmaceutical_dept"),
    ("proctor_office", "ceramic_dept"),
    ("ceramic_dept", "physics_dept"),
    ("physics_dept", "pharmaceutical_dept"),
    ("proctor_office", "school_material_science_tech"),
    ("physics_dept", "lt3"),
    ("school_material_science_tech", "lt3"),

    # Left column
    ("metallurgy_dept", "mining_dept"),
    ("central_library", "botony_dept"),
    ("agriculture_dept", "shatabdi_bhawan"),
    ("metallurgy_dept", "central_library"),
    ("central_library", "agriculture_dept"),
    ("metallurgy_dept", "civil_dept_a"),
    ("shatabdi_bhawan", "iit_bhu_gate"),

    # Gate links
    ("iit_bhu_gate", "lotus_pond"),

    # Row 3 complex
    ("shops", "vishwanath_temple"),
    ("health_centre", "vishwanath_temple"),
    ("shops", "lotus_pond"),
    ("vishwanath_temple", "dg_corner"),
    ("lotus_pond", "director_office"),
    ("director_office", "iit_bhu_library"),
    ("director_office", "tpc_office"),
    ("iit_bhu_library", "reading_room"),
    ("tpc_office", "tlc_office_idapt_hub"),
    ("ablt", "tlc_office_idapt_hub"),
    ("ablt", "sac"),
    ("tlc_office_idapt_hub", "rajputana_ground"),
    ("rajputana_ground", "dg_corner"),
    ("rajputana_ground", "limbdi_corner"),
    ("rajputana_ground", "sac"),
    ("gymkhana_ground", "gymkhana_building_dosa"),
    ("gymkhana_ground", "limbdi_corner"),
    ("adv_ground", "imc"),
    ("adv_ground", "gymkhana_ground"),

    # Down to hostels
    ("dg_corner", "morvi_hostel"),
    ("limbdi_corner", "rajputana_hostel"),
    ("limbdi_corner", "sc_dey_hostel"),

    # Hostel cluster 1
    ("dr_cv_raman_hostel", "morvi_hostel"),
    ("morvi_hostel", "dhanrajgiri_hostel"),
    ("morvi_hostel", "pc_ray_hostel"),
    ("dhanrajgiri_hostel", "ramanujan_hostel"),
    ("pc_ray_hostel", "satish_dhawan_hostel"),
    ("satish_dhawan_hostel", "ramanujan_hostel"),
    ("dr_cv_raman_hostel", "swimming_pool"),
    ("pc_ray_hostel", "aryabhatta_hostel"),
    ("ramanujan_hostel", "asn_bose_hostel"),
    ("aryabhatta_hostel", "asn_bose_hostel"),

    # Hostel cluster 2
    ("rajputana_hostel", "limbdi_hostel"),
    ("rajputana_hostel", "visvesvaraya_hostel"),
    ("limbdi_hostel", "gsc_ext_hostel"),
    ("visvesvaraya_hostel", "nivedita_hostel"),
    ("nivedita_hostel", "gsc_old_hostel"),
    ("gsc_ext_hostel", "nivedita_hostel"),

    # Hostel cluster 3
    ("sc_dey_hostel", "vivekanand_hostel"),
    ("sc_dey_hostel", "gtac_guest_house"),
    ("vivekanand_hostel", "faculty_apartments_1"),
    ("gtac_guest_house", "faculty_apartments_2"),
    ("faculty_apartments_1", "faculty_apartments_2"),
    ("faculty_apartments_2", "vishwakarma_hostel"),
    ("vishwakarma_hostel", "karman_veer_baba_temple"),
    ("karman_veer_baba_temple", "adv_ground"),

    # Bottom path
    ("auto_stand", "mother_dairy"),
    ("mother_dairy", "hyderabad_gate"),
    ("mother_dairy", "gsc_old_hostel"),
    ("auto_stand", "visvesvaraya_hostel"),
]

# Tune this once you know real-world distances for even a couple of edges.
DIST_SCALE = 0.3


def build_graph():
    g = defaultdict(list)
    for u, v in EDGES:
        _, x1, y1 = NODES[u]
        _, x2, y2 = NODES[v]
        w = round(hypot(x1 - x2, y1 - y2) * DIST_SCALE, 1)
        g[u].append((v, w))
        g[v].append((u, w))
    return g


GRAPH = build_graph()


@app.route('/')
def root():
    if os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return app.send_static_file('index.html')
    return 'Server has been started successfully!'


@app.route('/nodes')
def list_nodes():
    """Returns slug -> display name, so a frontend can build a dropdown."""
    return jsonify({slug: name for slug, (name, x, y) in NODES.items()})


@app.route('/shortd/<src>/<dst>')
def shortestPath(src, dst):
    if src not in NODES or dst not in NODES:
        abort(404, description="Unknown location slug. See /nodes for valid slugs.")

    distance = {node: float('inf') for node in NODES}
    prev = {node: None for node in NODES}
    distance[src] = 0
    heap = [(0, src)]

    # Dijkstra's algorithm
    while heap:
        dis, node = heappop(heap)
        if dis > distance[node]:
            continue
        for neigh, cost in GRAPH[node]:
            nd = dis + cost
            if nd < distance[neigh]:
                distance[neigh] = nd
                prev[neigh] = node
                heappush(heap, (nd, neigh))

    if distance[dst] == float('inf'):
        return jsonify({"from": NODES[src][0], "to": NODES[dst][0], "path": [], "totalDis": -1})

    route_slugs = []
    current = dst
    while current is not None:
        route_slugs.append(current)
        current = prev[current]
    route_slugs.reverse()

    result = {
        "from": NODES[src][0],
        "to": NODES[dst][0],
        "path": [NODES[s][0] for s in route_slugs],
        "pathSlugs": route_slugs,
        "totalDis": distance[dst],
    }
    return jsonify(result)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5010))  # Render sets the PORT variable
    app.run(host='0.0.0.0', port=port)