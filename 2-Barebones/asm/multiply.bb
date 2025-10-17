clear X;
do 3;
    incr X;
enddo;

clear Y;
do 4;
    incr Y;
enddo;

clear Z;
while X not 0 do;
   clear W;
   while Y not 0 do;
      incr Z;
      incr W;
      decr Y;
   endwhile;
   while W not 0 do;
      incr Y;
      decr W;
   endwhile;
   decr X;
endwhile;

print Z;
