module.exports = {
  run: [{
    method: "script.stop",
    params: {
      uri: ["select_input_file.js", "generate_script.js", "parse_voices.js", "configure_voice.js", "generate_audiobook.js"]
    }
  }, {
    method: "fs.rm",
    params: {
      path: "annotated_script.json"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "voices.json"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "voice_config.json"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "state.json"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "app/config.json"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "cloned_audiobook.mp3"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "app/output_audio_cloned"
    }
  }, {
    method: "fs.rm",
    params: {
      path: "voicelines"
    }
  }]
}
