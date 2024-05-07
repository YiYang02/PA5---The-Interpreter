 -- this does while loop, and if condition
class Main inherits IO {
    counter : Int <- 0;
    item : Object;

    fakeMethod(s: String) : Int {5};
    
    main() : Object {{
        while counter < 10 loop {
            counter <- counter + 2;
        } pool;
        item <- counter;
        if 10 < counter
            then out_string("Counter exceeded 10\n")
        else
            out_string("Counter did not exceed 10\n")
        fi;

        if isvoid(item)
            then out_string("Item is void\n")
        else
            out_string("Item is not void\n")
        fi;

        out_int(fakeMethod("hello"));
    }};
};