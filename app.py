from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid, cv2
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = "techsevak-demo-key"

# --- In-memory data ---
ghats = {
    "Ramghat": {"capacity": 5, "current": 0, "webcam_image": None},
    "DuttAkharaGhat": {"capacity": 100, "current": 0, "webcam_image": None},
    "NarsinghGhat": {"capacity": 80, "current": 0, "webcam_image": None},
}

missing_persons = []  # {id, name, parents, reported_at, photo_filename, status}
alerts = []           # recent alerts
staff_profiles = [
    {"name":"Ajay Singh","role":"Police","assigned":"Ramghat","phone":"9876543210"},
]

# Drones simulation placeholder
drones = [
    {"id":1,"status":"Normal","updated_at":datetime.now().strftime("%d-%b %H:%M:%S")},
    {"id":2,"status":"Normal","updated_at":datetime.now().strftime("%d-%b %H:%M:%S")},
]

UPLOAD_FOLDER = "static/uploads"
SNAPSHOT_FOLDER = "static/snapshots"
ALLOWED_EXT = {"png","jpg","jpeg","mp4"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SNAPSHOT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

# --- YOLO model ---
MODEL_PATH = "C:\\Users\\HP\\OneDrive\\Desktop\\techsevak\\models\\yolov8s.pt"
model = YOLO(MODEL_PATH)
RAMGHAT_LIMIT = 5  # max people before overcrowd alert

# --- ROUTES ---
@app.route("/")
def index():
    now = datetime.now().strftime("%d %b %Y %H:%M:%S")
    return render_template("dashboard.html",
                           ghats=ghats,
                           missing_persons=missing_persons,
                           staff_profiles=staff_profiles,
                           alerts=list(reversed(alerts))[:20],
                           time_str=now,
                           drones=drones)

# --- Missing person report ---
@app.route("/report_missing", methods=["POST"])
def report_missing():
    name = request.form.get("name","").strip()
    parents = request.form.get("parents","").strip()
    reported_at = request.form.get("ghat","").strip()
    file = request.files.get("photo")
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(f"mp_{int(datetime.now().timestamp())}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    mp = {"id": len(missing_persons)+1, "name": name, "parents": parents,
          "reported_at": reported_at, "photo": filename, "status":"Missing", "found_at":None}
    missing_persons.append(mp)
    alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - Missing reported: {name} near {reported_at}")
    flash("Missing person reported and saved.", "success")
    return redirect(url_for("index"))

@app.route("/found_person", methods=["POST"])
def found_person():
    try:
        pid = int(request.form.get("id"))
    except:
        pid = None
    found_at = request.form.get("found_at","").strip()
    for r in missing_persons:
        if r["id"] == pid:
            r["status"] = f"Found at {found_at}"
            r["found_at"] = found_at
            alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - Found: {r['name']} at {found_at}")
            flash(f"{r['name']} marked as found at {found_at}.", "success")
            break
    return redirect(url_for("index"))

@app.route("/add_alert", methods=["POST"])
def add_alert():
    alert_msg = request.form.get("alert", "").strip()
    if alert_msg:
        timestamp = datetime.now().strftime("%H:%M:%S")
        alerts.append(f"{timestamp} - 🚨 {alert_msg}")
        flash("Emergency alert added!", "danger")
    return redirect(url_for("index"))


# --- Upload video for Ramghat YOLO detection ---
@app.route("/upload_video", methods=["POST"])
def upload_video():
    file = request.files.get("video")
    if not file or not allowed_file(file.filename):
        flash("Invalid file or format. Only mp4/png/jpg allowed.", "danger")
        return redirect(url_for("index"))

    # Save video
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    cap = cv2.VideoCapture(filepath)
    snapshot_name = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, classes=[0])  # 0 = person
        person_count = sum([len(r.boxes) for r in results])
        ghats["Ramghat"]["current"] = person_count

        # Save snapshot with boxes
        if person_count > 0:
            annotated_frame = results[0].plot()  # draw boxes
            snapshot_name = f"ramghat_{uuid.uuid4()}.jpg"
            snapshot_path = os.path.join(SNAPSHOT_FOLDER, snapshot_name)
            cv2.imwrite(snapshot_path, annotated_frame)
            ghats["Ramghat"]["webcam_image"] = snapshot_name

        if person_count > RAMGHAT_LIMIT:
            alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - ⚠️ Overcrowd detected at Ramghat ({person_count} people)")
            break

    cap.release()
    flash("Video processed. Ramghat count updated.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
