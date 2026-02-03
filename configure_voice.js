module.exports = {
  run: [{
    method: "input",
    params: {
      title: "Configure Voice: {{args.speaker}}",
      description: "Select a voice and set the default style for this character. The style can be overridden per-line in the script.",
      form: [{
        key: "voice",
        title: "Voice",
        description: "Select a voice for this character",
        type: "select",
        items: [
          { text: "Aiden", value: "Aiden" },
          { text: "Dylan", value: "Dylan" },
          { text: "Eric", value: "Eric" },
          { text: "Ono_anna", value: "Ono_anna" },
          { text: "Ryan (default)", value: "Ryan" },
          { text: "Serena", value: "Serena" },
          { text: "Sohee", value: "Sohee" },
          { text: "Uncle_fu", value: "Uncle_fu" },
          { text: "Vivian", value: "Vivian" }
        ],
        default: "Ryan",
        required: true
      }, {
        key: "default_style",
        title: "Default Style",
        description: "Default delivery style for this character (used when no per-line style is specified)",
        type: "text",
        placeholder: "calm, professional narrator",
        required: false
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
    method: "json.set",
    params: {
      "voice_config.json": {
        "{{args.speaker}}.voice": "{{input.voice}}",
        "{{args.speaker}}.default_style": "{{input.default_style || ''}}",
        "{{args.speaker}}.seed": "{{input.seed || '-1'}}"
      }
    }
  }]
}
