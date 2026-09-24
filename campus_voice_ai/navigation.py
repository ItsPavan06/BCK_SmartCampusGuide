"""
navigation.py
-------------
This module handles route calculation, shortest pathfinding, and step-by-step
campus directions for requested destinations.

It takes a destination payload (e.g. from Prathiksha's AI module) and generates
human-readable turn-by-turn navigation instructions.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import math

# Default physical location of the Kiosk on campus
# Configured for Admin Block installation
DEFAULT_KIOSK_LOCATION = "admin_block"

# Campus locations registry with canonical IDs, display names, and details
CAMPUS_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "main_gate": {
        "name": "Main Entrance Gate",
        "block": "Entrance",
        "aliases": ["main gate", "gate", "entrance", "main entrance"]
    },
    "block_a": {
        "name": "Block A (Arts & Commerce)",
        "block": "Block A",
        "aliases": ["block a", "arts block", "commerce block"]
    },
    "block_b": {
        "name": "Block B (BCA & Science)",
        "block": "Block B",
        "aliases": ["block b", "bca department", "cs department", "science block", "bca"]
    },
    "library": {
        "name": "Central Library",
        "block": "Block B - 2nd Floor",
        "aliases": ["library", "central library", "reading room", "book bank"]
    },
    "canteen": {
        "name": "Campus Canteen",
        "block": "Student Amenities Block",
        "aliases": ["canteen", "cafeteria", "food court", "mess"]
    },
    "computer_lab": {
        "name": "Computer Science Lab",
        "block": "Block B - 1st Floor",
        "aliases": ["computer lab", "cs lab", "it lab", "programming lab"]
    },
    "principal_office": {
        "name": "Principal's Office",
        "block": "Admin Block - First Floor",
        "aliases": ["principal office", "principal's office", "principal cabin"]
    },
    "admin_block": {
        "name": "Administrative Office",
        "block": "Admin Block",
        "aliases": ["admin block", "admin office", "accounts section", "admission office"]
    },
    "auditorium": {
        "name": "Main Auditorium",
        "block": "Auditorium Complex",
        "aliases": ["auditorium", "audi", "seminar hall", "conference hall"]
    },
    "sports_complex": {
        "name": "Sports Complex & Ground",
        "block": "Sports Block",
        "aliases": ["sports complex", "gym", "playground", "sports ground"]
    },
    "parking": {
        "name": "Vehicle Parking Area",
        "block": "Main Gate West Wing",
        "aliases": ["parking", "parking lot", "bike stand", "vehicle parking"]
    },
    "hostel": {
        "name": "Student Hostels",
        "block": "Residential Zone",
        "aliases": ["hostel", "boys hostel", "girls hostel", "dormitory"]
    },
    "placement_cell": {
        "name": "Training & Placement Cell",
        "block": "Admin Block - 1st Floor",
        "aliases": ["placement cell", "tnp cell", "career center"]
    }
}

# Campus path adjacency list graph: (node_a, node_b, distance_in_meters, instruction_description)
CAMPUS_GRAPH_EDGES = [
    ("main_gate", "block_a", 50, "Walk straight along the main paved avenue past the fountain."),
    ("main_gate", "admin_block", 40, "Turn right at the entrance security booth towards Admin Block."),
    ("main_gate", "parking", 30, "Turn left at the entrance security booth into the Parking Area."),
    ("block_a", "block_b", 60, "Continue straight past Block A courtyard towards Block B."),
    ("block_a", "auditorium", 70, "Turn left at Block A corridor towards the Main Auditorium."),
    ("block_b", "library", 20, "Take the central stairs/elevator in Block B to the 2nd floor."),
    ("block_b", "computer_lab", 15, "Take the central stairs in Block B to the 1st floor, room 104."),
    ("block_b", "canteen", 45, "Exit Block B rear door and follow the covered walkway to the Canteen."),
    ("admin_block", "principal_office", 10, "Enter Admin Block main lobby; Principal's cabin is on the ground floor right."),
    ("admin_block", "placement_cell", 25, "Take the Admin Block main stairs to the 1st floor Placement Cell."),
    ("canteen", "sports_complex", 80, "Walk past the canteen garden along the perimeter path to the Sports Complex."),
    ("sports_complex", "hostel", 90, "Follow the tree-lined path behind the sports ground to the Student Hostels.")
]


def _build_adjacency_matrix() -> Dict[str, List[Tuple[str, int, str]]]:
    """Builds an undirected adjacency list graph from edges."""
    adj: Dict[str, List[Tuple[str, int, str]]] = {node: [] for node in CAMPUS_LOCATIONS}
    for u, v, dist, desc in CAMPUS_GRAPH_EDGES:
        adj[u].append((v, dist, desc))
        adj[v].append((u, dist, desc))
    return adj


ADJACENCY_GRAPH = _build_adjacency_matrix()


def resolve_location_id(location_query: Union[str, List[str]]) -> Optional[Union[str, List[str]]]:
    """Resolves a raw location string, alias, or list of locations into canonical location ID(s)."""
    if not location_query:
        return None
    
    if isinstance(location_query, list):
        resolved_list = []
        for item in location_query:
            res = resolve_location_id(item)
            if res and isinstance(res, str) and res not in resolved_list:
                resolved_list.append(res)
        return resolved_list if resolved_list else None

    query = str(location_query).strip().lower()
    
    # Exact key match
    if query in CAMPUS_LOCATIONS:
        return query

    # Alias search
    for loc_id, data in CAMPUS_LOCATIONS.items():
        for alias in data["aliases"]:
            if alias in query:
                return loc_id

    return None


def calculate_shortest_path(start_id: str, dest_id: str) -> Tuple[List[str], int, List[str]]:
    """
    Computes shortest path between two campus locations using Dijkstra's algorithm.

    Returns:
        Tuple of (node_path, total_distance_meters, step_instructions)
    """
    if start_id not in CAMPUS_LOCATIONS or dest_id not in CAMPUS_LOCATIONS:
        return ([], 0, [])

    if start_id == dest_id:
        return ([start_id], 0, [f"You are already at {CAMPUS_LOCATIONS[start_id]['name']}."])

    # Dijkstra initialization
    distances: Dict[str, float] = {node: float('inf') for node in CAMPUS_LOCATIONS}
    previous: Dict[str, Optional[str]] = {node: None for node in CAMPUS_LOCATIONS}
    edge_descriptions: Dict[Tuple[str, str], str] = {}
    
    for u, v, d, desc in CAMPUS_GRAPH_EDGES:
        edge_descriptions[(u, v)] = desc
        edge_descriptions[(v, u)] = desc

    distances[start_id] = 0
    unvisited = set(CAMPUS_LOCATIONS.keys())

    while unvisited:
        # Node with smallest distance in unvisited
        current = min(unvisited, key=lambda node: distances[node])
        
        if distances[current] == float('inf') or current == dest_id:
            break

        unvisited.remove(current)

        for neighbor, weight, desc in ADJACENCY_GRAPH[current]:
            if neighbor in unvisited:
                alt = distances[current] + weight
                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    previous[neighbor] = current

    # Reconstruct path
    path = []
    curr: Optional[str] = dest_id
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    if path[0] != start_id:
        return ([], 0, [])  # No path found

    total_dist = int(distances[dest_id])

    # Build step-by-step instructions
    instructions = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        desc = edge_descriptions.get((u, v), f"Walk from {CAMPUS_LOCATIONS[u]['name']} to {CAMPUS_LOCATIONS[v]['name']}.")
        step_num = i + 1
        instructions.append(f"Step {step_num}: {desc}")

    dest_name = CAMPUS_LOCATIONS[dest_id]['name']
    dest_block = CAMPUS_LOCATIONS[dest_id]['block']
    instructions.append(f"Arrive at {dest_name} ({dest_block}).")

    return (path, total_dist, instructions)


def get_directions(destination_query: Union[str, List[str]], start_location_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Main navigation API entry point. Receives single or multiple destinations,
    calculates optimal route/itinerary, and returns formatted direction payload.
    """
    effective_start = start_location_query if start_location_query else DEFAULT_KIOSK_LOCATION
    resolved_dest = resolve_location_id(destination_query)
    start_id = resolve_location_id(effective_start)
    if isinstance(start_id, list):
        start_id = start_id[0] if start_id else DEFAULT_KIOSK_LOCATION
    if not start_id:
        start_id = DEFAULT_KIOSK_LOCATION

    if not resolved_dest:
        return {
            "status": "error",
            "message": f"Destination '{destination_query}' was not recognized on the campus map.",
            "destination": destination_query,
            "directions_text": f"Sorry, could not find location '{destination_query}' on the campus map."
        }

    # Handle multi-destination itinerary
    if isinstance(resolved_dest, list):
        all_steps = []
        total_dist_m = 0
        current_start = start_id
        dest_names = []

        for idx, dest_id in enumerate(resolved_dest, start=1):
            path, dist, steps = calculate_shortest_path(current_start, dest_id)
            total_dist_m += dist
            dest_name = CAMPUS_LOCATIONS[dest_id]["name"]
            dest_names.append(dest_name)
            
            all_steps.append(f"--- Leg {idx}: To {dest_name} ---")
            all_steps.extend(steps)
            current_start = dest_id

        est_time_min = max(1, math.ceil(total_dist_m / 70)) if total_dist_m > 0 else 0
        start_name = CAMPUS_LOCATIONS[start_id]["name"]
        d_summary_names = " and ".join(dest_names)

        formatted_summary = (
            f"Multi-stop route to {d_summary_names}: Starting from {start_name}, total distance is approximately {total_dist_m} meters, "
            f"taking about {est_time_min} minute{'s' if est_time_min != 1 else ''}. "
            + " ".join([s for s in all_steps if not s.startswith("---")])
        )

        return {
            "status": "success",
            "destination_id": resolved_dest,
            "destination_name": dest_names,
            "start_name": start_name,
            "total_distance_meters": total_dist_m,
            "estimated_time_minutes": est_time_min,
            "steps": all_steps,
            "directions_text": formatted_summary
        }

    # Single destination route
    dest_id = resolved_dest
    path, total_dist_m, steps = calculate_shortest_path(start_id, dest_id)
    est_time_min = max(1, math.ceil(total_dist_m / 70)) if total_dist_m > 0 else 0

    dest_name = CAMPUS_LOCATIONS[dest_id]["name"]
    start_name = CAMPUS_LOCATIONS[start_id]["name"]

    formatted_summary = (
        f"Route to {dest_name}: Starting from {start_name}, total distance is approximately {total_dist_m} meters, "
        f"taking about {est_time_min} minute{'s' if est_time_min != 1 else ''}. "
        + " ".join(steps)
    )

    return {
        "status": "success",
        "destination_id": dest_id,
        "destination_name": dest_name,
        "location_block": CAMPUS_LOCATIONS[dest_id]["block"],
        "start_name": start_name,
        "total_distance_meters": total_dist_m,
        "estimated_time_minutes": est_time_min,
        "steps": steps,
        "directions_text": formatted_summary
    }


if __name__ == "__main__":
    # Test execution
    print("Testing Navigation Module...")
    res = get_directions("library")
    print(f"Status: {res['status']}")
    print(f"Destination: {res['destination_name']}")
    print(f"Directions Text:\n{res['directions_text']}")
