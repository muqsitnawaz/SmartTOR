// 'use strict';
var fs = require('fs')

var page = require('webpage').create(),
    system = require('system'),
    t, address, distance, ntimes, fp1, fp2, fp3, totalSize;

totalSize = 0;
var USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0';

// page.viewportSize = { width: 1366, height: 768 }

function getRealSize(response) {
    var tmp, size;
    for(var i=0; i<response.headers.length; i++) {
        tmp = response.headers[i];
        if(tmp.name == 'Content-Length') {
            return parseInt(tmp.value, 10);
        }
    } 
}

if (system.args.length !== 7) {
    console.log('Usage: loadspeed.js <some URL>');
    phantom.exit(1);
} else {
    t = Date.now();
    
    address = system.args[1];
    distance = system.args[2];
    ntimes = system.args[3];
    fp1 = system.args[4];
    fp2 = system.args[5];
    fp3 = system.args[6];

    // fs.write('./Results/Results.txt', 'Address: ' + address, 'a')
    name = address.split('.')[1]

    // page.clearMemoryCache();

    page.onResourceError = function(resourceError) {
        console.error("ERROR: " + resourceError.url + ': ' + resourceError.errorString);
    };

    page.onResourceReceived = function(response) {
  		size = getRealSize(response) || response.bodySize;

  		if (size !== undefined) {
  			totalSize = totalSize + size
  		}
	};

    page.settings.userAgent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0';

    page.open(address, function(status) {
        if (status !== 'success') {
            console.log(address + ': Failed to Load address');
        } else {
            t = Date.now() - t;
            fs.write("./Results/Results.txt", ' Page title is ' + page.evaluate(function () {
                return document.title;
            }), 'a');
            page.render("./Results/" + name + "_" + ntimes + "_" + Date.now().toString() + '.png')
            fs.write("./Results/Results.txt", ' ' + fp1 + ' ' + fp2 + ' ' + fp3 + ' Loading time ' + t + ' msec' + ' Distance ' + distance + ' Size ' + totalSize + ' File Generated ' + name + "_" + ntimes + "_" + Date.now().toString()  + '.png' + '\n', 'a');
            console.log(address + ': Success')
            
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