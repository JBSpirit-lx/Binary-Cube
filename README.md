----- How to Use -----

Simply change the upload_file variable, ensure the file you want to encode is in the same folder as the script (if not specify a path), and run. The program will generate a new_obj.stl file in the same folder, which can be uploaded to a
slicer for 3d printing. Note that because of the complexity of the mesh, programs such as Tinkercad that simplify meshes on import won't be able to properly display the model.

----- How to Decode -----

Data is written onto the cube starting in the bottom left corner of the first face, then going along the row until it reaches the end, then it moves up 1 row and starts on the left again. Once a face is filled up in this pattern it moves 
onto the next face adjacent to the current face's right edge (so to read you would rotate the cube clockwise after reading each face bottom to top).

----- Future Improvements -----

Eventually I will add information to the top and bottom of the cube that will include text saying what it is, an indicator for where to start the decoding, maybe some error correction, and other metadata. Also eventually I'll implement
some code to simplify the mesh because it gets quite complex very quickly.

Yes I know it looks like a Borg Cube :)

