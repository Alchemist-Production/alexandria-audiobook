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
      }]
    }
  }, {
    // Save ref_text to local variable before filepicker overwrites input
    method: "local.set",
    params: {
      ref_text: "{{input.ref_text}}"
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
        "{{args.speaker}}.ref_text": "{{local.ref_text}}"
      }
    }
  }]
}
