# Test comment
clear X;
do 3;
    incr X;
enddo;

# Another test comment
clear Y;
do 4;
    incr Y;
enddo;

clear Z;
while X not 0 do;
   clear W; # foo;
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
