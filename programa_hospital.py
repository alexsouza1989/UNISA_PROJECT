import sqlite3
import os
from tkinter import Tk, Toplevel, StringVar, messagebox, PhotoImage, Menu
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import csv
import shutil
import re

# Configuração inicial do banco de dados
def setup_database():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER,
                        address TEXT,
                        contact TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        specialty TEXT,
                        schedule TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        doctor_id INTEGER,
                        date TEXT,
                        time TEXT,
                        FOREIGN KEY(patient_id) REFERENCES patients(id),
                        FOREIGN KEY(doctor_id) REFERENCES doctors(id))''')
    # Tabela de usuários para login (opcional)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
    # Inserir usuário padrão se não existir
    cursor.execute("SELECT * FROM users")
    if not cursor.fetchall():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
    conn.close()

# Estilos personalizados
def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')  # Experimente 'alt', 'default', 'classic'
    
    # Estilos para Frames
    style.configure('TFrame', background='#f0f0f0')
    
    # Estilos para Labels
    style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
    
    # Estilos para Buttons
    style.configure('TButton',
                    font=('Arial', 10),  # Reduziu o tamanho da fonte de 12 para 10
                    padding=5,           # Reduziu o padding de 10 para 5
                    relief='flat',
                    foreground='#ffffff',
                    background='#4CAF50')
    style.map('TButton',
              background=[('active', '#45a049')])
    
    # Estilos para Entries e Combobox
    style.configure('TEntry', font=('Arial', 12), padding=5)
    style.configure('TCombobox', font=('Arial', 12))
    
    # Estilos para Treeview
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0")
    style.map('Treeview', background=[('selected', '#347083')])

# Função para exportar consultas para CSV
def export_appointments_to_csv():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT appointments.id, patients.name, doctors.name, appointments.date, appointments.time
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
    """)
    appointments = cursor.fetchall()
    conn.close()

    if not appointments:
        messagebox.showerror("Erro", "Nenhuma consulta para exportar.")
        return

    file_path = asksaveasfilename(defaultextension=".csv",
                                  filetypes=[("CSV files", "*.csv")],
                                  title="Salvar Consultas Como")
    if file_path:
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Paciente", "Médico", "Data", "Hora"])
                writer.writerows(appointments)
            messagebox.showinfo("Sucesso", f"Consultas exportadas para {file_path} com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar as consultas: {e}")

# Função para backup do banco de dados
def backup_database():
    backup_path = asksaveasfilename(defaultextension=".db",
                                    filetypes=[("SQLite DB", "*.db")],
                                    title="Salvar Backup do Banco de Dados")
    if backup_path:
        try:
            shutil.copy("hospital.db", backup_path)
            messagebox.showinfo("Sucesso", f"Backup realizado com sucesso em {backup_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao realizar o backup: {e}")

# Função para restaurar o banco de dados
def restore_database():
    restore_path = askopenfilename(defaultextension=".db",
                                   filetypes=[("SQLite DB", "*.db")],
                                   title="Selecionar Backup para Restauração")
    if restore_path:
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja restaurar o banco de dados? Todos os dados atuais serão perdidos.")
        if confirm:
            try:
                shutil.copy(restore_path, "hospital.db")
                messagebox.showinfo("Sucesso", "Banco de dados restaurado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao restaurar o banco de dados: {e}")

# Janela principal
def main_window():
    root = Tk()
    root.title("Sistema de Gestão Hospitalar")
    root.state('zoomed')  # Inicia a janela maximizada (tela cheia)
    root.configure(background='#f0f0f0')

    configure_styles()

    # Carregar ícones
    icons = {}
    icon_names = {
        'add': 'add.png',
        'view': 'view.png',
        'search': 'search.png',
        'export': 'export.png',
        'backup': 'backup.png',
        'restore': 'restore.png',
        'exit': 'exit.png'
    }
    icons_path = os.path.join(os.getcwd(), "icons")
    for key, filename in icon_names.items():
        path = os.path.join(icons_path, filename)
        if os.path.exists(path):
            icons[key] = PhotoImage(file=path)
        else:
            icons[key] = None  # Pode definir um ícone padrão ou None

    # Configuração da barra de menus
    menubar = Menu(root)
    
    # Menu de Pacientes
    menu_pacientes = Menu(menubar, tearoff=0)
    menu_pacientes.add_command(label="Cadastrar Paciente", command=register_patient)
    menu_pacientes.add_command(label="Visualizar Pacientes", command=view_patients)
    menu_pacientes.add_command(label="Buscar Pacientes", command=search_patients)
    menubar.add_cascade(label="Pacientes", menu=menu_pacientes)
    
    # Menu de Médicos
    menu_medicos = Menu(menubar, tearoff=0)
    menu_medicos.add_command(label="Cadastrar Médico", command=register_doctor)
    menu_medicos.add_command(label="Visualizar Médicos", command=view_doctors)
    menubar.add_cascade(label="Médicos", menu=menu_medicos)
    
    # Menu de Consultas
    menu_consultas = Menu(menubar, tearoff=0)
    menu_consultas.add_command(label="Agendar Consulta", command=schedule_appointment)
    menu_consultas.add_command(label="Visualizar Consultas", command=view_appointments)
    menu_consultas.add_command(label="Exportar Consultas (CSV)", command=export_appointments_to_csv)
    menubar.add_cascade(label="Consultas", menu=menu_consultas)
    
    # Menu de Ferramentas
    menu_ferramentas = Menu(menubar, tearoff=0)
    menu_ferramentas.add_command(label="Backup do Banco de Dados", command=backup_database)
    menu_ferramentas.add_command(label="Restaurar Banco de Dados", command=restore_database)
    menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas)
    
    # Menu de Sair
    menubar.add_command(label="Sair", command=root.quit)
    
    root.config(menu=menubar)

    # Frame principal com botões
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(expand=True)

    ttk.Label(main_frame, text="Bem-vindo ao Sistema!", font=("Arial", 24, 'bold')).grid(row=0, column=0, pady=40)

    # Reduziu o width de 30 para 20 nos botões
    btn_register_patient = ttk.Button(main_frame, text="Cadastrar Paciente", image=icons['add'], compound='left', width=20, command=register_patient)
    btn_register_patient.grid(row=1, column=0, pady=10)

    btn_view_patients = ttk.Button(main_frame, text="Visualizar Pacientes", image=icons['view'], compound='left', width=20, command=view_patients)
    btn_view_patients.grid(row=2, column=0, pady=10)

    btn_search_patients = ttk.Button(main_frame, text="Buscar Pacientes", image=icons['search'], compound='left', width=20, command=search_patients)
    btn_search_patients.grid(row=3, column=0, pady=10)

    btn_register_doctor = ttk.Button(main_frame, text="Cadastrar Médico", image=icons['add'], compound='left', width=20, command=register_doctor)
    btn_register_doctor.grid(row=4, column=0, pady=10)

    btn_view_doctors = ttk.Button(main_frame, text="Visualizar Médicos", image=icons['view'], compound='left', width=20, command=view_doctors)
    btn_view_doctors.grid(row=5, column=0, pady=10)

    btn_schedule_appointment = ttk.Button(main_frame, text="Agendar Consulta", image=icons['add'], compound='left', width=20, command=schedule_appointment)
    btn_schedule_appointment.grid(row=6, column=0, pady=10)

    btn_view_appointments = ttk.Button(main_frame, text="Visualizar Consultas", image=icons['view'], compound='left', width=20, command=view_appointments)
    btn_view_appointments.grid(row=7, column=0, pady=10)

    btn_export_appointments = ttk.Button(main_frame, text="Exportar Consultas (CSV)", image=icons['export'], compound='left', width=20, command=export_appointments_to_csv)
    btn_export_appointments.grid(row=8, column=0, pady=10)

    btn_backup = ttk.Button(main_frame, text="Backup do Banco de Dados", image=icons['backup'], compound='left', width=20, command=backup_database)
    btn_backup.grid(row=9, column=0, pady=10)

    btn_restore = ttk.Button(main_frame, text="Restaurar Banco de Dados", image=icons['restore'], compound='left', width=20, command=restore_database)
    btn_restore.grid(row=10, column=0, pady=10)

    btn_exit = ttk.Button(main_frame, text="Sair", image=icons['exit'], compound='left', width=20, command=root.quit)
    btn_exit.grid(row=11, column=0, pady=20)

    root.mainloop()

# Função para cadastrar pacientes
def register_patient():
    def save_patient():
        name = entry_name.get().strip()
        age = entry_age.get().strip()
        address = entry_address.get().strip()
        contact = entry_contact.get().strip()
        
        if not (name and age and address and contact):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Erro", "A idade deve ser um número.")
            return
        
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, address, contact) VALUES (?, ?, ?, ?)", 
                       (name, age, address, contact))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
        reg_window.destroy()
    
    reg_window = Toplevel()
    reg_window.title("Cadastrar Paciente")
    reg_window.geometry("400x400")
    reg_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')

    reg_frame = ttk.Frame(reg_window, padding=20)
    reg_frame.pack(expand=True, fill='both')

    ttk.Label(reg_frame, text="Cadastrar Paciente", font=("Arial", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)

    ttk.Label(reg_frame, text="Nome:").grid(row=1, column=0, sticky='e', pady=10, padx=10)
    entry_name = ttk.Entry(reg_frame, width=30)
    entry_name.grid(row=1, column=1, pady=10, padx=10)

    ttk.Label(reg_frame, text="Idade:").grid(row=2, column=0, sticky='e', pady=10, padx=10)
    entry_age = ttk.Entry(reg_frame, width=30)
    entry_age.grid(row=2, column=1, pady=10, padx=10)

    ttk.Label(reg_frame, text="Endereço:").grid(row=3, column=0, sticky='e', pady=10, padx=10)
    entry_address = ttk.Entry(reg_frame, width=30)
    entry_address.grid(row=3, column=1, pady=10, padx=10)

    ttk.Label(reg_frame, text="Contato:").grid(row=4, column=0, sticky='e', pady=10, padx=10)
    entry_contact = ttk.Entry(reg_frame, width=30)
    entry_contact.grid(row=4, column=1, pady=10, padx=10)

    btn_save = ttk.Button(reg_frame, text="Salvar", command=save_patient)
    btn_save.grid(row=5, column=0, columnspan=2, pady=20)

# Função para cadastrar médicos
def register_doctor():
    def save_doctor():
        name = entry_name.get().strip()
        specialty = entry_specialty.get().strip()
        schedule = entry_schedule.get().strip()
        
        if not (name and specialty and schedule):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO doctors (name, specialty, schedule) VALUES (?, ?, ?)", 
                       (name, specialty, schedule))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Médico cadastrado com sucesso!")
        doc_window.destroy()
    
    doc_window = Toplevel()
    doc_window.title("Cadastrar Médico")
    doc_window.geometry("400x400")
    doc_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')

    doc_frame = ttk.Frame(doc_window, padding=20)
    doc_frame.pack(expand=True, fill='both')

    ttk.Label(doc_frame, text="Cadastrar Médico", font=("Arial", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)

    ttk.Label(doc_frame, text="Nome:").grid(row=1, column=0, sticky='e', pady=10, padx=10)
    entry_name = ttk.Entry(doc_frame, width=30)
    entry_name.grid(row=1, column=1, pady=10, padx=10)

    ttk.Label(doc_frame, text="Especialidade:").grid(row=2, column=0, sticky='e', pady=10, padx=10)
    entry_specialty = ttk.Entry(doc_frame, width=30)
    entry_specialty.grid(row=2, column=1, pady=10, padx=10)

    ttk.Label(doc_frame, text="Horário de Trabalho:").grid(row=3, column=0, sticky='e', pady=10, padx=10)
    entry_schedule = ttk.Entry(doc_frame, width=30)
    entry_schedule.grid(row=3, column=1, pady=10, padx=10)

    btn_save = ttk.Button(doc_frame, text="Salvar", command=save_doctor)
    btn_save.grid(row=4, column=0, columnspan=2, pady=20)

# Função para agendar consultas
def schedule_appointment():
    def save_appointment():
        selected_patient = patient_var.get()
        selected_doctor = doctor_var.get()
        date = entry_date.get().strip()
        time = entry_time.get().strip()
        
        if not (selected_patient and selected_doctor and date and time):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        try:
            patient_id = int(selected_patient.split(":")[0])
            doctor_id = int(selected_doctor.split(":")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Seleção inválida de paciente ou médico.")
            return
        
        # Validação da data (DD/MM/AAAA)
        if not re.match(r"\d{2}/\d{2}/\d{4}", date):
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return
        
        # Validação da hora (HH:MM)
        if not re.match(r"^\d{2}:\d{2}$", time):
            messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")
            return
        
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)", 
                       (patient_id, doctor_id, date, time))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Consulta agendada com sucesso!")
        app_window.destroy()
    
    # Recuperar lista de pacientes e médicos
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    
    conn.close()
    
    if not patients:
        messagebox.showerror("Erro", "Nenhum paciente cadastrado. Por favor, cadastre um paciente primeiro.")
        return
    
    if not doctors:
        messagebox.showerror("Erro", "Nenhum médico cadastrado. Por favor, cadastre um médico primeiro.")
        return

    app_window = Toplevel()
    app_window.title("Agendar Consulta")
    app_window.geometry("500x400")
    app_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')

    app_frame = ttk.Frame(app_window, padding=20)
    app_frame.pack(expand=True, fill='both')

    ttk.Label(app_frame, text="Agendar Consulta", font=("Arial", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)

    ttk.Label(app_frame, text="Paciente:").grid(row=1, column=0, sticky='e', pady=10, padx=10)
    patient_var = StringVar(app_window)
    patient_options = [f"{patient[0]}: {patient[1]}" for patient in patients]
    patient_combobox = ttk.Combobox(app_frame, textvariable=patient_var, values=patient_options, state='readonly', width=27)
    patient_combobox.current(0)
    patient_combobox.grid(row=1, column=1, pady=10, padx=10)

    ttk.Label(app_frame, text="Médico:").grid(row=2, column=0, sticky='e', pady=10, padx=10)
    doctor_var = StringVar(app_window)
    doctor_options = [f"{doctor[0]}: {doctor[1]}" for doctor in doctors]
    doctor_combobox = ttk.Combobox(app_frame, textvariable=doctor_var, values=doctor_options, state='readonly', width=27)
    doctor_combobox.current(0)
    doctor_combobox.grid(row=2, column=1, pady=10, padx=10)

    ttk.Label(app_frame, text="Data (DD/MM/AAAA):").grid(row=3, column=0, sticky='e', pady=10, padx=10)
    entry_date = ttk.Entry(app_frame, width=30)
    entry_date.grid(row=3, column=1, pady=10, padx=10)

    ttk.Label(app_frame, text="Hora (HH:MM):").grid(row=4, column=0, sticky='e', pady=10, padx=10)
    entry_time = ttk.Entry(app_frame, width=30)
    entry_time.grid(row=4, column=1, pady=10, padx=10)

    # Reduziu o width de 30 para 20 no botão
    btn_schedule = ttk.Button(app_frame, text="Agendar", command=save_appointment, width=20)
    btn_schedule.grid(row=5, column=0, columnspan=2, pady=20)

# Função para visualizar pacientes
def view_patients():
    view_window = Toplevel()
    view_window.title("Lista de Pacientes")
    view_window.geometry("700x400")
    view_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0")

    style.map('Treeview', background=[('selected', '#347083')])

    tree = ttk.Treeview(view_window, columns=("ID", "Nome", "Idade", "Endereço", "Contato"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Idade", text="Idade")
    tree.heading("Endereço", text="Endereço")
    tree.heading("Contato", text="Contato")
    
    tree.column("ID", width=50, anchor='center')
    tree.column("Nome", width=150)
    tree.column("Idade", width=50, anchor='center')
    tree.column("Endereço", width=200)
    tree.column("Contato", width=100)
    
    # Inserir dados na Treeview
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()
    
    tree.pack(fill='both', expand=True)

    # Funções para editar e deletar
    def on_double_click(event):
        selected_items = tree.selection()
        if selected_items:
            item = selected_items[0]
            patient_id = tree.item(item, "values")[0]
            edit_patient(patient_id)

    def delete_patient():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione um paciente para deletar.")
            return
        patient_id = tree.item(selected_items[0], "values")[0]
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este paciente?")
        if confirm:
            try:
                conn = sqlite3.connect("hospital.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                conn.commit()
                conn.close()
                tree.delete(selected_items[0])
                messagebox.showinfo("Sucesso", "Paciente deletado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao deletar o paciente: {e}")

    tree.bind("<Double-1>", on_double_click)

    # Botões para deletar e fechar
    btn_frame = ttk.Frame(view_window, padding=10)
    btn_frame.pack()

    # Reduziu o width de 30 para 20 nos botões, se aplicável
    btn_delete = ttk.Button(btn_frame, text="Deletar Paciente", command=delete_patient, width=20)
    btn_delete.pack(side='left', padx=10)

    btn_close = ttk.Button(btn_frame, text="Fechar", command=view_window.destroy, width=20)
    btn_close.pack(side='left', padx=10)

# Função para editar paciente
def edit_patient(patient_id):
    def update_patient():
        name = entry_name.get().strip()
        age = entry_age.get().strip()
        address = entry_address.get().strip()
        contact = entry_contact.get().strip()
        
        if not (name and age and address and contact):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Erro", "A idade deve ser um número.")
            return
        
        try:
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patients
                SET name = ?, age = ?, address = ?, contact = ?
                WHERE id = ?
            """, (name, age, address, contact, patient_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Paciente atualizado com sucesso!")
            edit_window.destroy()
            view_patients()  # Atualiza a lista
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o paciente: {e}")

    # Buscar dados do paciente
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        messagebox.showerror("Erro", "Paciente não encontrado.")
        return
    
    edit_window = Toplevel()
    edit_window.title("Editar Paciente")
    edit_window.geometry("400x400")
    edit_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')
    
    edit_frame = ttk.Frame(edit_window, padding=20)
    edit_frame.pack(expand=True, fill='both')
    
    ttk.Label(edit_frame, text="Editar Paciente", font=("Arial", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
    
    ttk.Label(edit_frame, text="Nome:").grid(row=1, column=0, sticky='e', pady=10, padx=10)
    entry_name = ttk.Entry(edit_frame, width=30)
    entry_name.grid(row=1, column=1, pady=10, padx=10)
    entry_name.insert(0, patient[1])
    
    ttk.Label(edit_frame, text="Idade:").grid(row=2, column=0, sticky='e', pady=10, padx=10)
    entry_age = ttk.Entry(edit_frame, width=30)
    entry_age.grid(row=2, column=1, pady=10, padx=10)
    entry_age.insert(0, patient[2])
    
    ttk.Label(edit_frame, text="Endereço:").grid(row=3, column=0, sticky='e', pady=10, padx=10)
    entry_address = ttk.Entry(edit_frame, width=30)
    entry_address.grid(row=3, column=1, pady=10, padx=10)
    entry_address.insert(0, patient[3])
    
    ttk.Label(edit_frame, text="Contato:").grid(row=4, column=0, sticky='e', pady=10, padx=10)
    entry_contact = ttk.Entry(edit_frame, width=30)
    entry_contact.grid(row=4, column=1, pady=10, padx=10)
    entry_contact.insert(0, patient[4])
    
    btn_update = ttk.Button(edit_frame, text="Atualizar", command=update_patient, width=20)
    btn_update.grid(row=5, column=0, columnspan=2, pady=20)

# Função para visualizar médicos
def view_doctors():
    view_window = Toplevel()
    view_window.title("Lista de Médicos")
    view_window.geometry("700x400")
    view_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0")

    style.map('Treeview', background=[('selected', '#347083')])

    tree = ttk.Treeview(view_window, columns=("ID", "Nome", "Especialidade", "Horário"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Especialidade", text="Especialidade")
    tree.heading("Horário", text="Horário de Trabalho")
    
    tree.column("ID", width=50, anchor='center')
    tree.column("Nome", width=150)
    tree.column("Especialidade", width=150)
    tree.column("Horário", width=150)
    
    # Inserir dados na Treeview
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()
    
    tree.pack(fill='both', expand=True)

    # Funções para editar e deletar
    def on_double_click(event):
        selected_items = tree.selection()
        if selected_items:
            item = selected_items[0]
            doctor_id = tree.item(item, "values")[0]
            edit_doctor(doctor_id)

    def delete_doctor():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione um médico para deletar.")
            return
        doctor_id = tree.item(selected_items[0], "values")[0]
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este médico?")
        if confirm:
            try:
                conn = sqlite3.connect("hospital.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
                conn.commit()
                conn.close()
                tree.delete(selected_items[0])
                messagebox.showinfo("Sucesso", "Médico deletado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao deletar o médico: {e}")

    tree.bind("<Double-1>", on_double_click)

    # Botões para deletar e fechar
    btn_frame = ttk.Frame(view_window, padding=10)
    btn_frame.pack()

    # Reduziu o width de 30 para 20 nos botões
    btn_delete = ttk.Button(btn_frame, text="Deletar Médico", command=delete_doctor, width=20)
    btn_delete.pack(side='left', padx=10)

    btn_close = ttk.Button(btn_frame, text="Fechar", command=view_window.destroy, width=20)
    btn_close.pack(side='left', padx=10)

# Função para editar médico
def edit_doctor(doctor_id):
    def update_doctor():
        name = entry_name.get().strip()
        specialty = entry_specialty.get().strip()
        schedule = entry_schedule.get().strip()
        
        if not (name and specialty and schedule):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        try:
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE doctors
                SET name = ?, specialty = ?, schedule = ?
                WHERE id = ?
            """, (name, specialty, schedule, doctor_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Médico atualizado com sucesso!")
            edit_window.destroy()
            view_doctors()  # Atualiza a lista
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o médico: {e}")

    # Buscar dados do médico
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    conn.close()
    
    if not doctor:
        messagebox.showerror("Erro", "Médico não encontrado.")
        return
    
    edit_window = Toplevel()
    edit_window.title("Editar Médico")
    edit_window.geometry("400x400")
    edit_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')
    
    edit_frame = ttk.Frame(edit_window, padding=20)
    edit_frame.pack(expand=True, fill='both')
    
    ttk.Label(edit_frame, text="Editar Médico", font=("Arial", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
    
    ttk.Label(edit_frame, text="Nome:").grid(row=1, column=0, sticky='e', pady=10, padx=10)
    entry_name = ttk.Entry(edit_frame, width=30)
    entry_name.grid(row=1, column=1, pady=10, padx=10)
    entry_name.insert(0, doctor[1])
    
    ttk.Label(edit_frame, text="Especialidade:").grid(row=2, column=0, sticky='e', pady=10, padx=10)
    entry_specialty = ttk.Entry(edit_frame, width=30)
    entry_specialty.grid(row=2, column=1, pady=10, padx=10)
    entry_specialty.insert(0, doctor[2])
    
    ttk.Label(edit_frame, text="Horário de Trabalho:").grid(row=3, column=0, sticky='e', pady=10, padx=10)
    entry_schedule = ttk.Entry(edit_frame, width=30)
    entry_schedule.grid(row=3, column=1, pady=10, padx=10)
    entry_schedule.insert(0, doctor[3])
    
    # Reduziu o width de 30 para 20 no botão
    btn_update = ttk.Button(edit_frame, text="Atualizar", command=update_doctor, width=20)
    btn_update.grid(row=4, column=0, columnspan=2, pady=20)

# Função para visualizar consultas
def view_appointments():
    view_window = Toplevel()
    view_window.title("Lista de Consultas")
    view_window.geometry("800x400")
    view_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0")

    style.map('Treeview', background=[('selected', '#347083')])

    tree = ttk.Treeview(view_window, columns=("ID", "Paciente", "Médico", "Data", "Hora"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Paciente", text="Paciente")
    tree.heading("Médico", text="Médico")
    tree.heading("Data", text="Data")
    tree.heading("Hora", text="Hora")
    
    tree.column("ID", width=50, anchor='center')
    tree.column("Paciente", width=200)
    tree.column("Médico", width=200)
    tree.column("Data", width=100, anchor='center')
    tree.column("Hora", width=100, anchor='center')
    
    # Inserir dados na Treeview
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT appointments.id, patients.name, doctors.name, appointments.date, appointments.time
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()
    
    tree.pack(fill='both', expand=True)

    # Funções para deletar
    def delete_appointment():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione uma consulta para deletar.")
            return
        appointment_id = tree.item(selected_items[0], "values")[0]
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar esta consulta?")
        if confirm:
            try:
                conn = sqlite3.connect("hospital.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                conn.commit()
                conn.close()
                tree.delete(selected_items[0])
                messagebox.showinfo("Sucesso", "Consulta deletada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao deletar a consulta: {e}")

    tree.bind("<Double-1>", lambda event: None)  # Removido para evitar erros se tentar editar

    # Botões para deletar e fechar
    btn_frame = ttk.Frame(view_window, padding=10)
    btn_frame.pack()

    # Reduziu o width de 30 para 20 nos botões
    btn_delete = ttk.Button(btn_frame, text="Deletar Consulta", command=delete_appointment, width=20)
    btn_delete.pack(side='left', padx=10)

    btn_close = ttk.Button(btn_frame, text="Fechar", command=view_window.destroy, width=20)
    btn_close.pack(side='left', padx=10)

# Função para buscar pacientes
def search_patients():
    def perform_search():
        search_term = entry_search.get().strip()
        for item in tree.get_children():
            tree.delete(item)
        
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + search_term + '%',))
        results = cursor.fetchall()
        conn.close()

        if not results:
            messagebox.showinfo("Resultado da Busca", "Nenhum paciente encontrado com o nome especificado.")
            return

        for row in results:
            tree.insert("", "end", values=row)

    search_window = Toplevel()
    search_window.title("Buscar Pacientes")
    search_window.geometry("700x500")
    search_window.configure(background='#f0f0f0')

    style = ttk.Style()
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0f0f0")

    style.map('Treeview', background=[('selected', '#347083')])

    search_frame = ttk.Frame(search_window, padding=10)
    search_frame.pack()

    ttk.Label(search_frame, text="Buscar Pacientes por Nome:", font=("Arial", 12)).pack(side='left', padx=5)
    entry_search = ttk.Entry(search_frame, width=30)
    entry_search.pack(side='left', padx=5)
    btn_search = ttk.Button(search_frame, text="Buscar", command=perform_search, width=20)  # Reduziu o width para 20
    btn_search.pack(side='left', padx=5)

    tree = ttk.Treeview(search_window, columns=("ID", "Nome", "Idade", "Endereço", "Contato"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Idade", text="Idade")
    tree.heading("Endereço", text="Endereço")
    tree.heading("Contato", text="Contato")
    
    tree.column("ID", width=50, anchor='center')
    tree.column("Nome", width=150)
    tree.column("Idade", width=50, anchor='center')
    tree.column("Endereço", width=200)
    tree.column("Contato", width=100)
    
    tree.pack(fill='both', expand=True, pady=10)

    # Funções para editar e deletar
    def on_double_click(event):
        selected_items = tree.selection()
        if selected_items:
            item = selected_items[0]
            patient_id = tree.item(item, "values")[0]
            edit_patient(patient_id)

    def delete_patient_search():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione um paciente para deletar.")
            return
        patient_id = tree.item(selected_items[0], "values")[0]
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este paciente?")
        if confirm:
            try:
                conn = sqlite3.connect("hospital.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                conn.commit()
                conn.close()
                tree.delete(selected_items[0])
                messagebox.showinfo("Sucesso", "Paciente deletado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao deletar o paciente: {e}")

    tree.bind("<Double-1>", on_double_click)

    # Botões para deletar e fechar
    btn_frame = ttk.Frame(search_window, padding=10)
    btn_frame.pack()

    # Reduziu o width de 30 para 20 nos botões
    btn_delete = ttk.Button(btn_frame, text="Deletar Paciente", command=delete_patient_search, width=20)
    btn_delete.pack(side='left', padx=10)

    btn_close = ttk.Button(btn_frame, text="Fechar", command=search_window.destroy, width=20)
    btn_close.pack(side='left', padx=10)

# Função para visualizar médicos
def view_doctors():
    # ... (mesma implementação anterior)
    # [Código omitido para brevidade]
    pass  # Substitua pelo código fornecido anteriormente

if __name__ == "__main__":
    setup_database()
    main_window()
