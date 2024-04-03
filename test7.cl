-- infinite recursion while trying to print name
class Main inherits IO{

    print_first_let_of_name(x: String) : Object {
        if x.length() = 1 then
            out_string(x)
        else
            print_first_let_of_name(x) 
            -- never strips the last character of x
        fi
    };

    main() : Object {
        print_first_let_of_name("ppl")
    };

};