from spaceship_env import Space_Ship_Enviroment
import tensorflow as tf
#tf.config.experimental_run_functions_eagerly(True) # used for debuging and development
tf.compat.v1.disable_eager_execution() # usually using this for fastest performance
# from tensorflow.keras.models import Model, load_model
# from tensorflow.keras.layers import Input, Dense
# from tensorflow.keras.optimizers import Adam, RMSprop, Adagrad, Adadelta
# from tensorflow.keras import backend as Kfrom random import choice
from time import sleep
import numpy as np
from random import choice

def zxc(ZobZ):
    list=[]
    for i in range(env.number_of_bots):
        list.append(choice(['UP','DOWN','LEFT','RIGHT']))
    return list




if __name__ == '__main__':
    env=Space_Ship_Enviroment()

    while env.is_running:
        ZobZ=env.observe()
        env.display()
        step=zxc(ZobZ)
        env.step(step)

        #sleep(0.6)
    print("suck cock")


