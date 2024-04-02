Class X Inherits IO {
	methodA (x : Int) : SELF_TYPE {{
		out_int(x + 3);
        out_string("-");
        out_string("ClassA1");
        out_string(" ");
		self;
	}};
};

Class Y Inherits X {
	methodA (x : Int) : SELF_TYPE{{
		out_int(x + 2);
        out_string("-");
        out_string("ClassB");
        out_string(" ");
		self;
	}};
};

Class Z Inherits Y {
	methodA (x : Int) : SELF_TYPE{{
		out_int(x + 1);
        out_string("-");
        out_string("ClassC");
        out_string(" ");
		self;
	}};
};

Class Main Inherits IO{

	main() : Object {{
		(new Z).methodA(2147483647).methodA(~2147483647)@Y.methodA(~2147483647).methodA(~2147483647).methodA(~2147483647).methodA(~2147483647)@X.methodA(~2147483647);

	}};
};