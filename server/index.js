/*
 * This file is the entry point for the Node app.
 */

"use strict";

// connect to heroku database
const { Client } = require('pg');

const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
      }
  });

client.connect();

const express = require('express');
const app = express();

// use the PORT environment varaible if it is defined.
const defaultPort = 80;
const port = process.env.PORT || defaultPort; 

app.get('/', (req, res) => res.send("Helloaaaa"));

function onListen() {
    console.log(`Listening on port ${port}`);
}
app.listen(port, onListen);

// print test_table
client.query('SELECT * FROM test_table;', (err, res) => {
  if (err) {
      throw err;
  }
  for (let row of res.rows) {
    console.log(JSON.stringify(row));
  }
  client.end();
});
