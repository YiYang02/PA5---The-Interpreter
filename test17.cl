class Test inherits IO {
    x : Int <- 0;
    func (x: Int) : Int {
        func (x - 1) + func (x - 1) + func ( x <- 1)
    };
};

class Main {
    main(): Object {
        let test : Test <- new Test in
        let x : Int <- 2 in
        test.func(x <- 3)
    };
};