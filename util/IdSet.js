var IdSet = (function () {
    function IdSet() {
        this._items = {};
        this._size = 0;
    }

    IdSet.from = function (o) {
        if (o instanceof IdSet) {
            return o.clone();
        }
        var ret = new IdSet();
        if (Array.isArray(o)) {
            o.forEach(function (e) {
                ret.add(e);
            });
        } else {
            ret.add(o);
        }
        return ret;
    }

    IdSet.prototype = {
        constructor: IdSet,

        add: function (e) {
            var k = this._keyOf(e);
            if (this._accept(k) && !this._has(k)) {
                this._store(k, e);
                ++this._size;
            }
            return this;
        },
        remove: function (e) {
            var k = this._keyOf(e);
            if (this._accept(k) && this._has(k)) {
                this._drop(k);
                --this._size;
            }
            return this;
        },
        contains: function (e) {
            var k = this._keyOf(e);
            return this._accept(k) && this._has(k);
        },
        clear: function () {
            this._items = {};
            this._size = 0;
        },
        size: function () {
            return this._size;
        },
        isEmpty: function () {
            return !this._size;
        },
        allIn: function (c) {
            return this.intersect(c).size() === this._size;
        },
        allNotIn: function (c) {
            return this.intersect(c).size() === 0;
        },
        forEach: function (fn, thisArg) {
            thisArg = thisArg || this;
            for (var k in this._items) {
                // compatibles with the behavior of continuing traversal without a return value
                if (this._has(k) && fn.call(thisArg, this._load(k), thisArg) === false) {
                    return false;
                }
            }
            return true;
        },
        filter: function (fn, thisArg) {
            var ret = new IdSet();
            this.forEach(function (e) {
                fn.call(this, e, this) && ret.add(e);
            }, thisArg || this);
            return ret;
        },
        map: function (fn, thisArg) {
            var ret = new IdSet();
            this.forEach(function (e) {
                ret.add(fn.call(this, e, this));
            }, thisArg || this);
            return ret;
        },
        reduce: function (fn, initialValue) {
            return this.toArray().reduce(fn, initialValue);
        },
        every: function (fn, thisArg) {
            return this.forEach(function (e) {
                return !!fn.call(this, e, this);
            }, thisArg || this);
        },
        some: function (fn, thisArg) {
            return !this.forEach(function (e) {
                return !fn.call(this, e, this);
            }, thisArg || this);
        },
        intersect: function (c) {
            var ret = new IdSet();
            IdSet.from(c).forEach(function (e) {
                if (this.contains(e)) {
                    ret.add(e);
                }
            }, this);
            return ret;
        },
        unions: function (c) {
            var ret = IdSet.from(c);
            this.forEach(function (e) {
                ret.add(e);
            });
            return ret;
        },
        minus: function (c) {
            var ret = new IdSet();
            this.forEach(function (e) {
                if (!this.contains(e)) {
                    ret.add(e);
                }
            }, IdSet.from(c));
            return ret;
        },
        toArray: function () {
            var ret = [];
            this.forEach(function (e) {
                ret.push(e);
            });
            return ret;
        },
        clone: function () {
            var ret = new IdSet();
            this.forEach(function (e) {
                ret.add(e);
            });
            return ret;
        },
        equals: function (o) {
            if (!(o instanceof IdSet && this._size === o.size())) {
                return false;
            }
            return this.every(function (e) {
                return o.contains(e);
            });
        },
        toString: function () {
            return JSON.stringify(this.toArray());
        },
        
        // overridable low-level R/W interfaces
        // keyOf-> accept -> has -> store / drop / load
        _keyOf: function (e) {
            switch (typeof e) {
                case "string": return "S".concat(e);
                case "number": return "N".concat(String(e));
                default: return null;
            }
        },
        _accept: function (k) {
            return !!k;
        },
        _has: function (k) {
            return this._items[k] !== void 0;
        },
        _store: function (k, e) {
            this._items[k] = {value: e};
        },
        _load: function (k) {
            return this._items[k].value;
        },
        _drop: function (k) {
            this._items[k] = void 0;
        }
    };

    return IdSet;
})();
