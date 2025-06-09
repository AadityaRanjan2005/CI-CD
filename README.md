# Ollama Chat Application

A full-stack chat application using FastAPI, WebSockets, Redis, SQLite, and Ollama for LLM-powered conversations with persistent chat history and user authentication.

---

## Features

- User authentication (JWT)
- Real-time chat with LLM (Ollama)
- Chat history and session management (Redis)
- Continue previous conversations
- Modern frontend (HTML/JS/CSS)
- Easy to run locally

---

## Prerequisites

- **Python 3.9+**
- **pip**
- **Redis** (for chat/session storage)
- **Ollama** (for LLM inference)

---

## 1. Install Redis

### **Linux**

```bash
sudo apt update
sudo apt install redis-server
# Start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
# Check status
sudo systemctl status redis-server
```

### **Windows**

- Download the latest Redis release for Windows from [Memurai](https://www.memurai.com/get-memurai) (free for development) or [tporadowski/redis](https://github.com/tporadowski/redis/releases).
- Extract and run `redis-server.exe`.
- Optionally, install as a Windows service for auto-start.

### **macOS**

```bash
brew update
brew install redis
brew services start redis
```
If you don't have Homebrew, install it from [https://brew.sh/](https://brew.sh/).

---

## 2. Install Ollama

### **Linux**

See [Ollama's official install guide](https://ollama.com/download) for the latest instructions.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
- After install, start Ollama:
```bash
ollama serve
```
- Pull a model (e.g., llama2):
```bash
ollama pull llama2
```

### **Windows**

- Download the Ollama installer from [https://ollama.com/download](https://ollama.com/download).
- Run the installer and follow the prompts.
- Open a terminal (Command Prompt or PowerShell) and run:
    ```bash
    ollama serve
    ```
- Pull a model:
    ```bash
    ollama pull llama2
    ```

### **macOS**

- Download and install from [https://ollama.com/download](https://ollama.com/download) or use Homebrew:
    ```bash
    brew install ollama
    ```
- Start Ollama:
    ```bash
    ollama serve
    ```
- Pull a model:
    ```bash
    ollama pull llama2
    ```

---

## 3. Clone and Set Up This Project

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

---

## 4. Install Python Dependencies

It's recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Initialize the Database and Seed Users

```bash
python init_db.py
python seed_users.py
```

---

## 6. Start Redis and Ollama

Make sure both are running:

- **Redis:**  
  - Linux/macOS: `sudo systemctl start redis-server` or `brew services start redis`
  - Windows: Run `redis-server.exe`
- **Ollama:**  
  In a separate terminal:  
  `ollama serve`

---

## 7. Start the FastAPI Server

```bash
python server.py
```
Or, for development with auto-reload:
```bash
uvicorn server:app --reload
```

---

## 8. Access the Application

Open your browser and go to:  
[http://localhost:8000/](http://localhost:8000/)

- Login with one of the seeded users (see `seed_users.py` for usernames/passwords).
- Start chatting with the LLM!
- Your chat history is saved and you can continue any previous conversation.

---

## 9. Notes

- **To add more users:** Edit and re-run `seed_users.py`.
- **To change the model:** Edit `MODEL_NAME` in `server.py` and pull the model with `ollama pull <modelname>`.
- **Logs:** See `my_app.log` for server logs.

---

## Troubleshooting

- If you get connection errors, ensure Redis and Ollama are running.
- If you change models, make sure to pull them with Ollama before use.
- For any Python errors, check your virtual environment and dependencies.

---