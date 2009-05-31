# constants file to store doMove sequences
from burst.consts import DEG_TO_RAD
from numpy import array
# List and order of the devices
#HeadYaw HeadPitch	LShoulderPitch	LShoulderRoll LElbowYaw	LElbowRoll	LWristYaw	LHand	LHipYawPitch	LHipRoll	LHipPitch	LKneePitch	LAnklePitch	LAnkleRoll	RHipRoll	RHipPitch	RKneePitch	RAnklePitch	RAnkleRoll	RShoulderPitch	RShoulderRoll	RElbowYaw	RElbowRoll	RWristYaw	RHand	

#utility
ALLJOINTSONES = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
ALLJOINTSNAMES = ['HeadYaw', 'HeadPitch', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw', 'LHand', 'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw', 'RHand']

#Initial pose
INITIALPOSJOINTVALUES=(((1.75, 0.26, -1.57, -0.52),
    (0.0, -0.04, -0.58, 1.03, -0.51, 0.04), 
    (0, 0.04, -0.58, 1.03, -0.51, -0.04),
    (1.75, -0.26, 1.57, 0.52), 2.0),)
RIGHT_FOOT = "R"
LEFT_FOOT = "L"
STEP_PARAM=64.0/5184


A_V = "/Position/Actuator/Value"
PREFIX_JOINTS="Device/SubDeviceList/"

MOVEMENT_JOINTS_LEFT=[PREFIX_JOINTS + "LShoulderPitch" + A_V , PREFIX_JOINTS +"LElbowRoll" + A_V ,
        PREFIX_JOINTS +"LHipRoll" + A_V , PREFIX_JOINTS +"LHipPitch" + A_V ,
        PREFIX_JOINTS +"LKneePitch" + A_V , PREFIX_JOINTS +"LAnklePitch" + A_V, 
        PREFIX_JOINTS +"LAnkleRoll" + A_V , PREFIX_JOINTS +"RHipRoll" + A_V , 
        PREFIX_JOINTS +"RHipPitch" + A_V , PREFIX_JOINTS +"RKneePitch" + A_V , 
        PREFIX_JOINTS +"RAnklePitch" + A_V , PREFIX_JOINTS +"RAnkleRoll" + A_V , 
        PREFIX_JOINTS +"RShoulderPitch" + A_V , PREFIX_JOINTS +"RElbowRoll" + A_V ]

MOVEMENT_JOINTS_RIGHT=[PREFIX_JOINTS + "RShoulderPitch" + A_V , PREFIX_JOINTS +"RElbowRoll" + A_V ,
        PREFIX_JOINTS +"RHipRoll" + A_V , PREFIX_JOINTS +"RHipPitch" + A_V ,
        PREFIX_JOINTS +"RKneePitch" + A_V , PREFIX_JOINTS +"RAnklePitch" + A_V, 
        PREFIX_JOINTS +"RAnkleRoll" + A_V , PREFIX_JOINTS +"LHipRoll" + A_V , 
        PREFIX_JOINTS +"LHipPitch" + A_V , PREFIX_JOINTS +"LKneePitch" + A_V , 
        PREFIX_JOINTS +"LAnklePitch" + A_V , PREFIX_JOINTS +"LAnkleRoll" + A_V , 
        PREFIX_JOINTS +"LShoulderPitch" + A_V , PREFIX_JOINTS +"LElbowRoll" + A_V ]

def gait_attempt_generate(steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)

    #first attempt to generate some DCM gait 
    for jointcode, angle, time in [

       (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.45, -0.96,-0.86], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9 ]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0,0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.05,1.395,1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, -0.1, -0.3, -0.62, -0.82], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, 0.0, 0.28, 0.28, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.86, -1.1, -1.1], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395, 1.395,1.05], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.86, -0.86, -0.2], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.18, 0.38, 0.1, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, steptime*0.9])










        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times


