We took a very similar approach to PA4 to do PA5 since the code
construction and evaluating took similar patterns. Following from our 
guidelines on PA4, we chose to construct all of the expressions as
namedtuple because that provided us with a clean way to deserialize and later
identify each type of expression so that we can handle its operational
semantics differently. We added the extra InternalMethod class so that internal
methods could all be caught under the same if branch. After deserializing, 
we stored all parts of the annotated ast in their respective dictionaries
for fast look-ups during the evaluation process. We followed your Ocaml video
to get started and just converted to Python so after we did the first few 
expressions' evaluation and how the operational semantic rules on the COOL manual
could be converted to code (not just code but really our code with the way we 
set it up), the rest were pretty straightforward. 

While implementing while, we had a lot of problems though it was very simple
because we wrote an actual while loop in Python that executed eval recursively 
but that led to difficulties returning the last value as well as with the 
logic. DynamicDispatch was kind of hard to implement especially because of how we 
initially had structured our namedtuples. We didn't have a problem with the logic, 
but we needed to access the attributes and locations field from the 
returned v0 (the result of eval on the receiver expression), but sometimes the 
return expression didn't have the field. Therefore, we had sometimes 
populated empty dictionaries for some expressions that never get populated
instead of nasty if statements. When we did dynamic dispatch following the video, 
it was straightforward to do self dispatch and static dispatch. We chose not to 
implement case because it was quietly honestly more work than
we were willing to do since we're pass/failing the course. However, we did
take a look at the rules for it to see how we might implement it. Overall though,
it was a LOT easier to do PA5 than it was to do PA4 simply because we know
what to expect now and we've already done it. I don't know if we didn't stress
because we didn't need the grade anymore or because it was easier lol. (probably both)

When it came to testcases, we wanted to stress testing the core features of Cool. Thus,
we have 4 test cases. The first one tests all the internal methods of Cool,
i.e. out_string(), out_int(), etc. The second one tests infinite recursion in Cool.
The third one tests if statements, while loop, isvoid(), and passing in a method
as an argument to another method. Lastly, the fourth test case tests for dynamic 
method invocation for inherited classes, thus testing for inheritance and also inherited
methods.