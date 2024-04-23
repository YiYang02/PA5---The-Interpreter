-- class Main inherits IO {
--     msg : String <- "Hello World!\n";

--     sum(a: Int, b: Int) : Int {
--         a + b
--     };

--     main() : IO {
--         self.out_int(1)
--     };
-- };

class Main inherits IO {
	count : Int <- 7;
	main () : Object {{
		
		while 5 < count loop {
			count <- count - 1;
			out_int(count);
		} pool;
	}};
};