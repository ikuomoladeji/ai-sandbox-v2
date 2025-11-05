import requests
from pathlib import Path

# Which model in Ollama you want to use
MODEL_NAME = "qwen3-coder"  # you can change this to deepseek-r1:8b, mistral, etc.

def ask_model(prompt: str) -> str:
    """
    Send a prompt to your local Ollama model and return the raw text response.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    # Ollama returns something like { "response": "...text..." }
    return data.get("response", "")

def save_file(path: str, content: str):
    """
    Save the model output to disk at the given path.
    Creates folders if needed.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Wrote file: {file_path.resolve()}")

def main():
    print("Local AI Code Writer")
    print("--------------------")
    target_path = input("File to create (e.g. server.js or src/api/predict.js): ").strip()

    goal = input("Describe what you want the file to do:\n> ").strip()

    # Build a strong instruction for the model
    full_prompt = f"""
You are an expert software engineer.
Write ONLY the complete code for the requested file.
Do not include backticks. Do not explain.

Task: {goal}
Return just the code.

Tech stack: Node.js (Express), JavaScript, modern style.
If relevant, include imports at the top.
"""

    print("\n🤖 Generating code with model:", MODEL_NAME, "...\n")

    code = ask_model(full_prompt)

    save_file(target_path, code)

    print("\nDone. You can now open that file and run or edit it.")

if __name__ == "__main__":
    main()



