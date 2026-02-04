module.exports = {
  run: [{
    method: "shell.run",
    params: {
      venv: "env",
      path: "app",
      message: "python app.py",
      on: [{ "event": "/http:\/\/[0-9.:]+/", "done": true }]
    }
  }, {
    method: "local.set",
    params: {
      url: "{{input.event[0]}}"
    }
  }, {
    method: "browser.open",
    params: {
      uri: "{{local.url}}",
      target: "_blank"
    }
  }, {
    method: "input",
    params: {
      title: "Alexandria is Running",
      description: "The application is running. You can close this tab to stop the server."
    }
  }]
}
