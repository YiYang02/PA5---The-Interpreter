-- Dynamic dispatch chooses a method based on the dynamic type of the
-- dispatching object.

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
      child.parent();

    }
  };
};