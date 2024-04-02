(* From class video on pa5t *)

(* Test case to show off aliasing -- aliasing is when two names refer to the 
    same object in memory. *)

class IntWrapper {
    myInt: Int <- 0;

    set(newInt: Int): Int { myInt <- newInt };
    get() : Int { myInt } ;
    incr() : SELF_TYPE {{ myInt <- myInt + 1; self;}};
};

class IntWrapperChild inherits IntWrapper {

};

(*  ways to make new names for the same object:
    (1) formal parameters + dispatch
    (2) let
*)
class Main inherits IO {
    a : IntWrapper <- new IntWrapper;
    b : IntWrapper <- new IntWrapper;
    c : IntWrapper <- new IntWrapper;

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

    main() : Object {
        {
            a.set(11);
            b.set(33);
            c.set(55);
            process(a, b);
            process(c, c);

            let p : IntWrapper <- b in
            let q : IntWrapper <- b in
            let r : IntWrapper <- c in
            {
                out_int(p.get());
                out_string(" ");
                out_int(q.get());
                out_string(" ");
                out_int(r.get());
                p.incr();
                out_string(" ");
                out_int(p.get( ));
                out_string(" ");
                out_int(q.get());
                out_string(" ");
                out_int(r.get());
                out_string("\n");
            };
        }
    };
};