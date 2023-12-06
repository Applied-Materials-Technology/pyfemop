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
p0 = 1.73929;
p1 = 1.63760;
p2 = 1.23500;
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


Point(8) = {gaugeWidth+5,gaugeHeight,0,lc}; // radius centre
Point(9) = {gaugeWidth+5,gaugeHeight+5,0,lc}; // top of radius
Point(10) = {gaugeWidth+5,gaugeHeight+5+15,0,lc}; // top of tab
Point(11) = {0,gaugeHeight+5+15,0,lc};




// Connect things up with some lines
Line(1) = {1,7}; // Bottom Hor Line
Spline(2) = {7,2,3,4,5}; //Vertical up side
Line(3) = {5,6}; // Top Hor Line
Line(4) = {6,1}; // Centreline
Circle(5) = {5,8,9};
Line(6) = {9,10};
Line(7) = {10,11};
Line(8) = {11,6};

// Define tab end 1/4 symmetry surface.
Curve Loop(1) = {3,5,6,7,8};
Plane Surface(1) = {1};

//Define gauge section 1/2 symmetry surface
Curve Loop(3) = {1,2,3,4};
Plane Surface(3) = {3};

// Mirror tab
Symmetry{0,1,0,0}{Duplicata{Surface{1};}}

// Get all surfaces
delta=0.005;
all() = Surface In BoundingBox 
{-100,-100,0-delta,
100,100,gaugeThickness+delta};

Symmetry{1,0,0,0}{Duplicata{Surface{all()};}}

// Define Physical Surface
// Get all surfaces
delta=0.005;
all() = Surface In BoundingBox 
{-100,-100,0-delta,
100,100,gaugeThickness+delta};
Physical Surface("Plane",1) = {all()};

//Create holes
//Point(101) = {0,gaugeHeight+12-2.5,0,lc};
//Point(111) = {0,gaugeHeight+12,0,lc};
//Point(112) = {0,gaugeHeight+12+2.5,0,lc};

//Circle(91) = {101,111,112};
//Circle(92) = {112,111,101};

//Curve Loop(101) = {91,92};
//Surface(101) = {101};

//BooleanDifference{Plane{all()}}{Surface{101}};


Extrude {0, 0, gaugeThickness} { Surface{:}; Layers{3}; Recombine;}

//Mesh 3;

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

//Physical Surface("Top-BC",2) = {topsurf()};
//Physical Surface("Btm-BC",3) = {btmsurf()};

//Physical Surface("Mid-BC",5) = {midsurf()};
//Mesh.StlOneSolidPerSurface=2;

//Save Str(filename);
//Exit;