def short_walk_init_pose(steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)

    a = array


    #balance on right leg

    for jointcode, angle, time in [

        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times


def recorded_movement(steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)


    for jointcode, angle, time in [
        (PREFIX_JOINTS + "LShoulderPitch" + A_V , [1.745362, 1.483528, 2.007101, 1.483528, 2.006526, 1.48372, 2.007101, 1.483815, 2.006814, 1.483624, 2.007005, 1.745362]
, [steptime * 0.00001, steptime*0.147692307692308, steptime*0.292307692307693, steptime*0.390769230769232, steptime*0.470769230769232, steptime*0.544615384615386, steptime*0.621538461538463, steptime*0.695384615384617, steptime*0.775384615384618, steptime*0.849230769230772, steptime*0.923076923076926,steptime*1]
),
        (PREFIX_JOINTS +"LElbowRoll" + A_V , [-0.523627, -0.69812, -0.349039, -0.69812, -0.349422, -0.698024, -0.349039, -0.697928, -0.349231, -0.698024, -0.349135, -0.523627]
, [steptime * 0.00001, steptime*0.150769230769231, steptime*0.292307692307693, steptime*0.390769230769232, steptime*0.470769230769232, steptime*0.544615384615386, steptime*0.621538461538463, steptime*0.695384615384617, steptime*0.775384615384618, steptime*0.849230769230772, steptime*0.923076923076926,steptime*1]
),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [-5.4511E-02, -0.376939, 0.388048, -0.303211, -0.27905, -0.294965, 0.378556, -0.293336, 0.380762, -0.260163, -0.257766, -0.29324, -0.255465, -0.258437, 0.381241, -0.259779, -0.258821, -0.29324, -0.257095, -0.258245, 0.384117, -3.4952E-02]
, [steptime * 0.00001, steptime*0.104615384615385, steptime*0.246153846153847, steptime*0.338461538461539, steptime*0.347692307692308, steptime*0.366153846153847, steptime*0.443076923076924, steptime*0.520000000000001, steptime*0.593846153846155, steptime*0.649230769230771, steptime*0.652307692307694, steptime*0.673846153846156, steptime*0.689230769230771, steptime*0.692307692307694, steptime*0.74769230769231, steptime*0.803076923076926, steptime*0.806153846153849, steptime*0.824615384615387, steptime*0.843076923076926, steptime*0.846153846153849, steptime*0.901538461538464,steptime*1]
),
        (PREFIX_JOINTS +"LHipPitch" + A_V ,[-0.577701, -0.434751, -0.574729, 0.305979, -1.098302, -0.746728, -0.777217, -0.334274, -0.534269, 8.0385E-02, -1.080086, -0.767246, -0.770697, -0.368981, -0.535995, 7.8468E-02, -1.085934, -0.765999, -0.770122, -0.368214, -0.53542, 8.5083E-02, -1.083154, -0.766766, -0.76715, -0.36994, -0.53657, 8.3933E-02, -0.65536, -0.420849, -0.57818]
, [steptime * 0.00001, steptime*5.84615384615384E-02, steptime*0.107692307692308, steptime*0.203076923076923, steptime*0.258461538461539, steptime*0.292307692307693, steptime*0.304615384615385, steptime*0.347692307692308, steptime*0.375384615384616, steptime*0.418461538461539, steptime*0.452307692307693, steptime*0.470769230769232, steptime*0.473846153846155, steptime*0.501538461538463, steptime*0.529230769230771, steptime*0.575384615384617, steptime*0.603076923076925, steptime*0.621538461538463, steptime*0.627692307692309, steptime*0.655384615384617, steptime*0.680000000000002, steptime*0.726153846153848, steptime*0.756923076923079, steptime*0.775384615384618, steptime*0.778461538461541, steptime*0.806153846153849, steptime*0.830769230769233, steptime*0.87692307692308, steptime*0.907692307692311, steptime*0.926153846153849,steptime*1]
),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.02956, 0.778271, 1.005112, 0.837043, 0.952093, 0.166972, 1.677675, 0.689779, 0.994278, 0.754111, 0.972322, 0.88987, 0.957174, 0.509054, 1.655528, 0.808184, 1.004249, 0.779614, 0.972226, 0.890445, 0.959763, 0.517491, 1.677387, 0.813266, 0.996866, 0.778847, 0.973856, 0.891883, 0.957558, 0.507041, 1.679305, 0.808664, 1.003578, 0.780285, 0.973089, 0.890349, 0.96005, 0.524778, 1.563775, 0.871366, 1.032915, 1.032436]
, [steptime * 0.00001, steptime*5.84615384615384E-02, steptime*0.107692307692308, steptime*0.144615384615385, steptime*0.166153846153846, steptime*0.203076923076923, steptime*0.24923076923077, steptime*0.292307692307693, steptime*0.316923076923078, steptime*0.347692307692308, steptime*0.372307692307693, steptime*0.390769230769232, steptime*0.400000000000001, steptime*0.418461538461539, steptime*0.446153846153847, steptime*0.467692307692309, steptime*0.483076923076924, steptime*0.501538461538463, steptime*0.529230769230771, steptime*0.541538461538463, steptime*0.553846153846155, steptime*0.572307692307694, steptime*0.596923076923079, steptime*0.621538461538463, steptime*0.633846153846156, steptime*0.655384615384617, steptime*0.680000000000002, steptime*0.692307692307694, steptime*0.704615384615387, steptime*0.726153846153848, steptime*0.74769230769231, steptime*0.772307692307695, steptime*0.784615384615387, steptime*0.806153846153849, steptime*0.830769230769233, steptime*0.846153846153849, steptime*0.858461538461541, steptime*0.87692307692308, steptime*0.901538461538464, steptime*0.926153846153849, steptime*0.993846153846157,steptime*1]
),
        (PREFIX_JOINTS +"LAnklePitch" + A_V ,[-0.514028, -0.409524, -0.493798, -0.451038, -0.716708, -0.53723, -1.011044, -1.097E-03, -0.488429, -0.481334, -0.504632, -0.486895, -0.711818, -0.652951, -1.002223, -0.100519, -0.476157, -0.475965, -0.503194, -0.486895, -0.713735, -0.652855, -1.003757, -9.8122E-02, -0.503194, -0.487375, -0.71316, -0.655731, -1.000594, -9.793E-02, -0.503002, -0.486703, -0.714023, -0.654101, -1.09062, -0.514891, -0.537326, -0.516329]
, [steptime * 0.00001, steptime*5.84615384615384E-02, steptime*0.107692307692308, steptime*0.138461538461538, steptime*0.178461538461539, steptime*0.203076923076923, steptime*0.230769230769231, steptime*0.28923076923077, steptime*0.341538461538462, steptime*0.350769230769231, steptime*0.36923076923077, steptime*0.384615384615385, steptime*0.40923076923077, steptime*0.418461538461539, steptime*0.436923076923078, steptime*0.467692307692309, steptime*0.49846153846154, steptime*0.501538461538463, steptime*0.526153846153848, steptime*0.53846153846154, steptime*0.563076923076925, steptime*0.572307692307694, steptime*0.587692307692309, steptime*0.61846153846154, steptime*0.676923076923079, steptime*0.689230769230771, steptime*0.713846153846156, steptime*0.726153846153848, steptime*0.738461538461541, steptime*0.772307692307695, steptime*0.82769230769231, steptime*0.840000000000003, steptime*0.86769230769231, steptime*0.873846153846156, steptime*0.895384615384618, steptime*0.926153846153849, steptime*0.963076923076926,steptime*1]
),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [5.4595E-02, 0.376255, -0.283077, -6.9851E-02, -0.375692, 0.372804, -0.249137, -6.9851E-02, -0.356901, 0.371174, -0.244056, -6.9851E-02, -0.36668, 0.371078, -0.249712, -6.9851E-02, -0.359489, 0.371078, -0.241371, -6.1126E-02, -0.304936, 3.5036E-02]
, [steptime * 0.00001, steptime*0.104615384615385, steptime*0.206153846153846, steptime*0.236923076923077, steptime*0.252307692307693, steptime*0.366153846153847, steptime*0.421538461538463, steptime*0.440000000000001, steptime*0.44923076923077, steptime*0.520000000000001, steptime*0.575384615384617, steptime*0.590769230769232, steptime*0.600000000000002, steptime*0.673846153846156, steptime*0.729230769230771, steptime*0.741538461538464, steptime*0.753846153846156, steptime*0.824615384615387, steptime*0.87692307692308, steptime*0.895384615384618, steptime*0.91692307692308,steptime*1]
),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [3.2448E-02, -0.388444, 0.300994, 0.281819, 0.298213, 0.279997, 0.296392, -0.383458, 0.259576, 0.259384, 0.292557, 0.257562, 0.258042, -0.381349, 0.259959, 0.25785, 0.293036, 0.256412, 0.258329, -0.380486, 0.259671, 0.258904, 0.293228, -0.381253, 0.260151, 0.25785, 0.296487, 0.285078, 0.345575, 5.2006E-02]
, [steptime * 0.00001, steptime*0.101538461538461, steptime*0.2, steptime*0.209230769230769, steptime*0.246153846153847, steptime*0.28, steptime*0.292307692307693, steptime*0.366153846153847, steptime*0.421538461538463, steptime*0.424615384615386, steptime*0.443076923076924, steptime*0.461538461538463, steptime*0.464615384615386, steptime*0.520000000000001, steptime*0.575384615384617, steptime*0.57846153846154, steptime*0.593846153846155, steptime*0.615384615384617, steptime*0.61846153846154, steptime*0.673846153846156, steptime*0.726153846153848, steptime*0.729230769230771, steptime*0.74769230769231, steptime*0.824615384615387, steptime*0.87692307692308, steptime*0.880000000000003, steptime*0.901538461538464, steptime*0.920000000000003, steptime*0.929230769230772,steptime*1]
), 
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.579606, -0.580949, -0.505591, -1.208163, -0.748442, -0.778163, -0.326113, -0.536942, 0.280392, -1.078252, -0.369161, -0.535024, 8.1835E-02, -1.084772, -0.766179, -0.770398, -0.368969, -0.536271, 8.4999E-02, -1.083046, -0.768097, -0.770877, -0.371941, -0.535983, 7.8192E-02, -1.086114, -0.765987, -0.77011, -0.365517, -0.435027, -0.353341, -0.57673]
,[steptime * 0.00001, steptime*1.53846153846154E-02, steptime*5.53846153846154E-02, steptime*0.107692307692308, steptime*0.147692307692308, steptime*0.16, steptime*0.206153846153846, steptime*0.258461538461539, steptime*0.344615384615385, steptime*0.375384615384616, steptime*0.427692307692309, steptime*0.452307692307693, steptime*0.495384615384617, steptime*0.529230769230771, steptime*0.544615384615386, steptime*0.547692307692309, steptime*0.581538461538463, steptime*0.603076923076925, steptime*0.649230769230771, steptime*0.680000000000002, steptime*0.69846153846154, steptime*0.701538461538464, steptime*0.732307692307694, steptime*0.756923076923079, steptime*0.800000000000002, steptime*0.830769230769233, steptime*0.849230769230772, steptime*0.852307692307695, steptime*0.883076923076926, steptime*0.904615384615387, steptime*0.926153846153849, steptime*1]
),
        (PREFIX_JOINTS +"RKneePitch" + A_V ,[1.032807, 1.034533, 0.899062, 1.653119, 0.68689, 0.996854, 0.738855, 0.965599, 0.83751, 0.948917, 0.217391, 1.678334, 0.808556, 1.003853, 0.780081, 0.973269, 0.891967, 0.958025, 0.508371, 1.674786, 0.813637, 1.001648, 0.779985, 0.973749, 0.890625, 0.959559, 0.516329, 1.681018, 0.807022, 1.005004, 0.783628, 0.972982, 0.891104, 0.959367, 0.510864, 1.672102, 0.816705, 1.002415, 0.778451, 0.876339, 0.750647, 1.03089]
, [steptime * 0.00001, steptime*1.23076923076923E-02, steptime*5.53846153846154E-02, steptime*9.84615384615384E-02, steptime*0.147692307692308, steptime*0.175384615384616, steptime*0.209230769230769, steptime*0.255384615384616, steptime*0.28923076923077, steptime*0.307692307692308, steptime*0.344615384615385, steptime*0.366153846153847, steptime*0.390769230769232, steptime*0.403076923076924, steptime*0.424615384615386, steptime*0.44923076923077, steptime*0.467692307692309, steptime*0.480000000000001, steptime*0.495384615384617, steptime*0.520000000000001, steptime*0.541538461538463, steptime*0.556923076923078, steptime*0.581538461538463, steptime*0.603076923076925, steptime*0.61846153846154, steptime*0.630769230769233, steptime*0.649230769230771, steptime*0.673846153846156, steptime*0.695384615384617, steptime*0.710769230769233, steptime*0.732307692307694, steptime*0.753846153846156, steptime*0.772307692307695, steptime*0.781538461538464, steptime*0.800000000000002, steptime*0.824615384615387, steptime*0.846153846153849, steptime*0.864615384615387, steptime*0.883076923076926, steptime*0.904615384615387, steptime*0.923076923076926, steptime*1]
), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.51519, -0.515766, -0.457953, -0.649511, -2.451E-03, -0.485373, -0.482785, -0.485469, -0.474923, -0.496591, -0.451338, -0.714802, -0.562073, -1.016521, -9.9572E-02, -0.476169, -0.476073, -0.50311, -0.487291, -0.711926, -0.653826, -0.999743, -9.7559E-02, -0.503302, -0.487099, -0.714131, -0.656606, -1.004057, -0.101681, -0.502918, -0.486811, -0.713364, -0.652579, -1.001468, -9.6984E-02, -0.505795, -0.462843, -0.521806, -0.515382]
, [steptime * 0.00001, steptime*1.23076923076923E-02, steptime*5.53846153846154E-02, steptime*8.61538461538461E-02, steptime*0.144615384615385, steptime*0.196923076923077, steptime*0.2, steptime*0.203076923076923, steptime*0.215384615384616, steptime*0.24923076923077, steptime*0.283076923076924, steptime*0.323076923076924, steptime*0.344615384615385, steptime*0.356923076923078, steptime*0.390769230769232, steptime*0.421538461538463, steptime*0.424615384615386, steptime*0.446153846153847, steptime*0.461538461538463, steptime*0.489230769230771, steptime*0.495384615384617, steptime*0.513846153846155, steptime*0.541538461538463, steptime*0.600000000000002, steptime*0.612307692307694, steptime*0.636923076923079, steptime*0.646153846153848, steptime*0.664615384615387, steptime*0.692307692307694, steptime*0.753846153846156, steptime*0.766153846153848, steptime*0.790769230769233, steptime*0.800000000000002, steptime*0.818461538461541, steptime*0.846153846153849, steptime*0.901538461538464, steptime*0.923076923076926, steptime*0.975384615384618,steptime*1]
),
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [-3.246E-02, 0.38776, -0.376076, 0.277504, 6.9839E-02, 0.359381, -0.370419, 0.250851, 6.9839E-02, 0.362162, -0.370898, 0.237333, 6.9839E-02, 0.354108, -0.37109, 0.248071, 6.9839E-02, 0.364175, -0.37435, -5.2114E-02]
, [steptime * 0.00001, steptime*0.101538461538461, steptime*0.246153846153847, steptime*0.347692307692308, steptime*0.360000000000001, steptime*0.372307692307693, steptime*0.443076923076924, steptime*0.49846153846154, steptime*0.513846153846155, steptime*0.526153846153848, steptime*0.593846153846155, steptime*0.649230769230771, steptime*0.66769230769231, steptime*0.680000000000002, steptime*0.74769230769231, steptime*0.803076923076926, steptime*0.821538461538464, steptime*0.82769230769231, steptime*0.901538461538464,steptime*1]
),
        (PREFIX_JOINTS +"RShoulderPitch" + A_V , [1.74535, 1.74535, 2.007089, 1.483516, 2.007089, 1.484187, 2.006993, 1.483612, 2.006897, 1.483899, 2.006993, 1.483708, 1.74535]
,[steptime * 0.00001, steptime*6.15384615384615E-03, steptime*0.150769230769231, steptime*0.292307692307693, steptime*0.390769230769232, steptime*0.470769230769232, steptime*0.544615384615386, steptime*0.621538461538463, steptime*0.695384615384617, steptime*0.775384615384618, steptime*0.849230769230772, steptime*0.923076923076926,steptime*1]
),
        (PREFIX_JOINTS +"RElbowRoll" + A_V , [0.523615, 0.349123, 0.698108, 0.349027, 0.697724, 0.349123, 0.698108, 0.349219, 0.697916, 0.349123, 0.698012, 0.523615]
, [steptime * 0.00001, steptime*0.150769230769231, steptime*0.292307692307693, steptime*0.390769230769232, steptime*0.470769230769232, steptime*0.544615384615386, steptime*0.621538461538463, steptime*0.695384615384617, steptime*0.775384615384618, steptime*0.849230769230772, steptime*0.923076923076926,steptime*1]
)
        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times


