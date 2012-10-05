"""
Write a program that identifies musical notes from sound (AIFF) files. • Run it on the supplied sound files (12) and report your program’s results. Use the labeled sounds (4) to make sure it works correctly.
•
The provided sound files contain 1-3 simultaneous notes from different organs.
• Save copies of any example plots to illustrate how your program works.

You’ll want to decompose the sound into a frequency power spectrum. Use a Fast Fourier Transform. Be care about “unpacking” the string hexcode into python data structures. The sound files use 32 bit data. Play around with what happens when you convert the string data to other integer sizes, or signed vs unsigned integers. Also, beware of harmonics.
"""