-- out of range string substr

class Main inherits IO{
    toCut: String <- "hello";
    main() : Object {
        out_string(toCut.substr(992334534534534534534,99))
    };

};