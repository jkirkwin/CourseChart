/*
 * This file is the entry point for the Node app.
 */

"use strict";

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
app.get('/',db.printTestTable);
app.get('/test_table',db.getTestTable);
