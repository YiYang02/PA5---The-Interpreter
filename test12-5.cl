-- infinite recursion while trying to print name
class Main inherits IO{

  name: String <- "test";

  fakeMethod(s: String) : Int {5};

    main() : Object {
        if name.length() = 1 then
            out_string(name)
        else
            -- never strips the last character of x
            {
                let name : Int <- fakeMethod(name <- "50") in
                out_string("hi");
                out_string(name);
            }
        fi
    };

};