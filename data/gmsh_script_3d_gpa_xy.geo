// 
// Demo input file for parameterised geometries with Gmsh
// Author: Rory Spencer
// Date:  Nov-2023

// Geometry Variables
gaugeHeight = 10;
gaugeWidth = 2.5;
gaugeThickness = 1; 

// Parameterisation
//_*
p0 = 0.5;
p1 = 0.5;
//**
lc = 1E-1;
filename = "test_mesh.msh";


// Create some points defining the boundary
// Will have vertical symmetry
Point(1) = {0,-gaugeHeight,0,lc}; //Bottom of centreline on specimen
Point(2) = {gaugeWidth,gaugeHeight,0,lc}; //Top of gauge side line
Point(3) = {0,gaugeHeight,0,lc}; //Top of gauge centreline
Point(4) = {gaugeWidth,-gaugeHeight,0,lc}; // Bottom Edge of gauge

Point(5) = {gaugeWidth*p0,gaugeHeight*p1,0,lc}; // Parameterised point 0


// Connect things up with some lines
Line(1) = {1,4}; // Bottom Hor Line
Spline(2) = {4,5,2}; //Vertical up side
Line(3) = {2,3}; // Top Hor Line
Line(4) = {3,1}; // Centreline

Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};

// Top & Bottom
Transfinite Curve{1} = 10;
Transfinite Curve{3} = 10;

// Sides
Transfinite Curve{4} = 50;
Transfinite Curve{2} = 50;

Transfinite Surface{1};

Recombine Surface{:};

Extrude {0, 0, gaugeThickness} { Surface{:}; Layers{3}; Recombine;}

Mesh 3;

Physical Volume("Specimen",1) = {1};


delta = 5E-2;
topsurf() = Surface In BoundingBox 
{0-delta,gaugeHeight-delta,0-delta,
gaugeWidth+delta, gaugeHeight+delta,gaugeThickness+delta};

btmsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
gaugeWidth+delta,-gaugeHeight+delta,gaugeThickness+delta};

bcksurf() = Surface In BoundingBox 
{-100,-100,0-delta,
100,100,0+delta};

midsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
0+delta,gaugeHeight+delta,gaugeThickness+delta};
//Printf('%f',bcksurf());
// We now can use these variables to assign physical surfaces.
// Again note the tags! Physical tags start at 1 and tags are shared between all physical entities.
// Physical Volume("Vol",1) and Physical Surface("Sur",1) will cause errors!
// The names given to these surfaces will be used as the BC names in MOOSE.

Physical Surface("Top-BC",2) = {topsurf()};
Physical Surface("Btm-BC",3) = {btmsurf()};
Physical Surface("Bck-BC",4) = {bcksurf()};
Physical Surface("Mid-BC",5) = {midsurf()};


Save Str(filename);
Exit;
