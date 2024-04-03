class Main inherits IO {
	main() : Object { {
        --this will instead take in a null string
        let nullString: String <- in_string() in
        out_string(nullString);
    }
	} ;

} ;