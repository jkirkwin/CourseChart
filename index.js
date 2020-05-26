/*
 * This file is the entry point for the Node app.
 */

"use strict";

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