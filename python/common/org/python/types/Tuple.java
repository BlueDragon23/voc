package org.python.types;

public class Tuple extends org.python.types.Object {
    public java.util.ArrayList<org.python.Object> value;

    /**
     * A utility method to update the internal value of this object.
     *
     * Used by __i*__ operations to do an in-place operation.
     * obj must be of type org.python.types.Tuple
     */
    void setValue(org.python.Object obj) {
        this.value = ((org.python.types.Tuple) obj).value;
    }

    public Tuple() {
        super();
        this.value = new java.util.ArrayList<org.python.Object>();
    }

    public Tuple(java.util.ArrayList<org.python.Object> tuple) {
        super();
        this.value = tuple;
    }

    // public org.python.Object __new__() {
    //     throw new org.python.exceptions.NotImplementedError("tuple.__new__() has not been implemented.");
    // }

    // public org.python.Object __init__() {
    //     throw new org.python.exceptions.NotImplementedError("tuple.__init__() has not been implemented.");
    // }

    public org.python.types.Str __repr__() {
        java.lang.StringBuilder buffer = new java.lang.StringBuilder("(");
        boolean first = true;
        for (org.python.Object obj: this.value) {
            if (first) {
                first = false;
            } else {
                buffer.append(", ");
            }
            buffer.append(obj.__repr__());
        }
        buffer.append(")");
        return new org.python.types.Str(buffer.toString());
    }

    public org.python.types.Str __format__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__format__() has not been implemented.");
    }

    public org.python.Object __lt__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__lt__() has not been implemented.");
    }

    public org.python.Object __le__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__le__() has not been implemented.");
    }

    public org.python.Object __eq__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__eq__() has not been implemented.");
    }

    public org.python.Object __ne__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__ne__() has not been implemented.");
    }

    public org.python.Object __gt__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__gt__() has not been implemented.");
    }

    public org.python.Object __ge__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__ge__() has not been implemented.");
    }

    public org.python.Object __getattribute__(java.lang.String name) {
        throw new org.python.exceptions.NotImplementedError("tuple.__getattribute__() has not been implemented.");
    }

    public void __setattr__(java.lang.String name, org.python.Object value) {
        throw new org.python.exceptions.NotImplementedError("tuple.__setattr__() has not been implemented.");
    }

    public void __delattr__(java.lang.String name) {
        throw new org.python.exceptions.NotImplementedError("tuple.__delattr__() has not been implemented.");
    }

    public org.python.types.List __dir__() {
        throw new org.python.exceptions.NotImplementedError("tuple.__dir__() has not been implemented.");
    }

    public org.python.types.Int __len__() {
        throw new org.python.exceptions.NotImplementedError("tuple.__len__() has not been implemented.");
    }

    public org.python.Object __getitem__(org.python.Object index) {
        try {
            if (index instanceof org.python.types.Slice) {
                org.python.types.Slice slice = (org.python.types.Slice) index;
                java.util.ArrayList<org.python.Object> sliced = new java.util.ArrayList<org.python.Object>();

                if (slice.start == null && slice.stop == null && slice.step == null) {
                    sliced.addAll(this.value);
                }
                else {
                    long start;
                    if (slice.start != null) {
                        start = slice.start.value;
                    } else {
                        start = 0;
                    }

                    long stop;
                    if (slice.stop != null) {
                        stop = slice.stop.value;
                    } else {
                        stop = this.value.size();
                    }

                    long step;
                    if (slice.step != null) {
                        step = slice.step.value;
                    } else {
                        step = 1;
                    }

                    for (long i = start; i < stop; i += step) {
                        sliced.add(this.value.get((int)i));
                    }
                }
                return new org.python.types.Tuple(sliced);

            } else {
                int idx = (int)((org.python.types.Int) index).value;
                if (idx < 0) {
                    if (-idx > this.value.size()) {
                        throw new org.python.exceptions.IndexError("tuple index out of range");
                    } else {
                        return this.value.get(this.value.size() + idx);
                    }
                } else {
                    if (idx >= this.value.size()) {
                        throw new org.python.exceptions.IndexError("tuple index out of range");
                    } else {
                        return this.value.get(idx);
                    }
                }
            }
        } catch (ClassCastException e) {
            throw new org.python.exceptions.TypeError("tuple indices must be integers, not " + org.Python.pythonTypeName(index));
        }
    }

    public void __setitem__(org.python.Object index, org.python.Object value) {
        try {
            int idx = (int) ((org.python.types.Int) index).value;
            if (idx < 0) {
                if (-idx > this.value.size()) {
                    throw new org.python.exceptions.IndexError("tuple index out of range");
                } else {
                    this.value.set(this.value.size() + idx, value);
                }
            } else {
                if (idx >= this.value.size()) {
                    throw new org.python.exceptions.IndexError("tuple index out of range");
                } else {
                    this.value.set(idx, value);
                }
            }
        } catch (ClassCastException e) {
            throw new org.python.exceptions.TypeError("tuple indices must be integers, not " + org.Python.pythonTypeName(index));
        }
    }

    public void __delitem__(org.python.Object index) {
        throw new org.python.exceptions.TypeError("'tuple' object doesn't support item deletion");
    }


    public org.python.Iterable __iter__() {
        throw new org.python.exceptions.NotImplementedError("tuple.__iter__() has not been implemented.");
    }

    public org.python.types.Bool __contains__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__contains__() has not been implemented.");
    }

    public org.python.Object __add__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__add__() has not been implemented.");
    }

    public org.python.Object __mul__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__mul__() has not been implemented.");
    }

    public org.python.Object __rmul__(org.python.Object other) {
        throw new org.python.exceptions.NotImplementedError("tuple.__rmul__() has not been implemented.");
    }

}