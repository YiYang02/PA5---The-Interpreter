-- class Main inherits IO {
--     msg : String <- "Hello World!\n";

--     sum(a: Int, b: Int) : Int {
--         a + b
--     };

--     main() : IO {
--         self.out_int(1)
--     };
-- };

(* Simple program with a lets statement *)
class Main inherits IO{
	x : Int <- 1;
	main () : Object {
		out_string(x.type_name())
	};
};