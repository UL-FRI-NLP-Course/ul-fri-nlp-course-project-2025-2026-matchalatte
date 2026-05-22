# Natural language processing course: `Travel chatbot`

# ✈️ Travel Planning Chatbot

A smart travel chatbot that combines a language model with external tools to generate itineraries, fetch live weather, and retrieve train connections.

It balances 🎨 creative trip planning with 🌍 real-world accuracy.

---

## 🌍 Features

- 🧠 AI-powered itinerary generation  
- 🌦️ Live weather forecasting  
- 🚆 Train route & schedule search  
- 💬 Natural travel conversation  

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/UL-FRI-NLP-Course/ul-fri-nlp-course-project-2025-2026-matchalatte.git
cd ul-fri-nlp-course-project-2025-2026-matchalatte
```
### 2. Create the environment
```bash
module load Python/3.10.8-GCCcore-12.2.0
python -m venv my_env
source my_env/bin/activate
pip install torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 \
--index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```
### 3. Log in to Hugging Face
The model used in this project requires a Hugging Face access token.

First, create a Hugging Face account at:

https://huggingface.co/

Then generate an access token:

1. Open:
   https://huggingface.co/settings/tokens

2. Click **"New token"**

3. Give the token a name (for example `travel-chatbot`)

4. Select at least **Read** permissions

5. Click **Create token**

6. Copy the generated token

Then log in from the terminal:

```bash
hf auth login
```

Paste your Hugging Face token when prompted.

### 4. Run chatbot with prompt
The chatbot is executed through a Slurm job script.
Example:
```bash
sbatch scripts/chatbot.sh "What is a romantic weekend destination in Europe?"
```
To monitor the status and progress of your job, run:
```bash
sacct -j <job_id>
```

### 5. Read the ouput
After the job finishes, inspect the generated Slurm output file:
```bash
ls logs/chat-*.out
```
Example:
```bash
cat logs/chat-12345678.out
```
Replace `12345678` with your actual job ID. 

You can also open the logs/ directory directly and inspect the generated .out files.

---
## 🧩 System Overview

This chatbot is built on three main layers:

- 🧠 **Base LLM** → generates itineraries, tips, and recommendations  
- 🛠️ **smolagents** → handles tool calling and orchestration  
- 🔌 **External tools** → provide real-time data (weather + trains)  

---

## ⚙️ Tools

- 🌦️ `weather_forecast` → gets current and forecast weather  
- 🚆 `search_train_connections` → finds train routes and schedules  

---
## 💬 Example Usage

`User: Plan a 4-day trip to Rome with trains from Milan and weather info.`

Response includes:
- 🗺️ itinerary
- 🚆 train connections
- 🌦️ weather forecast

---

## 📊 Key Insight

This project shows that:

- 🛠️ tools improve factual accuracy
- ✍️ prompt engineering stabilizes output
- 📦 schema design strongly affects reliability
- ⚖️ creativity vs correctness is a core trade-off

