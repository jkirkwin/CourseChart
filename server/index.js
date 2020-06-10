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
const db = require('./queries');

// use the PORT environment varaible if it is defined.
const defaultPort = 80;
const port = process.env.PORT || defaultPort; 

app.get('/', (req, res) => res.send("Hello"));

function onListen() {
    console.log(`Listening on port ${port}`);
}
app.listen(port, onListen);

/*
* This method sets a path for the method "getTestTable", that is a method
* in queries.js, which prints the table out to the webpage (https://coursechart.herokuapp.com/test_table)

* Once buttons etc. are implemented we can be redirected from the landing page.
*/
app.get('/test_table',db.getTestTable);


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