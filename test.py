# imports
from .global_imports.smmpl_vis import *
import multiprocessing as mp

# params


# main func
@verbose
def main():

    print('hi')
    c = myclass()
    c.speak()

class myclass:
    def __init__(self):
        pass
    def speak(self):
        print('HelloWorld')

class mainclass:
    def __init__(self):
        pass
    def work(self):
        mp.Process(
            target=main,
            kwargs={'verbboo': True}
        ).start()


# testing
if __name__ == '__main__':
    mc = mainclass()
    mc.work()
