module.exports = {
  run: [{
    method: "input",
    params: {
      title: "Configure Alexandria",
      form: [{
        name: "llm_model_name",
        label: "LLM Model Name",
        type: "text",
        placeholder: "gemini-pro"
      }, {
        name: "tts_url",
        label: "TTS URL",
        type: "text",
        placeholder: "http://127.0.0.1:7860/"
      }]
    }
  }, {
    method: "fs.write",
    params: {
      path: "app/config.json",
      content: `{"llm":{"model_name":"{{input.llm_model_name}}"},"tts":{"url":"{{input.tts_url}}"}}`
    }
  }]
}
