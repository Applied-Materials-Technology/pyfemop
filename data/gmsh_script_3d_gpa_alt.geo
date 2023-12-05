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
p0 = 1.5;
p1 = 1;
p2 = 0.5;
//**
lc = 1E-1;
fmin = Fabs((-p1^2)/4*p0);
Printf('%f',fmin);
filename = "test_mesh.msh";

// Function
//f =  p2*(-p0^x -p1*x)/fmin + gaugeWidth;

// Create some points defining the boundary
// Will have vertical symmetry
Point(1) = {0,-gaugeHeight,0,lc}; //Bottom of centreline on specimen
Point(2) = {gaugeWidth,gaugeHeight,0,lc}; //Top of gauge side line
Point(3) = {0,gaugeHeight,0,lc}; //Top of gauge centreline
Point(4) = {gaugeWidth,-gaugeHeight,0,lc}; // Bottom Edge of gauge
// Quadratic shape 
y=-0.75;
Point(5) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 0
y=-0.5;
Point(6) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 1
y=-0.25;
Point(7) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 2
y=0;
Point(8) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 0
y=0.25;
Point(9) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 1
y=0.5;
Point(10) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 2
y=0.75;
Point(11) = {p2*(-p0^y -p1*y)/fmin + gaugeWidth,gaugeHeight*y,0,lc}; // Parameterised point 2

// Connect things up with some lines
Line(1) = {1,4}; // Bottom Hor Line
Spline(2) = {4,5,6,7,8,9,10,11,2}; //Vertical up side
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

// We now can use these variables to assign physical surfaces.
// Again note the tags! Physical tags start at 1 and tags are shared between all physical entities.
// Physical Volume("Vol",1) and Physical Surface("Sur",1) will cause errors!
// The names given to these surfaces will be used as the BC names in MOOSE.

Physical Surface("Top-BC",2) = {topsurf()};
Physical Surface("Btm-BC",3) = {btmsurf()};
Physical Surface("Bck-BC",4) = {bcksurf()};
Physical Surface("Mid-BC",5) = {midsurf()};


//Save Str(filename);
//Exit;
