module.exports = async (kernel) => {
  let installed = await kernel.exists(__dirname, "app", "venv")
  let running = await kernel.running(__dirname, "start.js")

  if (running) {
    let local = await kernel.local(__dirname, "start.js")
    if (local && local.url) {
      return [{
        icon: "fa-solid fa-spin fa-circle-notch",
        text: "Running",
        href: "start.js",
      }, {
        icon: "fa-solid fa-rocket",
        text: "Open Web UI",
        href: local.url,
        target: "_blank"
      }]
    } else {
      return [{
        icon: "fa-solid fa-spin fa-circle-notch",
        text: "Running",
        href: "start.js",
      }]
    }
  } else if (installed) {
    return [{
      icon: "fa-solid fa-book",
      text: "Select a book to process",
      href: "run.js",
      params: {
        run: true,
        requires: "file"
      }
    }, {
      icon: "fa-solid fa-wrench",
      text: "Configure",
      href: "configure.js",
      params: {
        run: true,
      }
    }, {
      icon: "fa-solid fa-power-off",
      text: "Start",
      href: "start.js",
      params: {
        run: true,
      }
    }, {
      icon: "fa-solid fa-arrows-rotate",
      text: "Update",
      href: "update.js",
       params: {
        run: true,
      }
    }, {
      icon: "fa-solid fa-plug",
      text: "Reinstall",
      href: "install.js",
      params: {
        run: true,
      }
    }]
  } else {
    return [{
      icon: "fa-solid fa-plug",
      text: "Install",
      href: "install.js",
      params: {
        run: true,
      }
    }]
  }
}
