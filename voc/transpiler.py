import importlib
import marshal
import os
import py_compile

from .python.module import transpile as transpile_module


def transpile(sourcefile, namespace, outdir=None):
    print("Compiling %s..." % sourcefile)
    py_compile.compile(sourcefile)

    transpiler = Transpiler(namespace)
    transpiler.transpile(sourcefile)
    transpiler.write(outdir)


class Transpiler:
    def __init__(self, namespace):
        self.namespace = namespace
        self.classfiles = []

    def write(self, outdir):
        # Create directory tree to store classfile
        if outdir:
            dirparts = [outdir]
        else:
            dirparts = []
        dirparts = dirparts + self.namespace.split('.')
        dirname = os.path.join(*dirparts)

        try:
            os.makedirs(dirname)
        except FileExistsError:
            pass

        for classname, module, classfile in self.classfiles:

            if module:
                classfilename = os.path.join(dirname, module, '%s.class' % classname)
                try:
                    os.mkdir(os.path.join(dirname, module))
                except FileExistsError:
                    pass
            else:
                classfilename = os.path.join(dirname, '%s.class' % classname)

            print("Writing %s..." % classfilename)
            with open(classfilename, 'wb') as out:
                classfile.write(out)
        print("Done.")

    def transpile(self, sourcefile):
        with open(importlib.util.cache_from_source(sourcefile), 'rb') as compiled:
            # Read off the magic from the start of the PYC file.
            compiled.read(12)

            # Decompile the code object.
            code = marshal.load(compiled)

            self.classfiles.extend(transpile_module(self.namespace, sourcefile, code))