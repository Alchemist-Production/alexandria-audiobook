import os
import json
from pydub import AudioSegment
from gradio_client import Client, handle_file
import shutil

MAX_CHUNK_CHARS = 500
DEFAULT_PAUSE_MS = 500  # Pause between different speakers
SAME_SPEAKER_PAUSE_MS = 250  # Shorter pause for same speaker continuing

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

def parse_lines(lines):
    """Parse lines into (speaker, text) tuples"""
    parsed = []
    for line in lines:
        if ':' not in line:
            continue
        speaker, text = line.split(':', 1)
        speaker = speaker.strip().replace('*', '').replace('#', '')
        text = text.strip()
        if speaker and text:
            parsed.append((speaker, text))
    return parsed

def group_into_chunks(parsed_lines, max_chars=MAX_CHUNK_CHARS):
    """Group consecutive lines by same speaker into chunks up to max_chars"""
    if not parsed_lines:
        return []

    chunks = []
    current_speaker = parsed_lines[0][0]
    current_text = parsed_lines[0][1]

    for speaker, text in parsed_lines[1:]:
        if speaker == current_speaker:
            # Same speaker - try to add to current chunk
            combined = current_text + " " + text
            if len(combined) <= max_chars:
                current_text = combined
            else:
                # Chunk would be too long, save current and start new
                chunks.append((current_speaker, current_text))
                current_text = text
        else:
            # Different speaker - save current chunk and start new
            chunks.append((current_speaker, current_text))
            current_speaker = speaker
            current_text = text

    # Don't forget the last chunk
    chunks.append((current_speaker, current_text))

    return chunks

def generate_cloned_voice_chunk(chunk_text, speaker, voice_config, output_path, client):
    """Generate audio for a text chunk using voice cloning"""
    try:
        voice_data = voice_config.get(speaker)
        if not voice_data:
            print(f"Warning: No voice configuration found for speaker '{speaker}'. Skipping.")
            return False

        ref_audio_path = voice_data.get("ref_audio")
        ref_text = voice_data.get("ref_text")
        seed = int(voice_data.get("seed", -1))

        if not ref_audio_path or not ref_text:
            print(f"Warning: Incomplete voice configuration for speaker '{speaker}'. Skipping.")
            return False

        if not os.path.exists(ref_audio_path):
            print(f"Warning: Reference audio file not found: {ref_audio_path}. Skipping.")
            return False

        result = client.predict(
            handle_file(ref_audio_path),
            ref_text,
            chunk_text,
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
            print(f"Error: No audio file generated for: '{chunk_text[:50]}...'")
            return False

        shutil.copy(generated_audio_filepath, output_path)
        return True

    except Exception as e:
        print(f"Error generating voice for '{speaker}': {e}")
        return False

def combine_audio_with_pauses(audio_segments, speakers, pause_ms=DEFAULT_PAUSE_MS, same_speaker_pause_ms=SAME_SPEAKER_PAUSE_MS):
    """Combine audio segments with pauses between them"""
    if not audio_segments:
        return None

    silence_between_speakers = AudioSegment.silent(duration=pause_ms)
    silence_same_speaker = AudioSegment.silent(duration=same_speaker_pause_ms)

    combined = audio_segments[0]
    prev_speaker = speakers[0]

    for i, (segment, speaker) in enumerate(zip(audio_segments[1:], speakers[1:]), 1):
        if speaker == prev_speaker:
            combined += silence_same_speaker + segment
        else:
            combined += silence_between_speakers + segment
        prev_speaker = speaker

    return combined

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

    # Parse lines and group into chunks
    parsed_lines = parse_lines(lines)
    chunks = group_into_chunks(parsed_lines, MAX_CHUNK_CHARS)

    print(f"Parsed {len(parsed_lines)} lines into {len(chunks)} chunks (max {MAX_CHUNK_CHARS} chars each)\n")

    audio_segments = []
    chunk_speakers = []
    output_dir = "output_audio_cloned"
    os.makedirs(output_dir, exist_ok=True)

    successful = 0
    failed = 0

    for i, (speaker, chunk_text) in enumerate(chunks):
        output_path = os.path.join(output_dir, f"chunk_{i}.wav")
        preview = chunk_text[:60] + "..." if len(chunk_text) > 60 else chunk_text
        print(f"[{i+1}/{len(chunks)}] {speaker} ({len(chunk_text)} chars): '{preview}'")

        if generate_cloned_voice_chunk(chunk_text, speaker, voice_config, output_path, client):
            try:
                audio_segments.append(AudioSegment.from_wav(output_path))
                chunk_speakers.append(speaker)
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

    print(f"\nCombining {len(audio_segments)} audio segments with pauses...")
    print(f"  Pause between speakers: {DEFAULT_PAUSE_MS}ms")
    print(f"  Pause within same speaker: {SAME_SPEAKER_PAUSE_MS}ms")

    final_audio = combine_audio_with_pauses(audio_segments, chunk_speakers)
    output_filename = "../cloned_audiobook.mp3"
    final_audio.export(output_filename, format="mp3")
    print(f"Audiobook saved as {output_filename}")


if __name__ == '__main__':
    main()
