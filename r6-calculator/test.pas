begin
  x := read();
  while x > 0 do
  begin
    if x > 10 then
    begin
      print(x and 2)
    end
    else
    begin
      print(not(x or 2))
    end
    x := x - 1
  end
end
