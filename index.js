const express = require("express");
const path = require("path");
const Mustache = require("mustache");
const fs = require("fs");

const app = express();
const port = 3000;
//connect to sqlite3
const sqlite3 = require("sqlite3").verbose();

//open the database
const db = new sqlite3.Database("sqlite3.db", (err) => {
  if (err) {
    console.error(err.message);
  }
  console.log("Connected to the lectures database.");
});

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
  // search for the lecture
  db.get(
    `SELECT * FROM lectures WHERE lecture_number = ? and part_number = ? `,
    [number, part],
    (err, row) => {
      if (err) {
        console.error(err.message);
        res.status(500).send("Internal Server Error");
        return;
      }
      if (row) {
        // Parse tags and wichtig as arrays
        row.tags = JSON.parse(row.tags);
        row.wichtig = JSON.parse(row.wichtig);
        res.send(Mustache.render(templates.lecture, { ...row, name }));
      } else {
        res.send(Mustache.render(templates.lecture404, { number, part, name }));
      }
    }
  );
});

app.get("/about", (req, res) => {
  //send index
  res.sendFile(path.join(__dirname, "views", "about.html"));
});
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
