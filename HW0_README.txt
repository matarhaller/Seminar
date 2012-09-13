Python Seminar
HW 0

For some reason I am not able to run my script more than once - so sadly it cannot be run smoothly in one call from the command line. The Bear class and the world work, but you'll have to look into the code.

You can import the file:
run HW0.py

Ideally, you would just be able to run answer_hw() but because of the bug I described above that won't work.

Instead, to see that the classes work, you can run:

World().runworld(150) which will return a (born, dead) tuple

In order to run it again, you need to reset ipython and reload the .py homework file.

Within answer_hw() there is code that shows how I would ideally run it (had it been working).

Same thing with b.