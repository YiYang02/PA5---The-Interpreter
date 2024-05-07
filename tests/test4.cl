(*
tests dynamic method invocation for inherited
classes. 
*)

class Parent inherits IO
{
  parent() : Object
  {
    out_int(1)
  };
};


class Child inherits Parent
{
  parent() : Object
  {
    out_int(2)
  };
};


class Main
{
  main() : Object
  {
    {
      let child : Parent <- new Child in
      child.parent(); -- should return 2. though its of type Parent, its a Child object

    }
  };
};