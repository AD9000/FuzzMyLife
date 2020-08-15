# FuzzMyLife
Binary fuzzer: Fuzz binaries as you like!

## Techniques
For a detailed description of how the fuzzer works, have a look at [writeup.md](https://github.com/AD9000/FuzzMyLife/blob/master/writeup.md)

## How To Use
Keeping usability in mind, all you need to run this are the commands:

```
cd /path/to/FuzzMyLife
```
and then
```
python3 src/fuzzer /path/to/binary /path/to/valid/input 
```

To use the fuzzer in debug mode, you can use the `-d` flag as:
```
python3 src/fuzzer /path/to/binary /path/to/valid/input -d
```
which would log outputs, errors and other debugging information.

## Optional Install (does not need root privileges)
We wanted this fuzzer to be very simple to use, and with that in mind, we have made a simple install script for you to use:
All you need to do is:

```
cd /path/to/FuzzMyLife
```
and then
```
chmod +x ./scripts/install
./scripts/install
```

Then you would be able to use:
```
# now you can use:
fml /path/to/binary /path/to/valid/input    <--- the OG fuzzer. Same as using ./src/fuzzer
fuzz /path/to/binary /path/to/valid/input   <--- run the fuzzer with the debugging
```

If you name your binaries and inputs as: `binary` and input as `binary.txt`,
you can put them in the bin folder to use:
```
fuzz json1                                  <--- Same as using: ./src/fuzzer ./bin/json1 ./bin/json1.txt
```
and if you want to run all pairs:
```
fuzzAll                                     <--- runs all binaries from ./bin folder in debug mode
```

If you want to test the .crash files created segfault the program you run the fuzzer on, you can use:
```
testLogs /path/to/log/directory
```

Once you're done, you can run the uninstall script:
```
uninstallFuzz
```
which would remove the scripts from your system.

**Note**: the installation is completely optional and you can use the scripts directly by running
```
./scripts/<scriptName> <arguments> <options>
```
if you like that better


## Credits:
- Atharv Damle
- Lasindu Shanil de Silva
- Song Fang
- Justin Mack
