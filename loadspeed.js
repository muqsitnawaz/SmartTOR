'use strict';
var fs = require('fs')

var page = require('webpage').create(),
    system = require('system'),
    t, address;

page.viewportSize = { width: 1366, height: 768 }

if (system.args.length === 1) {
    console.log('Usage: loadspeed.js <some URL>');
    phantom.exit(1);
} else {
    t = Date.now();
    address = system.args[1];
    console.log('address: ' + address)
    name = address.split('.')[1]

    page.open(address, function(status) {
        if (status !== 'success') {
            console.log('FAIL to load the address');
        } else {
            t = Date.now() - t;
            console.log('Page title is ' + page.evaluate(function () {
                return document.title;
            }));
            console.log('Loading time ' + t + ' msec');
            page.render(name+'.png')
		    fs.write(name+'.html', page.content, 'w')
		    console.log('page rendered and written')
        }
        phantom.exit();
    });
}