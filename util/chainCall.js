// Optional chaining polyfill and enhancement
var chainCall = (function (fieldCache) {
  var getNullDefault = function (nullDefault, computed) {
    if (computed && typeof nullDefault === "function") {
      return nullDefault();
    }
    return nullDefault;
  };
  return function (obj, path, nullDefault, computed, separator, bound) {
    if (obj == null) {
      return getNullDefault(nullDefault, computed);
    }
    if (path == null) {
      return obj;
    }
    var fields = path;
    if (!Array.isArray(path)) {
      path = String(path);
      separator = separator || ".";
      var key = String(separator.length) + separator + path;
      fields = fieldCache[key];
      if (!fields) {
        fieldCache[key] = fields = path.split(separator);
      }
    }
    var v1, v2, v3 = obj;
    for (var i = 0; i < fields.length; ++i) {
      v1 = v2;
      v2 = v3;
      v3 = fields[i];
      if (Array.isArray(v3)) {
        if (typeof v2 !== "function") {
          return getNullDefault(nullDefault, computed);
        }
        v3 = v2.apply(v1, v3);
      } else {
        v3 = v2[v3];
      }
      if (v3 == null) {
        return getNullDefault(nullDefault, computed);
      }
    }
    if (bound && typeof v3 === "function") {
      return v3.bind(v2);
    }
    return v3;
  };
})({});
