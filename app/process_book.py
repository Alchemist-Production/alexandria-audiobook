import argparse
import os
import json
import google.generativeai as genai
from pydub import AudioSegment
import requests # for TTS API

def generate_voice_line(line, output_path, tts_url):
    response = requests.post(tts_url, json={"text": line})
    with open(output_path, 'wb') as f:
        f.write(response.content)

def get_annotated_script(model, chunk):
    response = model.generate_content(
        "You are a script writer. Your task is to convert a book chapter into a script format. The script should be annotated with NARRATOR: for narrative parts and CHARACTER_NAME: for dialogue. Make sure to properly attribute the dialogue to the correct character.\n\n" + chunk
    )
    return response.text

def read_book_in_chunks(file_path, chunk_size=4096):
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def main():
    parser = argparse.ArgumentParser(description='Process a book.')
    parser.add_argument('--file', type=str, required=True, help='The path to the book file.')
    args = parser.parse_args()

    print(f"Processing book: {args.file}")

    with open("config.json", "r") as f:
        config = json.load(f)

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(config["llm"]["model_name"])

    annotated_script = ""
    for chunk in read_book_in_chunks(args.file):
        print(f"Processing chunk of size: {len(chunk)}")
        annotated_script += get_annotated_script(model, chunk)

    print("\n\nAnnotated Script:\n")
    print(annotated_script)

    lines = [line.strip() for line in annotated_script.split("\n") if line.strip()]
    
    audio_segments = []
    output_dir = "output_audio"
    os.makedirs(output_dir, exist_ok=True)

    for i, line in enumerate(lines):
        output_path = os.path.join(output_dir, f"line_{i}.mp3")
        print(f"Generating voice for: {line}")
        generate_voice_line(line, output_path, config["tts"]["url"])
        audio_segments.append(AudioSegment.from_mp3(output_path))

    final_audio = sum(audio_segments)
    output_filename = os.path.splitext(os.path.basename(args.file))[0] + ".mp3"
    final_audio.export(output_filename, format="mp3")
    print(f"\n\nAudiobook saved as {output_filename}")


if __name__ == '__main__':
    main()
