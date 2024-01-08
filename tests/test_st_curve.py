#
#
#
#%% 
#%matplotlib qt
from pycoatl.spatialdata.importmoose import moose_to_spatialdata
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
# %%

efile = '/home/rspencer/mtgo/data/moose_output.e'
efile2 = '/home/rspencer/mtgo/examples/moose-workdir-3/moose-sim-3_out.e'
efile3 = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'
test_data = moose_to_spatialdata(efile)
test_data2 = moose_to_spatialdata(efile2)
test_data3 = moose_to_spatialdata(efile3)
# %%
test_data.data_sets[-1].points[0]
test_data.data_sets[-1]['creep_strain_yy'][0]
# %%
creep_limit = 5E-4
num_points = test_data.data_sets[0].number_of_points
stresses = np.zeros(num_points)
times = np.empty(num_points)
for i,data_set in enumerate(test_data.data_sets):
    underlim = data_set['creep_strain_yy'] < creep_limit
    stresses[underlim] = data_set['stress_yy'][underlim]
    times[underlim] = np.ones(np.sum(underlim))*test_data._time[i]

plt.plot(times,stresses,'.')
creep_limit = 1E-4
for i,data_set in enumerate(test_data.data_sets):
    underlim = data_set['creep_strain_yy'] < creep_limit
    stresses[underlim] = data_set['stress_yy'][underlim]
    times[underlim] = np.ones(np.sum(underlim))*test_data._time[i]
plt.plot(times,stresses,'.')

# %%

def get_time_stress_curves(spatialdata,creep_limit):
    num_points = spatialdata.data_sets[0].number_of_points
    stresses = np.ones(num_points)
    times = np.empty(num_points)

    for i,data_set in enumerate(spatialdata.data_sets):
        underlim = data_set['creep_strain_yy'] < creep_limit

        stresses[underlim] = data_set['stress_yy'][underlim]
        times[underlim] = np.ones(np.sum(underlim))*spatialdata._time[i]
    times[times==np.max(spatialdata._time)]=np.nan
    return times, stresses

def lin_int(x,x0,y0,x1,y1):
    return (y0*(x1-x)+y1*(x-x0))/(x1-x0)

def get_time_stress_curves_int(spatialdata,creep_limit, field = 'creep_strain_yy'):
    num_points = spatialdata.data_sets[0].number_of_points
    stresses_under = np.ones(num_points)*np.nan
    strains_under = np.ones(num_points)*np.nan
    times_under = np.empty(num_points)
    stresses_over = np.ones(num_points)*np.nan
    strains_over = np.ones(num_points)*np.nan
    times_over = np.empty(num_points)
    times = np.empty(num_points)
    stresses = np.empty(num_points)

    for i,data_set in enumerate(spatialdata.data_sets):
        underlim = data_set[field] < creep_limit

        stresses_under[underlim] = data_set['stress_yy'][underlim]
        strains_under[underlim] = data_set[field][underlim]
        times_under[underlim] = np.ones(np.sum(underlim))*spatialdata._time[i]


    for i,data_set in reversed(list(enumerate(spatialdata.data_sets))):
        overlim = data_set[field] > creep_limit

        stresses_over[overlim] = data_set['stress_yy'][overlim]
        strains_over[overlim] = data_set[field][overlim]
        times_over[overlim] = np.ones(np.sum(overlim))*spatialdata._time[i]

    
    #plt.plot(stresses_under,'.')
    #plt.plot(stresses_over,'.')
    
    for i in range(len(stresses_over)):
        times[i] = lin_int(creep_limit,strains_under[i],times_under[i],strains_over[i],times_over[i])
        stresses[i] = lin_int(creep_limit,strains_under[i],stresses_under[i],strains_over[i],stresses_over[i])
    
    #plt.plot(stresses,'.')

    return times, stresses
# %%
t1,s1 = get_time_stress_curves_int(test_data,5E-3,field='mechanical_strain_yy')
t2,s2 = get_time_stress_curves_int(test_data2,5E-3,field='mechanical_strain_yy')
t3,s3 = get_time_stress_curves_int(test_data3,5E-3,field='mechanical_strain_yy')
# %%
fig  = plt.figure()
ax = fig.add_subplot()
ax.plot(1E-3*t1,1E3*s1,color='k',marker='.',linestyle='None',label='Design 1')
#plt.plot(t2,s2,'.')
ax.plot(1E-3*t3,1E3*s3,color='r',marker='P',linestyle='None', label='Design 2')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Stress [MPa]')
ax.set_title('Time to 0.2% Total Strain')
ax.legend()
# %%
def calc_area(t,s):
    #Remove NaNs
    t = t[~np.isnan(s)]
    s = s[~np.isnan(s)]
    ord = np.argsort(t)
    t=t[ord][::2]
    s=s[ord][::2]
    return np.trapz(s,t)

def fit_spline(t,s):
    #Remove NaNs
    t = t[~np.isnan(s)]
    s = s[~np.isnan(s)]
    ord = np.argsort(t)
    t=t[ord]
    s=s[ord]
    #plt.plot(t)
    return interpolate.splrep(t[210:],s[210:],s=0.001)
# %%
print(calc_area(t1,s1))
print(calc_area(t2,s2))
print(calc_area(t3,s3))
#spl = interpolate.UnivariateSpline(t1[~np.isnan(s1)],s1[~np.isnan(s1)])

# %%
spl = fit_spline(t1,s1)
t = np.geomspace(1,2.16E7,100)
plt.plot(t1,s1,'.')
plt.plot(t,interpolate.splev(t,spl),'.')
# %%

def update_exceeded(spatialdata,creep_limit,field='mechanical_strain_yy'):
    for data_set in spatialdata.data_sets:
        data_set['over_creep_limit'] = data_set[field]>creep_limit

    t,s = get_time_stress_curves_int(spatialdata,creep_limit)
    spatialdata.data_sets[-1]['time_to_limit'] = t
    spatialdata.data_sets[-1]['stress_at_limit'] = s


# %%
update_exceeded(test_data,1e-3)
# %%
