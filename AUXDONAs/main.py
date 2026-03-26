import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
from datetime import datetime

class AUXDONAs:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 AUXDONAs - Gestor Financeiro Doméstico")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # Cores da aplicação
        self.colors = {
            'navy_blue': '#1e3a8a',
            'off_white': '#f8fafc',
            'green': '#10b981',
            'red': '#ef4444',
            'light_gray': '#e2e8f0',
            'dark_gray': '#64748b',
            'white': '#ffffff'
        }
        
        # Dados
        self.transactions = []
        self.data_file = "auxdonas_data.json"
        self.load_data()
        
        self.setup_ui()
        self.update_dashboard()
        self.update_tree()  # ✅ Carrega histórico ao iniciar
    
    def setup_ui(self):
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'), foreground=self.colors['navy_blue'])
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='white')
        style.configure('Value.TLabel', font=('Arial', 28, 'bold'))
        style.configure('Chart.TLabel', font=('Arial', 11, 'bold'))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Cabeçalho
        header_frame = tk.Frame(main_frame, bg=self.colors['navy_blue'], height=90)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        header_frame.grid_propagate(False)
        
        ttk.Label(header_frame, text="💰 AUXDONAs", style='Title.TLabel').place(relx=0.5, rely=0.5, anchor='center')
        
        # Formulário de entrada
        form_frame = ttk.LabelFrame(main_frame, text="➕ Nova Transação", padding="20")
        form_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        form_frame.columnconfigure(1, weight=1)
        
        # Descrição
        ttk.Label(form_frame, text="Descrição:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=10, padx=(0, 15))
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var, width=35, font=('Arial', 11))
        self.desc_entry.grid(row=0, column=1, pady=10, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Valor
        ttk.Label(form_frame, text="Valor (R$):", font=('Arial', 11, 'bold')).grid(row=0, column=2, sticky=tk.W, pady=10)
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(form_frame, textvariable=self.value_var, width=15, font=('Arial', 11))
        self.value_entry.grid(row=0, column=3, pady=10, padx=(0, 20))
        self.value_entry.bind('<Return>', lambda e: self.add_transaction())
        
        # Tipo
        ttk.Label(form_frame, text="Tipo:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(15, 10))
        self.tipo_var = tk.StringVar(value="Saída")
        tipo_frame = ttk.Frame(form_frame)
        tipo_frame.grid(row=1, column=1, sticky=tk.W, pady=(15, 10))
        
        ttk.Radiobutton(tipo_frame, text="💰 Entrada", variable=self.tipo_var, value="Entrada",
                       command=self.on_tipo_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(tipo_frame, text="💸 Saída", variable=self.tipo_var, value="Saída",
                       command=self.on_tipo_change).pack(side=tk.LEFT)
        
        # Botão adicionar
        self.add_btn = ttk.Button(form_frame, text="➕ ADICIONAR TRANSAÇÃO", 
                                 command=self.add_transaction)
        self.add_btn.grid(row=1, column=3, pady=(15, 10), sticky=tk.E)
        
        # Dashboard
        dashboard_frame = ttk.LabelFrame(main_frame, text="📊 Dashboard Financeiro", padding="25")
        dashboard_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        dashboard_frame.columnconfigure(1, weight=1)
        
        # Saldo total
        saldo_container = tk.Frame(dashboard_frame, bg=self.colors['off_white'], relief='raised', bd=2)
        saldo_container.grid(row=0, column=0, padx=(0, 30), sticky=tk.N)
        saldo_container.place(relwidth=0.25, relheight=1)
        
        ttk.Label(saldo_container, text="SALDO TOTAL", font=('Arial', 12, 'bold')).place(relx=0.5, rely=0.1, anchor='center')
        self.saldo_label = ttk.Label(saldo_container, text="R$ 0,00", style='Value.TLabel')
        self.saldo_label.place(relx=0.5, rely=0.5, anchor='center')
        ttk.Label(saldo_container, text="Atualizado em tempo real", font=('Arial', 9)).place(relx=0.5, rely=0.85, anchor='center')
        
        # Gráfico
        chart_frame = tk.Frame(dashboard_frame, bg=self.colors['off_white'], relief='raised', bd=2)
        chart_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 20))
        chart_frame.columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(chart_frame, height=160, bg=self.colors['off_white'], 
                               highlightthickness=0, relief='flat')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)
        
        # Botões de gestão
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        btn_frame.columnconfigure(1, weight=1)
        
        self.delete_btn = ttk.Button(btn_frame, text="🗑️ Excluir Selecionado", 
                                    command=self.delete_selected, width=20)
        self.delete_btn.grid(row=0, column=0, padx=(0, 15), pady=10, sticky=tk.W)
        
        self.clear_btn = ttk.Button(btn_frame, text="🧹 Limpar Todo Histórico", 
                                   command=self.clear_all, width=22)
        self.clear_btn.grid(row=0, column=2, padx=15, pady=10, sticky=tk.W)
        
        # Treeview - Histórico ✅ FUNCIONANDO
        tree_frame = ttk.LabelFrame(main_frame, text="📋 Histórico Completo", padding="15")
        tree_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Configurar Treeview
        columns = ('Data', 'Descrição', 'Tipo', 'Valor')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=14)
        
        # Cabeçalhos
        self.tree.heading('Data', text='Data/Hora')
        self.tree.heading('Descrição', text='Descrição')
        self.tree.heading('Tipo', text='Tipo')
        self.tree.heading('Valor', text='Valor (R$)')
        
        # Largura das colunas
        self.tree.column('Data', width=130, anchor='center')
        self.tree.column('Descrição', width=350)
        self.tree.column('Tipo', width=90, anchor='center')
        self.tree.column('Valor', width=130, anchor='e')
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def on_tipo_change(self):
        pass
    
    def add_transaction(self):
        desc = self.desc_var.get().strip()
        try:
            value = float(self.value_var.get().replace(',', '.'))
            if value <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            messagebox.showerror("❌ Erro", "Valor inválido! Use números positivos (ex: 150,50)")
            return
        
        if len(desc) < 2:
            messagebox.showerror("❌ Erro", "Descrição deve ter pelo menos 2 caracteres!")
            return
        
        # Criar transação
        transaction = {
            'id': len(self.transactions) + 1,
            'data': datetime.now().strftime("%d/%m %H:%M"),
            'descricao': desc[:50],
            'tipo': self.tipo_var.get(),
            'valor': value
        }
        
        self.transactions.append(transaction)
        self.update_tree()
        self.update_dashboard()
        self.save_data()
        
        # Limpar e focar
        self.desc_var.set("")
        self.value_var.set("")
        self.desc_entry.focus()
        
        messagebox.showinfo("✅ Sucesso", f"Transação '{desc}' adicionada!")
    
    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        self.tree.focus(item)
    
    def update_tree(self):
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar transações ordenadas por data (mais recente primeiro)
        sorted_transactions = sorted(self.transactions, key=lambda x: x.get('data', ''), reverse=True)
        
        for trans in sorted_transactions:
            tag = 'entrada' if trans['tipo'] == 'Entrada' else 'saida'
            valor_fmt = f"+ R$ {trans['valor']:.2f}".replace('.', ',') if trans['tipo'] == 'Entrada' else f"- R$ {trans['valor']:.2f}".replace('.', ',')
            
            self.tree.insert('', 'end', values=(
                trans['data'],
                trans['descricao'],
                trans['tipo'],
                valor_fmt
            ), tags=(tag,))
        
        # Configurar cores
        self.tree.tag_configure('entrada', foreground=self.colors['green'], font=('Arial', 9, 'bold'))
        self.tree.tag_configure('saida', foreground=self.colors['red'], font=('Arial', 9, 'bold'))
    
    def update_dashboard(self):
        total_entradas = sum(t['valor'] for t in self.transactions if t['tipo'] == 'Entrada')
        total_saidas = sum(t['valor'] for t in self.transactions if t['tipo'] == 'Saída')
        saldo = total_entradas - total_saidas
        
        # Atualizar saldo
        saldo_abs = abs(saldo)
        if saldo >= 0:
            saldo_str = f"+ R$ {saldo_abs:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            color = self.colors['green']
        else:
            saldo_str = f"- R$ {saldo_abs:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            color = self.colors['red']
        
        self.saldo_label.configure(text=saldo_str, foreground=color)
        
        # Gráfico
        self.draw_improved_chart(total_entradas, total_saidas, max(total_entradas, total_saidas, 100))
    
    def draw_improved_chart(self, entradas, saidas, max_value):
        self.canvas.delete("all")
        canvas_width = max(self.canvas.winfo_width(), 500)
        canvas_height = 140
        
        # Fundo
        self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill=self.colors['off_white'], outline='')
        
        bar_width = 80
        bar_spacing = 25
        max_bar_height = canvas_height - 80
        
        # Barra ENTRADAS
        entrada_height = min((entradas / max_value) * max_bar_height, max_bar_height)
        x1, y1 = bar_spacing, canvas_height - 20 - entrada_height
        x2, y2 = x1 + bar_width, canvas_height - 20
        
        self.canvas.create_rectangle(x1+2, y1+2, x2+2, y2+2, fill='#d1d5db', outline='')
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors['green'], outline=self.colors['green'], width=3)
        self.canvas.create_rectangle(x1, y1, x1+25, y1+15, fill='#34d399', outline='')
        
        self.canvas.create_text(x1 + bar_width/2, 25, text="ENTRADAS", font=('Arial', 12, 'bold'), 
                              fill=self.colors['green'], anchor='center')
        valor_entradas = f"R$ {entradas:,.0f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        self.canvas.create_text(x1 + bar_width/2, 45, text=valor_entradas, font=('Arial', 11), 
                              fill=self.colors['dark_gray'], anchor='center')
        
        # Barra SAÍDAS
        saida_height = min((saidas / max_value) * max_bar_height, max_bar_height)
        x1 = canvas_width - bar_spacing - bar_width
        y1 = canvas_height - 20 - saida_height
        x2 = x1 + bar_width
        y2 = canvas_height - 20
        
        self.canvas.create_rectangle(x1+2, y1+2, x2+2, y2+2, fill='#f87171', outline='')
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors['red'], outline=self.colors['red'], width=3)
        self.canvas.create_rectangle(x1, y1, x1+25, y1+15, fill='#f87171', outline='')
        
        self.canvas.create_text(x1 + bar_width/2, 25, text="SAÍDAS", font=('Arial', 12, 'bold'), 
                              fill=self.colors['red'], anchor='center')
        valor_saidas = f"R$ {saidas:,.0f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        self.canvas.create_text(x1 + bar_width/2, 45, text=valor_saidas, font=('Arial', 11), 
                              fill=self.colors['dark_gray'], anchor='center')
        
        self.canvas.create_line(canvas_width/2 - 20, 60, canvas_width/2 + 20, 60, 
                              fill=self.colors['light_gray'], width=2)
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Aviso", "Selecione uma transação no histórico!")
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        desc = values[1]
        
        if messagebox.askyesno("🗑️ Confirmar", f"Excluir:\n'{desc}'?"):
            # Remover pelo índice da treeview
            index = self.tree.index(selected[0])
            if 0 <= index < len(self.transactions):
                del self.transactions[index]
                self.update_tree()
                self.update_dashboard()
                self.save_data()
                messagebox.showinfo("✅ Excluído", "Transação removida com sucesso!")
    
    def clear_all(self):
        if not self.transactions:
            messagebox.showinfo("ℹ️ Info", "Histórico vazio!")
            return
        
        if messagebox.askyesno("🧹 Limpar Tudo", 
            f"Limpar {len(self.transactions)} transações?\n⚠️ Não há volta!"):
            self.transactions = []
            self.update_tree()
            self.update_dashboard()
            self.save_data()
            messagebox.showinfo("✅ Limpo", "Histórico zerado!")
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.transactions, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # ✅ Validar dados carregados
                    self.transactions = []
                    for item in loaded_data:
                        if all(key in item for key in ['data', 'descricao', 'tipo', 'valor']):
                            self.transactions.append(item)
            except Exception:
                self.transactions = []
        else:
            self.transactions = []

def main():
    root = tk.Tk()
    app = AUXDONAs(root)
    root.mainloop()

if __name__ == "__main__":
    main()