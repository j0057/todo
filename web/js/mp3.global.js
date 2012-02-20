console = window.console || {};
console.log = window.console.log || function() {};
console.dir = window.console.dir || function() {};
console.error = window.console.error || function() {};

mp3 = {
    component: {},
    engine   : {},
    view     : {},
    
    template: function(templateId, values) {
        var fill = function(elem) {
                // replace text in attribute values
                for (var i = 0; i < elem.attributes.length; i++) {
                    var attr = elem.attributes[i];
                    Object.keys(values)
                        .map(function(key) { 
                            attr.value = attr.value.replace('{' + key + '}', values[key]);
                        });
                }
                // replace text in child nodes
                for (var i = 0; i < elem.childNodes.length; i++) {
                    var child = elem.childNodes[i];
                    switch (child.nodeType) {
                        // fill values in child elements recursively
                        case Node.ELEMENT_NODE:
                            fill(child);
                            break;
                        // replace values in text nodes
                        case Node.TEXT_NODE:
                            mp3.keys(values).map(function(key) {
                                child.nodeValue = child.nodeValue.replace('{' + key + '}', values[key]);
                            });
                            break;
                    }
                }
                return elem;
            };
        return fill(document.getElementById(templateId).firstElementChild.cloneNode(true));
    },
 
    keys: function(obj) { 
        var result = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                result.push(key);
            }
        }
        return result;
    },

    hook: function(obj, handlers, context) {
        Object.keys(handlers) 
            .map(function(n) {
                var handler = context ? handlers[n].bind(context) : handlers[n];
                if (obj.addEventListener) 
                    obj.addEventListener(n, handler, true); 
            });
    },

    unhook: function(obj, handlers) {
        Object.keys(handlers)
            .map(function(eventName) { 
                obj.removeEventListener(eventName, handlers[eventName], true); 
            });
    },
    
    urlJoin: function() {
        var result = "";
        for (var i = 0; i < arguments.length; i++) {
            result += "/";
            result += arguments[i].escapeURI();
        }
        return result;
    }
};
