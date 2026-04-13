# Wholesaling AI Agent Codebase

This folder contains the integration scripts and configuration files necessary to set up your Wholesaling AI agent using OpenClaw, Nexos AI credits, and Oxylabs Data Tools. It has been pre-configured to deploy easily to modern cloud platforms like Render or Heroku.

## Deployment Instructions (Render or Heroku)

Since this AI agent runs as a background worker 24/7 using the `schedule` python package, it is extremely easy to deploy to cloud PaaS providers without managing a Linux server.

### Option 1: Render.com
1. Create a GitHub repository and push this entire folder to it.
2. Log into Render, click **New+** -> **Background Worker**.
3. Connect your GitHub repository.
4. Set the Build Command to: `pip install -r requirements.txt`
5. Set the Start Command to: `python price_monitor.py`
6. Put your keys (`NEXOS_API_KEY`, etc.) into the Render Environment Variables tab.
7. Deploy!

### Option 2: Heroku.com
1. Create a GitHub repository and push this entire folder to it.
2. Log into Heroku, click **Create New App**.
3. Under the **Deploy** tab, connect your GitHub repository and hit Deploy.
4. Under the **Resources** tab, turn off the `web` worker (if any) and turn ON the `worker` process (which uses our `Procfile`).
5. Add your keys securely in the Heroku **Settings -> Config Vars**.

## Local Configuration
For local testing, place your keys inside `config.yaml` and update the keys inside `scrape_wholesale.py`.

Install the dependencies:
```bash
pip install -r requirements.txt
```

Run the background worker:
```bash
python price_monitor.py
```
This will start the monitor, run a check immediately, and then wait to run every day at 8:00 AM.
