import os
import re
import json
from pydub import AudioSegment
from gradio_client import Client
import shutil

MAX_CHUNK_CHARS = 500
DEFAULT_PAUSE_MS = 500  # Pause between different speakers
SAME_SPEAKER_PAUSE_MS = 250  # Shorter pause for same speaker continuing

def sanitize_filename(name):
    """Make a string safe for use in filenames"""
    name = re.sub(r'[^\w\-]', '_', name)
    return name.lower()

def preprocess_text_for_tts(text):
    """Remove brackets from non-verbal cues so TTS reads them naturally.
    [laughs] -> laughs
    [sighs] I'm tired -> sighs... I'm tired
    """
    # Replace bracketed non-verbals with just the word + ellipsis for pacing
    # e.g., "[laughs]" -> "laughs...", "[sighs] I'm tired" -> "sighs... I'm tired"
    processed = re.sub(r'\[([^\]]+)\]', r'\1...', text)
    # Clean up multiple ellipsis or spaces
    processed = re.sub(r'\.{4,}', '...', processed)
    processed = re.sub(r'\s+', ' ', processed).strip()
    return processed

def test_tts_connection(tts_url, voice_config):
    """Test the TTS connection with the first configured voice"""
    print(f"Testing TTS connection to {tts_url}...")

    speaker = list(voice_config.keys())[0] if voice_config else None
    if not speaker:
        print("Error: No voices configured in voice_config.json")
        return False

    voice_data = voice_config[speaker]
    voice = voice_data.get("voice", "Ryan")
    seed = int(voice_data.get("seed", -1))

    print(f"  Voice: {voice}")
    print(f"  Seed: {seed}")

    try:
        client = Client(tts_url)

        result = client.predict(
            text="Testing, one two three.",
            language="Auto",
            speaker=voice,
            instruct="neutral, clear",
            model_size="1.7B",
            seed=seed,
            api_name="/generate_custom_voice"
        )
        print(f"  Test successful! Output: {result[0]}")
        return True
    except Exception as e:
        print(f"  TTS Test FAILED: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Make sure the TTS server is running")
        print("  2. Check if the CustomVoice model is loaded")
        return False

def group_into_chunks(script_entries, max_chars=MAX_CHUNK_CHARS):
    """Group consecutive entries by same speaker into chunks up to max_chars"""
    if not script_entries:
        return []

    chunks = []
    current_speaker = script_entries[0].get("speaker")
    current_text = script_entries[0].get("text", "")
    current_style = script_entries[0].get("style", "")

    for entry in script_entries[1:]:
        speaker = entry.get("speaker")
        text = entry.get("text", "")
        style = entry.get("style", "")

        if speaker == current_speaker:
            combined = current_text + " " + text
            if len(combined) <= max_chars:
                current_text = combined
                # Keep the more specific style if available
                if style and not current_style:
                    current_style = style
            else:
                chunks.append({
                    "speaker": current_speaker,
                    "text": current_text,
                    "style": current_style
                })
                current_text = text
                current_style = style
        else:
            chunks.append({
                "speaker": current_speaker,
                "text": current_text,
                "style": current_style
            })
            current_speaker = speaker
            current_text = text
            current_style = style

    # Don't forget the last chunk
    chunks.append({
        "speaker": current_speaker,
        "text": current_text,
        "style": current_style
    })

    return chunks

def generate_custom_voice(text, style, speaker, voice_config, output_path, client):
    """Generate audio using CustomVoice model"""
    try:
        voice_data = voice_config.get(speaker)
        if not voice_data:
            print(f"Warning: No voice configuration for '{speaker}'. Skipping.")
            return False

        voice = voice_data.get("voice", "Ryan")
        default_style = voice_data.get("default_style", "")
        seed = int(voice_data.get("seed", -1))

        # Use per-line style if available, otherwise fall back to default
        instruct = style if style else default_style
        if not instruct:
            instruct = "neutral"

        # Preprocess text to handle non-verbal cues naturally
        processed_text = preprocess_text_for_tts(text)

        result = client.predict(
            text=processed_text,
            language="Auto",
            speaker=voice,
            instruct=instruct,
            model_size="1.7B",
            seed=seed,
            api_name="/generate_custom_voice"
        )

        generated_audio_filepath = result[0]
        if not generated_audio_filepath or not os.path.exists(generated_audio_filepath):
            print(f"Error: No audio file generated for: '{text[:50]}...'")
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

    for segment, speaker in zip(audio_segments[1:], speakers[1:]):
        if speaker == prev_speaker:
            combined += silence_same_speaker + segment
        else:
            combined += silence_between_speakers + segment
        prev_speaker = speaker

    return combined

def main():
    # Load configurations
    with open("config.json", "r") as f:
        config = json.load(f)

    with open("../voice_config.json", "r") as f:
        voice_config = json.load(f)

    tts_url = config.get("tts", {}).get("url")
    if not tts_url:
        print("Error: TTS URL not found in config.json")
        return

    # Test TTS connection
    if not test_tts_connection(tts_url, voice_config):
        print("\nAborting: TTS connection test failed.")
        return

    print(f"\nConnecting to TTS server at {tts_url}...")
    client = Client(tts_url)

    # Read the JSON script
    with open("../annotated_script.json", "r", encoding="utf-8") as f:
        script_entries = json.load(f)

    # Group into chunks
    chunks = group_into_chunks(script_entries, MAX_CHUNK_CHARS)

    print(f"Loaded {len(script_entries)} script entries, grouped into {len(chunks)} chunks\n")

    audio_segments = []
    chunk_speakers = []

    temp_dir = "output_audio_cloned"
    os.makedirs(temp_dir, exist_ok=True)

    voicelines_dir = "../voicelines"
    os.makedirs(voicelines_dir, exist_ok=True)

    successful = 0
    failed = 0

    for i, chunk in enumerate(chunks):
        speaker = chunk["speaker"]
        text = chunk["text"]
        style = chunk["style"]

        temp_path = os.path.join(temp_dir, f"chunk_{i}.wav")
        preview = text[:60] + "..." if len(text) > 60 else text
        style_preview = f" [{style}]" if style else ""
        print(f"[{i+1}/{len(chunks)}] {speaker}{style_preview} ({len(text)} chars): '{preview}'")

        if generate_custom_voice(text, style, speaker, voice_config, temp_path, client):
            try:
                segment = AudioSegment.from_wav(temp_path)
                audio_segments.append(segment)
                chunk_speakers.append(speaker)

                # Export individual voiceline
                voiceline_filename = f"voiceline_{i+1:04d}_{sanitize_filename(speaker)}.mp3"
                voiceline_path = os.path.join(voicelines_dir, voiceline_filename)
                segment.export(voiceline_path, format="mp3")

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

    unique_speakers = sorted(set(chunk_speakers))
    print(f"\nSpeakers ({len(unique_speakers)}): {', '.join(unique_speakers)}")
    print(f"Individual voicelines saved to: {os.path.abspath(voicelines_dir)}/")

    print(f"\nCombining {len(audio_segments)} audio segments with pauses...")
    print(f"  Pause between speakers: {DEFAULT_PAUSE_MS}ms")
    print(f"  Pause within same speaker: {SAME_SPEAKER_PAUSE_MS}ms")

    final_audio = combine_audio_with_pauses(audio_segments, chunk_speakers)
    output_filename = "../cloned_audiobook.mp3"
    final_audio.export(output_filename, format="mp3")
    print(f"Combined audiobook saved as {output_filename}")


if __name__ == '__main__':
    main()
