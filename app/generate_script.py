import os
import sys
import json
import google.generativeai as genai

SCRIPT_PROMPT = """Convert this book/novel text into an audioplay script as a JSON array.

OUTPUT FORMAT - Return ONLY a valid JSON array:
[
  {"speaker": "NARRATOR", "text": "Description text here.", "style": "tone direction"},
  {"speaker": "CHARACTER", "text": "Dialogue here.", "style": "emotional direction"}
]

FIELDS:
- "speaker": Character name in UPPERCASE (use "NARRATOR" for descriptions/scene-setting)
- "text": The spoken text, with bracketed non-verbal sounds where appropriate
- "style": Brief delivery direction (2-5 words like "warm, nostalgic" or "cold, threatening")

NON-VERBAL SOUNDS - Include where emotionally appropriate:
[sighs], [laughs], [chuckles], [giggles], [scoffs], [gasps], [groans], [moans],
[whimpers], [sobs], [cries], [sniffs], [whispers], [shouts], [screams],
[clears throat], [coughs], [pauses], [hesitates], [stammers], [gulps]

Can be inline: "[sighs] I suppose you're right."
Or standalone: {"speaker": "ELENA", "text": "[sobs]", "style": "heartbroken"}

RULES:
1. NARRATOR handles all descriptive text, scene-setting, actions, inner thoughts
2. Character dialogue attributed to named characters (extract from context)
3. Use style directions to convey emotional tone
4. Break long passages into chunks under 400 characters each
5. Output ONLY valid JSON - no markdown, no code blocks, no explanations
6. Preserve the emotional arc of the story

EXAMPLE:
[
  {"speaker": "NARRATOR", "text": "The old mansion loomed against the stormy sky.", "style": "ominous, foreboding"},
  {"speaker": "ELENA", "text": "[shivers] I don't like this place.", "style": "nervous, quiet"},
  {"speaker": "MARCUS", "text": "[chuckles] Scared of a little dust?", "style": "teasing, confident"},
  {"speaker": "NARRATOR", "text": "A floorboard creaked somewhere above them.", "style": "tense, suspenseful"},
  {"speaker": "ELENA", "text": "[gasps]", "style": "startled"}
]

TEXT TO CONVERT:
"""

def process_chunk(model, chunk):
    """Process a text chunk and return JSON script entries"""
    response = model.generate_content(SCRIPT_PROMPT + chunk)
    text = response.text.strip()

    # Clean up markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

    try:
        entries = json.loads(text)
        if isinstance(entries, list):
            return entries
    except json.JSONDecodeError:
        print(f"Warning: Could not parse chunk response as JSON")
        print(f"Response preview: {text[:200]}...")

    return []

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

    print(f"Read {len(book_content)} characters")

    # Load LLM config
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print("Error: config.json not found. Please run configure.js first.")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    llm_config = config.get("llm", {})
    api_key = llm_config.get("api_key")
    model_name = llm_config.get("model_name", "gemini-2.0-flash")

    if not api_key:
        print("Error: LLM API Key not found in config.json")
        sys.exit(1)

    print(f"Using model: {model_name}")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    # Process in chunks to handle long texts
    all_entries = []
    chunk_size = 4096
    total_chunks = (len(book_content) + chunk_size - 1) // chunk_size

    for i, start in enumerate(range(0, len(book_content), chunk_size)):
        chunk = book_content[start:start + chunk_size]
        print(f"Processing chunk {i+1}/{total_chunks} ({len(chunk)} chars)...")

        entries = process_chunk(model, chunk)
        all_entries.extend(entries)
        print(f"  Got {len(entries)} entries")

    if not all_entries:
        print("Error: No script entries generated")
        sys.exit(1)

    # Save as JSON
    output_path = os.path.join("..", "annotated_script.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)

    # Summary
    speakers = set(entry.get("speaker", "UNKNOWN") for entry in all_entries)
    print(f"\nGenerated {len(all_entries)} script entries")
    print(f"Speakers found: {', '.join(sorted(speakers))}")
    print(f"Output saved to: {output_path}")


if __name__ == '__main__':
    main()
