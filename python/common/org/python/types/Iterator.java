package org.python.types;

class Iterator extends org.python.types.Object implements org.python.Iterable {
    java.util.Iterator<org.python.Object> iterator;

    public Iterator(org.python.types.List list) {
        this.iterator = list.value.iterator();
    }

    public Iterator(org.python.types.Tuple tuple) {
        this.iterator = tuple.value.iterator();
    }

    @org.python.Method(
        __doc__ = ""
    )
    public org.python.Iterable __iter__(org.python.Object [] args, java.util.Map<java.lang.String, org.python.Object> kwargs) {
        if (kwargs.size() != 0) {
            throw new org.python.exceptions.TypeError("__iter__ doesn't take keyword arguments");
        }
        if (args.length != 0) {
            throw new org.python.exceptions.TypeError("Expected 0 arguments, got " + args.length);
        }
        return this.__iter__();
    }

    public org.python.Iterable __iter__() {
        return this;
    }

    @org.python.Method(
        __doc__ = ""
    )
    public org.python.Object __next__(org.python.Object [] args, java.util.Map<java.lang.String, org.python.Object> kwargs) {
        if (kwargs.size() != 0) {
            throw new org.python.exceptions.TypeError("__next__ doesn't take keyword arguments");
        }
        if (args.length != 0) {
            throw new org.python.exceptions.TypeError("Expected 0 arguments, got " + args.length);
        }
        return this.__next__();
    }

    public org.python.Object __next__() {
        try {
            return this.iterator.next();
        } catch (java.util.NoSuchElementException e) {
            throw new org.python.exceptions.StopIteration();
        }
    }
}
