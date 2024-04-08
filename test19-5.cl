
class Main inherits IO{
    x : Main;

    main(): Object {
        if isvoid x then {
            out_int(0);
        } else {
            out_int(1);
        } fi
    };
};