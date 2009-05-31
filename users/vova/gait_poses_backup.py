        

#BALANCE ON ONE LEG -- KIND OF IDEAL -- SLOW!!!

        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96], [steptime* 0.1]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395], [steptime*0.1]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62], [steptime*0.1]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1], [steptime*0.1, steptime * 0.4, steptime*0.5]),
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96], [steptime*0.1]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395], [steptime*0.1]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62], [steptime*0.1]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28], [steptime*0.1, steptime * 0.5])

#same /2
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96], [steptime* 0.05]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395], [steptime*0.05]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62], [steptime*0.05]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1], [steptime*0.05, steptime * 0.2, steptime*0.25]),
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96], [steptime*0.05]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395], [steptime*0.05]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62], [steptime*0.05]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28], [steptime*0.05, steptime * 0.25])

#same, baseline 
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96], [steptime* 0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1], [steptime*0.05, steptime * 0.2, steptime*0.25]),
        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395], [steptime*0.05, steptime*0.25]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62], [steptime*0.05, steptime*0.25]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28], [steptime*0.05, steptime * 0.25])

# BALANCE ON THE LEG -- FASTER

        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96], [steptime* 0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0, -0.18], [steptime* 0.05, steptime*0.15, steptime*0.25]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1], [steptime*0.05, steptime * 0.2, steptime*0.25]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96], [steptime*0.05, steptime*0.25]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395], [steptime*0.05, steptime*0.25]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62], [steptime*0.05, steptime*0.25]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28], [steptime*0.05, steptime * 0.25]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0, -0.18], [steptime* 0.05, steptime*0.15, steptime*0.25])


#left leg forward
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.4], [steptime* 0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.395], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, -0.2], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28], [steptime*0.05, steptime * 0.25, steptime*0.4]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4])


#step - stable on raul
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.2], [steptime* 0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.7], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.3], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4])

#baseline
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.2, -1.2], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.7,0.7], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.3, 0.3], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])


#smaller - nicer
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.1], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.7,0.7], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.20, 0.3], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])

#smaller step - easier to move on

        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.05, -1.05], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.95,0.95], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.00, 0.1], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])

#from double support to single support - first attempt
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.05, -1.05, -0.96], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.95,0.95, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.00, 0.1, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.2, -0.2, 0.0, 0.28], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0, 0.38], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])


# no good
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.05, -1.05, -1.05, -0.96], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0, 0.0, 0.28], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0 ]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.95,0.95,0.95, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.05, 0.1, 0.1, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.2, -0.2, 0.0, 0.28], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96,-0.96 -1.05], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395, 1.395, 1.095], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6,steptime*0.75,steptime*1.0 ]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62, 0.05, 0.1], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6,steptime*0.75,steptime*1.0]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0, 0.38, -0.2], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.28], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75,steptime*1.0])


        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.0, -1.0], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,0.8,0.8], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.10, 0.2], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.96], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.295, 1.295], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])






#attempt to move better COM (double support)
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.1], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.05,1.05], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, 0.0, -0.2], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, -0.1, 0.0], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.86], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.82], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.28, 0.0], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])


#to single support
        (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.45], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.05,1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, -0.1, -0.3], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, 0.0, 0.28], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.86], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.86], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.18, 0.38], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])





#swing
       (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.45, -0.96], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.05,1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, -0.1, -0.3, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, 0.0, 0.28], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.86, -1.1], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.86], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.18, 0.38], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6])






#swing baseline
       (PREFIX_JOINTS +"LHipPitch" + A_V , [-0.96, -0.96, -1.1, -1.45, -0.96], [steptime* 0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LHipRoll" + A_V , [0.0, 0.0, 0.0,0.0,0.0,0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LKneePitch" + A_V , [1.395,1.395,1.05,1.395,1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LAnklePitch" + A_V , [-0.62,-0.62, -0.1, -0.3, -0.62], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"LAnkleRoll" + A_V , [0, -0.38, -0.1, 0.0, 0.28, 0.28], [steptime*0.05, steptime * 0.2, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),

        (PREFIX_JOINTS +"RHipPitch" + A_V , [-0.96, -0.96,-0.96,-0.86, -1.1], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"RKneePitch" + A_V , [1.395,1.395, 1.395, 1.395, 1.395], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]), 
        (PREFIX_JOINTS +"RAnklePitch" + A_V , [-0.62,-0.62, -0.62, -0.86, -0.86], [steptime*0.05, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75]), 
        (PREFIX_JOINTS +"RAnkleRoll" + A_V , [0, -0.28, -0.18, 0.38, 0.1], [steptime*0.05, steptime * 0.25, steptime*0.4, steptime*0.6, steptime*0.75]),
        (PREFIX_JOINTS +"RHipRoll" + A_V , [0.0, 0.0,0.0, 0.0, 0.0], [steptime* 0.05, steptime*0.15, steptime*0.25, steptime*0.4, steptime*0.6, steptime*0.75, 0.0])


# next double support
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



