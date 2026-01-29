
python early:
    import time

    renpy.config.containers_pass_transform_events.add("active") #не повлияет на работу других контейнеров
    timers = list()
    default_action = None
    screen_center_x, screen_center_y = (1280, 720)


    class Layered(renpy.display.layout.Container):
        FALLBACK_MAP = {
            "idle": ["idle"],
            "hover": ["hover", "idle"],
            "active": ["active", "idle"],
            "selected_idle": ["selected_idle", "idle"],
            "selected_hover": ["selected_hover", "hover", "idle"]
        }
        def __init__(self, *args, parent=None):
            # контейнер, хранящий в себе слои изображения.
            # слои будут меняться, и за их изменение отвечает класс LayeredDependent
            self.parent = parent
            for state in self.FALLBACK_MAP:
                setattr(self, state+"_c", list())
            self.clean_up(args)
            super().__init__(*self.idle_c)


        def render(self, width, height, st, at):
            canvas = renpy.Render(*self.get_maximums(width, height, st, at))
            for index, c in enumerate(self.children):
                crender = renpy.render(c, width, height, st, at)

                cx, cy = (c.style.xpos, c.style.ypos)
                cw, ch = crender.get_size()
                x_offset, y_offset = self.calculate_offset(index,  width, height, cx, cy, cw, ch)
                cx = c.style.xpos + x_offset
                cy = c.style.ypos + y_offset

                canvas.blit(crender, (cx, cy))

            return canvas


        def clean_up(self, childs):
            for vals in childs:
                child, pos = vals #child: {состояния: картинки}
                for state, search in self.FALLBACK_MAP.items():
                    for current_search in search:
                        if current_search in child:
                            disp = renpy.easy.displayable(child[current_search])
                            disp.style.pos = pos
                            getattr(self, state+"_c").append(disp)
                            break


        def set_transform_event(self, event):
            #всегда, когда мы проявляем новое состояние, вызываем set_transform_event
            new_children = getattr(self, event+"_c")
            # print(event, new_children)

            self._clear()
            for nchild in new_children:
                self.add(nchild)
            
            super().set_transform_event(event)


        def get_maximums(self, width, height, st, at):
            xmax = ymax = 0
            for index, c in enumerate(self.children):
                crender = renpy.render(c, width, height, st, at)
                w, h = crender.get_size()
                x, y = renpy.display.displayable.place(width, height, w, h, c.get_placement())
                x_offset, y_offset = self.calculate_offset(index, width, height, x, y, w, h)
                c_xmax = w + x + x_offset
                c_ymax = h + y + y_offset

                xmax = c_xmax if c_xmax>xmax else xmax
                ymax = c_ymax if c_ymax>ymax else ymax
            return (xmax, ymax)

        def calculate_offset(self, w, h, cx, cy, cw, ch):
            return (0, 0)





    class PerspectiveLayered(Layered):
        def __init__(self, *args, p_influence=0.2, **kwargs):
            super().__init__(*args, **kwargs)
            self.p_influence = p_influence
            self.cached_rect = None

        def render(self, width, height, st, at):
            renpy.redraw(self, 0) #при анимациях смещения слоев могут меняться
            return super().render(width, height, st, at)

        def get_global_rect(self):
            focus_list = renpy.display.focus.focus_list
            for focus in focus_list:
                if focus.widget is self.parent:
                    self.cached_rect = focus.inset_rect()

            if self.cached_rect is not None:
                return self.cached_rect
            return (screen_center_x, screen_center_y, 0, 0)


        def calculate_offset(self, index, w, h, cx, cy, cw, ch): #оффсет вычисляется для каждого слоя
            pp = self.parent.get_placement()
            parent_x, parent_y = self.get_global_rect()[:2]
            cx, cy = (cx + cw/2, cy + ch/2)

            from_c_to_x = screen_center_x - (parent_x + cx)
            from_c_to_y = screen_center_y - (parent_y + cy)
            print(parent_x, parent_y)

            p_influence = (-(1+self.p_influence)**-index + 1)*self.p_influence # y=-1.5^(-x)+1 умножаю на p_influence, чтобы сделать коэффициент меньше
            return (from_c_to_x*p_influence, from_c_to_y*p_influence)
            





    def block_control(func): #декоратор
        def wrapper(self, *args, **kwargs):
            if not self.locked:
                func(self, *args, **kwargs)
        return wrapper


    class ActiveTextButton(Button):
        focusable = True
        transform_event_responder = True

        def __init__(self, text, layered_bg, style="button", text_style="button_text", active_text_style=None, at=None, clicked=None, action=None, **properties):
            # layered_bg: экземпляр подкласса Layered, хранящий в себе все слои вместе с их состояниями
            text_properties, button_properties = renpy.easy.split_properties(properties, "text_", "")

            self.locked=False
            self.active_time=2
            self.click_time=0
            self.text_style = Style(text_style, properties=text_properties)
            self.active_text_style = Style(active_text_style, properties=text_properties) if active_text_style is not None else self.text_style

            self.text = Text(text)
            self.text.style = self.text_style
            self.layered_bg = layered_bg
            self.layered_bg.parent = self

            child = Fixed(self.layered_bg, self.text)
            super().__init__(child, style=style, **button_properties)

            if action is None: #нельзя указать это в качестве значения по умолчанию тк они вычисляются на этапе компиляции
                action = default_action
            inst = self
            #если я оберну action, то мне не придется лезть в event (это сложнее)
            class WrappedAction(action.__class__):
                def __init__(self):
                    #действие может ожидать аргументов, но они уже переданы в action
                    self.__dict__ = action.__dict__
                def __call__(self):
                    res = renpy.run(action)
                    inst.active()
                    return res

            self.action = WrappedAction()


        def render(self, width, height, st, at):
            activing_time = time.time()-self.click_time
            if self.locked: #обрабатываю active состояние, если есть
                if activing_time>self.active_time:
                    self.unactive()
                renpy.redraw(self,0)
                
            if self.style.focus_rect:
                x, y, w, h = rect
            else:
                x, y = (0,0)
                w, h = self.get_maximums(width, height, st, at)

            rv = super(Button, self).render(width, height, st, at)
            rv.add_focus(self, None, x, y, w, h, None, None, None)
            return rv 


        def active(self):
            self.set_style_prefix("active", True)
            self.set_transform_event("active")
            self.text.style = self.active_text_style
            self.text.set_text("active!")
            self.locked = True

            self.click_time = time.time()
            renpy.redraw(self, 0)

        def unactive(self):
            self.locked = False
            self.click_time = 0
            
            if self.is_focused():
                self.focus()
            else:
                self.unfocus()


        def get_maximums(self, width, height, st, at):
            layered_x, layered_y = self.layered_bg.get_maximums(width, height, st, at)
            text_canvas = renpy.render(self.text, width, height, st, at)
            
            w = max(layered_x, text_canvas.width)
            h = max(layered_y, text_canvas.height)
            return (w, h)


        @block_control
        def focus(self, default=False):
            self.text.set_text("focus!")

            return super().focus(default)

        @block_control
        def unfocus(self, default=False):
            self.text.set_text("unfocus!")

            return super().unfocus(default)

        def event(self, ev, x , y, st):
            renpy.display.render.invalidate(self.layered_bg)
            return super().event(ev, x , y, st)

           

    renpy.register_sl_displayable("clickable", ActiveTextButton, "button_text").add_positional("text").add_positional("layered_bg").add_property("active_text_style").add_property_group("button").add_property_group("text", prefix="text_").add_property_group("position", prefix="text_")





init -1000:
    default default_action = NullAction()
