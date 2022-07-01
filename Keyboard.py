import pygame as pg
import random, time

pg.init()
pg.mixer.pre_init(44100,-16,2,512)
pg.key.set_repeat(210,30)

display = [500, 700]
#display = pg.display.list_modes()[0]
screen = pg.display.set_mode((display[0],display[1])) 
pg.display.set_caption("Sly'oul Keyboard")

clock = pg.time.Clock()
events = list(pg.event.get())

class Mouse:

    def __init__(self):
        self.position = (0,0)
        
    def pos(self):
        self.position = pg.mouse.get_pos()

    def Lclick(self):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                return True

    def Rclick(self):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                return True

    # def Uscroll(self):
    #     for event in events:
    #         if event.type == pg.MOUSEBUTTONDOWN and event.button == 4:   
    #             return True

    # def Dscroll(self):
    #     for event in events:
    #         if event.type == pg.MOUSEBUTTONDOWN and event.button == 5:   
    #             return True
            
mouse = Mouse()

class Keyboard:

    def __init__(self):
        self.letters = {}
        self.compound_letters = {}
        self.keys_dict = {}
        self.letter_groups = {"consonants":[], "vowels":[], "other":[]}
        self.font = pg.image.load(f"assets/font.png").convert_alpha()
        self.message = ""
        self.characters = []
        self.blocksize = 120
        self.lsiz = 50

        self.text_img = pg.Surface((display[0],display[1]),pg.SRCALPHA)

    def file_write(self):
        for c in self.characters:
            self.message += c[0]

        with open(f"text.txt","a",encoding="utf-8") as file:
            file.write("\n")
            file.write(f">>> {self.message}")
            file.write("\n")

    def language_rules(self, letter):
        ### Letter Compounding ###
        if letter in self.compound_letters.keys():
            replace = True
            for n, l in enumerate(self.compound_letters[letter][::-1]):
                if len(self.characters) > n and self.characters[-(n+1)][0] == l:
                    continue
                else:
                    replace = False
                    break

            if replace:
                for _ in range(n + 1):
                    self.backspace()
                return self.letters[self.compound_letters[letter] + letter], False, self.compound_letters[letter] + letter

        if letter == "h":
            if len(self.characters) > 0:
                return self.characters[-2][1], self.characters[-2][4], letter
            else:
                return None, False, letter

        if len(self.characters) > 0:

            if self.characters[-1][0] in self.letter_groups["consonants"] and self.characters[-1][4]:
                if letter in self.letter_groups["vowels"] or letter == "":
                    self.characters[-2][1] = pg.transform.scale(self.letters[self.characters[-2][0]],(self.lsiz,int(self.lsiz/2))) ## The vowel prior

                    self.characters[-1][1] = self.letters[self.characters[-1][0]] ## The last letter
                    self.characters[-1][2] += int(self.lsiz/2) ## X
                    self.characters[-1][3] -= int(self.lsiz/2) ## Y
                    self.characters[-1][4] = False ## Compound


        ### Null Letter ###
            if letter == "" and self.characters[-1][0] != "":
                self.characters[-1][1] = pg.transform.scale(self.letters[self.characters[-1][0]],(self.lsiz,int(self.lsiz/2)))
                
                return pg.transform.scale(self.letters[letter],(self.lsiz,int(self.lsiz/2))), True, letter

        ### Block Forming ###
            elif self.characters[-1][0] in self.letter_groups["consonants"] and not self.characters[-1][4]:
                if letter in self.letter_groups["vowels"]:
                    self.characters[-1][1] = pg.transform.scale(self.letters[self.characters[-1][0]],(self.lsiz,int(self.lsiz/2)))
                    
                    return pg.transform.scale(self.letters[letter],(self.lsiz,int(self.lsiz/2))), True, letter

            elif self.characters[-1][0] in self.letter_groups["vowels"] and self.characters[-1][4]:
                if letter in self.letter_groups["consonants"]:
                    self.characters[-1][1] = pg.transform.scale(self.letters[self.characters[-1][0]],(int(self.lsiz/2),int(self.lsiz/2)))

                    return pg.transform.scale(self.letters[letter],(int(self.lsiz/2),int(self.lsiz/2))), True, letter

        
        return self.letters[letter], False, letter

    def key_init(self, letter, key, type, posx, posy, w = 1, h = 1):
        block = pg.Rect(posx*self.blocksize, posy*self.blocksize, w*self.blocksize, h*self.blocksize)
        letterimg = self.font.subsurface(block)
        
        self.letters[letter] = pg.transform.scale(letterimg, (self.lsiz*w,self.lsiz*h))
        self.letter_groups[type].append(letter)
        if len(letter) > 1:
            self.compound_letters[letter[-1]] = letter[:-1]
        else:
            self.keys_dict[key] = letter
    
    def backspace(self):
        if self.characters[-1][0] in self.letter_groups["consonants"]:
            if self.characters[-1][4]:
                self.characters[-2][1] = pg.transform.scale(self.letters[self.characters[-2][0]],(self.lsiz,int(self.lsiz/2))) ## The vowel prior
                self.characters[-2][4] = False
            else:
                pass

        elif self.characters[-1][0] in self.letter_groups["vowels"]:
            if self.characters[-1][4]:
                self.characters[-2][1] = pg.transform.scale(self.letters[self.characters[-2][0]],(self.lsiz,self.lsiz)) ## The Consonant prior                
            else:
                pass

        elif self.characters[-1][0] == "":
            self.characters[-2][1] = pg.transform.scale(self.letters[self.characters[-2][0]],(self.lsiz,self.lsiz))

        self.characters = self.characters[:-1]

        self.text_update()

    def key(self):
        for event in events:
            if event.type == pg.KEYDOWN:
                for key in self.keys_dict.keys():
                    if event.key == key:
                        char, compound, letter = self.language_rules(self.keys_dict[key])
                        if letter != "h":
                            
                            # if self.keys_dict[key] in self.letter_groups["vowels"] and not compound:
                            #     char = pg.transform.scale(char,(self.lsiz,int(self.lsiz/2)))

                            y = int(len([c for c in self.characters if not c[-1]])*self.lsiz//(display[0] - int(self.lsiz/2)))

                            xpos = (len([c for c in self.characters if not c[-1]])*self.lsiz) - y*self.lsiz*(display[0]//self.lsiz)
                            xpos -= compound*self.lsiz
                            xpos += (compound and self.characters[-1][4])*int(self.lsiz/2)

                            ypos = y*int(self.lsiz*1.5)
                            ypos += compound*int(self.lsiz/2)
                            self.characters.append([letter, char, xpos, ypos, compound])

                            # if self.keys_dict[key] in self.letter_groups["vowels"] and not compound:
                            #     self.characters.append(["", pg.transform.scale(self.letters[""], (self.lsiz,int(self.lsiz/2))), xpos, ypos + int(self.lsiz/2), True])

                            self.text_update()

                if event.key == pg.K_BACKSPACE:
                    if len(self.characters) > 0:
                        self.backspace()

    def text_update(self):
        self.text_img = pg.Surface((display[0],display[1]),pg.SRCALPHA)
        for c in self.characters:
            _, char, posx, posy,_ = c
            self.text_img.blit(char, (posx, posy))

    def text_display(self):
        screen.blit(self.text_img, (0,0))

keyboard = Keyboard()

keyboard.key_init(" ", pg.K_SPACE, "other", 5,0)

keyboard.key_init("a", pg.K_a, "vowels", 0,0)
keyboard.key_init("e", pg.K_e, "vowels", 1,0)
keyboard.key_init("i", pg.K_i, "vowels", 2,0)
keyboard.key_init("o", pg.K_o, "vowels", 3,0)
keyboard.key_init("u", pg.K_u, "vowels", 4,0)

keyboard.key_init("b", pg.K_b, "consonants", 0,1)
keyboard.key_init("p", pg.K_p, "consonants", 1,1)
keyboard.key_init("ts", pg.K_s, "consonants", 3,1)
keyboard.key_init("c", pg.K_c, "consonants", 3,1)
keyboard.key_init("h", pg.K_h, "consonants", 5,0) ## Fix
keyboard.key_init("ch", pg.K_h, "consonants", 4,1)

keyboard.key_init("j", pg.K_j, "consonants", 0,2)
keyboard.key_init("y", pg.K_y, "consonants", 0,2)
keyboard.key_init("dz", pg.K_z, "consonants", 1,2)
keyboard.key_init("d", pg.K_d, "consonants", 2,2)
keyboard.key_init("t", pg.K_t, "consonants", 3,2)
keyboard.key_init("g", pg.K_g, "consonants", 4,2)
keyboard.key_init("k", pg.K_k, "consonants", 5,2)

keyboard.key_init("m", pg.K_m, "consonants", 0,3)
keyboard.key_init("s", pg.K_s, "consonants", 2,3)
keyboard.key_init("l", pg.K_l, "consonants", 3,3)
keyboard.key_init("r", pg.K_r, "consonants", 3,3)
keyboard.key_init("n", pg.K_n, "consonants", 4,3, h = 2)
keyboard.key_init("oul", pg.K_l, "other", 5,3, h = 2)

keyboard.key_init("", pg.K_COMMA, "other", 1,4)

running = True
while running:
    events = list(pg.event.get())
    mouse.pos()

    for event in events:
        if event.type == pg.QUIT:
            running = False

    screen.fill((175,175,175))
    keyboard.key()
    keyboard.text_display()

    clock.tick(60)
    pg.display.update()
    

keyboard.file_write()
pg.quit()
quit()