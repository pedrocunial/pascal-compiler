program xdk;

var
   x,z: integer;
   y,k:  boolean;


begin
   x := read();
   y := x > 2;
   k := y or y;
   while y do
   begin
      if x > 10 then
      begin
        z := x * 3;
        print(y or y);
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
