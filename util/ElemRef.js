// emulate two-way binding
var ElemRef = (function () {
  function ElemRef() {
    this._value = void 0;
    this._handlers = {};
    this._enabled = true;
    this._writable = true;
  }

  ElemRef.GET_EVENT = 0;
  ElemRef.SET_EVENT = 1;

  ElemRef.prototype = {
    constructor: ElemRef,
    getValue: function () {
      return this._pipe(ElemRef.GET_EVENT, this._value, this._value);
    },
    setValue: function (value) {
      if (this._writable) {
        return this._value = this._pipe(ElemRef.SET_EVENT, {prev: this._value, value: value}, {prev: this._value, value: value}).value;
      }
    },
    addHandler: function (event, handler) {
      var handlers;
      typeof handler === "function" && Array.isArray(handlers = this._getHandlers(event)) && handlers.push(handler);
    },
    removeHandler: function (event, handler) {
      var handlers;
      typeof handler === "function" && Array.isArray(handlers = this._getHandlers(event)) && handlers.splice(handlers.indexOf(handler), 1);
    },
    isEnabled: function () {
      return this._enabled;
    },
    setEnabled: function (value) {
      return this._enabled = !!value;
    },
    isWritable: function () {
      return this._writable;
    },
    setWritable: function (value) {
      return this._writable = !!value;
    },
    _getHandlers: function (event) {
      if (!event && event !== 0) return;
      this._handlers = this._handlers || {};
      return this._handlers[event] = this._handlers[event] || [];
    },
    _pipe: function (event, prev, initial) {
      var ref = this, handlers = this._getHandlers(event), env = {interrupt: false};
      this._enabled && Array.isArray(handlers) && handlers.forEach(function (handle) {
        env.interrupt || (typeof handle === "function" && (prev = handle(prev, initial, ref, env)));
      });
      return prev;
    }
  };

  return ElemRef;
})();