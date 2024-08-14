[Documentation for MCL (My Complicated Language)]

How to use:
    Flags:
        --profile - Output interpreter profile.
        --show-memory - Show max memory used.
        --show-memory-advance - Higher resolution.
        --version - Output version info.
        --serious - (with version flag) shows more info.
        --goof    - (with version flag) Easter egg.
    Commands:
        run [file] args...
            Run scripts.
        analyze [file] args...
            Analyze scripts.
        compile [source] [destination]
            Compile scripts.
        rc [file] args...
            Run compiled scripts.
        ac [file] args...
            Analyze compiled scripts.

Note:
    When analyzing scripts the "$input" argument
    is replaced with a default value.
    This is for convenience.

Comments:
    NOTE:
        Comments cannot be before or after a line of code.
        Examples:
            `code * comment`
            Or
            ::
            code <** Title
                Comment
            **>
            ::
    <** Title
        Stuff
    **>
        The title forces the user to make sure
        to stay to the topic and make sure that
        the topic is well known.
    * line comment
        A line comment.

MCL Instructions:
    Directives ("!" prefix):
        include [file]
            Include a MCL file.
        pyimport [file]
            Import a python file.
        includec [file]
            Import a CMCL file.
        dontOptimize
            Tell the compiler to dont modify the code.
        optimize (default)
            Tell the compiler to optimize the code.
            Items to optimize:
                Loops
                Unused subroutines
                Unused lbels
        printCode
            Print the resulting code (after compilation)
        noPrintCode (default)
            Do not out put the code to the console.
        hideWarnings
            Hide compiler warnings.
        showWarnings (default)
            Show conpiler warnings.
        clearDocs
            Clears docs dict.
        warning [message]
            Raises the warning.
        IUseArchBTW {easter egg}
            Changes System Build Name to linux (script only)
    Instructions:
        == Program Info  ==
        program name
            Used for debugging.
            It is customary to use "program <main>" in the main script.
        == Control Flow  ==
        label name
            Define a label.
        goto name
            Goto a label.
        subroutine name
            Define a subroutine.
        return value
            Return the value and go to the caller.
        give value
            Return the value without exiting subroutine.
            Useful for cleaning up.
        ends
            End a subroutine.
        call name.
            Define a name to catch the return value.
            Call the given subroutine.
        set1 value
            Set the first operand.
        set2 value
            Set the second operand.
        ifeq subroutine
            If set1 and set2 are equal it calls the subroutine.
        ifne subroutine
            If not equal.
        iflt subroutine
            If less than.
        ifgt subroutine
            If greater than.
        ==   Text I/O   ==
        ARGUMENT: $input
            Ask for an input
            `println $input`
        print value
            Print value.
        println value
            Print the value with a newline.
        ==    Variable   ==
        define name
            Define the name.
        set value
            Aet the current name.
        SEMANTIC: .object-in-an-object
            Python equivalent "object.in_.an.object"
            The rules bellow apply.
        ARGUMENT: .name
            Acess the value of name.
        ARGUMENT: !name
            Access the value of name (global)
        ARGUMENT: :name
            Access the value of name.
            Local first then global.
        ARGUMENT: @name
            Access the value of the value of name.
            ::
            define test
            set number[90]
            define ok
            set test
            * Outputs 90
            println @ok
            ::
        ARGUMENT: ?name
            Returns 1 if name exists (local or global) else 0.
        ARGUMENT: &name[index]
            Index name.
        ==    Looping    ==
        loop iterations
            Iterate, inclusive.
            loop 2 would be 0, 1, 2
        xloop iterations
            Iterate, exclusive.
            xloop 2 would be 0, 1
        endl
            Mark the end of the loop.
        ==  Mathematics  ==
        add value
            ::
            * set test
            define test
            set number[90]
            * define what var to add to
            define test
            add number[90]
            * output it
            println .test
            ::
            Output: 180
        sub value
            Subtract value.
        mul value
            Multiply value.
        div value
            Divide value.
        mod value
            Modulo value.
        ==    Strings    ==
        newstring
            Clear line buffer.
        > string
            Add to the line buffer.
        string name
            Save the string.
        == Builtin Tools ==
        %START
            Set the starting time.
        %END
            Set the ending time.
        %OUTTIME
            Print the time.
        %GETTIME name
            Set name to the estimated time.
        %GETUNIXTIME name
            Set name to the current unix time stamp.
        == Scope N Stuff ==
        [ (also .newscope)
            New scope.
        ] (also .endscope)
            Close current scope.

MCL Constants:
    NOTE:
        Other than `$input` these are actual constants.
    dict[]
        Returns an empty dictionary.
    $true
        Returns 1.
    $false
        Returns 0.
    $nil
        Returns 0.
    $noarg
        Basically an explicit way of telling that there is no given argument.
    $system-name
        Returns os.name
    $system-build-name
        Return platform.uname().system
    $system-architechture
        Return the cpu architechture.
    $interpreter-version
        Return the interpreter version.

MCL Literals:
    "string"
        The string `string`
    number[number]
        Returns the int of number or float of `number`
    identifier
        Valid identifiers (also strings)

[About MCL]

  MCL is a fun nd hobby programming language.
It is not ment to be for production but cam be used if you want to.
A HTML request ("requests" like) library will be soon be out.

  Complex things come from even the simplest things.
From molecules to complex life. From silicon to computer processors.
One wise man once said "We tricked sand into thinking".

  MCL is more like challenging the norms, MCL is for making simplistic
programs. Its like brainf*ck but instead of f*cking up your brain. It helps
you organize your thoughts, the limits of the syntax helps you
use your creativity, not help you kill yourself.


[From the founder "Darren Chase Papa" himself.]

  You are great not because your good. But because
of the little things that made you good. Dont say that
you "made" a mistake. You just came to the wring conclusion 
since you didnt have enough experience. Dont look back on
your mistakes to blame your self but to use it to find the
better path for yourself in the future.


Contributers [0.1-a]:
    Darren Chase Papa
    ChatGPT
