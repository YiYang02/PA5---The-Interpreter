class Main inherits IO {
    x : Main;
    main(): Object {{
        out_string((isvoid true).type_name());
        out_string((isvoid false).type_name());
        out_string((isvoid true = true).type_name());
        out_string((isvoid false = false).type_name());
        out_string((isvoid true = false).type_name());
        out_string((isvoid true < false).type_name());
        out_string((isvoid self).type_name());
        out_string((x <- new Main).type_name());
    }};
};