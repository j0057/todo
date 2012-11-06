mp3.component.Object = function() {
};

mp3.component.Object.extend(window.Object, {
    CLASSNAME: 'mp3.component.Object',
    
    constructor: mp3.component.Object,
    
    log: function(message) {
        message = '[' + this.CLASSNAME + '] ' + message;
        if (console && console.log) {
            console.log(message);
        }
    },
    
    error: function(message) {
        message = '[' + this.CLASSNAME + '] ' + message;
        if (console && console.error) {
            console.error(message);
        }
    },
    
    dir: function(obj) {
        if (console && console.dir) {
            console.dir(obj);
        }
    },
    
    dirxml: function(obj) {
        if (console && console.dirxml) {
            console.dirxml(obj);
        }
    },

    HTTP_REQUEST_ID: 0,
    httpRequest: function(method, target, handler, headers, content) {
        var request = new XMLHttpRequest(),
            id = ++mp3.component.Object.prototype.HTTP_REQUEST_ID,
            t = function() { return (new Date()).getTime(); },
            t1 = t();

        headers = headers || {};
        content = content || '';
        
        this.log('{0} -> {1} {2}'.format(id, method, target));

        // if headers is a string, treat it as if it were the content type
        if (typeof headers == 'string') 
            headers = {'Content-Type': headers};
            
        // send extra header like jQuery does
        headers['X-Requested-With'] = 'XMLHttpRequest';
        
        // serialize content
        switch (headers['Content-Type']) {
            case 'application/json':
                content = JSON.stringify(content);
                break;
            case 'application/xml':
                content = mp3.xml(content);
                break;
        }
        
        if (content) {
            this.log('{0} -> {1}'.format(id, content));
        }    
        
        // listen for state change events
        mp3.hook(request, {
            readystatechange: function() {
                if (request.readyState == request.DONE) {
                    var t2 = t();
                    if (handler) {
                        // deserialize result
                        var response = null;
                        switch (request.getResponseHeader('Content-Type')) {
                            case 'application/json; charset=UTF-8':
                            case 'application/json':
                                response = JSON.parse(request.responseText);
                                break;
                            case 'application/xml':
                                response = request.responseXml;
                                break;
                            case 'text/plain':
                                response = request.responseText;
                                break;
                        }
                        
                        if (response)
                            this.dir(response);
                        
                        // call handler with result
                        handler(request, response);
                    }

                    var t3 = t();
                    this.log('{0} <- {1} {2} (request {3} + handler {4} = {5}s)'.format(
                        id, request.status, request.statusText, 
                        (t2 - t1) / 1000,
                        (t3 - t2) / 1000,
                        (t3 - t1) / 1000));
                }
            }.bind(this)
        });

        // open connection, set headers and send request
        request.open(method, target, true);
        Object.keys(headers)
            .map(function(key) {
                request.setRequestHeader(key, headers[key]);
            });
        request.send(content);
    },
});
