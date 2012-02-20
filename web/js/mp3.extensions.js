(function(ext) {
    for (var typeName in ext) {
        for (var funcName in ext[typeName]) {
            if (!window[typeName].prototype[funcName]) {
                window[typeName].prototype[funcName] = ext[typeName][funcName];
            }
        }
    }
})({
    /*Object: {
        keys: function() {
            var result = [];
            for (var key in this) {
                if (this.hasOwnProperty(key) {
                    result.push(key);
                }
            }
            return result;
        },
        
        values: function() {
            var result = [];
            for (var key in this) {
                if (this.hasOwnProperty(key)) {
                    result.push(this[key]);
                }
            }
            return result;
        }
    },*/

    Function: {
        bind: function(obj) {
            var func = this;
            return function() {
                return func.apply(obj, arguments);
            }
        },

        extend: function(parent, newPrototype) {
            this.prototype = new parent;
            this.prototype.constructor = this;
            this.prototype.SUPER = parent;
            Object.keys(newPrototype).map(function(k) { 
                var m = /^_set_(.*)$/.exec(k); 
                if (m) 
                    this.prototype.__defineSetter__(m[1], newPrototype[k]);
                else {
                    m = /^_get_(.*)$/.exec(k); 
                    if (m) 
                        this.prototype.__defineGetter__(m[1], newPrototype[k]);
                    else
                        this.prototype[k] = newPrototype[k]; 
                }
            }.bind(this));
            return this;
        }
    },
    
    Array: {
        map: function(proj) {
            var result = [];
            for (var i = 0; i < this.length; i++) {
                result.push(proj(this[i]));
            }
            return result;
        },

        filter: function(pred) {
            var result = [];
            for (var i = 0; i < this.length; i++) {
                if (pred(this[i])) {
                    result.push(this[i]);
                }
            }
            return result;
        },

        reduce: function(acc, init) {
            var result = init;
            for (var i = 0; i < this.length; i++) {
                result = acc(init, this[i]);
            }
            return result;
        },

        sorted: function(opt) {
            opt = opt || {};
            opt.cmp = opt.cmp || function(a,b) { return a < b ? -1 : a == b ? 0 : 1; };
            opt.sel = opt.sel || function(i)   { return i; };
            return this.concat().sort(function(a, b) {
                return opt.cmp(opt.sel(a), opt.sel(b));
            });
        },

        any: function(p) {
            for (var i = 0; i < this.length; i++) {
                if (p(this[i])) {
                    return true;
                }
            }
            return false;
        },

        all: function(p) {
            for (var i = 0; i < this.length; i++) {
                if (!p(this[i])) {
                    return false;
                }
            }
            return true;
        },

        contains: function(item) {
            return this.any(function(x) { return x == item; });
        }
    },
    
    String: {
        escapeURI: function() {
            return encodeURI(this)
                .replace(/\//g, '%2F')
                .replace(/\+/g, '%2B')
                .replace(/%20/g,'+')
                .replace(/#/g, '%23')
        },

        format: function(/*...*/) {
            var result = this;
            for (var i = 0; i < arguments.length; i++) {
                result = result.replace('{'+i+'}', arguments[i])
            }
            return result;
        }
    }
});
