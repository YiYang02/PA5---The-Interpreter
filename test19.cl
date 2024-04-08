class Main inherits IO {
    y : Object <- 5;

    main(): Object {

        if isvoid y then {
            out_int(0);
        } else {
            out_int(1);
        } fi
    };
};