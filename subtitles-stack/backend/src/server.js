const config = require("./config");
const createApp = require("./app");

createApp()
  .then((app) => {
    app.listen(config.port, () => {
      console.log(`Subtitle backend listening on http://localhost:${config.port}`);
    });
  })
  .catch((error) => {
    console.error("Unable to start subtitle backend.", error);
    process.exit(1);
  });
