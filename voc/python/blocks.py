import dis

from ..java import (
    Code as JavaCode,
    opcodes as JavaOpcodes,
    ExceptionInfo as JavaExceptionInfo,
    LineNumberTable
)

from .utils import extract_command, find_blocks
from .opcodes import resolve_jump


class IgnoreBlock(Exception):
    """An escape hatch; enable a block to be flagged as ignorable"""
    pass


class Block:
    def __init__(self, parent=None, commands=None):
        self.parent = parent
        self.commands = commands if commands else []
        self.local_vars = {}
        self.deleted_vars = set()

        self.code = []
        self.try_catches = []
        self.blocks = []
        self.jumps = []
        self.loops = []
        self.jump_targets = {}
        self.unknown_jump_targets = {}

        self.next_resolve_list = []
        self.next_opcode_starts_line = None

    @property
    def module(self):
        return self.parent

    def store_name(self, name, use_locals):
        raise NotImplementedError('Abstract class `block` cannot be used directly.')

    def load_name(self, name, use_locals):
        raise NotImplementedError('Abstract class `block` cannot be used directly.')

    def delete_name(self, name, use_locals):
        raise NotImplementedError('Abstract class `block` cannot be used directly.')

    def extract(self, code, debug=False):
        """Break a code object into the parts it defines, populating the
        provided block.

        """
        instructions = list(dis.Bytecode(code))

        blocks = find_blocks(instructions)

        i = len(instructions)
        commands = []
        while i > 0:
            i, command = extract_command(instructions, blocks, i)
            commands.append(command)

        commands.reverse()

        if True:
            print ('=====' * 10)
            print (code)
            print ('-----' * 10)
            for command in commands:
                command.dump()
            print ('=====' * 10)

        # Append the extracted commands to any pre-existing ones.
        self.commands.extend(commands)

    def transpile_setup(self):
        """Tweak the bytecode generated for this block."""
        pass

    def transpile_teardown(self):
        """Tweak the bytecode generated for this block."""
        pass

    @property
    def can_ignore_empty(self):
        return False

    @property
    def has_void_return(self):
        return False

    def add_opcodes(self, *opcodes):
        # Add the opcodes to the code list and process them.
        for opcode in opcodes:
            # print("ADD OPCODE", id(opcode), opcode)
            if opcode.process(self):
                self.code.append(opcode)

                # If we've flagged a code line change, attach that to the opcode
                if self.next_opcode_starts_line:
                    opcode.starts_line = self.next_opcode_starts_line
                    self.next_opcode_starts_line = None

                # Resolve any references to the "next" opcode.
                for (obj, attr) in self.next_resolve_list:
                    # print("        resolve %s reference on %s %s with %s %s" % (attr, obj, id(obj), opcode, id(opcode)))
                    setattr(obj, attr, opcode)

                self.next_resolve_list = []

    def stack_depth(self):
        "Evaluate the maximum stack depth required by a sequence of Java opcodes"
        depth = 0
        max_depth = 0

        for opcode in self.code:
            depth = depth + opcode.stack_effect
            # print("   ", opcode, depth)
            if depth > max_depth:
                max_depth = depth
        return max_depth

    def void_return(self):
        """Ensure that end of the code sequence is a Java-style return of void.

        Java has a separate opcode for VOID returns, which is different to
        RETURN NULL. Replace all "SET NULL" "ARETURN" pairs with "RETURN".
        """

        if len(self.code) >= 2:
            new_code = []
            i = 0
            while i < len(self.code):
                if (isinstance(self.code[i], JavaOpcodes.GETSTATIC)
                        and self.code[i].field.class_name == 'org/python/types/NoneType'):

                    if isinstance(self.code[i + 1], JavaOpcodes.ARETURN):
                        return_opcode = JavaOpcodes.RETURN()

                        # Update the jump operation to point at the new return opcode.
                        for opcode in self.code[-1].references:
                            opcode.jump_op = return_opcode
                            return_opcode.references.append(opcode)

                        for opcode in self.code[-2].references:
                            opcode.jump_op = return_opcode
                            return_opcode.references.append(opcode)

                        # Then, check to see if either opcode had a line number association.
                        # if so, preserve the first one.
                        if self.code[-2].starts_line is not None:
                            return_opcode.starts_line = self.code[-2].starts_line
                        elif self.code[-1].starts_line is not None:
                            return_opcode.starts_line = self.code[-1].starts_line

                        new_code.append(return_opcode)
                        i += 1
                    else:
                        new_code.append(self.code[i])
                else:
                    new_code.append(self.code[i])
                i += 1

            self.code = new_code

    def add_return(self):
        self.add_opcodes(JavaOpcodes.RETURN())

    def transpile(self):
        """Create a JavaCode object representing the commands stored in the block

        May raise ``IgnoreBlock`` if the block should be ignored.
        """
        #
        argument_vars = len(self.local_vars)

        # Most opcodes need no preparation, but MAKE_FUNCTION,
        # CALL_FUNCTION/LOAD_BUILD_CLASS, and MAKE_CLOSURE all create
        # blocks of code that might be referenced elsewhere, so they
        # need to be handled first, and materialized into actual class
        # definitions.
        for cmd in self.commands:
            cmd.materialize(self)

        # Insert content that needs to occur before the main block commands
        self.transpile_setup()

        # Convert the sequence of commands into instructions.
        # Most of the instructions will be opcodes. However, some will
        # be instructions to add exception blocks, line number references, etc
        for cmd in self.commands:
            cmd.transpile(self)

        # Insert content that needs to occur after the main block commands
        self.transpile_teardown()

        # Java requires that every body of code finishes with a return.
        # Make sure there is one.
        if len(self.code) == 0 or not isinstance(self.code[-1], (JavaOpcodes.RETURN, JavaOpcodes.ARETURN)):
            self.add_return()

        # Make sure every local variable slot has been initialized
        # as an object. This is needed because Python allows a variable
        # to be instantiated in a sub-block, and used outside that block.
        # The JVM doesn't, and raises a verify error if you try. By
        # initializing all variables, we can trick the verifier.
        # TODO: Ideally, we'd only initialize the variables that are ambiguous.
        init_vars = []
        for i in range(argument_vars, len(self.local_vars) + len(self.deleted_vars)):
            if i == 0:
                opcode = JavaOpcodes.ASTORE_0()
            elif i == 1:
                opcode = JavaOpcodes.ASTORE_1()
            elif i == 2:
                opcode = JavaOpcodes.ASTORE_2()
            elif i == 3:
                opcode = JavaOpcodes.ASTORE_3()
            else:
                opcode = JavaOpcodes.ASTORE(i)
            init_vars.extend([
                JavaOpcodes.ACONST_NULL(),
                opcode
            ])

        self.code = init_vars + self.code

        # Since we've processed all the Python opcodes, we can now resolve
        # all the unknown jump targets.
        # print('>>>>> Resolve references')
        for target, references in self.unknown_jump_targets.items():
            # print("   resolving %s references to %s" % (len(references), target))
            for opcode, position in references:
                resolve_jump(opcode, self, target, position)

        # If the block has no content in it, and the block allows,
        # ignore this block.
        if self.can_ignore_empty:
            if len(self.code) == 1 and isinstance(self.code[0], JavaOpcodes.RETURN):
                raise IgnoreBlock()
            elif len(self.code) == 2 and isinstance(self.code[1], JavaOpcodes.ARETURN):
                raise IgnoreBlock()

        # If the block has a void return, make sure that is honored.
        if self.has_void_return:
            self.void_return()

        # Now that we have a complete opcode list, postprocess the list
        # with the known offsets.
        offset = 0
        # print('>>>>> set offsets', self)
        for index, instruction in enumerate(self.code):
            # print("%4d:%4d (0x%x) %s" % (index, offset, id(instruction), instruction))
            instruction.java_index = index
            instruction.java_offset = offset
            offset += len(instruction)
        # print('>>>>> end set offsets')

        # Construct the exception table, updating any
        # end-of-exception GOTO operations with the right opcode.
        # Record a frame range for each one.
        exceptions = []
        for try_catch in self.try_catches:
            # print("TRY CATCH START", id(try_catch), try_catch.start_op, try_catch.start_op.java_offset)
            # print("        TRY END", try_catch.try_end_op, try_catch.try_end_op.java_offset)
            # print("            END", try_catch.end_op, try_catch.end_op.java_offset)
            for handler in try_catch.handlers:
                # print("  HANDLER", handler.start_op, handler.end_op, handler.descriptors)
                if handler.descriptors:
                    for descriptor in handler.descriptors:
                        exceptions.append(JavaExceptionInfo(
                            try_catch.start_op.java_offset,
                            try_catch.try_end_op.java_offset,
                            handler.start_op.java_offset,
                            descriptor
                        ))
                else:
                    exceptions.append(JavaExceptionInfo(
                        try_catch.start_op.java_offset,
                        try_catch.try_end_op.java_offset,
                        handler.start_op.java_offset,
                        'org/python/exceptions/BaseException'
                    ))

            # Add definitions for the finally block
            if try_catch.finally_handler:
                # print("  FINALLY", try_catch.finally_handler.start_op.java_offset, try_catch.finally_handler.end_op.java_offset)
                exceptions.append(JavaExceptionInfo(
                    try_catch.start_op.java_offset,
                    try_catch.try_end_op.java_offset,
                    try_catch.finally_handler.start_op.java_offset,
                    None
                ))
                for handler in try_catch.handlers:
                    # print("   h", handler.descriptors)
                    exceptions.append(JavaExceptionInfo(
                        handler.start_op.java_offset,
                        handler.catch_end_op.java_offset,
                        try_catch.finally_handler.start_op.java_offset,
                        None
                    ))

        # Update any jump instructions
        # print ("There are %s jumps" % len(self.jumps))
        for jump in self.jumps:
            # print ("JUMP", hex(id(jump)), jump, jump.java_offset, jump.jump_op, hex(id(jump.jump_op)))

            try:
                jump.offset = jump.jump_op.java_offset - jump.java_offset
            except AttributeError:
                jump.offset = jump.jump_op.start_op.java_offset - jump.java_offset

        # Construct a line number table from
        # the source code reference data on opcodes.
        line_numbers = []
        for code in self.code:
            if code.starts_line is not None:
                line_numbers.append((code.java_offset, code.starts_line))
        line_number_table = LineNumberTable(line_numbers)

        return JavaCode(
            max_stack=self.stack_depth() + len(exceptions),
            max_locals=len(self.local_vars) + len(self.deleted_vars),
            code=self.code,
            exceptions=exceptions,
            attributes=[
                line_number_table
            ]
        )
