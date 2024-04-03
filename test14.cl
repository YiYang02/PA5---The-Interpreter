-- case without matching branch
class Main inherits IO{
    voidObject: IO;
    var: String <- "hello";
    main() : Object {
    {
        case voidObject of
            var : String => out_string("hello");
        esac;
    }
        
    };

};