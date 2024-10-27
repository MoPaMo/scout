const express = require("express");
const path = require("path");
const Mustache = require("mustache");
const fs = require("fs");

const app = express();
const port = 3000;

//load templates from views
const templates = {};

// Preload templates
function preloadTemplates(templateDir) {
  const files = fs.readdirSync(templateDir);

  files.forEach((file) => {
    const filePath = path.join(templateDir, file);
    const templateName = path.basename(file, ".mustache");

    templates[templateName] = fs.readFileSync(filePath, "utf8");
  });
}

// Initialize templates on startup
preloadTemplates("./views");

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  //send index.html file
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.get("/search", (req, res) => {
  //send index.html file
  res.sendFile(path.join(__dirname, "views", "search.html"));
});

app.get("/lecture/:number/:part?/:name?", (req, res) => {
  const { number, part = 1, name } = req.params;
  console.log({ number, part, name });
  //send index.html file
  res.send(Mustache.render(templates.lecture, { number, part, name }));
});

app.get("/about", (req, res) => {
  //send index
  res.sendFile(path.join(__dirname, "views", "about.html"));
});
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
