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
            self.verified = False



        def render(self, width, height, st, at):
            return renpy.Render(width, height)



        def event(self, ev, x, y, st):
            if self.verified:
                return


            delete_set = set()

            for victim in persistent.victim_set:
                if not (victim in self.alive_set):
                    del persistent.buttons[victim]
                    delete_set.add(victim)

            persistent.victim_set = persistent.victim_set.difference(delete_set)
            
            self.alive_set = set()
            self.verified = True

            if persistent.victim_set == set():
                renpy.hide("stalker")



        def per_interact(self):
            self.verified = False

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