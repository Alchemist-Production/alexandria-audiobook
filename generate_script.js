module.exports = {
  run: [{
    method: "shell.run",
    params: {
      venv: "env",
      path: "app",
      message: "python generate_script.py \"{{args.input_file_path}}\""
    }
  }]
}
