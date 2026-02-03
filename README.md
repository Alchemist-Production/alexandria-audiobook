<img width="475" height="467" alt="Gemini_Generated_Image_yk5astyk5astyk5a" src="https://github.com/user-attachments/assets/fa2c36d3-a5f3-49ab-9dfe-30933359dfbd" />


# Alexandria Audiobook Generator

Transform any book or novel into a fully-voiced audioplay using AI-powered script annotation and styled TTS.

## Features

- **LLM Script Annotation** - Google Gemini parses your text into a JSON script with speakers, dialogue, and style directions
- **Non-verbal Sounds** - Supports `[laughs]`, `[sighs]`, `[gasps]`, and other locutions inline with dialogue
- **Style Instructions** - Per-line delivery directions like "nervous, whispered" or "angry, shouting"
- **Custom Voices** - 9 pre-trained voices (Aiden, Dylan, Eric, Ono_anna, Ryan, Serena, Sohee, Uncle_fu, Vivian)
- **Smart Chunking** - Groups consecutive lines by speaker (up to 500 chars) for natural flow
- **Natural Pauses** - Automatic delays between speakers and segments
- **Audioplay Export** - Individual voiceline files for audio editing (Audacity, etc.)

## Requirements

- [Pinokio](https://pinokio.computer/)
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))
- Qwen3 TTS server running locally (Gradio interface)

## Installation

1. Install [Pinokio](https://pinokio.computer/) if you haven't already
2. In Pinokio, click **Download** and paste this URL:
   ```
   https://github.com/Finrandojin/alexandria-audiobook
   ```
3. Click **Install** to set up dependencies
4. Click **Configure** and enter:
   - Your Gemini API key
   - TTS server URL (default: `http://127.0.0.1:7860`)

## Usage

1. **Select File** - Choose your book/novel text file (.txt or .md)
2. **Generate Script** - LLM creates JSON script with speakers, text, style, and non-verbals
3. **Parse Voices** - Extracts unique speakers from script
4. **Configure Voices** - For each speaker, select:
   - A voice (Aiden, Dylan, Eric, Ono_anna, Ryan, Serena, Sohee, Uncle_fu, Vivian)
   - Default style direction
   - Optional: seed for reproducible output
5. **Generate Audiobook** - Creates final MP3 and individual voicelines

## Script Format

The generated script is a JSON array with style directions and non-verbal cues:

```json
[
  {"speaker": "NARRATOR", "text": "The door creaked open slowly.", "style": "tense, suspenseful"},
  {"speaker": "ELENA", "text": "[gasps] Who's there?", "style": "frightened, whispered"},
  {"speaker": "MARCUS", "text": "[chuckles] Did you miss me?", "style": "smug, menacing"}
]
```

## Output

**Combined Audiobook:**
- `cloned_audiobook.mp3` - Full audiobook with natural pauses

**Individual Voicelines (for audio editing):**
- `voicelines/voiceline_0001_narrator.mp3`
- `voicelines/voiceline_0002_elena.mp3`
- `voicelines/voiceline_0003_marcus.mp3`
- ...

Files are numbered in timeline order and include the speaker name, making it easy to:
- Import into Audacity or other DAWs
- Place each character on separate tracks
- Color-code by speaker
- Fine-tune timing and effects

## License

MIT
