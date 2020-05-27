/*
 * This file is the entry point for the Node app.
 */
const express = require('express'); 
const app = express();

// use the PORT environment varaible if it is defined.
const defaultPort = 80;
const port = process.env.PORT || defaultPort; 

app.get('/', (req, res) => res.send("Hello"));

function onListen() {
    console.log(`Listening on port ${port}`);
}
app.listen(port, onListen);

// connect to heroku database
const { Client } = require('pg');

const client = new Client({
    host: 'ec2-18-233-32-61.compute-1.amazonaws.com',
    port: 5432,
    user: 'gadyrjddeeskwc',
    password: '8a6d028082f3a13122125822711519bb0b547f597301b1e6006f89978c04e5aa',
    database: 'd4i5njekim7upa',
    ssl: {
        rejectUnauthorized: false
      }
  })

client.connect();

// print test_table
client.query('SELECT * FROM test_table;', (err, res) => {
  if (err) throw err;
  for (let row of res.rows) {
    console.log(JSON.stringify(row));
  }
  client.end();
});