def recorded_movement_2(steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)


    for jointcode, angle, time in [
        (PREFIX_JOINTS + "LShoulderPitch" + A_V , [1.744595, 1.483528, 2.007101, 1.483528, 2.007005, 1.483624, 2.007101, 1.483528, 1.745362]
, [steptime * 0.00001, steptime*0.183080808080808, steptime*0.371212121212121, steptime*0.5, steptime*0.601010101010101, steptime*0.69949494949495, steptime*0.799242424242424, steptime*0.898989898989899,steptime*1]
),
        (PREFIX_JOINTS +"LElbowRoll" + A_V , [-0.524107, -0.69812, -0.349039, -0.69812, -0.349135, -0.698024, -0.349039, -0.69812, -0.523627]
, [steptime * 0.00001, steptime*0.184343434343434, steptime*0.371212121212121, steptime*0.5, steptime*0.601010101010101, steptime*0.69949494949495, steptime*0.799242424242424, steptime*0.898989898989899,steptime*1]
),
        (PREFIX_JOINTS +"LHipRoll" + A_V, [-7.3015E-02, -0.376939, 0.388048, -0.303211, -0.274544, -0.295157, -0.255944, -0.258533, 0.381241, -0.260067, -0.257862, -0.293336, -0.256328, -0.258437, 0.381241, -0.260355, -0.257766, -0.296691, -0.283365, -0.346546, -5.2018E-02, -5.2114E-02], [steptime * 0.00001, steptime*0.125, steptime*0.309343434343434, steptime*0.429292929292929, steptime*0.444444444444444, steptime*0.467171717171717, steptime*0.492424242424242, steptime*0.496212121212121, steptime*0.566919191919192, steptime*0.638888888888889, steptime*0.642676767676768, steptime*0.666666666666667, steptime*0.690656565656566, steptime*0.695707070707071, steptime*0.766414141414141, steptime*0.837121212121212, steptime*0.840909090909091, steptime*0.869949494949495, steptime*0.890151515151515, steptime*0.906565656565657, steptime*0.998737373737374,steptime*1]
),
        (PREFIX_JOINTS +"LHipPitch" + A_V, [-0.575304, -0.433792, -0.574825, 0.30665, -1.098206, -0.74692, -0.777408, -0.334082, -0.533886, 7.5591E-02, -1.08277, -0.764849, -0.769259, -0.369077, -0.535516, 7.5016E-02, -1.083825, -0.764561, -0.769259, -0.366105, -0.435902, -0.352107, -0.576934, -0.576359], [steptime * 0.00001, steptime*6.56565656565657E-02, steptime*0.128787878787879, steptime*0.252525252525253, steptime*0.328282828282828, steptime*0.369949494949495, steptime*0.387626262626263, steptime*0.443181818181818, steptime*0.478535353535354, steptime*0.537878787878788, steptime*0.577020202020202, steptime*0.601010101010101, steptime*0.606060606060606, steptime*0.64520202020202, steptime*0.676767676767677, steptime*0.737373737373737, steptime*0.776515151515151, steptime*0.799242424242424, steptime*0.805555555555556, steptime*0.845959595959596, steptime*0.873737373737374, steptime*0.900252525252525, steptime*0.998737373737374,steptime*1]
),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.025437, 0.776641, 1.005112, 0.836563, 0.952189, 0.166397, 1.679209, 0.687382, 0.994374, 0.752097, 0.972514, 0.888719, 0.959092, 0.52008, 1.680263, 0.812978, 1.005207, 0.778942, 0.973089, 0.890253, 0.960434, 0.519313, 1.680934, 0.812115, 1.005687, 0.777984, 0.876543, 0.749509, 1.031094, 1.029847]
, [steptime * 0.00001, steptime*6.56565656565657E-02, steptime*0.128787878787879, steptime*0.178030303030303, steptime*0.207070707070707, steptime*0.252525252525253, steptime*0.311868686868687, steptime*0.368686868686869, steptime*0.404040404040404, steptime*0.443181818181818, steptime*0.477272727272727, steptime*0.497474747474747, steptime*0.512626262626263, steptime*0.536616161616162, steptime*0.568181818181818, steptime*0.598484848484849, steptime*0.617424242424242, steptime*0.64520202020202, steptime*0.67550505050505, steptime*0.695707070707071, steptime*0.712121212121212, steptime*0.736111111111111, steptime*0.767676767676768, steptime*0.797979797979798, steptime*0.816919191919192, steptime*0.84469696969697, steptime*0.871212121212121, steptime*0.900252525252525, steptime*0.997474747474748,steptime*1]
),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.512398, -0.408853, -0.493894, -0.45075, -0.716899, -0.536846, -1.011811, -1.097E-03, -0.488046, -0.485169, -0.48747, -0.481047, -0.504824, -0.486991, -0.712297, -0.654964, -1.002319, -0.10397, -0.473185, -0.472418, -0.475198, -0.475103, -0.503386, -0.486991, -0.713256, -0.654005, -1.002223, -0.103779, -0.47376, -0.471363, -0.505878, -0.462926, -0.521985, -0.515562]
, [steptime * 0.00001, steptime*6.56565656565657E-02, steptime*0.128787878787879, steptime*0.170454545454545, steptime*0.223484848484848, steptime*0.251262626262626, steptime*0.291666666666667, steptime*0.366161616161616, steptime*0.433080808080808, steptime*0.435606060606061, steptime*0.439393939393939, steptime*0.448232323232323, steptime*0.473484848484849, steptime*0.48989898989899, steptime*0.523989898989899, steptime*0.535353535353535, steptime*0.558080808080808, steptime*0.597222222222222, steptime*0.632575757575758, steptime*0.633838383838384, steptime*0.641414141414141, steptime*0.643939393939394, steptime*0.672979797979798, steptime*0.689393939393939, steptime*0.722222222222222, steptime*0.734848484848485, steptime*0.756313131313131, steptime*0.795454545454545, steptime*0.832070707070707, steptime*0.833333333333333, steptime*0.868686868686869, steptime*0.897727272727273, steptime*0.968434343434343,steptime*1]
),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [7.3099E-02, 0.376255, -0.286049, -6.9851E-02, -0.377706, 0.372996, -0.249904, -6.9851E-02, -0.367639, 0.371174, -0.252205, -6.9851E-02, -0.365913, 0.37453, 5.2102E-02, 5.2198E-02]
, [steptime * 0.00001, steptime*0.123737373737374, steptime*0.261363636363636, steptime*0.30050505050505, steptime*0.319444444444444, steptime*0.467171717171717, steptime*0.54040404040404, steptime*0.561868686868687, steptime*0.573232323232323, steptime*0.666666666666667, steptime*0.73989898989899, steptime*0.761363636363636, steptime*0.772727272727273, steptime*0.869949494949495, steptime*0.998737373737374,steptime*1]
),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [1.3944E-02, -0.388539, 0.300994, 0.28038, 0.298213, 0.280189, 0.296392, -0.383842, 0.260055, 0.257658, 0.293228, 0.256028, 0.258329, -0.381349, 0.260055, 0.257658, 0.293228, 0.255357, 0.258329, -0.385184, 3.4845E-02]
, [steptime * 0.00001, steptime*0.121212121212121, steptime*0.248737373737374, steptime*0.265151515151515, steptime*0.311868686868687, steptime*0.35479797979798, steptime*0.369949494949495, steptime*0.467171717171717, steptime*0.539141414141414, steptime*0.542929292929293, steptime*0.566919191919192, steptime*0.592171717171717, steptime*0.595959595959596, steptime*0.666666666666667, steptime*0.737373737373737, steptime*0.741161616161616, steptime*0.766414141414141, steptime*0.79040404040404, steptime*0.795454545454545, steptime*0.866161616161616,steptime*1]
), 
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.580757, -0.58114, -0.505207, -1.211327, -0.746716, -0.778259, -0.326017, -0.536846, 0.282118, -1.077677, -0.764453, -0.768959, -0.369065, -0.535408, 7.5316E-02, -1.083334, -0.764933, -0.769247, -0.369161, -0.535791, 7.685E-02, -0.65832, -0.420262, -0.577976]
, [steptime * 0.00001, steptime*6.31313131313131E-03, steptime*6.06060606060606E-02, steptime*0.130050505050505, steptime*0.181818181818182, steptime*0.19949494949495, steptime*0.261363636363636, steptime*0.328282828282828, steptime*0.436868686868687, steptime*0.478535353535354, steptime*0.501262626262626, steptime*0.506313131313131, steptime*0.545454545454545, steptime*0.578282828282828, steptime*0.637626262626263, steptime*0.676767676767677, steptime*0.69949494949495, steptime*0.705808080808081, steptime*0.744949494949495, steptime*0.776515151515151, steptime*0.837121212121212, steptime*0.876262626262626, steptime*0.900252525252525,steptime*1]
),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.034341, 1.034821, 0.89887, 1.654461, 0.686795, 0.997813, 0.738855, 0.965599, 0.837606, 0.950259, 0.207611, 1.679484, 0.81335, 1.0051, 0.779026, 0.973269, 0.890337, 0.960422, 0.519493, 1.680443, 0.812583, 1.005579, 0.779122, 0.973461, 0.890145, 0.960518, 0.517575, 1.56779, 0.870203, 1.032807, 1.032424]
,[steptime * 0.00001, steptime*6.31313131313131E-03, steptime*5.93434343434343E-02, steptime*0.117424242424242, steptime*0.180555555555556, steptime*0.217171717171717, steptime*0.263888888888889, steptime*0.32449494949495, steptime*0.366161616161616, steptime*0.393939393939394, steptime*0.436868686868687, steptime*0.46969696969697, steptime*0.498737373737374, steptime*0.518939393939394, steptime*0.545454545454545, steptime*0.577020202020202, steptime*0.597222222222222, steptime*0.612373737373737, steptime*0.636363636363636, steptime*0.667929292929293, steptime*0.698232323232323, steptime*0.717171717171717, steptime*0.744949494949495, steptime*0.775252525252525, steptime*0.795454545454545, steptime*0.811868686868687, steptime*0.835858585858586, steptime*0.868686868686869, steptime*0.900252525252525, steptime*0.991161616161616,steptime*1]
), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.515766, -0.515766, -0.457857, -0.649799, -9.17E-04, -0.486907, -0.482497, -0.485948, -0.474923, -0.496974, -0.451338, -0.71509, -0.553924, -1.021698, -0.104078, -0.473101, -0.47243, -0.475402, -0.475306, -0.503494, -0.487099, -0.71298, -0.654401, -1.002044, -0.103887, -0.473581, -0.472047, -0.475306, -0.475115, -0.503302, -0.486907, -0.713268, -0.653346, -1.090728, -0.514136, -0.537529, -0.516533]
, [steptime * 0.00001, steptime*6.31313131313131E-03, steptime*5.93434343434343E-02, steptime*9.97474747474748E-02, steptime*0.178030303030303, steptime*0.246212121212121, steptime*0.247474747474747, steptime*0.253787878787879, steptime*0.272727272727273, steptime*0.316919191919192, steptime*0.358585858585859, steptime*0.410353535353535, steptime*0.436868686868687, steptime*0.458333333333333, steptime*0.497474747474747, steptime*0.534090909090909, steptime*0.535353535353535, steptime*0.541666666666667, steptime*0.545454545454545, steptime*0.573232323232323, steptime*0.589646464646465, steptime*0.622474747474748, steptime*0.63510101010101, steptime*0.657828282828283, steptime*0.696969696969697, steptime*0.732323232323232, steptime*0.733585858585859, steptime*0.73989898989899, steptime*0.743686868686869, steptime*0.772727272727273, steptime*0.789141414141414, steptime*0.821969696969697, steptime*0.83459595959596, steptime*0.861111111111111, steptime*0.898989898989899, steptime*0.94949494949495,steptime*1]
),
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [-1.3956E-02, 0.387856, -0.376076, 0.278079, 6.9839E-02, 0.364846, -0.370994, 0.251618, 6.9839E-02, 0.36686, -0.37109, 0.249509, 6.1114E-02, 0.306746, -3.4952E-02]
,  [steptime * 0.00001, steptime*0.121212121212121, steptime*0.311868686868687, steptime*0.441919191919192, steptime*0.463383838383838, steptime*0.474747474747475, steptime*0.568181818181818, steptime*0.640151515151515, steptime*0.661616161616162, steptime*0.672979797979798, steptime*0.766414141414141, steptime*0.839646464646465, steptime*0.861111111111111, steptime*0.886363636363636,steptime*1]
),
        (PREFIX_JOINTS +"RShoulderPitch" + A_V , [1.746117, 2.007089, 1.483516, 2.007089, 1.483612, 2.007089, 1.483516, 2.007089, 1.74535]
,[steptime * 0.00001, steptime*0.184343434343434, steptime*0.369949494949495, steptime*0.5, steptime*0.599747474747475, steptime*0.69949494949495, steptime*0.799242424242424, steptime*0.898989898989899,steptime*1]
),
        (PREFIX_JOINTS +"RElbowRoll" + A_V , [0.523136, 0.349027, 0.698108, 0.349027, 0.698108, 0.349123, 0.698108, 0.349027, 0.523615]
, [steptime * 0.00001, steptime*0.183080808080808, steptime*0.371212121212121, steptime*0.5, steptime*0.599747474747475, steptime*0.69949494949495, steptime*0.799242424242424, steptime*0.898989898989899,steptime*1]
)
        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times





