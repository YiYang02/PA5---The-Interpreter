-- class Main inherits IO {
--    main(): SELF_TYPE {
-- 	self@IO.out_string("Hello, World.\n")
--    };
-- };

class Main inherits IO {
	main(): IO {
	 self.out_string("Hello World.")
	};
 };