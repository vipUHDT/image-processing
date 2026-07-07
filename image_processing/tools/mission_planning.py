"""Survey-mission planning: lawnmower waypoint grids, exports, and map previews."""

import json
import math

from pyproj import Transformer
from shapely.geometry import Polygon


def haversine_distance(point1, point2):
    """Return the great-circle distance in meters between two ``(lat, lon, alt)`` points."""
    lat1, lon1, _ = point1
    lat2, lon2, _ = point2

    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_total_distance(waypoints):
    """Return the total path length in meters over a sequence of ``(lat, lon, alt)`` waypoints."""
    return sum(haversine_distance(waypoints[i - 1], waypoints[i])
               for i in range(1, len(waypoints)))


def rotate_point_local(point, angle):
    """Rotate a 2-D point around the origin by ``angle`` radians."""
    x, y = point
    return (x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle))


def plan_mission(airdrop_coords, photo_width_px, photo_height_px,
                 horizontal_fov_deg, vertical_fov_deg, overlap_percent,
                 altitude=100, row_traversal=False):
    """
    Plan a lawnmower survey pattern covering a polygonal search area.

    The area is projected to UTM, aligned to its minimum rotated rectangle,
    and tiled with camera footprints computed from the flight altitude and
    field of view, spaced for the requested overlap.

    Parameters
    ----------
    airdrop_coords : list[tuple[float, float]]
        Boundary vertices as ``(lat, lon)`` pairs.
    photo_width_px, photo_height_px : int
        Image resolution (currently informational).
    horizontal_fov_deg, vertical_fov_deg : float
        Camera field of view in degrees.
    overlap_percent : float
        Desired overlap between adjacent footprints, 0-100.
    altitude : float, optional
        Flight altitude in meters (default 100).
    row_traversal : bool, optional
        Traverse the grid row-by-row instead of column-by-column.

    Returns
    -------
    tuple
        ``(gps_waypoints, angle, rect_centroid, transformer_to_utm,
        transformer_from_utm, ground_width, ground_height, n_cols, n_rows,
        area_m2)`` where ``gps_waypoints`` is a list of
        ``(lat, lon, altitude)`` tuples in boustrophedon order.
    """
    h_fov_rad = math.radians(horizontal_fov_deg)
    v_fov_rad = math.radians(vertical_fov_deg)
    ground_width = 2 * altitude * math.tan(h_fov_rad / 2)
    ground_height = 2 * altitude * math.tan(v_fov_rad / 2)
    print(f"Ground Height: {ground_width} x {ground_height} m")

    step_x = ground_width * (1 - overlap_percent / 100.0)
    step_y = ground_height * (1 - overlap_percent / 100.0)

    airdrop_coords_lonlat = [(lon, lat) for lat, lon in airdrop_coords]
    area_polygon = Polygon(airdrop_coords_lonlat)
    centroid = area_polygon.centroid
    lon0, lat0 = centroid.x, centroid.y
    utm_zone = math.floor((lon0 + 180) / 6) + 1
    is_northern = (lat0 >= 0)
    proj_str = (f"+proj=utm +zone={utm_zone} +{'north' if is_northern else 'south'} "
                "+ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    transformer_to_utm = Transformer.from_crs("epsg:4326", proj_str, always_xy=True)
    transformer_from_utm = Transformer.from_crs(proj_str, "epsg:4326", always_xy=True)

    utm_polygon_coords = [transformer_to_utm.transform(lon, lat) for lon, lat in airdrop_coords_lonlat]
    utm_polygon = Polygon(utm_polygon_coords)


    min_rect = utm_polygon.minimum_rotated_rectangle
    rect_points = list(min_rect.exterior.coords)[:4]

    max_length = 0
    angle = 0
    for i in range(4):
        p1 = rect_points[i]
        p2 = rect_points[(i + 1) % 4]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > max_length:
            max_length = length
            angle = math.atan2(dy, dx)

    def rotate(point, angle, origin=(0, 0)):
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return (qx, qy)

    rect_centroid = Polygon(rect_points).centroid.coords[0]

    utm_polygon_rot = [rotate(p, -angle, origin=rect_centroid) for p in utm_polygon_coords]
    polygon_rot = Polygon(utm_polygon_rot)
    min_x, min_y, max_x, max_y = polygon_rot.bounds

    half_w = ground_width / 2.0
    half_h = ground_height / 2.0
    start_x_center = min_x + half_w
    start_y_center = min_y + half_h

    n_cols = 1 if (max_x - min_x) <= ground_width else math.ceil((max_x - min_x - ground_width) / step_x) + 1
    n_rows = 1 if (max_y - min_y) <= ground_height else math.ceil((max_y - min_y - ground_height) / step_y) + 1

    if row_traversal:
        grid = []
        for j in range(n_rows):
            row = []
            for i in range(n_cols):
                x = start_x_center + i * step_x
                y = start_y_center + j * step_y
                row.append((x, y))

            if j % 2 == 0:
                row.reverse()
            grid.append(row)
        
        grid = grid[::-1]

    else:
        grid = []
        for i in range(n_cols):
            col = []
            for j in range(n_rows):
                x = start_x_center + i * step_x
                y = start_y_center + j * step_y
                col.append((x, y))
            if i % 2 == 0:
                col.reverse()
            grid.append(col)

        grid = grid[::-1]

    grid_points_rot = [pt for collection in grid for pt in collection]


    grid_points_utm = [rotate(pt, angle, origin=rect_centroid) for pt in grid_points_rot]

    gps_waypoints = []
    for (xx, yy) in grid_points_utm:
        lon, lat = transformer_from_utm.transform(xx, yy)
        gps_waypoints.append((lat, lon, altitude))

    return (gps_waypoints, angle, rect_centroid, transformer_to_utm,
            transformer_from_utm, ground_width, ground_height, n_cols, n_rows, utm_polygon.area)


def save_to_mission_planner_file(waypoints, filename="mission.waypoints", reverse=False):
    """Write waypoints to a Mission Planner / QGroundControl ``.waypoints`` file."""
    with open(filename, 'w') as f:
        f.write("QGC WPL 110\n")
        for i, (lat, lon, alt) in enumerate(waypoints):
            f.write(f"{i}\t0\t3\t16\t0\t0\t0\t0\t{lat:.7f}\t{lon:.7f}\t{alt:.2f}\t1\n")
    print(f"Saved Mission Planner file as '{filename}' ({'reversed' if reverse else 'normal'} order)")

def export_search_area_waypoints(search_waypoints, filepath):
    """Write waypoints to a JSON file under the ``search_waypoints`` key."""
    json_data = [[lat, lon, alt] for lat, lon, alt in search_waypoints]
    with open(filepath, "w") as f:
        json.dump({"search_waypoints": json_data}, f, indent=4)

    print(f"Saved waypoints to {filepath}")
    
def sort_coordinates(coordinates):
    """Order four boundary corners as top-left, top-right, bottom-left, bottom-right."""
    sorted_by_y = sorted(coordinates, key=lambda coord: (-coord[1], coord[0]))
    highest = sorted(sorted_by_y[:2], key=lambda c: c[0])
    lowest = sorted(sorted_by_y[2:], key=lambda c: c[0])
    return highest + lowest


def export_map(map_file_path, boundary_coords, drone_waypoints, angle, rect_centroid,
               transformer_to_utm, transformer_from_utm, ground_width, ground_height,
               n_cols, n_rows, mission_planner_file):
    """
    Render the mission to an interactive HTML map and Mission Planner file.

    Draws the boundary points, numbered waypoints, flight path, and each
    waypoint's camera footprint on a folium map saved to ``map_file_path``,
    and writes the waypoints to ``mission_planner_file``.
    """
    from offline_folium import offline  # noqa: F401 - enables folium offline assets
    import folium
    center_lat = sum(pt[0] for pt in boundary_coords) / len(boundary_coords)
    center_lon = sum(pt[1] for pt in boundary_coords) / len(boundary_coords)

    mission_map = folium.Map(location=[center_lat, center_lon], zoom_start=18)

    #folium.PolyLine(locations=boundary_coords, color='red', weight=2.5).add_to(mission_map)
    for coord in boundary_coords:
        folium.CircleMarker(location=coord, radius=4, color='red', fill=True).add_to(mission_map)


    for idx, (lat, lon, alt) in enumerate(drone_waypoints):
        folium.map.Marker(
            [lat, lon],
            icon=folium.DivIcon(
                icon_size=(20, 20),
                icon_anchor=(10, 10),
                html=f'<div style="font-size: 12px; color: blue;"><b>{idx + 1}</b></div>',
            ),
            popup=f"WP {idx + 1} ({alt} m)"
        ).add_to(mission_map)

    folium.PolyLine(locations=[(lat, lon) for lat, lon, _ in drone_waypoints],
                    color='blue', weight=2.5, opacity=1).add_to(mission_map)

    half_w = ground_width / 2.0
    half_h = ground_height / 2.0
    local_corners = [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]

    for wp in drone_waypoints:
        wp_utm = transformer_to_utm.transform(wp[1], wp[0])
        footprint_utm = [(wp_utm[0] + rotate_point_local(corner, angle)[0],
                          wp_utm[1] + rotate_point_local(corner, angle)[1])
                         for corner in local_corners]
        footprint_utm.append(footprint_utm[0])
        footprint_gps = [transformer_from_utm.transform(x, y)[::-1] for x, y in footprint_utm]
        folium.Polygon(locations=footprint_gps, color='green',
                       weight=1.5, opacity=0.8, fill=True, fill_opacity=0.2).add_to(mission_map)

    save_to_mission_planner_file(drone_waypoints, mission_planner_file)
    mission_map.save(map_file_path)
    print(f"Map saved as '{map_file_path}'.")


def generate_mission_from_params(bounds, photo_width, photo_height,
                                 horizontal_fov, vertical_fov,
                                 overlap, flight_altitude,
                                 waypoint_save_path="waypoints.json",
                                 html_save_path="mission_waypoints.html",
                                 mission_planner_file="mission.waypoints",
                                 is_reversed=False,
                                 row_traversal=False):
    """
    Plan a survey mission and export the waypoint JSON, HTML map, and
    Mission Planner file in one call.

    Parameters mirror ``plan_mission``; ``bounds`` is a list of four
    ``(lat, lon)`` corners and ``is_reversed`` flies the pattern backwards.
    """
    boundary_coords = sort_coordinates(bounds)
    (drone_waypoints, angle, rect_centroid, transformer_to_utm, transformer_from_utm,
     ground_width, ground_height, n_cols, n_rows, area) = plan_mission(
        boundary_coords, photo_width, photo_height,
        horizontal_fov, vertical_fov, overlap,
        altitude=flight_altitude,
        row_traversal=row_traversal
    )


    if is_reversed:
        drone_waypoints = list(reversed(drone_waypoints))  
        
    print(f"Width (m) x Height (m): {ground_width}, {ground_height}")
    print(f"Airdrop Area: {area}")
    print(f"Grid: {n_cols} columns, {n_rows} rows")
    print(f"Total waypoints: {len(drone_waypoints)}")
    print(f"Total distance traveled: {calculate_total_distance(drone_waypoints):.2f} meters")
        

    export_search_area_waypoints(drone_waypoints, waypoint_save_path)
    export_map(html_save_path, boundary_coords, drone_waypoints,
               angle, rect_centroid, transformer_to_utm, transformer_from_utm,
               ground_width, ground_height, n_cols, n_rows, mission_planner_file)  