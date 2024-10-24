const express = require("express");
const path = require("path");

const app = express();
const port = 3000;

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
app.get("/lecture/abc", (req, res) => {
  //send index.html file
  res.sendFile(path.join(__dirname, "views", "lecture.html"));
});

app.get("/about", (req, res) => {
  //send index
  res.sendFile(path.join(__dirname, "views", "about.html"));
});
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
