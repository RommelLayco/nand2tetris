// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
  @R2
  M=0 // Set the result to zero

(LOOP)
  @R1
  D=M     // D=R1
  @END
  D;JEQ   // if R1 == 0 goto END

  @R1
  M=D-1 // Decrease the value of R1 by 1

  //Load the current sum into D
  @R2
  D=M
  // Add R0 to the total
  @R0
  D=D+M

  // Store result in R2
  @R2
  M=D
  @LOOP
  0;JMP

(END)
  @END
  0;JMP
