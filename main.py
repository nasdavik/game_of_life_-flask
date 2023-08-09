from flask import Flask, render_template
import random
from threading import Lock
import copy


app: Flask = Flask(__name__)


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances or args or kwargs:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class GameOfLife(metaclass=SingletonMeta):
    def __init__(self, width=20, height=20):
        self.__width = width
        self.__height = height
        self.counter = 0
        self.world = self.generate_universe()
        self.old_world = self.world

    def form_new_generation(self):
        universe = self.world
        new_world = [[0 for _ in range(self.__width)] for _ in range(self.__height)]

        for i in range(len(universe)):
            for j in range(len(universe[0])):

                if universe[i][j]:
                    if self.__get_near(universe, [i, j]) not in (2, 3):
                        new_world[i][j] = 0
                    else:
                        new_world[i][j] = 1

                else:
                    if self.__get_near(universe, [i, j]) == 3:
                        new_world[i][j] = 1
                    else:
                        new_world[i][j] = 0

        self.old_world = copy.deepcopy(self.world)
        self.world = new_world

    def generate_universe(self):
        return [[random.randint(0, 1) for _ in range(self.__width)] for _ in range(self.__height)]

    @staticmethod
    def __get_near(universe, pos, system=None):
        if system is None:
            system = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        count = 0
        for i in system:
            if universe[(pos[0] + i[0]) % len(universe)][(pos[1] + i[1]) % len(universe[0])]:
                count += 1
        return count

    def next_page(self):
        self.counter += 1


@app.route('/')
def index():
    GameOfLife(25, 25)
    return render_template('index.html')


@app.route('/live')
def live():
    live_world = GameOfLife()
    live_world.form_new_generation()
    live_world.next_page()
    return render_template('live.html',
                           live_world=live_world.world,
                           counter=live_world.counter,
                           old_world=live_world.old_world)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
