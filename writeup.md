## Functionality / Techniques
---
Our fuzzer does fuzzing specific to each file type as well as generic fuzzing techniques for all file types.
### 1. Mutate values
--- This was copied from report 1
Maintains the format of the sample input, and changes the values of the fields one field at a time. This attempts to find basic buffer overflow and format string vulnerabilities, or difficulties with unusual characters. The values it tries are:
- integer values: 0, 2**0 to 2**20 and -2**0 to -2**20
- string values: ASCII special characters, null bytes, unicode characters, sequences with spaces.
- overflow values: Powers of 2 up to 2^15 A’s
- format values: small number of %n’s, large number of %n’s, 
Originally, the fuzzer tried all permutations of these values and the original values. This created far too many permutations, so we changed it to one field at a time. For each field, we test all cases (regardless of field type), while the rest of the fields remain as the sample values.
### 2. Plaintext fuzzing techniques
---
- Mutate bytes one by one.   
We replace each byte position in the sample input with every possible byte value, insert every byte value in every position, and send payloads with one byte position deleted, testing all byte positions.
We do this in random order to get a good distribution - if the input file is short, eventually all cases will be tested. If the input file is long, it should test a variety of byte indices before the fuzzer is stopped.
This technique is based on plaintext but runs for all file types after all other techniques have completed.
 
### 3. CSV fuzzing techniques
---
There are 2 CSV specific fuzzing techniques used. The first is increasing the number of rows. This is done by tripling the number of values in input up to 4 times. Each time the number of values is tripled, the second CSV specific fuzzing technique is run. This increases the number of columns while maintaining the number of values in the input. This occurs sequentially from having one column to having just 1 row with only valid csv input being tested (same number of columns for every row).
 
### 4. JSON fuzzing techniques
---
- Increasing the size of the input. This is done by making an array of objects where each object is this input and increasing the length of the array.
- Inserting increasingly long lists into the JSON.
### 5. XML fuzzing techniques
---
- Increasing the size of the input. This is done by multiplying the number of XML nodes at the first level (after <html>). This is similar to the JSON specific fuzzing technique however they cannot be done generically as they both have different requirements to maintain the validity of the input.
- Increasing the depth of nested tags. This is done by creating a large number of nested tags.
- Random mutations of XML tree - we randomly move and/or copy nodes to be children of other nodes. We do a random number of moves/copies before resetting to a fresh mutation.
 
### 6. General
Finally, we also do an “invalid” fuzz which increases the size of the input in a similar way to the JSON specific technique. The difference here is there is no attempt to maintain the validity of the file format. While the output may end up being valid, there is no guarantee of it.
 
## Something Awesome: Multi threading
---
 
## Something Awesome: Command API
---
 
## Something Awesome: Generic Fuzzing
Since there is a large section of fuzzing that is the same regardless of file type, we made a part of the fuzzer handle generic fuzzing. 
We generalise all file formats to a standard protocol which allows us to fuzz fields using a standard set of values. 
We use a dictionary with a values key which contains an array of all the values in the input. It also has a template key which is used for reconstructing the input before it is sent to the binary. The benefit of doing this is we are able to fuzz for a bunch of common vulnerabilities on any file type while minimising code repetition. We are also able to add new file formats and protocols fast since we just need to create functions to parse and reconstruct the format. 
 
Once the input has been converted to a dictionary, we mutate the values in the values array. This is where we cycle through the types of values specified in the Mutate values part of the report for each value in the values array. For each mutation, the dictionary is converted back to its original format and sent to the binary.
 
 
## Design
---
- First we find the type of the sample input by attempting to parse with Python's libraries.
- When a parse is successful, we assume that that type is the correct type. To avoid false positives, we test the types in order from most to least restrictive. 
- Then we produce a dictionary of the values to fuzz in such a way that, after the values are changed by the fuzzing logic, the dictionary can be converted back into text that fits the format of the sample input. We also do file type specific fuzzer
## Bugs detected
---
- basic format string
- basic buffer overflow
- bugs caused due to larger amounts of input than a user would normally enter (becomes buffer overflow due to logic error)
- bugs caused due to larger amounts of nesting than a user would normally enter (becomes buffer overflow due to logic error)
- anymore?
## Potential improvements
---
Dynamic analysis
The major way in which the fuzzer could be improved is by doing some sort of dynamic analysis since right now, the fuzzer focuses on static analysis. One way dynamic analysis could be done is by attempting to map the execution pathways of a program. This would allow the fuzzer to fuzz different parts of the program. While the current version of the fuzzer is able to reach new execution paths, mapping out the pathways would make it so the fuzzer could focus on a specific part of the program rather than treating them all the same.
 
Another way to possibly conduct dynamic analysis would be to try and incorporate GDB into the fuzzing process. Doing this would allow us to analyse the memory of the program as it is running and make decisions on how to mutate based off of it.
 
Multithreading
One last way we could improve the fuzzer is by using a programming language with better multithreading. The multithreading implemented here currently uses user level threads. This means that even though we use multiple threads, the programs still get CPU time at the same rate. This is because python implements something called the Global Interpreter Lock which means only one thread is able to control the python interpreter at a time. While this still provides a performance benefit due to threads needing to wait for binary files to execute, a programming language that allows for multiple threads to control the process could still boost performance.
--------------------------
 

 
 
## Functionality / Techniques
---
Our fuzzer does two fuzzing techniques sequentially: 
### 1. Mutate values
---
Maintains the format of the sample input, and changes the values of the fields one field at a time. This attempts to find basic buffer overflow and format string vulnerabilities. The values it tries are: 
  - integer values: large negative number, small negative number, 0, small positive number, large positive number. These cases may induce a segfault if the sign is unexpected, or a buffer overflow if the number affects a buffer size.
  - string values: very long strings of varying length, (for buffer overflow), long sequences of “%n” (for format string), “%1000000x” (for format string).  

Originally, the fuzzer tried all permutations of these values and the original values. This created far too many permutations, so we changed it to one field at a time for now. For each field, we try all testing cases (regardless of field type) while the rest of the fields remain as the sample values.
 
### 2. Vary the size of the input structure. 
---
For CSV files, this means varying the number of fields per line, and the number of lines provided. We also run the fuzzer on these new fields.
- To test the number of rows in a csv, the input size gets doubled while keeping the number of values per row equal. This only happens 8 times since the size of the inputs gets very large and starts to take a lot of time.  
- Additionally, the fuzzer tests to see if changing the number of values per row causes any errors. The number of values per row has to divide the total number of values so the choice of values per row is generated by looping from 1 to the number of values and testing each valid value in the range.
## Design
--- 
- First we find the type of the sample input by attempting to parse with Python's libraries.
- When a parse is successful, we assume that that type is the correct type. To avoid false positives, we test the types in order from most to least restrictive. 
- Then we produce a dictionary of the values to fuzz in such a way that, after the values are changed by the fuzzing logic, the dictionary can be converted back into text that fits the format of the sample input.
## Bugs detected
---
- basic format string
- basic buffer overflow
- bugs caused due to larger amounts of input than a user would normally enter (becomes buffer overflow due to logic error)
## Next steps
---
- Mutate more than a single field at a time. A likely use case may be when the path to an overflow requires a large number provided as a length and a long string provided as the input.
- We should also test a larger range of numbers.
- We may need to follow and store discovered paths.
- We also need to optimise the current actions.



