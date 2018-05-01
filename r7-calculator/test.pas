program xdk;

var
   x,z: integer;
   y:  boolean;


begin
   x := read();
   y := x > 2;
   while y do
   begin
      if x > 10 then
      begin
        z := x * 3;
        print(z);
        print((x - 13) and 1)
      end
      else
      begin
        print(not(x or 2))
      end
      x := x - 1;
      y := x > 2
  end
end.
