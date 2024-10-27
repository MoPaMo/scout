const express = require("express");
const path = require("path");
const mustacheExpress = require("mustache-express");
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

app.engine("mustache", mustacheExpress());
app.set("view engine", "mustache");
app.set("views", __dirname + "/views");

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  //send index.html file
  res.render("index");
});

app.get("/search", (req, res) => {
  res.render("search");
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
        //get lecture_excerpts
        db.all(
          `SELECT * FROM lecture_excerpts WHERE lecture_id = ? `,
          [row.id],
          (err, excerpts) => {
            if (err) {
              console.error(err.message);
              res.status(500).send("Internal Server Error");
              return;
            }
            if (excerpts) {
              // Parse tags and wichtig as arrays
              console.log(excerpts, row.id);
              res.render("lecture", { ...row, name, excerpts });
            } else {
              res.render("lecture404", { number, part, name });
            }
          }
        );
      } else {
        res.render("lecture404", { number, part, name });
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
