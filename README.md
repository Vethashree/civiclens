# CivicLens – Beginner Setup Guide

CivicLens is a web app. Citizens report a civic problem with one photo, AI identifies it,
duplicates are merged, and departments fix it while everyone watches on a public dashboard.

Built with **Python + Streamlit** (web app), **SQLite** (database), **Folium** (maps) and
**CLIP** (a free pre-trained AI model).

---

## Step 1 – Install Python

1. Go to https://www.python.org/downloads/ and download **Python 3.12** (3.11 or 3.12 work best).
2. Run the installer. **Tick "Add python.exe to PATH"** at the bottom of the first screen.
3. Check it worked: open **Command Prompt** (Windows key → type `cmd` → Enter) and type:
   ```
   python --version
   ```
   You should see `Python 3.12.x`.

(Optional but recommended: install **VS Code** from https://code.visualstudio.com to read and edit the code.)

## Step 2 – Put the project on your computer

1. Unzip `CivicLens.zip` somewhere easy, e.g. `C:\Projects\civiclens`.
2. Open Command Prompt and go into that folder:
   ```
   cd C:\Projects\civiclens
   ```

## Step 3 – Create a virtual environment (a private box for this project's libraries)

```
python -m venv venv
venv\Scripts\activate
```
You'll now see `(venv)` at the start of the line. **Do this `activate` step every time you open a new Command Prompt.**

Mac/Linux: use `python3 -m venv venv` and `source venv/bin/activate`.

## Step 4 – Install the libraries

```
pip install -r requirements.txt
```
This downloads Streamlit, the AI libraries (PyTorch, Transformers) and map tools.
It's large (around 1 GB) and can take **10–20 minutes**. Use good Wi-Fi.

## Step 5 – Run the app

```
streamlit run Home.py
```
Your browser opens at **http://localhost:8501**. To stop the app, press `Ctrl + C` in Command Prompt.

**The first time you report a photo**, the AI model (~600 MB) downloads automatically.
Wait a few minutes; after that it's fast.

## Step 6 – Set the map to your college

Open `config.py` and change:
```python
MAP_CENTER = (13.0827, 80.2707)
```
to your college's location. (In Google Maps, right-click your college → click the numbers to copy them.)
Also add real nearby schools/hospitals to `SENSITIVE_PLACES`. Save the file; the app reloads automatically.

## Step 7 – Try the full flow

1. **Report Problem** → Upload a photo of garbage or a pothole (download one from Google Images) →
   see the AI's guess → tap the map → **Submit**. Note the tracking ID.
2. Report **the same kind of photo at the same spot again** → it gets **merged** ("2 reports").
3. **Department Portal** → password `admin123` → open the issue → upload an "after" photo → **Mark Resolved**.
4. **Report Problem** → *Track your report* → enter the ID → see the before and after photos.
5. **Public Dashboard** → live map, heat map, women's safety map, charts and SDG impact.
6. Leave an issue open for a few minutes → it becomes **⚠️ ESCALATED** (demo mode in `config.py`).

## Step 8 – Open it on your phone (great for the expo demo)

1. Connect your phone and laptop to the **same Wi-Fi** (or your phone's hotspot).
2. Stop the app and start it like this:
   ```
   streamlit run Home.py --server.address 0.0.0.0
   ```
3. Find your laptop's IP: in a new Command Prompt type `ipconfig` and look for **IPv4 Address** (e.g. `192.168.1.5`).
4. On your phone's browser open `http://192.168.1.5:8501`.

On the phone, use the **Upload** tab: it lets you take a photo with the phone camera directly.
(The in-page *Camera* tab only works on the laptop, because phone browsers block cameras on non-HTTPS sites.)

## Start fresh (clear all test data)

Stop the app and delete `civiclens.db` and the `photos` folder. They are recreated automatically.

---

## How the code is organised

| File | What it does |
| --- | --- |
| `Home.py` | Home page |
| `pages/1_Report_Problem.py` | Citizen page: photo → AI → map → submit; tracking |
| `pages/2_Department_Portal.py` | Staff page: issues by priority, status updates, after-photo |
| `pages/3_Public_Dashboard.py` | Maps, heat map, safety map, charts, SDG impact |
| `core/ai.py` | AI photo classification (CLIP zero-shot) |
| `core/logic.py` | Duplicate merging, severity score, escalation |
| `core/db.py` | Saving and reading data (SQLite) |
| `config.py` | **All settings you can change** |

## Common problems

| Problem | Fix |
| --- | --- |
| `'python' is not recognized` | Reinstall Python and tick "Add python.exe to PATH" |
| `venv\Scripts\activate` gives a red error in PowerShell | Use **Command Prompt** (cmd) instead of PowerShell |
| `No module named streamlit` | You forgot `venv\Scripts\activate` before running |
| "AI model is not available" | Check your internet for the first run; look at the error in Command Prompt |
| AI guesses wrong | Normal for some photos; pick the right category from the dropdown. Improve it by editing `AI_PROMPTS` in `config.py` |
| Maps are blank | The maps need internet |
| Phone can't open the app | Same Wi-Fi? Correct IP? Allow Python through Windows Firewall when asked |
