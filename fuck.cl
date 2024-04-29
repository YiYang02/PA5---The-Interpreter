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
-- class Main inherits IO{
-- 	x : Int <- 5;
-- 	y : Int <- 5;
-- 	z : Bool <- true;
-- 	a : Bool <- not z;
-- 	main () : Object {
-- 		out_string("hello")
-- 	};
-- };

-- not.cl
-- show off quick negation

class Main {
  main():Object {
    let
      x:Int <- 0,
      b:Bool
    in {
      while x < 100 loop {
        b = not not not not not  not not not not not  not b;
        b = not not not not not  not not not not not  not b;
        b = not not not not not  not not not not not  not b;
        b = not not not not not  not not not not not  not b;
        b = not not not not not  not not not not not  not b;
        x <- x + 1;
      } pool;
      if b then abort() else 0 fi;
    }
  };
};


