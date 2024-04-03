class Main inherits IO {
	main() : Object { {
        --this will instead take in a non numeric string instead of int
        let fakeStr: Int <- in_int() in
        out_int(fakeStr);
    }
	} ;

} ;