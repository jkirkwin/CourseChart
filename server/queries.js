"use strict";

const { Client } = require('pg');

const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
      }
  });

client.connect();

const getTestTable = (req,res) => {
    var list = [];
    client.query('SELECT * FROM test_table;', (err, result) => {
        if (err) {
            throw err;
        }
        for (let row of result.rows) {
          list.push(JSON.stringify(row));
        }
        res.send(list);    
    });
};
// print test_table
function printTestTable() {
    client.query('SELECT * FROM test_table;', (err, result) => {
        if (err) {
            throw err;
        }
        for (let row of result.rows) {
            console.log(JSON.stringify(row));
        }
    });    
}

const getCourseLink = (req,res) => {
    var list = [];
    client.query('SELECT * FROM course_urls;', (err, result) => {
        if (err) {
            throw err;
        }
        for (let row of result.rows) {
          list.push(JSON.stringify(row));
        }
        res.send(list);    
    });
};

module.exports = {
    getTestTable:getTestTable,
    printTestTable:printTestTable,
    getCourseLink:getCourseLink
};
