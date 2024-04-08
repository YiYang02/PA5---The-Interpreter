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
    child : Parent;
    new_child : Parent;
    newest_child : Parent;
    main() : Object
    {
        {
            let child : Parent <- new Child in
            child.parent();

            let new_child : Object <- new Parent in
            new_child.copy();
            new_child.parent();
            
            let newest_child : Parent <- child.copy() in 
            newest_child.abort();
            newest_child.parent();
        }
    };
};