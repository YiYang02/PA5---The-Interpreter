-- neg index string substr

class Main inherits IO{
    toCut: String <- "hello";
    main() : Object {
        out_string(toCut.substr(~1, ~2))
    };

};