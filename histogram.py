from flask import render_template, jsonify, request
from SkeletonRaytheonMap import app
from SkeletonRaytheonMap.services.sci_api import get_access_token, api_get


# --- ROUTE 1: Home Page ---
@app.route("/")
def home():
    return render_template("homepage.html")


# --- ROUTE 2: Map Page ---
@app.route("/map")
def show_map():
    return render_template("map.html")


# --- ROUTE 3: API Test (Token only) ---
@app.route("/api-test")
def api_test():
    try:
        token = get_access_token()
        return jsonify({
            "ok": True,
            "token_starts_with": token[:10],
            "token_length": len(token)
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# --- ROUTE 4: Gazetteer Search ---
# Example: /gazetteer?keyword=Malvern
@app.route("/gazetteer")
def gazetteer():
    try:
        keyword = request.args.get("keyword", "")
        data = api_get("/discover/api/v1/gazetteer/search", params={"keyword": keyword})
        return jsonify(data)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# --- ROUTE 5: Missions List ---
# Example: /missions?keyword=&datestart=&dateend=&archived=false
@app.route("/missions")
def missions():
    try:
        keyword = request.args.get("keyword", "")
        datestart = request.args.get("datestart", "")
        dateend = request.args.get("dateend", "")
        archived = request.args.get("archived", "")

        params = {}
        if keyword:
            params["keyword"] = keyword
        if datestart:
            params["datestart"] = datestart
        if dateend:
            params["dateend"] = dateend
        if archived:
            params["archived"] = archived

        data = api_get("/discover/api/v1/missionfeed/missions", params=params or None)
        return jsonify(data)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# --- ROUTE 6: Mission Footprint ---
# Example: /missions/<missionId>/footprint
@app.route("/missions/<mission_id>/footprint")
def mission_footprint(mission_id):
    try:
        data = api_get(f"/discover/api/v1/missionfeed/missions/{mission_id}/footprint")
        return jsonify(data)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# --- ROUTE 7: Histogram Data (Frames per Scene Date) ---
@app.route("/histogram-data")
def histogram_data():
    try:
        # Limit to 5 missions to prevent API timeouts during nested loops
        limit = int(request.args.get("limit", 5))
        
        missions_data = api_get("/discover/api/v1/missionfeed/missions")
        missions = missions_data.get("missions", missions_data) if isinstance(missions_data, dict) else missions_data
        
        if not isinstance(missions, list):
            missions = []

        date_counts = {}

        # Drill Down: Missions -> Scenes -> Frames
        for mission in missions[:limit]:
            m_id = mission.get("id") or mission.get("missionId")
            scenes = mission.get("scenes", [])
            
            for scene in scenes:
                s_id = scene.get("id") or scene.get("sceneId")
                # Get the date of the scene
                scene_date = scene.get("timestamp") or scene.get("startDate") or ""

                if m_id and s_id:
                    try:
                        # Fetch frames for this specific scene
                        frames_data = api_get(f"/discover/api/v1/missionfeed/missions/{m_id}/scene/{s_id}/frames")
                        frames = frames_data.get("frames", frames_data) if isinstance(frames_data, dict) else frames_data

                        if isinstance(frames, list) and len(frames) > 0:
                            # Use scene date. If empty, try to derive from the first frame.
                            ts = scene_date or frames[0].get("timestamp") or frames[0].get("startDate")
                            
                            if ts and len(str(ts)) >= 10:
                                date_key = str(ts)[:10] # Extract YYYY-MM-DD
                                
                                # Add the total amount of frames in this scene to the corresponding date
                                date_counts[date_key] = date_counts.get(date_key, 0) + len(frames)
                                
                    except Exception as e:
                        continue

        # Format for Chart.js
        sorted_dates = sorted(date_counts.keys())
        
        return jsonify({
            "labels": sorted_dates,
            "values": [date_counts[d] for d in sorted_dates]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
