# так образуются новые каменистые планеты 
python early:
    import time
    import pygame

    renpy.config.containers_pass_transform_events.add("active") #не повлияет на работу других контейнеров
    timers = list()
    default_action = None


    class LayeredDependent(renpy.display.layout.Container):
        FALLBACK_MAP = {
            "idle": ["idle"],
            "hover": ["hover", "idle"],
            "active": ["active", "idle"],
            "selected_idle": ["selected_idle", "idle"],
            "selected_hover": ["selected_hover", "hover", "idle"]
        }
        def __init__(self, *args):
            # контейнер, хранящий в себе слои изображения.
            # слои будут меняться, и за их изменение отвечает класс LayeredDependent
            for state in self.FALLBACK_MAP:
                setattr(self, state+"_c", list())
            self.clean_up(args)
            super().__init__(*self.idle_c)


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
            print(event, new_children)

            self._clear()
            for nchild in new_children:
                self.add(nchild)
            
            super().set_transform_event(event)





    def block_control(func): #декоратор
        def wrapper(self, *args, **kwargs):
            if not self.locked:
                func(self, *args, **kwargs)
        return wrapper


    class LayeredTextButton(Button):
        focusable = True
        transform_event_responder = True

        def __init__(self, text, layered_bg, style="button", text_style="button_text", active_text_style=None, clicked=None, action=None, **properties):
            # layered_background: LayeredDependent объект, хранящий в себе все слои вместе с их состояниями
            self.text_style = Style(text_style)
            self.active_text_style = Style(active_text_style) if active_text_style is not None else self.text_style

            text_properties, button_properties = renpy.easy.split_properties(properties, "text_", "")
            text = Text(text, **text_properties)
            text.style = self.text_style

            child = Fixed(layered_bg, text)
            self.locked=False
            self.active_time=2
            self.click_time=0

            super().__init__(child, style=style, **button_properties)

            if action is None: #нельзя указать это в качестве значения по умолчанию тк они вычисляются на этапе компиляции
                action = default_action
            inst = self
            #если я оберну action, то мне не придется лезть в event (это сложнее)
            class WrappedAction(action.__class__):
                def __call__(self):
                    res = renpy.run(action)
                    inst.active()
                    return res

            self.action = WrappedAction()


        def render(self, width, height, st, at):
            activing_time = time.time()-self.click_time
            if self.locked:
                if activing_time>self.active_time:
                    self.unactive()
                renpy.redraw(self,0)
                
            return super().render(width, height, st, at)


        def active(self):
            self.set_style_prefix("active", True)
            self.set_transform_event("active")
            self.child.children[1].style = self.active_text_style
            self.child.children[1].set_text("active!")
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

        @block_control
        def focus(self, default=False):
            self.child.children[1].set_text("focus!")

            return super().focus(default)

        @block_control
        def unfocus(self, default=False):
            self.child.children[1].set_text("unfocus!")

            return super().unfocus(default)



    renpy.register_sl_displayable("l_textbutton", LayeredTextButton, "button_text").add_positional("text").add_positional("layered_bg").add_property("active_text_style")




init -1000:
    default default_action = NullAction()
