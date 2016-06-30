const publicIp = require('public-ip')
const http = require('http')
const fs = require('fs')
const exec = require('child_process').exec

const sizes = [10000, 100000, 1000000, 10000000, 100000000, 1000000000]

exec('bash generator.sh', function callback(err, stdout, stderr) {
  if (err) {
    console.error(err)
  } else {
    console.log('files generated')
    
    // finding public ip
    publicIp.v4().then(ip => {
      // creating and running server
      const server = http.createServer(function (req, res) {
      const fileName = req.url.substring(1,req.url.length)
      console.log('REQ: file requested '+fileName+'B')

      if (sizes.indexOf(parseInt(fileName)) === -1) {
        res.end('File not found')
        console.log('RESP: file not found')
      } else {
        res.writeHead(200, {
          'Content-Type': 'audio/mpeg',
          'Content-Length': 10000
        })

        var readStream = fs.createReadStream(req.url.substring(1,req.url.length))
        readStream.on('open', function () {
          readStream.pipe(res)
        })

        readStream.on('end', function() {
          console.log('RESP: file sent')
          res.end('')
        })
      }
    }).listen(80, ip.toString())

    console.log("Server running at http://127.0.0.1:8000/")
  })
  }
})