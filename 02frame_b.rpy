init python early:
    #кнопка-фрейм

    class FrameButtonD(renpy.display.layout.Container):
        transform_event_responder = True
        _store_transform_event = True
        focusable = True

        def __init__(self, idle_img, hover_img, *args, hovered=None, unhovered=None, **kwargs):
            # основным должен быть контейнер.
            super().__init__()

            # Frame я использую лишь в render для отрисовки, в остальном он мне не нужен
            self.frame_d = Frame(idle_img, *args, **kwargs)

            # для event метода
            self.idle_image = renpy.easy.displayable(self.frame_d.image)
            self.hover_image = renpy.easy.displayable(hover_img)
            self.hovered = hovered
            self.unhovered = unhovered



        def render(self, width, height, st, at):

            childrens = super().render(width, height, st, at)

            maxw = 0
            maxh = 0
            for index, c in enumerate(self.children):

                csize = renpy.render(c, width, height, st, at).get_size()
                #offsets мы обновляем в super().render. значения сохр. до след вызова
                cpos = self.offsets[index]

                realw = cpos[0] + csize[0]
                realh = cpos[1] + csize[1]
                
                #если крайние границы доч. элемента дальше maxw или maxh, обновляем
                if realw > maxw:
                    maxw = realw
                if realh > maxh:
                    maxh = realh

            #отрисовываю frame
            rv = renpy.render(self.frame_d, maxw, maxh, st, at)
            rv.blit(childrens, (0, 0))

            #позволяю FrameButtonD фокусироваться
            rv.add_focus(self, None, 0, 0, maxw, maxh)
            return rv



        def event(self, ev , x, y, st):
            e = super().event(ev , x, y, st)

            def check_c(childs):
                for f in childs:
                    if f.is_focused():
                        return True
                    #рекурсивно проверяю детей дочернего элемента, если имеются
                    if hasattr(f, "children"):
                        if check_c(f.children): return True
                return False
                        
            # focus и unfocus вызываются не тогда, когда нужно для fb, поэтому я описываю
            # эту логику в event
            if self.is_focused() or check_c(self.children): self.free_focus()
            elif self.frame_d.image == self.hover_image: self.free_unfocus()

            renpy.redraw(self, 0)
            return e


        #этот метод вызывается, когда fb сфокусирован
        def focus(self, default=False): pass
        #этот метод вызывается, когда fb теряет фокус
        def unfocus(self, default=False): pass


        def free_focus(self, default=False):
            super().focus(default)
            self.set_transform_event("hover")
            self.frame_d.image = self.hover_image

            if not default:
                renpy.run(self.hovered)


        def free_unfocus(self, default=False):
            super().unfocus()
            self.set_transform_event("idle")
            self.frame_d.image = self.idle_image

            if not default:
                renpy.run_unhovered(self.hovered)
                renpy.run(self.unhovered)





    renpy.register_sl_displayable("f_button", FrameButtonD, "frame", nchildren="many").add_property_group("window").add_positional("idle_img").add_positional("hover_img").add_property("unhovered").add_property("hovered")

