
from tkinter import Tk, W, E
from tkinter.ttk import Frame, Button, Entry, Style
import tkinter as tk
from PIL import Image, ImageTk
#Its not pretty but it add and removes from list displays the list and has a quit button

class ShoppingCart(Frame):
    def __init__(self):
        super().__init__()
        self.shoppinglist = []
        self.adding = True
        self.initUI()


    def initUI(self):
        def press():
            sc.delete("1.0", tk.END)
            sc.insert(tk.END, getList(self))

        def addpress():
            self.adding=not self.adding
            if self.adding==True:
                ar['text'] = "Click to Start \r Removing"
                press()
            else:
                ar['text']="Click to Start \r Adding"
                press()

        def shop(s):
            if(self.adding==True):
                self.shoppinglist.append(s)
            else:
                if s in self.shoppinglist:
                    self.shoppinglist.remove(s)
                    

        self.master.title("Kevin's Fried Rice Store")

        zuc = tk.Button(self, command=lambda:[shop("Zucchini"),press()])
        image = ImageTk.PhotoImage(file="zuc.gif")
        zuc.config(image=image, width=200, height=200, bg="black")
        zuc.image = image
        zuc.grid(row=2, column=1)

        onion = tk.Button(self, command=lambda:[shop("Onion"),press()])
        image = ImageTk.PhotoImage(file="onion.gif")
        onion.config(image=image, width=200, height=200, bg="black")
        onion.image = image
        onion.grid(row=2, column=2)

        chick = tk.Button(self, command=lambda: [shop("Chicken"),press()])
        image = ImageTk.PhotoImage(file="chicken.gif")
        chick.config(image=image, width=200, height=200, bg="black")
        chick.image = image
        chick.grid(row=2, column=3)

        egg = tk.Button(self, command=lambda:[shop("Egg"),press()])
        image = ImageTk.PhotoImage(file="egg.gif")
        egg.config(image=image, width=200, height=200, bg="black")
        egg.image = image
        egg.grid(row=2, column=4)

        gonion = tk.Button(self, command=lambda: [shop("Green Onion"), press()])
        image = ImageTk.PhotoImage(file="gonion.gif")
        gonion.config(image=image, width=200, height=200, bg="black")
        gonion.image = image
        gonion.grid(row=3, column=1)   

        mush = tk.Button(self, command=lambda: [shop("Mushroom"), press()])
        image = ImageTk.PhotoImage(file="mush.gif")
        mush.config(image=image, width=200, height=200, bg="black")
        mush.image = image
        mush.grid(row=3, column=2)

        redppr = tk.Button(self, command=lambda: [shop("Red Peppers"), press()])
        image = ImageTk.PhotoImage(file="redppr.gif")
        redppr.config(image=image, width=200, height=200, bg="black")
        redppr.image = image
        redppr.grid(row=3, column=3)

        rice = tk.Button(self, command=lambda: [shop("Rice"), press()])
        image = ImageTk.PhotoImage(file="rice.gif")
        rice.config(image=image, width=200, height=200, bg="black")
        rice.image = image
        rice.grid(row=3, column=4)

        soy = tk.Button(self, command=lambda: [shop("Soy Sauce"), press()])
        image = ImageTk.PhotoImage(file="soy.gif")
        soy.config(image=image, width=200, height=200, bg="black")
        soy.image = image
        soy.grid(row=4, column=1)

        carrot = tk.Button(self, command=lambda: [shop("Carrot"), press()])
        image = ImageTk.PhotoImage(file="carrot.gif")
        carrot.config(image=image, width=200, height=200, bg="black")
        carrot.image = image
        carrot.grid(row=4, column=2)

        garlic = tk.Button(self, command=lambda: [shop("Garlic"), press()])
        image = ImageTk.PhotoImage(file="garlic.gif")
        garlic.config(image=image, width=200, height=200, bg="black")
        garlic.image = image
        garlic.grid(row=4, column=3)

        peas = tk.Button(self, command=lambda: [shop("Peas"), press()])
        image = ImageTk.PhotoImage(file="peas.gif")
        peas.config(image=image, width=200, height=200, bg="black")
        peas.image = image
        peas.grid(row=4, column=4)

        sc = tk.Text(self, height=13, width=30)
        sc.insert(tk.END, getList(self))
        sc.grid(row=2, column=5)

        ar = tk.Button(self, text="Click to start \r Removing", bg="darkblue", fg="white", font='Helvetica 18 bold', width=15, height=5, command=lambda: [addpress()])
        ar.grid(row=3, column=5)

        quit = tk.Button(self, text="QUIT", fg="black", bg="red", font='Helvetica 18 bold', command=self.master.destroy, width=10, height=5)
        quit.grid(row=4, column=5)

        self.pack()


def getList(self):
    items='Your Shopping Cart Contains: \n'
    for item in self.shoppinglist:
        items+= item + "\n"
    return items

def main():
    root = Tk()
    app = ShoppingCart()
    root.configure(background="black")
    root.mainloop()

if __name__ == '__main__':
    main()
