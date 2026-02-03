import os
import json
from pydub import AudioSegment
from gradio_client import Client, handle_file
import shutil

def test_tts_connection(tts_url, voice_config):
    """Test the TTS connection with the first configured voice"""
    print(f"Testing TTS connection to {tts_url}...")

    # Get first configured voice
    speaker = list(voice_config.keys())[0] if voice_config else None
    if not speaker:
        print("Error: No voices configured in voice_config.json")
        return False

    voice_data = voice_config[speaker]
    ref_audio_path = voice_data.get("ref_audio")
    ref_text = voice_data.get("ref_text")
    seed = int(voice_data.get("seed", -1))

    if not os.path.exists(ref_audio_path):
        print(f"Error: Reference audio file not found: {ref_audio_path}")
        return False

    print(f"  Reference audio: {ref_audio_path}")
    print(f"  Reference text: {ref_text[:50]}...")
    print(f"  Seed: {seed}")

    try:
        client = Client(tts_url)

        # Try a short test phrase
        result = client.predict(
            handle_file(ref_audio_path),
            ref_text,
            "Testing, one two three.",  # short test phrase
            "Auto",
            False,
            "1.7B",
            200,
            0.0,
            seed,
            api_name="/generate_voice_clone"
        )
        print(f"  Test successful! Output: {result[0]}")
        return True
    except Exception as e:
        print(f"  TTS Test FAILED: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Make sure the TTS model is loaded in the Gradio UI")
        print("  2. Try generating audio manually in the TTS web interface first")
        print("  3. Check if the reference audio file is accessible")
        return False

def generate_cloned_voice_line(line_text, speaker, voice_config, tts_url, output_path, client):
    try:
        voice_data = voice_config.get(speaker)
        if not voice_data:
            print(f"Warning: No voice configuration found for speaker '{speaker}'. Skipping line.")
            return False

        ref_audio_path = voice_data.get("ref_audio")
        ref_text = voice_data.get("ref_text")
        seed = int(voice_data.get("seed", -1))

        if not ref_audio_path or not ref_text:
            print(f"Warning: Incomplete voice configuration for speaker '{speaker}'. Skipping line.")
            return False

        if not os.path.exists(ref_audio_path):
            print(f"Warning: Reference audio file not found: {ref_audio_path}. Skipping.")
            return False

        result = client.predict(
            handle_file(ref_audio_path),
            ref_text,
            line_text,
            "Auto",
            False,
            "1.7B",
            200,
            0.0,
            seed,
            api_name="/generate_voice_clone"
        )

        generated_audio_filepath = result[0]
        if not generated_audio_filepath or not os.path.exists(generated_audio_filepath):
            print(f"Error: No audio file generated for: '{line_text[:50]}...'")
            return False

        shutil.copy(generated_audio_filepath, output_path)
        return True

    except Exception as e:
        print(f"Error generating voice for '{speaker}': {e}")
        return False

def main():
    # Load configurations (config.json is in app/, voice_config.json is in project root)
    with open("config.json", "r") as f:
        config = json.load(f)

    with open("../voice_config.json", "r") as f:
        voice_config = json.load(f)

    tts_url = config.get("tts", {}).get("url")
    if not tts_url:
        print("Error: TTS URL not found in config.json")
        return

    # Test TTS connection first
    if not test_tts_connection(tts_url, voice_config):
        print("\nAborting: TTS connection test failed.")
        print("Please ensure the TTS server is running and the model is loaded.")
        return

    # Create client once and reuse
    print(f"\nConnecting to TTS server at {tts_url}...")
    client = Client(tts_url)

    # Read the annotated script (in project root)
    with open("../annotated_script.txt", "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Processing {len(lines)} lines...\n")

    audio_segments = []
    output_dir = "output_audio_cloned"
    os.makedirs(output_dir, exist_ok=True)

    successful = 0
    failed = 0

    for i, line in enumerate(lines):
        if ':' not in line:
            print(f"Skipping line without speaker: '{line}'")
            continue

        speaker, text_to_speak = line.split(':', 1)
        speaker = speaker.strip().replace('*', '').replace('#', '')
        text_to_speak = text_to_speak.strip()

        if not text_to_speak or not speaker:
            continue

        output_path = os.path.join(output_dir, f"line_{i}.wav")
        print(f"[{i+1}/{len(lines)}] {speaker}: '{text_to_speak[:50]}...'")

        if generate_cloned_voice_line(text_to_speak, speaker, voice_config, tts_url, output_path, client):
            try:
                audio_segments.append(AudioSegment.from_wav(output_path))
                successful += 1
            except Exception as e:
                print(f"  Could not process audio file: {e}")
                failed += 1
        else:
            failed += 1

    print(f"\n--- Generation Complete ---")
    print(f"Successful: {successful}, Failed: {failed}")

    if not audio_segments:
        print("No audio segments were generated. Exiting.")
        return

    print(f"\nCombining {len(audio_segments)} audio segments...")
    final_audio = sum(audio_segments)
    output_filename = "../cloned_audiobook.mp3"
    final_audio.export(output_filename, format="mp3")
    print(f"Audiobook saved as {output_filename}")


if __name__ == '__main__':
    main()
