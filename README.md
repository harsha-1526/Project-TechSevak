# Project-TechSevak
“Smart Command &amp; AI Safety Dashboard for MahaKumbh”
# 🚦 Crowd & Traffic Monitoring using YOLO + Flask

This project uses a **YOLOv8 object detection model** integrated with a **Flask backend** and an **HTML dashboard frontend** to monitor crowd and traffic in real-time.

---

## ✨ Features
- Real-time object detection using YOLOv8
- Flask backend for inference
- HTML/CSS dashboard for visualization
- Snapshot saving functionality
- Clean modular project structure

---

## 📂 Project Structure
├── app.py # Flask Backend
├── templates/ # HTML templates (dashboard.html etc.)
├── static/ # Images, CSS, JS files, snapshots
├── models/ # Placeholder for YOLO model
├── requirements.txt # Python dependencies
├── README.md # Project Documentation


---

## ⚡ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>


   pip install -r requirements.txt



   Download the model separately and place it inside the models/ folder.
Example:

  models/
    └── yolov8s.pt


(Provide your model download link here – Google Drive / HuggingFace / Roboflow etc.)

▶️ Running the Project

Start the Flask server:

python app.py


Open the browser and visit:

http://127.0.0.1:5000

📸 Snapshots

Some sample detection outputs are saved inside the static/ folder.

👩‍💻 Author

Harshan Dhulkar

📜 License

This project is for educational and research purposes only.

