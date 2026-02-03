const fs = require('fs')
const path = require('path')

module.exports = {
  version: "5.0",
  title: "Alexandria",
  description: "A tool that takes a text document containing a book or a novel, ingests it with an LLM to produce an annotated script, and then uses a TTS API to generate the voice lines, finally stitching them together into an audiobook in MP3 format.",
  icon: "icon.png",
  menu: async (kernel, info) => {
    // Check running states
    let running = {
      install: info.running("install.js"),
      configure: info.running("configure.js"),
      select_input_file: info.running("select_input_file.js"),
      generate_script: info.running("generate_script.js"),
      parse_voices: info.running("parse_voices.js"),
      configure_voice: info.running("configure_voice.js"),
      generate_audiobook: info.running("generate_audiobook.js"),
      reset: info.running("reset.js"),
      update: info.running("update.js")
    }

    // Check file existence states
    let installed = info.exists("app/env")
    let configured = info.exists("app/config.json")
    let hasState = info.exists("state.json")
    let hasScript = info.exists("annotated_script.txt")
    let hasVoices = info.exists("voices.json")
    let hasVoiceConfig = info.exists("voice_config.json")
    let hasAudiobook = info.exists("cloned_audiobook.mp3")

    // Read state.json for input file path
    let inputFilePath = null
    if (hasState) {
      try {
        const statePath = path.join(__dirname, "state.json")
        const stateContent = fs.readFileSync(statePath, 'utf8')
        const state = JSON.parse(stateContent)
        inputFilePath = state.input_file_path
      } catch (e) {
        // Ignore parse errors
      }
    }

    // Read voices.json and voice_config.json to find unconfigured voices
    let voices = []
    let configuredVoices = {}
    let unconfiguredVoices = []

    if (hasVoices) {
      try {
        const voicesPath = path.join(__dirname, "voices.json")
        const voicesContent = fs.readFileSync(voicesPath, 'utf8')
        voices = JSON.parse(voicesContent)
      } catch (e) {
        // Ignore parse errors
      }
    }

    if (hasVoiceConfig) {
      try {
        const voiceConfigPath = path.join(__dirname, "voice_config.json")
        const voiceConfigContent = fs.readFileSync(voiceConfigPath, 'utf8')
        configuredVoices = JSON.parse(voiceConfigContent)
      } catch (e) {
        // Ignore parse errors
      }
    }

    // Find unconfigured voices
    unconfiguredVoices = voices.filter(voice => {
      const config = configuredVoices[voice]
      return !config || !config.ref_audio || !config.ref_text
    })

    // Handle running states first (show terminal with default: true)
    if (running.install) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing",
        href: "install.js"
      }]
    }

    if (running.configure) {
      return [{
        default: true,
        icon: "fa-solid fa-wrench",
        text: "Configuring",
        href: "configure.js"
      }]
    }

    if (running.select_input_file) {
      return [{
        default: true,
        icon: "fa-solid fa-file",
        text: "Selecting File",
        href: "select_input_file.js"
      }]
    }

    if (running.generate_script) {
      return [{
        default: true,
        icon: "fa-solid fa-scroll",
        text: "Generating Script",
        href: "generate_script.js"
      }]
    }

    if (running.parse_voices) {
      return [{
        default: true,
        icon: "fa-solid fa-users",
        text: "Parsing Voices",
        href: "parse_voices.js"
      }]
    }

    if (running.configure_voice) {
      return [{
        default: true,
        icon: "fa-solid fa-microphone",
        text: "Configuring Voice",
        href: "configure_voice.js"
      }]
    }

    if (running.generate_audiobook) {
      return [{
        default: true,
        icon: "fa-solid fa-headphones",
        text: "Generating Audiobook",
        href: "generate_audiobook.js"
      }]
    }

    if (running.reset) {
      return [{
        default: true,
        icon: "fa-solid fa-rotate-left",
        text: "Resetting",
        href: "reset.js"
      }]
    }

    if (running.update) {
      return [{
        default: true,
        icon: "fa-solid fa-arrows-rotate",
        text: "Updating",
        href: "update.js"
      }]
    }

    // STATE: NOT_INSTALLED - auto-run install
    if (!installed) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Install",
        href: "install.js"
      }]
    }

    // STATE: NOT_CONFIGURED
    if (!configured) {
      return [{
        icon: "fa-solid fa-wrench",
        text: "Configure Alexandria",
        href: "configure.js"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      }]
    }

    // STATE: NO_INPUT_FILE
    if (!inputFilePath) {
      return [{
        icon: "fa-solid fa-file-import",
        text: "Select Input File",
        href: "select_input_file.js"
      }, {
        icon: "fa-solid fa-wrench",
        text: "Reconfigure",
        href: "configure.js"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      }]
    }

    // STATE: NO_SCRIPT
    if (!hasScript) {
      return [{
        icon: "fa-solid fa-scroll",
        text: "Generate Script",
        href: "generate_script.js",
        params: {
          input_file_path: inputFilePath
        }
      }, {
        icon: "fa-solid fa-file-import",
        text: "Change Input File",
        href: "select_input_file.js"
      }, {
        icon: "fa-solid fa-wrench",
        text: "Reconfigure",
        href: "configure.js"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      }]
    }

    // STATE: NO_VOICES_PARSED
    if (!hasVoices) {
      return [{
        icon: "fa-solid fa-users",
        text: "Parse Voices",
        href: "parse_voices.js"
      }, {
        icon: "fa-solid fa-scroll",
        text: "Regenerate Script",
        href: "generate_script.js",
        params: {
          input_file_path: inputFilePath
        }
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      }]
    }

    // STATE: VOICES_NOT_CONFIGURED
    if (unconfiguredVoices.length > 0) {
      let menu = []

      menu.push({
        icon: "fa-solid fa-info-circle",
        text: `${unconfiguredVoices.length} voice(s) need configuration`
      })

      // Add menu item for each unconfigured voice
      unconfiguredVoices.forEach(voice => {
        menu.push({
          icon: "fa-solid fa-microphone",
          text: `Configure: ${voice}`,
          href: "configure_voice.js",
          params: {
            speaker: voice
          }
        })
      })

      menu.push({
        icon: "fa-solid fa-users",
        text: "Re-parse Voices",
        href: "parse_voices.js"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      })

      return menu
    }

    // STATE: READY_TO_GENERATE
    if (!hasAudiobook) {
      return [{
        icon: "fa-solid fa-headphones",
        text: "Generate Audiobook",
        href: "generate_audiobook.js"
      }, {
        icon: "fa-solid fa-microphone",
        text: "Reconfigure Voices",
        href: "parse_voices.js"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.js"
      }, {
        icon: "fa-solid fa-rotate-left",
        text: "Reset",
        href: "reset.js"
      }]
    }

    // STATE: COMPLETE - default to open audiobook
    return [{
      default: true,
      icon: "fa-solid fa-play",
      text: "Open Audiobook",
      href: "cloned_audiobook.mp3"
    }, {
      icon: "fa-solid fa-folder-open",
      text: "Open Output Folder",
      href: "app/output_audio_cloned"
    }, {
      icon: "fa-solid fa-headphones",
      text: "Regenerate Audiobook",
      href: "generate_audiobook.js"
    }, {
      icon: "fa-solid fa-file-import",
      text: "New Book",
      href: "select_input_file.js"
    }, {
      icon: "fa-solid fa-plug",
      text: "Reinstall",
      href: "install.js"
    }, {
      icon: "fa-solid fa-rotate-left",
      text: "Reset",
      href: "reset.js"
    }]
  }
}
