class Main inherits IO {
    msg : String <- "Hello World!\n";

    sum(a: Int, b: Int) : Int {
        a + b
    };

    main() : IO {
        self.out_int(1)
    };
};