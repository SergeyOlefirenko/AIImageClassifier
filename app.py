import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import cv2
import numpy as np
import tensorflow as tf
import os
import sys

def resource_path(relative_path): # Возвращает абсолютный путь к файлу (необходим при упаковке с PyInstaller (создание AIImageClassifier.exe))
    
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path) # Если запускается как .exe, ищет файл в папке с ресурсами
    return os.path.join(os.path.abspath("."), relative_path)  # Иначе использует текущую директорию

model_path = resource_path("ai_imageclassifier.keras") # Указываем путь к модели
model = tf.keras.models.load_model(model_path) # Загружаем модель

img = None # Оригинальное изображение
img_sr = None  # Улучшенное изображение
img_label = None # Элемент интерфейса для отображения изображения
result_label = None # Элемент интерфейса для вывода результата


# Удаляем элементы интерфейса и сбрасываем состояния (в основном этот метод написан для переопределения кнопок и возврату к форме исходного отображения интерфейса после загрузки)
def reset_interface():
    
    global img_label, result_label, img, img_sr
    if img_label:
        img_label.destroy()
        img_label = None
    if result_label:
        result_label.destroy()
        result_label = None
    img = None
    img_sr = None
    
    # Показываем/скрываем нужные кнопки
    load_btn.pack(pady=10)
    enhance_btn.pack_forget()
    change_btn.pack_forget()
    save_btn.pack_forget()
    cancel_btn.pack_forget()

def resize_to_fit(image_array, max_size=350): # Изменяем размер изображения пропорционально, чтобы вписать его в max_size
    
    height, width = image_array.shape[:2]
    
    if width > height:
        new_width = max_size
        new_height = int(max_size * height / width)
    else:
        new_height = max_size
        new_width = int(max_size * width / height)
    return cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_AREA)

def load_and_predict():
    
    global img, img_label, result_label
    file_path = filedialog.askopenfilename(  # Диалог выбора файла
        title="Select Image",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )
    if not file_path:
        messagebox.showinfo("Info", "No file selected.") # Выводим сообщение, если файл не выбран
        return

    try:
        img = cv2.imread(file_path)  # Чтение изображения
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Преобразование BGR в RGB

        preview = resize_to_fit(img, max_size=350) # Создание миниатюры (имеется ввиду отображаемое изображение)
        preview_pil = Image.fromarray(preview)
        preview_imgtk = ImageTk.PhotoImage(image=preview_pil)
        
        # Создание или обновление метки изображения в интерфейсе
        if img_label:
            img_label.configure(image=preview_imgtk)
            img_label.image = preview_imgtk
        else:
            img_label = tk.Label(root, image=preview_imgtk, bg=root["bg"], bd=0, highlightthickness=0)
            img_label.image = preview_imgtk
            img_label.pack(pady=5)

        # Подготовка изображения для модели и предсказание
        resize = tf.image.resize(img, (32, 32))
        y_pred = model.predict(np.expand_dims(resize / 255, 0), verbose=0)

        result = "REAL IMAGE" if y_pred[0] > 0.61 else "IMAGE MIGHT BE AI-GENERATED OR EDITED"

        # Отображение результата
        if result_label:
            result_label.configure(text=result)
        else:
            result_label = ctk.CTkLabel(root,
                                        text=result,
                                        font=("Arial", 18, "bold"),
                                        text_color="#1E90FF")
            result_label.pack(pady=5)

        # Обновление состояния кнопок
        enhance_btn.pack(pady=10)
        change_btn.pack(pady=10)
        load_btn.pack_forget()
        save_btn.pack_forget()
        cancel_btn.pack_forget()

    except Exception as e:
        messagebox.showerror("Error", str(e)) # Вывод ошибки

