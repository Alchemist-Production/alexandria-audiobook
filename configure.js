module.exports = {
  run: [{
    method: "input",
    params: {
      title: "Configure Alexandria",
      description: "Alexandria uses an LLM to convert your book into an annotated script, then a TTS server to generate voice lines for each character.",
      form: [{
        key: "llm_api_key",
        title: "LLM API Key",
        description: "Your Google Gemini API key for script generation. Get one free at https://aistudio.google.com/apikey",
        type: "password",
        placeholder: "AIza...",
        required: true
      }, {
        key: "llm_model_name",
        title: "LLM Model Name",
        description: "The Gemini model to use. Recommended: gemini-2.0-flash (fast) or gemini-1.5-pro (better quality)",
        type: "text",
        default: "gemini-2.0-flash",
        placeholder: "gemini-2.0-flash",
        required: true
      }, {
        key: "tts_url",
        title: "TTS Server URL",
        description: "URL of your Qwen3 TTS Gradio server. Start the TTS server first, then enter its URL here.",
        type: "text",
        default: "http://127.0.0.1:7860",
        placeholder: "http://127.0.0.1:7860",
        required: true
      }]
    }
  }, {
    method: "fs.write",
    params: {
      path: "app/config.json",
      json2: {
        llm: {
          api_key: "{{input.llm_api_key}}",
          model_name: "{{input.llm_model_name}}"
        },
        tts: {
          url: "{{input.tts_url}}"
        }
      }
    }
  }]
}
