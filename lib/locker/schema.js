/* ============================================================================
   GOLFRAW LOCKER — SCHEMA
   ----------------------------------------------------------------------------
   A tiny structural validator in the shape of Zod's safeParse. This site has no
   bundler and no npm runtime (every page is hand-written static HTML), so a
   real Zod dependency cannot be installed without introducing a build step for
   283 pages. The contract we actually need is small and fully covered here:

     - parse never throws; it returns { ok, value, errors[] }
     - unknown keys are dropped, so a tampered or future export cannot smuggle
       fields into IndexedDB
     - no coercion: a string where a number belongs is an error, not a silent 0
     - every error carries a JSON path, so import failures are explainable

   Exposed as window.GolfrawSchema. ES5 syntax to match the rest of the site.
   ========================================================================== */
(function (root) {
  'use strict';

  function ok(value) { return { ok: true, value: value, errors: [] }; }
  function fail(path, message) { return { ok: false, value: null, errors: [{ path: path, message: message }] }; }
  function failAll(errors) { return { ok: false, value: null, errors: errors }; }

  /* Deep clone for defaults, so two records can never share a mutable literal. */
  function clone(v) {
    if (v === null || typeof v !== 'object') return v;
    if (Object.prototype.toString.call(v) === '[object Array]') {
      var a = [];
      for (var i = 0; i < v.length; i++) a.push(clone(v[i]));
      return a;
    }
    var o = {};
    for (var k in v) if (Object.prototype.hasOwnProperty.call(v, k)) o[k] = clone(v[k]);
    return o;
  }

  function isArray(v) { return Object.prototype.toString.call(v) === '[object Array]'; }
  function isPlainObject(v) { return v !== null && typeof v === 'object' && !isArray(v); }

  /* Builds a type. `fn(value, path, self)` runs only once the value is known to
     be present and non-null, so individual types never repeat those checks. */
  function make(fn) {
    var self = {
      _optional: false,
      _nullable: false,
      _hasDefault: false,
      _default: undefined
    };

    self.parse = function (v, path) {
      path = path || '$';
      if (v === undefined) {
        if (self._hasDefault) return ok(clone(self._default));
        if (self._optional) return ok(undefined);
        return fail(path, 'is required');
      }
      if (v === null) {
        if (self._nullable) return ok(null);
        return fail(path, 'must not be null');
      }
      return fn(v, path, self);
    };

    self.optional = function () { self._optional = true; return self; };
    self.nullable = function () { self._nullable = true; return self; };
    self.def = function (d) { self._default = d; self._hasDefault = true; self._optional = true; return self; };

    return self;
  }

  /* ---------------------------------------------------------------- string */
  function string(opts) {
    opts = opts || {};
    var t = make(function (v, path) {
      if (typeof v !== 'string') return fail(path, 'must be a string');
      var s = opts.trim === false ? v : v.replace(/^\s+|\s+$/g, '');
      if (opts.max !== undefined && s.length > opts.max) return fail(path, 'must be at most ' + opts.max + ' characters');
      if (opts.min !== undefined && s.length < opts.min) return fail(path, 'must be at least ' + opts.min + ' characters');
      return ok(s);
    });
    return t;
  }

  /* ---------------------------------------------------------------- number */
  function number(opts) {
    opts = opts || {};
    var t = make(function (v, path) {
      if (typeof v !== 'number' || !isFinite(v)) return fail(path, 'must be a finite number');
      if (opts.int && Math.floor(v) !== v) return fail(path, 'must be a whole number');
      if (opts.min !== undefined && v < opts.min) return fail(path, 'must be at least ' + opts.min);
      if (opts.max !== undefined && v > opts.max) return fail(path, 'must be at most ' + opts.max);
      return ok(v);
    });
    return t;
  }

  function integer(opts) {
    opts = opts || {};
    opts.int = true;
    return number(opts);
  }

  /* --------------------------------------------------------------- boolean */
  function boolean() {
    return make(function (v, path) {
      if (typeof v !== 'boolean') return fail(path, 'must be true or false');
      return ok(v);
    });
  }

  /* ------------------------------------------------------------------ enum */
  function oneOf(values) {
    return make(function (v, path) {
      for (var i = 0; i < values.length; i++) if (values[i] === v) return ok(v);
      return fail(path, 'must be one of: ' + values.join(', '));
    });
  }

  /* ----------------------------------------------------------------- array */
  function arrayOf(inner, opts) {
    opts = opts || {};
    return make(function (v, path) {
      if (!isArray(v)) return fail(path, 'must be an array');
      if (opts.max !== undefined && v.length > opts.max) return fail(path, 'must have at most ' + opts.max + ' items');
      if (opts.min !== undefined && v.length < opts.min) return fail(path, 'must have at least ' + opts.min + ' items');
      var out = [], errs = [];
      for (var i = 0; i < v.length; i++) {
        var r = inner.parse(v[i], path + '[' + i + ']');
        if (r.ok) out.push(r.value); else errs = errs.concat(r.errors);
      }
      return errs.length ? failAll(errs) : ok(out);
    });
  }

  /* ---------------------------------------------------------------- object */
  function object(shape) {
    return make(function (v, path) {
      if (!isPlainObject(v)) return fail(path, 'must be an object');
      var out = {}, errs = [];
      for (var k in shape) {
        if (!Object.prototype.hasOwnProperty.call(shape, k)) continue;
        var r = shape[k].parse(v[k], path + '.' + k);
        if (!r.ok) { errs = errs.concat(r.errors); continue; }
        /* An absent optional stays absent rather than becoming an explicit
           undefined — structuredClone (IndexedDB) preserves that distinction. */
        if (r.value !== undefined) out[k] = r.value;
      }
      return errs.length ? failAll(errs) : ok(out);
    });
  }

  /* A free-form JSON blob: per-tool scratch state whose shape belongs to the
     tool, not to this layer. Still guarded — it must be clonable and bounded,
     because anything stored here is written straight into IndexedDB. */
  function jsonBlob(maxBytes) {
    maxBytes = maxBytes || 64 * 1024;
    return make(function (v, path) {
      if (!isPlainObject(v)) return fail(path, 'must be an object');
      var text;
      try { text = JSON.stringify(v); } catch (e) { return fail(path, 'must be JSON-serialisable'); }
      if (text === undefined) return fail(path, 'must be JSON-serialisable');
      if (text.length > maxBytes) return fail(path, 'is too large (limit ' + maxBytes + ' bytes)');
      var copy;
      try { copy = JSON.parse(text); } catch (e) { return fail(path, 'must be JSON-serialisable'); }
      return ok(copy);
    });
  }

  root.GolfrawSchema = {
    string: string,
    number: number,
    integer: integer,
    boolean: boolean,
    oneOf: oneOf,
    arrayOf: arrayOf,
    object: object,
    jsonBlob: jsonBlob,
    clone: clone,
    isArray: isArray,
    isPlainObject: isPlainObject
  };
})(window);
