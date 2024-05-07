(*
This test case will test all the internal methods of Cool. i.e. out_string()
*)

class Main inherits IO {
    str: String <- "Hello, World!";
    num: Int <- 42;
    bool: Bool <- true;
    
    main(): Object {
        {

            (* Use methods from Object class *)
            self.copy();
            out_string(self.type_name());
            out_string("\n");

            (* Use methods from IO class *)
            out_string(str);
            out_string("\n");
            out_int(num);
            in_string();
            in_int();

            (* Use methods from String class *)
            out_int(str.length());
            out_string("\n");
            out_string(str.concat(" Concatenated."));
            out_string(str.substr(0, 5));
            out_string("\n");

            self.abort();
        }
    };
};