import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_model(model_name: str, prompt: str) -> str:
    """
    Send a prompt to the local Ollama model and return the raw text response.
    """
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    resp = requests.post(OLLAMA_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def save_file(path: Path, content: str):
    """
    Save (or overwrite) a file at 'path' with 'content'.
    Creates folders if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n✅ Wrote file: {path.resolve()}")


def read_multiline_input(prompt_header: str) -> str:
    """
    Capture multi-line user input.
    User ends input by pressing Enter on a blank line twice.
    """
    print(prompt_header)
    print("When you're done, press Enter on an empty blank line.\n")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    return "\n".join(lines)


def create_new_file(model_name: str):
    """
    1. Ask for target filename
    2. Ask for requirements (multi-line)
    3. Ask model to generate mentor-style code
    4. Save result
    """
    target_path_input = input("File to create (e.g. app/page.tsx or src/api/predict.js): ").strip()

    goal = read_multiline_input(
        "Describe what you want this file to do (features, styling, behavior, inputs/outputs):"
    )

    prompt = f"""
You are a senior full-stack engineer and mentor.

Your job is to generate a production-ready file called {target_path_input}.

Answer in THREE SECTIONS:

1. PLAN
- Describe what you are building.
- Mention any assumptions you are making.
- List dependencies or env vars I must set up.
- Mention commands I should run to test it locally.

2. EXPLAIN
- Walk me through how the file works, step by step.
- Highlight validation, security, or edge cases.
- If this is UI (Next.js/React), explain the layout.
- If API route, explain input validation and error handling.

3. FINAL CODE
- Provide the FULL code for {target_path_input}.
- The code must be valid and ready to paste.
- Do NOT use backticks.
- Include imports at the top if needed.

TASK / REQUIREMENTS:
{goal}

Rules:
- Use modern, idiomatic code.
- For Next.js pages, export a default React component in TypeScript.
- For API endpoints, return JSON and handle bad input safely.
- For utility files, make them clean and reusable.
- Keep naming consistent and readable.
"""

    print("\n🤖 Generating with model:", model_name, "...\n")
    response_text = ask_model(model_name, prompt)

    print("----- BEGIN MODEL OUTPUT -----")
    print(response_text)
    print("----- END MODEL OUTPUT -----\n")

    final_code = extract_section(response_text, "FINAL CODE")
    if not final_code:
        print("⚠️ Could not detect FINAL CODE section. Saving entire output.")
        final_code = response_text

    save_file(Path(target_path_input), final_code)
    print("✅ Done. You can now open or run that file.\n")


def improve_existing_file(model_name: str):
    """
    1. Ask for file path
    2. Read file
    3. Ask for improvement request
    4. Send to model for review + refactor
    """
    file_path_input = input("Which file do you want to improve (e.g. app/page.tsx): ").strip()
    file_path = Path(file_path_input)

    if not file_path.exists():
        print("❌ That file doesn't exist. Run again with a valid filename.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    instruction = read_multiline_input(
        "Describe what you want improved (style, validation, performance, etc.):"
    )

    prompt = f"""
You are a senior reviewer and refactorer.

You will receive an existing source file. You will respond in THREE SECTIONS:

1. ISSUES
- Explain what's risky, unclear, outdated, or could crash.
- Mention any TypeScript, runtime, or security problems.

2. FIX PLAN
- Explain how you will improve it.
- Include validation, structure, and code quality steps.
- Mention accessibility or responsive UI if relevant.

3. REWRITTEN FILE
- Return the FULL improved version of {file_path_input}.
- Must be complete and ready to paste.
- Do NOT wrap in backticks.

USER REQUEST:
{instruction}

ORIGINAL FILE ({file_path_input}):
<START_OF_FILE>
{original_code}
<END_OF_FILE>
"""

    print("\n🤖 Reviewing and improving with model:", model_name, "...\n")
    response_text = ask_model(model_name, prompt)

    print("----- BEGIN MODEL OUTPUT -----")
    print(response_text)
    print("----- END MODEL OUTPUT -----\n")

    improved_code = extract_section(response_text, "REWRITTEN FILE")
    if not improved_code:
        print("⚠️ Could not detect REWRITTEN FILE section. Saving entire output.")
        improved_code = response_text

    save_file(file_path, improved_code)
    print("✨ File updated successfully.\n")


def extract_section(full_response: str, marker: str):
    """
    Extract text following a marker like 'FINAL CODE' or 'REWRITTEN FILE'.
    """
    lower = full_response.lower()
    idx = lower.find(marker.lower())
    if idx == -1:
        return None
    after = full_response[idx + len(marker):].strip()
    return after


def main():
    print("Local AI Dev Assistant")
    print("----------------------")
    print("Available models: llama3:latest, mistral:latest, qwen3-coder:30b (heavy)\n")

    model_name = input("Which model do you want to use? ").strip()

    print("\n1) Create new file")
    print("2) Improve existing file")
    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        create_new_file(model_name)
    elif choice == "2":
        improve_existing_file(model_name)
    else:
        print("❌ Invalid choice. Run again and choose 1 or 2.")


if __name__ == "__main__":
    main()
