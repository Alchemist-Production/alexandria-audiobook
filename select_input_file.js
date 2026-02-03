module.exports = {
  run: [{
    method: "filepicker.open",
    params: {
      title: "Select Book/Novel Text File",
      type: "file",
      filetypes: [["Text Files", "*.txt *.md"]]
    }
  }, {
    method: "json.set",
    params: {
      "state.json": {
        "input_file_path": "{{input.paths[0]}}"
      }
    }
  }]
}
