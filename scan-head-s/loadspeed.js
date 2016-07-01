'use strict';
var fs = require('fs')

var page = require('webpage').create(),
    system = require('system'),
    t, address, distance, ntimes, type;

// page.viewportSize = { width: 1366, height: 768 }

if (system.args.length !== 5) {
    console.log('Usage: loadspeed.js <some URL>');
    phantom.exit(1);
} else {
    t = Date.now();

    // console.log("A")
    
    address = system.args[1];
    distance = system.args[2];
    ntimes = system.args[3];
    type = system.args[4];

    // fs.write('./Results/Results.txt', 'Address: ' + address, 'a')
    name = address.split('.')[1]

    page.open(address, function(status) {
        console.log('SUCCESS')
        if (status !== 'success') {
            console.log('Failed to Load address');
        } else {
            t = Date.now() - t;
            fs.write("./Results/Results.txt", ' Page title is ' + page.evaluate(function () {
                return document.title;
            }), 'a');
            page.render("./Results/" + type + "_" + name + ntimes + "_" + Date.now().toString() + '.png')
            fs.write("./Results/Results.txt", ' Loading time ' + t + ' msec' + ' Distance ' + distance + ' File Generated ' + type + "_" + name + "_" + ntimes + Date.now().toString()  + '.png' + '\n', 'a');
            
        }
        phantom.exit();
    });
}

// "use strict";
// var page = require('webpage').create(),
//     system = require('system'),
//     t, address;

// if (system.args.length === 1) {
//     console.log('Usage: loadspeed.js <some URL>');
//     phantom.exit(1);
// } else {
//     t = Date.now();
//     address = system.args[1];
//     console.log(address);
//     page.open(address, function (status) {
//         if (status !== 'success') {
//             console.log('FAIL to load the address');
//         } else {
//             t = Date.now() - t;
//             console.log('Page title is ' + page.evaluate(function () {
//                 return document.title;
//             }));
//             console.log('Loading time ' + t + ' msec');
//         }
//         phantom.exit();
//     });
// }