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
    //res.json({ info: 'Node.js, Express, and PSQL Api'})
    client.query('SELECT * FROM test_table;', (err, result) => {
        if (err) {
            throw err;
        }
        //res.send(result)
        for (let row of result.rows) {
          list.push(JSON.stringify(row));
        }
        res.send(list);
        //client.end()     
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

module.exports = {
    getTestTable:getTestTable,
    printTestTable:printTestTable
};
