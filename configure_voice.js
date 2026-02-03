module.exports = {
  run: [{
    method: "input",
    params: {
      title: "Configure Voice: {{args.speaker}}",
      description: "Provide a short audio sample (~5-15 seconds) of someone speaking in the voice you want for this character, along with the exact transcript of what they say.",
      form: [{
        key: "ref_text",
        title: "Reference Audio Transcript",
        description: "Type the EXACT words spoken in your reference audio file. This must match precisely for voice cloning to work.",
        type: "text",
        placeholder: "Hello, this is a sample of my voice...",
        required: true
      }, {
        key: "seed",
        title: "Voice Seed (Optional)",
        description: "Set a consistent seed for reproducible voice output. Use -1 for random, or any positive integer for consistent results.",
        type: "text",
        default: "-1",
        required: false
      }]
    }
  }, {
    // Save form values to local variables before filepicker overwrites input
    method: "local.set",
    params: {
      ref_text: "{{input.ref_text}}",
      seed: "{{input.seed || '-1'}}"
    }
  }, {
    method: "filepicker.open",
    params: {
      title: "Select Reference Audio for {{args.speaker}}",
      type: "file",
      filetypes: [["Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a"]]
    }
  }, {
    method: "json.set",
    params: {
      "voice_config.json": {
        "{{args.speaker}}.ref_audio": "{{input.paths[0]}}",
        "{{args.speaker}}.ref_text": "{{local.ref_text}}",
        "{{args.speaker}}.seed": "{{local.seed}}"
      }
    }
  }]
}
