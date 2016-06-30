const publicIp = require('public-ip')
const https = require('https')
const fs = require('fs')
const exec = require('child_process').exec

const sizes = [10000, 100000, 1000000, 10000000, 100000000, 1000000000]
// reading certificates
const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
}

// finding public ip
publicIp.v4().then(ip => {
  // creating and running server
  const server = https.createServer(options, function (req, res) {
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
  }).listen(16667, ip.toString())

  console.log("Server running at http://"+ip+":80/")
})