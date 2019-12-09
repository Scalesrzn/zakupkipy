from tkinter import *
import Zakupki_main as zk
def click(): 
    zk.start(1)

def setVar():
    zk.keys = "{}".format(keyword.get()) 
    if selected == 44: 
        zk.setParams.fz44 = "on"
        zk.fz223 = "off"
    else:
        zk.fz44 = "off"
        zk.fz223 = "on"
    
window = Tk()
window.title("Парсер Госзакупок")
window.geometry('500x300')  
selected = IntVar()  
lbl = Label(window, text="Введите ключевые слова в поле:")  
lbl.grid(column=0, row=0)  
keyword = Entry(window,width=40)  
keyword.grid(column=0, row=2)  
lbl = Label(window, text="Введите минимальную сумму закупки:")  
lbl.grid(column=0, row=3)  
keyword = Entry(window,width=40)  
keyword.grid(column=0, row=4) 
lbl = Label(window, text="Выберете ФЗ:")  
lbl.grid(column=0, row=5)  
rad1 = Radiobutton(window, text='ФЗ-44', value='44', variable=selected)  
rad2 = Radiobutton(window, text='ФЗ-223', value='223', variable=selected)   
rad1.grid(column=0, row=6)  
rad2.grid(column=1, row=6)  
lbl = Label(window, text="Введите ключевые слова в поле:")  
lbl.grid(column=0, row=0)  
keyword = Entry(window,width=40)  
keyword.grid(column=0, row=2) 
btn = Button(window, text="Сохранить фильтры", command=setVar)
btn.grid(column=2, row=2)
btnStart = Button(window, text="Запустить процесс сбора данных", command=click)
btnStart.grid(column=2, row=3)
window.mainloop()