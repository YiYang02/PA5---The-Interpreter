-- out of range string substr

class Main inherits IO{
    toCut: String <- "hello";
    main() : Object {
        out_string(toCut.substr(2147483647 + 1,99))
    };

};