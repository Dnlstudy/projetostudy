import tkinter as tk
from tkinter import ttk, messagebox
from utils.file_utils import load_channels, save_channels
from utils.youtube_utils import get_youtube_client, get_channel_info, extract_channel_id

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studyflix Admin")
        self.root.geometry("800x600")
        
        # Carregar dados
        self.channels_data = load_channels()
        
        # Criar notebook para abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Aba de Categorias
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text='Categorias')
        self.setup_categories_tab()
        
        # Aba de Canais
        self.channels_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.channels_frame, text='Canais')
        self.setup_channels_tab()

    def setup_categories_tab(self):
        # Frame para adicionar categoria
        add_frame = ttk.LabelFrame(self.categories_frame, text="Adicionar Categoria")
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5)
        self.cat_id = ttk.Entry(add_frame)
        self.cat_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Nome:").grid(row=0, column=2, padx=5, pady=5)
        self.cat_name = ttk.Entry(add_frame)
        self.cat_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
        self.cat_desc = ttk.Entry(add_frame, width=50)
        self.cat_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Adicionar", command=self.add_category).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Lista de categorias
        list_frame = ttk.LabelFrame(self.categories_frame, text="Categorias Existentes")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.cat_tree = ttk.Treeview(list_frame, columns=('ID', 'Nome', 'Descrição'), show='headings')
        self.cat_tree.heading('ID', text='ID')
        self.cat_tree.heading('Nome', text='Nome')
        self.cat_tree.heading('Descrição', text='Descrição')
        self.cat_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(list_frame, text="Remover Selecionada", command=self.remove_category).pack(pady=5)
        
        self.update_categories_list()

    def setup_channels_tab(self):
        # Frame para adicionar canal
        add_frame = ttk.LabelFrame(self.channels_frame, text="Adicionar Canal")
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="URL do Canal:").grid(row=0, column=0, padx=5, pady=5)
        self.channel_url = ttk.Entry(add_frame, width=50)
        self.channel_url.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Categoria:").grid(row=1, column=0, padx=5, pady=5)
        self.channel_category = ttk.Combobox(add_frame, values=list(self.channels_data["categories"].keys()))
        self.channel_category.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Matéria:").grid(row=2, column=0, padx=5, pady=5)
        self.channel_subject = ttk.Entry(add_frame)
        self.channel_subject.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Adicionar", command=self.add_channel).grid(row=3, column=0, columnspan=3, pady=10)
        
        # Lista de canais
        list_frame = ttk.LabelFrame(self.channels_frame, text="Canais Cadastrados")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.channel_tree = ttk.Treeview(list_frame, columns=('Nome', 'Matéria', 'Categoria'), show='headings')
        self.channel_tree.heading('Nome', text='Nome')
        self.channel_tree.heading('Matéria', text='Matéria')
        self.channel_tree.heading('Categoria', text='Categoria')
        self.channel_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(list_frame, text="Remover Selecionado", command=self.remove_channel).pack(pady=5)
        
        self.update_channels_list()

    def add_category(self):
        cat_id = self.cat_id.get().strip().lower()
        name = self.cat_name.get().strip()
        desc = self.cat_desc.get().strip()
        
        if not cat_id or not name:
            messagebox.showerror("Erro", "ID e Nome são obrigatórios!")
            return
        
        if not cat_id.isalnum():
            messagebox.showerror("Erro", "ID deve conter apenas letras e números!")
            return
        
        if cat_id in self.channels_data["categories"]:
            messagebox.showerror("Erro", "Esta categoria já existe!")
            return
        
        self.channels_data["categories"][cat_id] = {
            "name": name,
            "description": desc
        }
        
        save_channels(self.channels_data)
        self.update_categories_list()
        
        # Limpar campos
        self.cat_id.delete(0, tk.END)
        self.cat_name.delete(0, tk.END)
        self.cat_desc.delete(0, tk.END)
        
        messagebox.showinfo("Sucesso", "Categoria adicionada com sucesso!")

    def remove_category(self):
        selection = self.cat_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma categoria para remover!")
            return
        
        cat_id = self.cat_tree.item(selection[0])['values'][0]
        
        # Verificar se há canais nesta categoria
        has_channels = any(ch.get("category") == cat_id for ch in self.channels_data.get("featured_channels", []))
        if has_channels:
            messagebox.showerror("Erro", "Não é possível remover uma categoria que possui canais!")
            return
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover esta categoria?"):
            del self.channels_data["categories"][cat_id]
            save_channels(self.channels_data)
            self.update_categories_list()
            messagebox.showinfo("Sucesso", "Categoria removida com sucesso!")

    def add_channel(self):
        url = self.channel_url.get().strip()
        category = self.channel_category.get()
        subject = self.channel_subject.get().strip()
        
        if not url or not category or not subject:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            channel_id = extract_channel_id(url)
            if not channel_id:
                messagebox.showerror("Erro", "URL do canal inválida!")
                return
            
            # Verificar se o canal já existe
            if any(ch.get("id") == channel_id for ch in self.channels_data.get("featured_channels", [])):
                messagebox.showerror("Erro", "Este canal já está cadastrado!")
                return
            
            youtube = get_youtube_client()
            channel_info = get_channel_info(youtube, channel_id)
            
            if not channel_info:
                messagebox.showerror("Erro", "Não foi possível obter informações do canal!")
                return
            
            new_channel = {
                "id": channel_id,
                "name": channel_info["title"],
                "subject": subject,
                "category": category,
                "thumbnail": channel_info["thumbnail"],
                "featured": False
            }
            
            if "featured_channels" not in self.channels_data:
                self.channels_data["featured_channels"] = []
            
            self.channels_data["featured_channels"].append(new_channel)
            save_channels(self.channels_data)
            self.update_channels_list()
            
            # Limpar campos
            self.channel_url.delete(0, tk.END)
            self.channel_subject.delete(0, tk.END)
            self.channel_category.set('')
            
            messagebox.showinfo("Sucesso", f"Canal '{channel_info['title']}' adicionado com sucesso!")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar canal: {str(e)}")

    def remove_channel(self):
        selection = self.channel_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um canal para remover!")
            return
        
        channel_name = self.channel_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o canal '{channel_name}'?"):
            # Encontrar e remover o canal
            self.channels_data["featured_channels"] = [
                ch for ch in self.channels_data["featured_channels"]
                if ch["name"] != channel_name
            ]
            save_channels(self.channels_data)
            self.update_channels_list()
            messagebox.showinfo("Sucesso", "Canal removido com sucesso!")

    def update_categories_list(self):
        # Limpar lista atual
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        
        # Adicionar categorias
        for cat_id, category in self.channels_data["categories"].items():
            self.cat_tree.insert('', 'end', values=(cat_id, category["name"], category["description"]))
        
        # Atualizar combobox de categorias na aba de canais
        self.channel_category['values'] = list(self.channels_data["categories"].keys())

    def update_channels_list(self):
        # Limpar lista atual
        for item in self.channel_tree.get_children():
            self.channel_tree.delete(item)
        
        # Adicionar canais
        for channel in self.channels_data.get("featured_channels", []):
            category_name = self.channels_data["categories"][channel["category"]]["name"]
            self.channel_tree.insert('', 'end', values=(channel["name"], channel["subject"], category_name))

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
