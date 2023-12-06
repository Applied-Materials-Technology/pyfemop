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
h1x = 0.5;
h1y = 0.5;
h1r = 0.3;
h2x = 0.1;
h2y = -0.4;
h2r = 0.1;
//**
lc = 0.4;
filename = "test_mesh.msh";


// Create rectangular box
Rectangle(1) = {-gaugeWidth,-gaugeHeight,0, 2*gaugeWidth,
    2*gaugeHeight};

// Create Circles
Circle(5) = {h1x*gaugeWidth,h1y*gaugeHeight,0, gaugeWidth*h1r};
Circle(6) = {h2x*gaugeWidth,h2y*gaugeHeight,0, gaugeWidth*h2r};

//Curve Loop(1) = {1,2,3,4};
//Plane Surface(1) = {1};

Curve Loop(2) = {5};
Curve Loop(3) = {6};

Plane Surface(2)= {2};
Plane Surface(3) = {3};

BooleanDifference(4)=  {Surface{1};Delete;}{Surface{2,3};Delete;};

MeshSize{ PointsOf{Surface{:};}} = lc;
//Mesh 2;
Recombine Surface{:};

Extrude {0, 0, gaugeThickness} { Surface{:}; Layers{3}; Recombine;}
Mesh 3;
Physical Volume("Specimen",1) = {1};

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

Save Str(filename);
Exit;
