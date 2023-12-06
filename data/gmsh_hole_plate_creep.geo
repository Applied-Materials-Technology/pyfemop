// 
// Demo input file for parameterised geometries with Gmsh
// Author: Rory Spencer
// Date:  Nov-2023

// Geometry Variables
gaugeHeight = 10;
gaugeWidth = 5;
gaugeThickness = 1; 
SetFactory("OpenCASCADE");
// Parameterisation
//_*
h1x = 4.5;
h1y = 0.5;
h1r = 2;
h2x = 3;
h2y = 4;
h2r = 1;
//**
lc = 0.6;
filename = "test_mesh.msh";


// Create rectangular box
Box(1) = {-gaugeWidth,-gaugeHeight,0, 2*gaugeWidth,
    2*gaugeHeight,gaugeThickness};

// Create Cylinder
Cylinder(2) = {h1x,h1y,0, 0,0,1, h1r};
Cylinder(3) = {h2x,h2y,0, 0,0,1, h2r};

BooleanDifference(4)=  {Volume{1};Delete;}{Volume{2,3};Delete;};

delta=0.05;
allvol() = Volume In BoundingBox 
{-100,-100,0-delta,
100,100,100};

Physical Volume(1) = {allvol()};

MeshSize{ PointsOf{Volume{:};}} = lc;

Recombine Volume;

Mesh 3;

delta = 5E-2;
topsurf() = Surface In BoundingBox 
{-gaugeWidth-delta,gaugeHeight-delta,0-delta,
gaugeWidth+delta, gaugeHeight+delta,gaugeThickness+delta};

btmsurf() = Surface In BoundingBox 
{-gaugeWidth-delta,-gaugeHeight-delta,0-delta,
gaugeWidth+delta,-gaugeHeight+delta,gaugeThickness+delta};

bcksurf() = Surface In BoundingBox 
{-100,-100,0-delta,
100,100,0+delta};

Physical Surface("Top-BC",2) = {topsurf()};
Physical Surface("Btm-BC",3) = {btmsurf()};
Physical Surface("Bck-BC",4) = {bcksurf()};

//Save Str(filename);
//Exit;