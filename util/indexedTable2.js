var IndexedTable = (function () {
  "use strict";
  var util = {
    Optional: function (value) {
      var op = {
        map: function (f) {
          if (value != null && f != null) {
            if (typeof f === "function") {
              value = f(value);
            } else {
              value = value[f];
            }
          }
          return op;
        },
        filter: function (fn) {
          if (value != null && !fn(value)) {
            value = null;
          }
          return op;
        },
        flat: function () {
          if (value != null && typeof value.val === "function") {
            value = value.val();
          }
          return op;
        },
        peek: function (fn) {
          if (value != null) {
            fn(value);
          }
          return op;
        },
        val: function (defaultValue) {
          if (value != null) {
            return value;
          }
          return defaultValue;
        }
      };
      return op;
    }
  };

  function IndexedTable(config) {
    this._id = 0;

    this._nodes = {};
    this._size = 0;
    this._head = {};
    this._tail = {prev: this._head};
    this._head.next = this._tail;
    this._cachedArray = null;

    this._indexes = {};

    this._config = config || {
      indexes: {}
    };
  }
  IndexedTable.prototype = {
    constructor: IndexedTable,
    deepCopy: function (obj) {
      return structuredClone(obj);
    },
    unmodifiableNode: function (node) {
      var that = this;
      if (!node) {
        return;
      }
      return {
        id: node.id,
        get value() {
          if (this._cachedValue) {
            return this._cachedValue;
          }
          return this._cachedValue = that.deepCopy(node.value);
        },
        get prev() {
          return that.unmodifiableNode(node.prev);
        },
        get next() {
          return that.unmodifiableNode(node.next);
        },
      };
    },

    append: function (prevNode, value) {
      if (!prevNode || !value || !prevNode.next) {
        return;
      }
      var nodeId = this.internal_nextId();
      var node = {
        id: nodeId,
        value: this.deepCopy(value),
        prev: prevNode,
        next: prevNode.next
      };
      prevNode.next.prev = node;
      prevNode.next = node;
      this._nodes[nodeId] = node;
      this.internal_setIndexes(node);
      ++this._size;
      this._cachedArray = null;
      return node;
    },
    insert: function (nextNode, value) {
      if (!nextNode || !value || !nextNode.prev) {
        return;
      }
      var nodeId = this.internal_nextId();
      var node = {
        id: nodeId,
        value: this.deepCopy(value),
        prev: nextNode.prev,
        next: nextNode
      };
      nextNode.prev.next = node;
      nextNode.prev = node;
      this._nodes[nodeId] = node;
      this.internal_setIndexes(node);
      ++this._size;
      this._cachedArray = null;
      return node;
    },
    remove: function (node) {
      if (!node || !this._nodes[node.id]) {
        return;
      }
      node.prev.next = node.next;
      node.next.prev = node.prev;
      this.internal_clearIndexes(node);
      delete this._nodes[node.id];
      --this._size;
      this._cachedArray = null;
    },
    update: function (node, value) {
      if (!node || !value || !this._nodes[node.id]) {
        return;
      }
      this.internal_clearIndexes(node);
      node.value = this.deepCopy(value);
      this.internal_setIndexes(node);
      this._cachedArray = null;
    },
    swap: function (node1, node2) {
      if (!node1 || !node2 || !this._nodes[node1.id] || !this._nodes[node2.id]) {
        return;
      }
      this.internal_clearIndexes(node1);
      this.internal_clearIndexes(node2);
      var t = node1.value;
      node1.value = node2.value;
      node2.value = t;
      this.internal_setIndexes(node1);
      this.internal_setIndexes(node2);
      this._cachedArray = null;
    },
    getIndexedNode: function (indexName, value) {
      if (!indexName || !value) {
        return;
      }
      var index = this.internal_getIndex(indexName, value);
      for (var nodeId in index) {
        return index[nodeId];
      }
    },
    listIndexedNodes: function (indexName, value) {
      if (!indexName || !value) {
        return [];
      }
      var index = this.internal_getIndex(indexName, value);
      return Object.keys(index).map(function (nodeId) {
        return index[nodeId];
      });
    },
    getNode: function (nodeId) {
      return this._nodes[nodeId];
    },
    headNode: function () {
      return this._head;
    },
    tailNode: function () {
      return this._tail;
    },
    clear: function () {
      this.constructor(this._config);
    },
    size: function () {
      return this._size;
    },
    isEmpty: function () {
      return this._size === 0;
    },
    forEach: function (fn, thisArg) {
      thisArg = thisArg || this;
      for (var curr = this._head.next; curr !== this._tail; curr = curr.next) {
        if (fn.call(thisArg, curr, this) === false) {
          return;
        }
      }
    },
    toArray: function () {
      if (this._cachedArray) {
        return this._cachedArray;
      }
      var ret = [];
      this.forEach(function (node) {
        ret.push(node);
      });
      return this._cachedArray = ret;
    },
    internal_nextId: function () {
      return this._id++;
    },

    addIndex: function (indexName, columns) {
      if (!indexName || !Array.isArray(columns) || !columns.length || this._config.indexes[indexName]) {
        return this;
      }
      this._config.indexes[indexName] = columns;
      this.forEach(function (node) {
        this.internal_setIndex(indexName, node);
      }, this);
      return this;
    },
    removeIndex: function (indexName) {
      if (!indexName) {
        return this;
      }
      delete this._config.indexes[indexName];
      delete this._indexes[indexName];
      return this;
    },
    internal_getIndex: function (indexName, value) {
      var columns = this._config.indexes[indexName];
      if (!columns) {
        return {};
      }
      var key = columns.map(function (column) {
        return JSON.stringify(value[column]);
      }).join("\0");
      var c = this._indexes;
      c = c[indexName] = c[indexName] || {};
      return c = c[key] = c[key] || {};
    },
    internal_setIndex: function (indexName, node) {
      this.internal_getIndex(indexName, node.value)[node.id] = node;
    },
    internal_clearIndex: function (indexName, node) {
      delete this.internal_getIndex(indexName, node.value)[node.id];
    },
    internal_setIndexes: function (node) {
      Object.keys(this._config.indexes).forEach(function (indexName) {
        this.internal_setIndex(indexName, node);
      }, this);
    },
    internal_clearIndexes: function (node) {
      Object.keys(this._config.indexes).forEach(function (indexName) {
        this.internal_clearIndex(indexName, node);
      }, this);
    }
  };
  return IndexedTable;
})();
