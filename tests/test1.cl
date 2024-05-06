(*
This test case will test all the internal methods of Cool. i.e. out_string()
Along with Test case to show off aliasing -- aliasing is when two names refer to the 
    same object in memory. From the PA5 class video.
*)

class IntWrapper {
    myInt: Int <- 0;

    set(newInt: Int): Int { myInt <- newInt };
    get() : Int { myInt } ;
    incr() : SELF_TYPE {{ myInt <- myInt + 1; self;}};
};

class IntWrapperChild inherits IntWrapper {

};

class Main inherits IO {
    str: String <- "Hello, World!";
    num: Int <- 42;
    bool: Bool <- true;

    a : IntWrapper <- new IntWrapper;
    b : IntWrapper <- new IntWrapper;
    c : IntWrapper <- new IntWrapper;

    p : IntWrapper <- b;
    q : IntWrapper <- b;
    r : IntWrapper <- c;

    process(x: IntWrapper, y: IntWrapper) : Object {
        {
            out_int(x.get());
            out_string(" ");
            out_int(y.get());
            x.incr();
            out_string(" ");
            out_int(x.get( ));
            out_string(" ");
            out_int(y.get());
            out_string("\n");
        }
    };
    
    main(): Object {
        {

            (* Use methods from Object class *)
            -- self.copy();
            out_string(self.type_name());

            (* Use methods from IO class *)
            out_string(str);
            out_int(num);
            -- in_string();
            -- in_int();

            (* Use methods from String class *)
            out_int(str.length());
            -- out_string(str.concat(" Concatenated."));
            out_string(str.substr(0, 5));

            a.set(11);
            b.set(33);
            c.set(55);
            process(a, b);
            process(c, c);

            self.abort();
        }
    };
};