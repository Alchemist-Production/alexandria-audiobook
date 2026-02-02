module.exports = {
  run: [{
    method: "shell.run",
    params: {
      venv: "env",
      path: "app",
      message: "python process_book.py --file {{args.file}}",
    }
  }]
}