def first_step_generator(steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)


    for jointcode, angle, time in [
        (PREFIX_JOINTS + "LShoulderPitch" + A_V , [1.92], [steptime]),
        (PREFIX_JOINTS +"LElbowRoll" + A_V , [-0.7], [steptime]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.38], [steptime*0.5]),
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.43, -0.58], [steptime * 0.5, steptime]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [0.78, 1.0], [steptime * 0.5,steptime]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.41, -0.51], [steptime * 0.5,steptime]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0.38, 0.1], [steptime*0.9, steptime]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.29], [steptime]), 
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.51,-1.21], [steptime * 0.5, steptime]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [0.90,1.65], [steptime * 0.3, steptime]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.46,-0.65,0.0], [steptime * 0.4 ,steptime * 0.7 ,steptime]),
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0.38],  [steptime]),
        (PREFIX_JOINTS +"RShoulderPitch" + A_V , [2.0],[steptime]),
        (PREFIX_JOINTS +"RElbowRoll" + A_V , [0.35], [steptime])
        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times


def regular_step_generator(foot, steptime):
    jointCodes = list()
    angles = list()
    times = list()

    steptime = float(steptime)
    if foot==LEFT_FOOT:
        swing_foot=LEFT_FOOT
        support_foot=RIGHT_FOOT
    else:
        swing_foot=RIGHT_FOOT
        support_foot=LEFT_FOOT

    for jointcode, angle, time in [
        (PREFIX_JOINTS + swing_foot + "ShoulderPitch" + A_V , [2.01, 1.48], []),
        (PREFIX_JOINTS + swing_foot + "ElbowRoll" + A_V , [-0.35, -0.7], []),
        (PREFIX_JOINTS + swing_foot + "HipRoll" + A_V , [0.38, -0.29], []),
        (PREFIX_JOINTS + swing_foot + "HipPitch" + A_V , [0.1,-1.1, -0.77, -0.37, -0.5 ], []),
        (PREFIX_JOINTS + swing_foot + "KneePitch" + A_V , [0.45, 1.68, 0.79,  1.00, 0.89, 0.98], []),
        (PREFIX_JOINTS + swing_foot + "AnklePitch" + A_V , [-0.72,-0.65, -1.01, -0.07,  -0.5,-0.51  ], []),
        (PREFIX_JOINTS + swing_foot + "AnkleRoll" + A_V , [-0.23, -0.07, -0.35, 0.37], []),
        (PREFIX_JOINTS + support_foot + "HipRoll" + A_V , [0.38, -0.29], []), 
        (PREFIX_JOINTS + support_foot + "HipPitch" + A_V , [], []),
        (PREFIX_JOINTS + support_foot + "KneePitch" + A_V , [], []), 
        (PREFIX_JOINTS + support_foot + "AnklePitch" + A_V , [], []),
        (PREFIX_JOINTS + support_foot + "AnkleRoll" + A_V , [],  []),
        (PREFIX_JOINTS + support_foot + "ShoulderPitch" + A_V , [1.48, 2.01],[]),
        (PREFIX_JOINTS + support_foot + "ElbowRoll" + A_V , [0.7, 0.35], [])
        ]:
        jointCodes.append(jointcode)
        angles.append(angle)
        times.append(time)
    return jointCodes, angles, times


def regular_step_generator(self):   
    #d = {}
    #d = dict()
    #d = dict([(k, v) for k,v in [(1,2),(3,4),(5,6)])
    #for v in d.values():
    #for k in d.keys():
    #for k,v in d.items():
    #d.has_key('x')
    #'x' in d
    #'x' not in d
    a=2


def add_single_step(self, steptime, foot):
    if foot==LEFT_FOOT:
        legvar='L'
    else:
        legvar='R'
    
