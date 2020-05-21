var WebSocketServer = require('websocket').server;
var http = require('http');
var net = require('net');


var args = process.argv.slice(2);
var argsSplit = args[0].split('-');
var ip = argsSplit[0]
var port = parseInt(argsSplit[1])
var portInternal = parseInt(argsSplit[2])

var server = http.createServer(function(request, response) {
});

server.listen(port, function() {
    console.log("[NODE]:: " + (new Date()) + " Server is listening on ip: " + ip + " on port: " + port);
});

wsServer = new WebSocketServer({
    httpServer: server
});

wsServer.on('request', function(request) {

    var client = new net.Socket();
    
    client.connect(portInternal, ip, function() {
        console.log("[NODE]:: Connected");        
    });

    client.on('data', function(data) {
        console.log('[NODE]:: Received: ' + data);
        connection.sendUTF(data);
        //client.destroy();
    });

    client.on('close', function() {
        console.log('[NODE]:: Connection closed');
    });

    var connection = request.accept(null, request.origin);

    connection.on('message', function(message) {
        client.write(message.utf8Data + "\n");
    });

    connection.on('close', function(connection) {
    });

});