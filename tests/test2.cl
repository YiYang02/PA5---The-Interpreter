-- should throw stack overflow error
class Main inherits IO {
    recursiveMethod() : SELF_TYPE {{
        self.recursiveMethod();
    }};

    main() : Object {
        {
            self.recursiveMethod();
        }
    };
};