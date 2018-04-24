'''
Created on April 20, 2018

@author: David Coppin
@institution: Department of Physics, University of Auckland

@description: Configuration file that lists all the non-fixed variables and paths that are needed 
              by the tracking algorithm
'''

# Folder where the precipitation data is stored
data_path = $PWD/Data/CMORPH/

# Folder where the land-sea mask is stored
lsm_path = $PWD/Data/LSM/Cmorph_slm_8km.nc

# Folder where the output go to
targetdir = $PWD/Data/Tracking/8km-30min/

# Name of the precipitation variable
varname = CMORPH

# Unit of the precipitation data
units = mm/h

# Resolution of the data (in km)
reso = 8

# Low threshold for watershed on precipitation data
min_prec = 0.

# High threshold for watershed on precipitation data
max_prec = 2.5

# Distance to coast in pixels used to create mask of islands and close surrounding areas
szone = 6

# Distance to coast in pixels used to create mask of islands and large areas of surrounding oceans
lzone = 50

# Threshold to keep clusters and tracks once clusters overlap with mask (minimum overlap necessary)
frac_mask = 0.8

# Threshold to merge overlapping ellipses (minimum overlap between ellipses)
frac_ellipse = 0.8

# Minimum ellipse axis used for tracking (in pixels)
min_axis = 6 

# Area below which islands are deleted from the masks (in km^2)
min_size = 300

# Maximum area of islands (in km^2) that are filled by the land-sea mask (above, for continents, only coasts)
max_size = 800000

# Save time connected clusters for debugging
save = False