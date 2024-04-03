-- case without matching branch
class Main inherits IO{
    num: Int <- 10;
    main() : Object {
    {
        case "no matching branch" of
            num : Int => out_int(0);
        esac;
    }
        
    };

};