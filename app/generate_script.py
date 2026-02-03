import os
import sys
import json
import re
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
7. IMPORTANT: Always output COMPLETE sentences. Never truncate text mid-sentence.

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

def split_into_chunks(text, max_size=3000):
    """Split text into chunks at paragraph/sentence boundaries."""
    # First split by paragraphs (double newlines)
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed max_size
        if len(current_chunk) + len(para) + 2 > max_size:
            # If current chunk has content, save it
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # If single paragraph is too long, split by sentences
            if len(para) > max_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 > max_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
            else:
                current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def process_chunk(model, chunk, chunk_num, total_chunks):
    """Process a text chunk and return JSON script entries"""
    # Add context about chunk position to help LLM
    context = ""
    if chunk_num == 1:
        context = "(This is the beginning of the text)\n\n"
    elif chunk_num == total_chunks:
        context = "(This is the end of the text)\n\n"
    else:
        context = f"(This is part {chunk_num} of {total_chunks}, continue from previous context)\n\n"

    response = model.generate_content(SCRIPT_PROMPT + context + chunk)
    text = response.text.strip()

    # Clean up markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Find the closing ``` and remove both markers
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip().startswith("```"):
                end_idx = i
                break
        if end_idx > 0:
            text = "\n".join(lines[1:end_idx])
        else:
            text = "\n".join(lines[1:])

    try:
        entries = json.loads(text)
        if isinstance(entries, list):
            return entries
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse chunk {chunk_num} response as JSON: {e}")
        print(f"Response preview: {text[:300]}...")

        # Try to salvage partial JSON
        try:
            # Find the last complete entry by looking for the last "},"
            last_complete = text.rfind('},')
            if last_complete > 0:
                salvaged = text[:last_complete+1] + ']'
                entries = json.loads(salvaged)
                print(f"Salvaged {len(entries)} entries from partial response")
                return entries
        except:
            pass

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

    # Split into chunks at natural boundaries
    chunks = split_into_chunks(book_content, max_size=3000)
    total_chunks = len(chunks)

    print(f"Split into {total_chunks} chunks at paragraph/sentence boundaries")

    all_entries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{total_chunks} ({len(chunk)} chars)...")

        entries = process_chunk(model, chunk, i, total_chunks)
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
