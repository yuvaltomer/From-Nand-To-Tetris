// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Set length variable to 8192 - the number of pixels in the screen
@8192
D=A
@length
M=D

// Read input from keyboard
@KEYBOARD
0;JMP

// Initialize i (performs as a for loop iterator) and choose color according to input
(KEYBOARD)
    @i
    M=0
    @KBD
    D=M
    @WHITE
    D;JEQ
    @BLACK
    0;JMP

// WHITE LOOP - entered if no key is pressed
(WHITE)
    // go back to reading input if the entire screen is white
    @i
    D=M
    @length
    D=M-D
    @KEYBOARD
    D;JEQ
    // whiten the SCREEN+i pixel
    @SCREEN
    D=A
    @i
    A=D+M
    M=0
    // i=i+1
    @i
    M=M+1
    // iterate
    @WHITE
    0;JMP

// BLACK LOOP - entered if a key is pressed
(BLACK)
    // go back to reading input if the entire screen is black
    @i
    D=M
    @length
    D=M-D
    @KEYBOARD
    D;JEQ
    // blacken the SCREEN+i pixel
    @SCREEN
    D=A
    @i
    A=D+M
    M=-1
    // i=i+1
    @i
    M=M+1
    // iterate
    @BLACK
    0;JMP