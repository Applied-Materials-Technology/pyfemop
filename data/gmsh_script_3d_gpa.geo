// 
// Demo input file for parameterised geometries with Gmsh
// Author: Rory Spencer
// Date:  Nov-2023

// Geometry Variables
gaugeHeight = 10;
gaugeWidth = 2.5;
gaugeThickness = 1; 
SetFactory("OpenCASCADE");
// Parameterisation
//_*
p0 = 1.5;
p1 = 1;
p2 = 1.2;
//**
lc = 1E-1;
filename = "test_mesh.msh";


// Create some points defining the boundary
// Will have vertical symmetry
Point(1) = {0,-gaugeHeight,0,lc}; //Bottom of centreline on specimen
Point(2) = {p0,-gaugeHeight/2,0,lc}; // Parameterised point 0
Point(3) = {p1,0,0,lc}; // Parameterised point 1
Point(4) = {p2,gaugeHeight/2,0,lc}; // Parameterised point 2
Point(5) = {gaugeWidth,gaugeHeight,0,lc}; //Top of gauge side line
Point(6) = {0,gaugeHeight,0,lc}; //Top of gauge centreline
Point(7) = {gaugeWidth,-gaugeHeight,0,lc}; // Bottom Edge of gauge

// Connect things up with some lines
Line(1) = {1,7}; // Bottom Hor Line
Spline(2) = {7,2,3,4,5}; //Vertical up side
Line(3) = {5,6}; // Top Hor Line
Line(4) = {6,1}; // Centreline

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


delta = 0.005E-3;
topsurf() = Surface In BoundingBox 
{0-delta,gaugeHeight-delta,0-delta,
gaugeWidth+delta, gaugeHeight+delta,gaugeThickness+delta};

btmsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
gaugeWidth+delta,-gaugeHeight+delta,gaugeThickness+delta};

bcksurf() = Surface In BoundingBox 
{-100,-gaugeHeight-delta,0-delta,
100,gaugeHeight+delta,0+delta};

midsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
0+delta,gaugeHeight+delta,gaugeThickness+delta};

vissurf() = Surface In BoundingBox 
{-100,-100,gaugeThickness-delta,
100,100,gaugeThickness+delta};



Physical Surface("Top-BC",2) = {topsurf()};
Physical Surface("Btm-BC",3) = {btmsurf()};
Physical Surface("Z-Symm",4) = {bcksurf()};
Physical Surface("X-Symm",5) = {midsurf()};
Physical Surface("Visible-Surface",6) = {vissurf()};

Save Str(filename);
Exit;
