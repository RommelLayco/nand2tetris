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

// Put your code here.

  // Store Current Black Screen Location into R0
(RESET)
  @SCREEN
  D=A
  @R0
  M=D

  //Store current White screen location
  @SCREEN
  D=A
  @R1
  M=D

(START)
  // Check the value of the keyboard
  @KBD
  D=M

  @CLEAR
  D;JEQ  // CLEAR SCREEN if no input

  @R0
  A=M
  M=-1    // COLOR SCREEN

  @R0
  D=M+1

  @R3
  M=D // tmp store next screen location

  // Check if greater than last RAM address
  @24576
  D=D-A
  @RESET
  D;JGT

  @R3
  D=M
  @R0
  M=D

  @SCREEN
  D=A
  @R1
  M=D    // RESET White start location

  @START
  0;JMP

(CLEAR)
  @R1
  A=M
  M=0   // CLEAR SCREEN

  @R1
  D=M+1

  @R3
  M=D // tmp store next screen location

  // Check if greater than last RAM address
  @24576
  D=D-A
  @RESET
  D;JGT

  @R3
  D=M
  @R1
  M=D

  @SCREEN
  D=A
  @R0
  M=D    // RESET black start location

  @START
  0;JMP
