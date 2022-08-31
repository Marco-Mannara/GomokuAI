from time import time
from experiment import Experiment

ai_sd2_v2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 2,
        'version' : 2
    }
}
ai_sd4_v2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 4,
        'version' : 2
    }
}

ai_sd2 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 2
    }
}
ai_sd3 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 3
    }
}
ai_sd4 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 4
    }
}

players_ft = {
    #'sd2' : ai_sd2,
    # 'sd2v2' : ai_sd2_v2,
    'sd4v2' : ai_sd4_v2,
    #'sd3' : ai_sd3,
    #'sd4' : ai_sd4
    }

start_time = time()
experiment_sd_var = Experiment('v2-test', players_ft, repetitions=1)
experiment_sd_var.run()
print('Experiment took %f to run.' % (round(time() - start_time,3)))



