import os
import sys
import json
import google.generativeai as genai

SCRIPT_PROMPT = """You are converting a book/novel into an audiobook script. Your task is to output ONLY plain text lines in this exact format:

SPEAKER_NAME: The text they speak or narrate.

RULES:
1. Use "NARRATOR" for ALL descriptive text, scene-setting, action descriptions, inner thoughts, and anything that is NOT spoken dialogue by a character.
2. Use the CHARACTER'S NAME (in CAPS, underscores for spaces) for spoken dialogue only.
3. Output ONLY plain text. NO HTML tags, NO markdown, NO formatting (no <center>, <b>, **, ##, etc.).
4. Each line must start with a speaker label followed by a colon and space.
5. Keep the original meaning and content - do not summarize or skip text.
6. If a character's name is unknown, use a descriptive label like "UNKNOWN_VOICE" or "OLD_MAN".

EXAMPLE INPUT:
The sun set over the mountains. "I can't believe we made it," Sarah whispered. John nodded silently, his eyes fixed on the horizon.

EXAMPLE OUTPUT:
NARRATOR: The sun set over the mountains.
SARAH: I can't believe we made it.
NARRATOR: John nodded silently, his eyes fixed on the horizon.

Now convert this text:

"""

def get_annotated_script(model, chunk):
    response = model.generate_content(SCRIPT_PROMPT + chunk)
    return response.text

def main():
    if len(sys.argv) < 2:
        print("Error: No input file path provided.")
        print("Usage: python generate_script.py <input_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    print(f"Processing book from: {input_file_path}")

    if not os.path.exists(input_file_path):
        print(f"Error: Input file not found: {input_file_path}")
        sys.exit(1)

    with open(input_file_path, 'r', encoding='utf-8') as f:
        book_content = f.read()

    # Load LLM config from config.json
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print("Error: config.json not found. Please run configure.js first.")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    llm_config = config.get("llm", {})
    api_key = llm_config.get("api_key")
    model_name = llm_config.get("model_name", "gemini-pro") # Default to gemini-pro if not specified

    if not api_key:
        print("Error: LLM API Key not found in config.json. Please run configure.js to set it.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    annotated_script = ""
    # Process content in chunks if necessary, or pass the entire content
    # For now, let's pass the entire content as one chunk for simplicity
    # If API has length limits, this would need to be re-chunked
    chunk_size = 4096 # Re-using chunk_size for consistency, though not reading from file
    for i in range(0, len(book_content), chunk_size):
        chunk = book_content[i:i+chunk_size]
        print(f"Processing chunk of size: {len(chunk)}")
        annotated_script += get_annotated_script(model, chunk)

    # Save the script to a file in the parent directory
    output_path = os.path.join("..", "annotated_script.txt")
    with open(output_path, 'w') as f:
        f.write(annotated_script)
    
    print(f"\nAnnotated script saved to {output_path}")


if __name__ == '__main__':
    main()
