init:
    #словарь, через который будет передаваться инфо о префиксах стиля
    #каждой текстовой кнопки
    default persistent.buttons = {}
    default persistent.victim_set = set()
    
python early:



    class Stalker(renpy.Displayable):
        '''Удаляет состояние кнопки из списка, если она неактивна.
        (список нужен, тк каждое нажатие кнопки вызывает функцию restart interaction,
        которая перерисовывает все, вследствие чего кнопка не помнит, что была нажата)'''

        def __init__(self):
            super().__init__(self)         
            self.alive_set = set()

            self.first_time = True


        def render(self, width, height, st, at):
            return renpy.Render(width, height)


        def per_interact(self):

            if self.first_time:
                self.first_time = False
                return

            deadset = set()

            # если кнопка не вызвала im_here за время всей предыдущей интеракции, т.е. за все время до того,
            # как вызвалась restart_interaction или ui.interact (а только две эти функции начнут новую интеракцию), то кнопка не активна.
            for victim in persistent.victim_set:
                if not victim in self.alive_set:
                    deadset.add(victim)
            
            persistent.victim_set = persistent.victim_set.difference(deadset)
            self.alive_set = set()



        def im_here(self, tag):
            self.alive_set.add(tag)

        def hello(self, tag):
            persistent.victim_set.add(tag)
            self.im_here(tag)


    stalker = Stalker()





    def hello_stalker(tag):
        if not renpy.showing("stalker"):
            renpy.show("stalker", what=stalker)

        stalker.hello(tag)
