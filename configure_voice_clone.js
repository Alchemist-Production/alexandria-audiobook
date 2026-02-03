module.exports = {
  run: [{
    method: "input",
    params: {
      title: "Clone Voice: {{args.speaker}}",
      description: "Clone a voice from reference audio. The voice characteristics will be captured from your sample. Note: Style directions from the script will be ignored for cloned voices.",
      form: [{
        key: "ref_text",
        title: "Reference Text",
        description: "The EXACT transcript of what is spoken in your reference audio",
        type: "text",
        placeholder: "Type the exact words spoken in the audio...",
        required: true
      }, {
        key: "seed",
        title: "Seed (Optional)",
        description: "Set a consistent seed for reproducible output. Use -1 for random.",
        type: "text",
        default: "-1",
        required: false
      }]
    }
  }, {
    method: "local.set",
    params: {
      ref_text: "{{input.ref_text}}",
      seed: "{{input.seed || '-1'}}"
    }
  }, {
    method: "filepicker.open",
    params: {
      title: "Select Reference Audio for {{args.speaker}}",
      type: "file"
    }
  }, {
    method: "json.set",
    params: {
      "voice_config.json": {
        "{{args.speaker}}.type": "clone",
        "{{args.speaker}}.ref_audio": "{{input.paths[0]}}",
        "{{args.speaker}}.ref_text": "{{local.ref_text}}",
        "{{args.speaker}}.seed": "{{local.seed}}"
      }
    }
  }]
}