def enhance_image():
    global img, img_sr, img_label
    if img is None:
        messagebox.showwarning("Warning", "Please load an image first.")
        return
    # Подробное описание img_denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    # src (img) - исходное изображение
    # dst=None - место хранения результата (если None — будет возвращено значение)
    # h=10 - степень фильтрации для яркостного канала
    # hColor=10 - степень фильтрации для цветовых каналов
    # templateWindowSize=7 - размер окна шаблона (в пикселях)
    # searchWindowSize=21 - размер окна поиска (в пикселях)
    try:
        img_denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21) # Удаление шумов и масштабирование
        
        img_sr = cv2.resize(img_denoised, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        preview = resize_to_fit(img_sr, max_size=350)
        preview_pil = Image.fromarray(preview)
        preview_imgtk = ImageTk.PhotoImage(image=preview_pil)

        if img_label:
            img_label.configure(image=preview_imgtk)
            img_label.image = preview_imgtk

        # Активируем кнопки
        save_btn.configure(state="normal")
        save_btn.pack(pady=10)
        cancel_btn.configure(state="normal")
        cancel_btn.pack(pady=10)

        enhance_btn.pack_forget()
        change_btn.pack_forget()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def save_result():
    global img_sr
    if img_sr is None:
        messagebox.showwarning("Warning", "Please enhance the image first.")
        return

    try:
        os.makedirs("results", exist_ok=True)  # Создаём директорию, если она не существует

        base_name = "enhanced_image"
        ext = ".png"
        counter = 1
        save_path = os.path.join("results", base_name + ext)

        # Проверка на существование файла, если существует — увеличиваем номер
        while os.path.exists(save_path):
            save_path = os.path.join("results", f"{base_name}({counter}){ext}")
            counter += 1

        # Сохраняем изображение
        cv2.imwrite(save_path, cv2.cvtColor(img_sr, cv2.COLOR_RGB2BGR)) # Сохраняем в BGR
        messagebox.showinfo("Saved", f"Image saved at {save_path}")
        reset_interface()

    except Exception as e:
        messagebox.showerror("Save Error", str(e))


# UI 
ctk.set_appearance_mode("light") # Устанавливаем тему
ctk.set_default_color_theme("blue") # Устанавливаем цветовую схему (по умолчанию) для цвета текста

root = ctk.CTk()  # Создаем главное окно
root.title("AI Image Classifier & Enhancer")
root.geometry("610x410") # Размеры главного окна
root.resizable(True, True)

# Background Image
try:
    background_image = Image.open(resource_path("background.jpg"))
    bg_resized = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root)
    background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    def resize_bg(event): # Адаптируем фон при изменении окна
        new_bg = background_image.resize((event.width, event.height))
        bg_img = ImageTk.PhotoImage(new_bg)
        background_label.config(image=bg_img)
        background_label.image = bg_img

    root.bind("<Configure>", resize_bg)
except:
    pass

# Logo
try:
    logo_image = Image.open(resource_path("logo.png")).resize((100, 100), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo, bg=root["bg"], bd=0, highlightthickness=0)
    logo_label.image = logo
    logo_label.pack(pady=10)
except:  # Показываем текст, если логотип не загружен
    logo_label = ctk.CTkLabel(root,
                              text="AI Image Classifier",
                              font=("Arial", 18, "bold"),
                              text_color="#1E90FF")
    logo_label.pack(pady=10)

# Custom Button Creator (подключаем кастомный tKinter так как обычный tKinter не позоляет манипуляции с кнопками такие как радиусы и т.д.)
def create_button(text, command):
    default_fg_color = "#1E90FF"
    hover_fg_color = "#87CEEB"
    default_text_color = "white"
    hover_text_color = "pink"

    btn = ctk.CTkButton(master=root,
                        text=text,
                        command=command,
                        fg_color=default_fg_color,
                        hover_color=hover_fg_color,
                        text_color=default_text_color,
                        corner_radius=3,
                        width=180,
                        height=40,
                        font=("Arial", 14, "bold"))

    def on_enter(e):  # Наведение мыши меняет курсор
        btn.configure(cursor="hand2",
                      fg_color=hover_fg_color,
                      text_color=hover_text_color)

    def on_leave(e):
        btn.configure(cursor="arrow",
                      fg_color=default_fg_color,
                      text_color=default_text_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

# Buttons
load_btn = create_button("Load Image", load_and_predict)
enhance_btn = create_button("Enhance Resolution", enhance_image)
change_btn = create_button("Change Image", load_and_predict)
save_btn = create_button("Save Result", save_result)
cancel_btn = create_button("Cancel", reset_interface)

load_btn.pack(pady=10)

# Theme Toggle Logic
current_theme = "light"

def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
    else:
        current_theme = "light"
    ctk.set_appearance_mode(current_theme)

# Theme Switch Button (переключение темы)
def create_theme_button():
    default_fg_color = "#1E90FF"
    hover_fg_color = "#87CEEB"
    default_text_color = "white"
    hover_text_color = "pink"

    btn = ctk.CTkButton(master=root,
                        text="Theme",
                        command=toggle_theme,
                        fg_color=default_fg_color,
                        hover_color=hover_fg_color,
                        text_color=default_text_color,
                        width=100,
                        height=30,
                        font=("Arial", 12, "bold"))

    def on_enter(e):
        btn.configure(cursor="hand2",
                      fg_color=hover_fg_color,
                      text_color=hover_text_color)

    def on_leave(e):
        btn.configure(cursor="arrow",
                      fg_color=default_fg_color,
                      text_color=default_text_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

theme_btn = create_theme_button()
theme_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

def on_closing():
    root.destroy() # Завершение процесса

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start App (Запуск главного цикла приложения)
root.mainloop()
