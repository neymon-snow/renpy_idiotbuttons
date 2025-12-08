# ня кнопка няяя
python early:
    import time
    import pygame
    class OButtonStyle():
        #класс-родитель
        def __init__(self, idle_transform=None, hover_transform=None, active_time=2.0, active_transform=None,
                    selected_idle_transform=None, selected_hover_transform=None, selected_active_transform=None, **kwargs):

            self.idle_transform = idle_transform
            self.active_time = active_time
            self.hover_transform = hover_transform
            self.active_transform = active_transform
            self.selected_idle_transform = selected_idle_transform
            self.selected_hover_transform = selected_hover_transform
            self.selected_active_transform = selected_active_transform


    class OTextButtonStyle(OButtonStyle):
        """ arguments{
            active_time: float = 2,
                the time during which, after clicking the button, the style properties with the active_ prefix will be used. in seconds
            base: OTextButtonStyle = None
                the base style from which this one is inherited,
            idle_textstyle: str ="default"
                the style used by the text when the button is selected,
            hover_textstyle: str = None,
            active_textstyle: str = None,
            selected_idle_textstyle: str = None
                selected_ means thet the style is used when the button is already pressed,
            selected_hover_textstyle: str = None,
            selected_active_textstyle: str = None,
            textpos: tuple(float, float) = (0,0)
                the coordinates of the text relative to the upper left corner of the background, if present,
            idle_background: renpy.Displayable =None
                button background in "normal" state,
            hover_background=None, active_background=None, selected_idle_background=None, selected_hover_background=None, selected_active_background=None,

            idle_transform=None
                a transform applied to the button in its "normal" state,
            hover_transform=None, active_transform=None, selected_idle_transform=None, selected_hover_transform=None, selected_active_transform=None
        }
        """
        def __init__(self, base=None,
                    idle_textstyle="default", hover_textstyle=None, active_textstyle=None,
                    selected_idle_textstyle=None, selected_hover_textstyle=None, selected_active_textstyle=None,
                    textpos=(0,0),
                    idle_background=None, hover_background=None, active_background=None,
                    selected_idle_background=None, selected_hover_background=None, selected_active_background=None,
                    **kwargs):

            self.idle_textstyle = idle_textstyle
            self.hover_textstyle = hover_textstyle
            self.active_textstyle = active_textstyle
            self.selected_idle_textstyle = selected_idle_textstyle
            self.selected_hover_textstyle = selected_hover_textstyle
            self.selected_active_textstyle = selected_active_textstyle

            self.textpos = textpos
            self.idle_background = idle_background
            self.hover_background = hover_background
            self.active_background = active_background
            self.selected_idle_background = selected_idle_background
            self.selected_hover_background = selected_hover_background
            self.selected_active_background = selected_active_background

            #добавить переходы.
            super().__init__(**kwargs)

            if base is not None:
                self.__dict__ = self.return_tbarg(base)
            self.__dict__ = self.prefix_distribution()

        def return_tbarg(self, base): #позволяет наследовать другие стили
            base = base.__dict__
            dictionary = self.__dict__
            new_dict = {}

            for name, value in dictionary.items():
                if value == None:
                    new_dict[name] = base[name]
                else:
                    new_dict[name] = value

            if dictionary["idle_textstyle"] == "default":
                new_dict["idle_textstyle"] = base["idle_textstyle"]

            return new_dict


        def prefix_distribution(self): #возвращает новый словарь с нормализованными свойствами, зав. от состояний
            new_dict = self.__dict__.copy()

            for prop, value in self.__dict__.items():
                if value is None: #не равны None в основном именно не idle_ свойства (однако есть необязательные идлы)
                    strings = prop.split("_")
                    prefix = strings[0]
                    name = strings[len(strings)-1]

                    if prefix == "selected" and strings[1] != "idle":
                        s_idle = self.__dict__[f"selected_idle_{name}"]
                        if s_idle is not None:
                            new_dict[prop] = s_idle
                            continue
                        not_s = self.__dict__[f"{strings[1]}_{name}"]
                        if not_s is not None:
                            new_dict[prop] = not_s
                            continue
                            
                    new_dict[prop] = self.__dict__["idle_"+name] #если и идл none, то ладно

            return new_dict
                
    






    #общие функции
    def greater2(x1, x2): 
        result = [None,None]
        for index in range(2): #это функция чисто для сравнивания двух кортежей из двух элементов
            if x1[index-1] >= x2[index-1]: val = True
            else: val=False
            result[index-1] = val
        return tuple(result)


    def compute_pos(pos , width=0, height=0):
        real_pos = list()
        size = (width, height)

        for i in range(2):
            if isinstance(pos[i], int):
                real_pos.append(pos[i])
                continue
            if isinstance(pos[i], float):
                position = pos[i]*size[i]
                real_pos.append(position)
                continue

        return real_pos

    
    def get_rect(text_pos ,text_size, bg_size=None):
        #возвращает размер прямоугольника, в который вписана кнопка
        max_w = text_pos[0] + text_size[0]
        max_h = text_pos[1] + text_size[1]
        real_ts = (max_w, max_h)
        if bg_size is not None:
            max_w = max(max_w, bg_size[0])
            max_h = max(max_h, bg_size[1])
        return (max_w, max_h)


    def is_hover(mouse_pos, obj_pos, obj_size):
        #крайняя левая точка это obj pos.
        #нужна крайняя правая нижняя точка для построения. это extr
        extr = (obj_pos[0]+obj_size[0], obj_pos[1]+obj_size[1])

        if all(greater2(extr, mouse_pos)) and all(greater2(mouse_pos, obj_pos)):
            return True
        return False


    def is_clicked(ev, is_hover):
        if is_hover and renpy.map_event(ev, "button_select"):
            return True
        return False


    def change_prefixes(self, prefixes, index=None):

        if index is None:
            real_prefixes = prefixes[0]

            persistent.buttons[self.tag] = prefixes
            self._prefixes = real_prefixes
            return

        persistent.buttons[self.tag][0][index] = self._prefixes[index] = prefixes


    

    class TBDisplayable(renpy.Displayable):
        focusable = True
        transform_event_responder = True

        def __init__(self, text, a_style, action, hovered=None, **kwargs):

            super().__init__()
            self.tag = str((text, action))
            self.text = text
            self.a_style = a_style
            self.action = action
            self.hovered = hovered
            self.size = (0,0)
            self.position = (0,0)
        
            self._click_time = None
            self._init_time = time.time()
            self._kwargs = kwargs

            if self.tag in persistent.buttons:
                self._prefixes = persistent.buttons[self.tag][0]
            else:
                change_prefixes(self, [["", "idle_"], 0.0])
            self._persistent = persistent.buttons[self.tag]

            self._update_displayables()
            hello_stalker(self.tag)


        def render(self, width, height, st, at):

            prefixes = "".join(self._prefixes)
            style = self.a_style
            
            text_render = renpy.render(self.text_disp, width, height, st, at)
            text_size = text_render.get_size()

            #свойства указанные в kwargs init метода относятся ко всем displ которые будут отображаться
            placement = renpy.get_placement(self.text_disp)

            abs_position = renpy.display.displayable.place(width, height, text_size[0], text_size[1], placement.__dict__.values())
            text_spos = compute_pos(style.textpos, width, height)
            text_realpos = (text_spos[0]+abs_position[0], text_spos[1]+abs_position[1])

            if self.bg_disp:
                bg_render = renpy.render(self.bg_disp, width, height, st, at)

                bg_size = bg_render.get_size()
                bg_realpos = renpy.display.displayable.place(width, height, bg_size[0], bg_size[1], placement.__dict__.values())

                #передаю данные о размере и крайней левой точке
                self.size = get_rect(text_spos, text_size, bg_size=bg_size)

                canvas = renpy.Render(*self.size)
                canvas.blit(bg_render, bg_realpos)

                xmin = min(text_realpos[0], bg_realpos[0])
                ymin = min(text_realpos[1], bg_realpos[1])
                self.position = (xmin, ymin)

            else:
                self.size = get_rect(text_spos, text_size)
                canvas = renpy.Render(*self.size)

                self.position = text_realpos

            canvas.blit(text_render, text_realpos)
            return canvas
            

        def event(self, ev, x, y, st):

            if self._prefixes[1] == "active_":
                click_time = self._persistent[1]
                if time.time()-click_time <= self.a_style.active_time:
                    return
                change_prefixes(self, "selected_", 0)

            hover = is_hover((x,y), self.position, self.size)
            active = is_clicked(ev, hover)

            if active:
                change_prefixes(self, "active_", 1)
                self._update_displayables()
                self._persistent[1] = time.time()
                
                renpy.redraw(self, 0)

                rv = renpy.run(self.action)

                if rv is not None:
                    return rv
                raise renpy.IgnoreEvent()

            if hover:
                if self._prefixes[1] != "hover_":
                    change_prefixes(self, "hover_", 1)
                    self._update_displayables()

                    renpy.run(self.hovered)

            else:
                if self._prefixes[1] != "idle_":
                    change_prefixes(self, "idle_", 1)
                    self._update_displayables()

            renpy.redraw(self, 0)


        def per_interact(self):
            stalker.im_here(self.tag)


        def _update_displayables(self):

            prefixes = "".join(self._prefixes)
            style = self.a_style
            sdict = style.__dict__
            transform = sdict[prefixes+"transform"]

            self.text_disp = Text(self.text, style=sdict[prefixes+"textstyle"], **self._kwargs)

            if sdict[prefixes+"background"]:
                self.bg_disp = renpy.displayable(sdict[prefixes+"background"])

                if transform:
                    self.text_disp = At(self.text_disp, transform)
                    self.bg_disp = At(self.bg_disp, transform)
                return

            self.bg_disp = None
            if transform:
                self.text_disp = At(self.text_disp, transform)


########################################################################################
    def textbuttontext_return(a_text, style="default", a_style=OTextButtonStyle(), action=None, **kwargs):
        
        changed_style = OTextButtonStyle(base=a_style, **kwargs)

        return TBDisplayable(a_text ,changed_style, action, **kwargs)



    renpy.register_sl_displayable("textbuttani", textbuttontext_return, "button_text").add_property_group("text").add_positional("a_text").add_property("a_style").add_property("textpos").add_property("active_time").add_property("action").add_style_property("transform").add_style_property("textstyle").add_style_property("background").add_property("active_textstyle").add_property("active_transform").add_property("active_background")
