var fs = require('fs');

var page = require("webpage").create();
var urls = ["http://www.deals.com.pk/"]

var url = urls[0]
var len = urls.length
var lasturl = urls[len-1]
var time =-1;
var counter =1;
var glob =-1;
// time for a simple page around 30s ; time for proxy around 70s 

page.viewportSize = { width: 1024, height: 768 };
setInterval(starter, 20000);
//starter()
function starter()
{

page.open(url, function (status) 
{   glob = glob +1;
    time = time + 1 ;
    console.log(time)

    checkReadyState();
    
    });
}    
function onPageReady() {
    
    page.render(glob+'result' + time  + '.png');
    var content = page.content;
    fs.write(glob+"test" + time+ ".html", content, 'w')
//    page.render('result' + time + url + '.pdf');

    if (time === 4)
    {
	if (url ===lasturl)
    		{
		phantom.exit();
		}
	else 
		{
	 	time =-1;
		url = urls[counter];
		counter = counter +1
		}
    }
}    
    
function checkReadyState() {
        setTimeout(function () {
            var readyState = page.evaluate(function () {
                return document.readyState;
            });

            if ("complete" === readyState) {
                onPageReady();
            } else {
                checkReadyState();
            }
        });
    }
