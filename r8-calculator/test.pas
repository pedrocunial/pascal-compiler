program xdk;

var
   x: integer

function daba(n : integer; i: boolean ): integer;
var j :integer

j := 2;
   daba := j
   while j < n do
   begin
      if i then
         print(j)
         j := j - 1;
   end

begin
   x := read();
   print(daba(x, true))
end.
