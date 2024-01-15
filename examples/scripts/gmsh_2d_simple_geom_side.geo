// 
// Demo input file for parameterised geometries with Gmsh
// Author: Rory Spencer
// Date:  Jan 2024
// 
// Simple Geometry to update
// Elastic only model. 
// Target shape will be rectangular with height = 1, width = 0.8
// gaugeWidth parameter moves the width of the rectangular
// Model will have 

// Geometry Variables
gaugeHeight = 1;
// gaugeThickness = 1E-3; //2D for now

// Parameterisation
//_*
gaugeWidth = 0.8;
//**
lc = 0.1;
filename = "mesh_simple_geom.msh";


// Create some points defining the boundary
// Will have vertical symmetry
Point(1) = {0,0,0,lc}; //Bottom of centreline on specimen
Point(2) = {gaugeWidth,0,0,lc}; // Parameterised point 0
Point(3) = {gaugeWidth,gaugeHeight,0,lc}; // Parameterised point 1
Point(4) = {0,gaugeHeight,0,lc}; // Parameterised point 2

// Connect things up with some lines
Line(1) = {1,2}; // Bottom Hor Line
Line(2) = {2,3}; // Vertical line outer side
Line(3) = {3,4}; // Top Hor Line
Line(4) = {4,1}; // Inner vertical line


Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};

Recombine Surface{:};
Mesh 2;


Physical Surface("Specimen",1) = {1};

Physical Curve("Top-BC",2) = {3};
Physical Curve("X-Symm",3) = {4};
Physical Curve("Btm-BC",4) = {1};

Save Str(filename);
Exit;
