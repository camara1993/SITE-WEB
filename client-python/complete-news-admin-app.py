import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
from zeep import Client
from zeep.transports import Transport
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter.font as tkFont
import threading
import time
from functools import wraps

class ModernButton(tk.Frame):
    """Bouton moderne avec effet de survol"""
    def __init__(self, parent, text="", command=None, style="primary", icon="", width=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Couleurs selon le style
        colors = {
            "primary": {"bg": "#007AFF", "hover": "#0051D5", "fg": "white"},
            "success": {"bg": "#34C759", "hover": "#248A3D", "fg": "white"},
            "danger": {"bg": "#FF3B30", "hover": "#C70F0F", "fg": "white"},
            "secondary": {"bg": "#5E5CE6", "hover": "#4B4BC8", "fg": "white"},
            "dark": {"bg": "#1C1C1E", "hover": "#2C2C2E", "fg": "white"},
            "warning": {"bg": "#FF9500", "hover": "#E07F00", "fg": "white"},
        }
        
        self.colors = colors.get(style, colors["primary"])
        self.configure(bg=self.colors["bg"])
        
        # Frame interne pour le padding
        self.inner_frame = tk.Frame(self, bg=self.colors["bg"])
        self.inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Contenu (icône + texte)
        content_frame = tk.Frame(self.inner_frame, bg=self.colors["bg"])
        content_frame.pack(expand=True, padx=15, pady=8)
        
        if icon:
            icon_label = tk.Label(content_frame, text=icon, bg=self.colors["bg"], 
                                 fg=self.colors["fg"], font=("Segoe UI", 12))
            icon_label.pack(side="left", padx=(0, 5))
        
        self.label = tk.Label(content_frame, text=text, bg=self.colors["bg"], 
                             fg=self.colors["fg"], font=("Segoe UI", 10, "bold"))
        self.label.pack(side="left")
        
        # Bindings
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", lambda e: command() if command else None)
        
        for widget in [self.inner_frame, content_frame] + content_frame.winfo_children():
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", lambda e: command() if command else None)
        
        # Curseur
        self.configure(cursor="hand2")
        for widget in [self.inner_frame, content_frame] + content_frame.winfo_children():
            widget.configure(cursor="hand2")
        
    def on_enter(self, e):
        self.configure(bg=self.colors["hover"])
        self.inner_frame.configure(bg=self.colors["hover"])
        self.inner_frame.winfo_children()[0].configure(bg=self.colors["hover"])
        for widget in self.inner_frame.winfo_children()[0].winfo_children():
            widget.configure(bg=self.colors["hover"])
        
    def on_leave(self, e):
        self.configure(bg=self.colors["bg"])
        self.inner_frame.configure(bg=self.colors["bg"])
        self.inner_frame.winfo_children()[0].configure(bg=self.colors["bg"])
        for widget in self.inner_frame.winfo_children()[0].winfo_children():
            widget.configure(bg=self.colors["bg"])

class ModernEntry(tk.Frame):
    """Champ de saisie moderne"""
    def __init__(self, parent, placeholder="", show="", **kwargs):
        super().__init__(parent, bg="#2C2C2E", **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = "#8E8E93"
        self.normal_color = "#FFFFFF"
        
        # Bordure
        self.configure(highlightbackground="#3A3A3C", highlightthickness=1)
        
        # Entry
        self.entry = tk.Entry(self, bg="#1C1C1E", fg=self.placeholder_color, 
                             border=0, font=("Segoe UI", 11), show=show)
        self.entry.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Placeholder
        if placeholder and not show:
            self.entry.insert(0, placeholder)
            self.entry.bind("<FocusIn>", self.on_focus_in)
            self.entry.bind("<FocusOut>", self.on_focus_out)
        else:
            self.entry.configure(fg=self.normal_color)
        
        # Style au focus
        self.entry.bind("<FocusIn>", lambda e: self.configure(highlightbackground="#007AFF"))
        self.entry.bind("<FocusOut>", lambda e: self.configure(highlightbackground="#3A3A3C"))
        
    def on_focus_in(self, e):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=self.normal_color)
            
    def on_focus_out(self, e):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.placeholder_color)
            
    def get(self):
        value = self.entry.get()
        if value == self.placeholder:
            return ""
        return value
        
    def set(self, value):
        self.entry.delete(0, "end")
        if value:
            self.entry.configure(fg=self.normal_color)
            self.entry.insert(0, value)
        elif self.placeholder and not self.entry["show"]:
            self.entry.configure(fg=self.placeholder_color)
            self.entry.insert(0, self.placeholder)

class NewsAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News Platform Admin")
        self.root.geometry("1400x800")
        self.root.configure(bg="#000000")
        
        # Configuration des services
        self.base_url = "http://localhost:8080"
        self.soap_client = None
        self.auth_token = None
        self.jwt_token = None
        self.current_user = None
        
        # Cache pour les données
        self.all_users = []
        self.all_articles = []
        self.all_categories = []
        
        # Polices personnalisées
        self.title_font = tkFont.Font(family="Segoe UI", size=32, weight="bold")
        self.subtitle_font = tkFont.Font(family="Segoe UI", size=18, weight="bold")
        self.normal_font = tkFont.Font(family="Segoe UI", size=11)
        
        # Style sombre pour ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuration du thème sombre
        self.configure_dark_theme()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Initialisation de l'interface
        self.setup_login_screen()
        
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def configure_dark_theme(self):
        """Configure le thème sombre pour ttk"""
        # Couleurs
        bg_color = "#1C1C1E"
        fg_color = "#FFFFFF"
        select_color = "#007AFF"
        
        # Configuration générale
        self.style.configure(".", background=bg_color, foreground=fg_color, 
                           fieldbackground=bg_color, borderwidth=0)
        
        # Treeview
        self.style.configure("Treeview", background="#2C2C2E", foreground=fg_color,
                           fieldbackground="#2C2C2E", borderwidth=0, rowheight=30)
        self.style.configure("Treeview.Heading", background="#1C1C1E", foreground=fg_color,
                           relief="flat", font=("Segoe UI", 11, "bold"))
        self.style.map("Treeview.Heading", background=[('active', '#3A3A3C')])
        self.style.map("Treeview", background=[('selected', '#007AFF')])
        
        # Scrollbar
        self.style.configure("Vertical.TScrollbar", background="#3A3A3C", 
                           troughcolor="#1C1C1E", borderwidth=0, width=12)
        self.style.configure("Horizontal.TScrollbar", background="#3A3A3C", 
                           troughcolor="#1C1C1E", borderwidth=0, height=12)
        
        # Combobox
        self.style.configure("TCombobox", fieldbackground="#2C2C2E", background="#2C2C2E",
                           foreground=fg_color, borderwidth=0, arrowcolor=fg_color)
        
    def setup_login_screen(self):
        """Configure l'écran de connexion moderne"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Gradient background
        self.create_gradient_background()
        
        # Container central
        container = tk.Frame(self.root, bg="#1C1C1E", highlightbackground="#2C2C2E", 
                           highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", width=450, height=550)
        
        # Logo/Icon
        logo_label = tk.Label(container, text="📰", font=("Segoe UI", 48), 
                            bg="#1C1C1E", fg="#007AFF")
        logo_label.pack(pady=(50, 20))
        
        # Titre
        title_label = tk.Label(container, text="News Platform", font=self.title_font,
                             bg="#1C1C1E", fg="#FFFFFF")
        title_label.pack()
        
        subtitle_label = tk.Label(container, text="Administration", 
                                font=("Segoe UI", 14, "normal"),
                                bg="#1C1C1E", fg="#8E8E93")
        subtitle_label.pack(pady=(5, 40))
        
        # Formulaire
        form_frame = tk.Frame(container, bg="#1C1C1E")
        form_frame.pack(padx=50, fill="x")
        
        # Username
        self.username_entry = ModernEntry(form_frame, placeholder="Nom d'utilisateur")
        self.username_entry.pack(fill="x", pady=(0, 20))
        
        # Password
        self.password_entry = ModernEntry(form_frame, placeholder="Mot de passe", show="•")
        self.password_entry.pack(fill="x", pady=(0, 30))
        
        # Bouton de connexion
        self.login_btn = ModernButton(form_frame, text="Se connecter", 
                                    command=self.login, icon="🔐")
        self.login_btn.pack(fill="x", pady=(0, 20))
        
        # Message d'erreur (caché par défaut)
        self.error_label = tk.Label(form_frame, text="", font=("Segoe UI", 10),
                                  bg="#1C1C1E", fg="#FF3B30")
        self.error_label.pack()
        
        # Footer
        footer_label = tk.Label(container, text="© 2024 News Platform. Tous droits réservés.",
                              font=("Segoe UI", 9), bg="#1C1C1E", fg="#8E8E93")
        footer_label.pack(side="bottom", pady=20)
        
        # Bind Enter key
        self.password_entry.entry.bind('<Return>', lambda e: self.login())
        
        # Focus
        self.username_entry.entry.focus()
        
    def create_gradient_background(self):
        """Crée un fond en dégradé"""
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Dégradé du noir vers le bleu foncé
        height = 800
        for i in range(height):
            color_value = int(20 + (i/height) * 30)
            color = f"#{color_value:02x}{color_value:02x}{color_value+10:02x}"
            canvas.create_line(0, i, 1400, i, fill=color, width=1)
            
    def show_loading(self, message="Chargement..."):
        """Affiche un indicateur de chargement"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.overrideredirect(True)
        self.loading_window.configure(bg="#1C1C1E")
        
        frame = tk.Frame(self.loading_window, bg="#1C1C1E", highlightbackground="#3A3A3C",
                        highlightthickness=1)
        frame.pack(padx=2, pady=2)
        
        tk.Label(frame, text="⏳", font=("Segoe UI", 24), bg="#1C1C1E", fg="#007AFF").pack(pady=10)
        tk.Label(frame, text=message, font=("Segoe UI", 11), bg="#1C1C1E", fg="white").pack(padx=30, pady=(0, 15))
        
        # Centrer la fenêtre de chargement
        self.loading_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (self.loading_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (self.loading_window.winfo_height() // 2)
        self.loading_window.geometry(f"+{x}+{y}")
        
        self.loading_window.update()
        
    def hide_loading(self):
        """Cache l'indicateur de chargement"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
            
    def login(self):
        """Gère la connexion de l'utilisateur via SOAP et REST"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.config(text="⚠️ Veuillez remplir tous les champs")
            return
            
        self.show_loading("Connexion en cours...")
        self.error_label.config(text="")
        
        try:
            # 1. D'abord, authentification via REST pour obtenir le JWT
            response = requests.post(f"{self.base_url}/api/auth/login", 
                                   json={"username": username, "password": password})
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data['token']
                self.current_user = {
                    'username': data['username'],
                    'role': data['role'],
                    'id': data['userId']
                }
                
                # 2. Ensuite, initialiser le client SOAP avec le token
                try:
                    transport = Transport()
                    transport.session.headers['Authorization'] = f'Bearer {self.jwt_token}'
                    self.soap_client = Client(f'{self.base_url}/soap/users?wsdl', 
                                            transport=transport)
                    
                    # 3. Tester l'authentification SOAP
                    soap_auth = self.soap_client.service.authenticate(username, password)
                    
                    if soap_auth and self.current_user['role'] == 'ADMIN':
                        self.hide_loading()
                        self.animate_transition()
                    else:
                        self.hide_loading()
                        self.error_label.config(text="❌ Accès réservé aux administrateurs")
                        
                except Exception as e:
                    print(f"Erreur SOAP: {e}")
                    # Continuer même si SOAP échoue
                    if self.current_user['role'] == 'ADMIN':
                        self.hide_loading()
                        self.animate_transition()
                    else:
                        self.hide_loading()
                        self.error_label.config(text="❌ Accès réservé aux administrateurs")
            else:
                self.hide_loading()
                self.error_label.config(text="❌ Identifiants incorrects")
                
        except Exception as e:
            self.hide_loading()
            self.error_label.config(text="❌ Erreur de connexion au serveur")
            
    def animate_transition(self):
        """Animation de transition vers l'interface principale"""
        # Fondu sortant
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Message de bienvenue
        welcome_frame = tk.Frame(self.root, bg="#000000")
        welcome_frame.pack(fill="both", expand=True)
        
        welcome_label = tk.Label(welcome_frame, text=f"Bienvenue, {self.current_user['username']}!",
                               font=("Segoe UI", 36, "bold"), bg="#000000", fg="#007AFF")
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Transition après 1 seconde
        self.root.after(1000, self.setup_main_interface)
        
    def setup_main_interface(self):
        """Configure l'interface principale moderne"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Container principal
        main_container = tk.Frame(self.root, bg="#000000")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(main_container, bg="#1C1C1E", width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo dans la sidebar
        logo_frame = tk.Frame(self.sidebar, bg="#1C1C1E")
        logo_frame.pack(fill="x", pady=20)
        
        tk.Label(logo_frame, text="📰", font=("Segoe UI", 32), 
                bg="#1C1C1E", fg="#007AFF").pack()
        tk.Label(logo_frame, text="News Admin", font=("Segoe UI", 16, "bold"),
                bg="#1C1C1E", fg="white").pack()
        
        # Menu items
        self.menu_items = [
            {"icon": "📊", "text": "Tableau de bord", "command": self.show_dashboard},
            {"icon": "👥", "text": "Utilisateurs", "command": self.show_user_management},
            {"icon": "📄", "text": "Articles", "command": self.show_article_management},
            {"icon": "🏷️", "text": "Catégories", "command": self.show_categories},
            {"icon": "🔑", "text": "Jetons API", "command": self.show_token_management},
            {"icon": "🌐", "text": "Services REST", "command": self.show_rest_services},
        ]
        
        self.menu_buttons = []
        for item in self.menu_items:
            btn = self.create_menu_button(self.sidebar, item["icon"], item["text"], item["command"])
            btn.pack(fill="x", padx=20, pady=5)
            self.menu_buttons.append(btn)
            
        # Bouton de déconnexion en bas
        logout_frame = tk.Frame(self.sidebar, bg="#1C1C1E")
        logout_frame.pack(side="bottom", fill="x", pady=20)
        
        logout_btn = self.create_menu_button(logout_frame, "🚪", "Déconnexion", self.logout)
        logout_btn.pack(fill="x", padx=20)
        
        # User info
        user_frame = tk.Frame(logout_frame, bg="#1C1C1E")
        user_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(user_frame, text=self.current_user['username'], 
                font=("Segoe UI", 12, "bold"), bg="#1C1C1E", fg="white").pack()
        tk.Label(user_frame, text="Administrateur", 
                font=("Segoe UI", 10), bg="#1C1C1E", fg="#8E8E93").pack()
        
        # Zone de contenu principal
        self.content_area = tk.Frame(main_container, bg="#000000")
        self.content_area.pack(side="left", fill="both", expand=True)
        
        # Afficher le tableau de bord par défaut
        self.show_dashboard()
        
    def create_menu_button(self, parent, icon, text, command):
        """Crée un bouton de menu avec icône"""
        frame = tk.Frame(parent, bg="#1C1C1E", cursor="hand2")
        
        # Contenu
        content = tk.Frame(frame, bg="#1C1C1E")
        content.pack(fill="x", padx=15, pady=10)
        
        tk.Label(content, text=icon, font=("Segoe UI", 16), 
                bg="#1C1C1E", fg="#007AFF").pack(side="left", padx=(0, 10))
        tk.Label(content, text=text, font=("Segoe UI", 12), 
                bg="#1C1C1E", fg="white").pack(side="left")
        
        # Hover effect
        def on_enter(e):
            frame.configure(bg="#2C2C2E")
            content.configure(bg="#2C2C2E")
            for widget in content.winfo_children():
                widget.configure(bg="#2C2C2E")
                
        def on_leave(e):
            frame.configure(bg="#1C1C1E")
            content.configure(bg="#1C1C1E")
            for widget in content.winfo_children():
                widget.configure(bg="#1C1C1E")
                
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        frame.bind("<Button-1>", lambda e: command())
        
        for widget in [content] + content.winfo_children():
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: command())
            
        return frame
        
    def show_dashboard(self):
        """Affiche le tableau de bord avec statistiques"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="Tableau de bord", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Container principal
        main_container = tk.Frame(self.content_area, bg="#000000")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Statistiques générales
        stats_frame = tk.Frame(main_container, bg="#000000")
        stats_frame.pack(fill="x", pady=(0, 30))
        
        # Chargement des statistiques
        self.load_dashboard_stats(stats_frame)
        
        # Activité récente
        activity_frame = tk.Frame(main_container, bg="#1C1C1E")
        activity_frame.pack(fill="both", expand=True)
        
        activity_header = tk.Frame(activity_frame, bg="#2C2C2E")
        activity_header.pack(fill="x")
        
        tk.Label(activity_header, text="📈 Activité récente", font=("Segoe UI", 16, "bold"),
                bg="#2C2C2E", fg="white").pack(anchor="w", padx=20, pady=15)
        
        # Liste des activités
        activity_list = tk.Frame(activity_frame, bg="#1C1C1E")
        activity_list.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Simuler des activités récentes
        activities = [
            {"icon": "➕", "text": "Nouvel article publié: 'Actualités du jour'", "time": "Il y a 2 heures"},
            {"icon": "👤", "text": "Nouvel utilisateur inscrit: Jean Dupont", "time": "Il y a 5 heures"},
            {"icon": "✏️", "text": "Article modifié: 'Technologie et innovation'", "time": "Hier"},
            {"icon": "🏷️", "text": "Nouvelle catégorie créée: 'Sport'", "time": "Il y a 2 jours"},
        ]
        
        for activity in activities:
            self.create_activity_item(activity_list, activity)
            
    def load_dashboard_stats(self, parent):
        """Charge les statistiques du tableau de bord"""
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            
            # Récupérer les stats via API
            stats_data = {
                "users": 0,
                "articles": 0,
                "categories": 0,
                "active_users": 0
            }
            
            # Compter les utilisateurs
            try:
                response = requests.get(f"{self.base_url}/api/users", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    stats_data["users"] = len(users)
                    stats_data["active_users"] = len([u for u in users if u.get('active', False)])
            except:
                pass
                
            # Compter les articles
            try:
                response = requests.get(f"{self.base_url}/api/articles", headers=headers)
                if response.status_code == 200:
                    stats_data["articles"] = len(response.json())
            except:
                pass
                
            # Compter les catégories
            try:
                response = requests.get(f"{self.base_url}/api/categories", headers=headers)
                if response.status_code == 200:
                    stats_data["categories"] = len(response.json())
            except:
                pass
                
            # Afficher les cartes
            cards = [
                {"label": "Utilisateurs", "value": str(stats_data["users"]), 
                 "icon": "👥", "color": "#007AFF", "subtext": f"{stats_data['active_users']} actifs"},
                {"label": "Articles", "value": str(stats_data["articles"]), 
                 "icon": "📄", "color": "#34C759", "subtext": "Publiés"},
                {"label": "Catégories", "value": str(stats_data["categories"]), 
                 "icon": "🏷️", "color": "#FF9500", "subtext": "Actives"},
                {"label": "Visiteurs", "value": "1.2k", 
                 "icon": "👁️", "color": "#5856D6", "subtext": "Cette semaine"},
            ]
            
            for i, card in enumerate(cards):
                stat_card = self.create_dashboard_card(parent, card)
                stat_card.grid(row=0, column=i, padx=10, sticky="nsew")
                
            parent.grid_columnconfigure(0, weight=1)
            parent.grid_columnconfigure(1, weight=1)
            parent.grid_columnconfigure(2, weight=1)
            parent.grid_columnconfigure(3, weight=1)
            
        except Exception as e:
            print(f"Erreur lors du chargement des stats: {e}")
            
    def create_dashboard_card(self, parent, data):
        """Crée une carte pour le tableau de bord"""
        card = tk.Frame(parent, bg="#1C1C1E", height=150)
        card.pack_propagate(False)
        
        # Icône en haut à gauche
        icon_label = tk.Label(card, text=data["icon"], font=("Segoe UI", 28),
                            bg="#1C1C1E", fg=data["color"])
        icon_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Valeur
        value_label = tk.Label(card, text=data["value"], font=("Segoe UI", 32, "bold"),
                             bg="#1C1C1E", fg="white")
        value_label.pack(anchor="w", padx=20)
        
        # Label et sous-texte
        info_frame = tk.Frame(card, bg="#1C1C1E")
        info_frame.pack(anchor="w", padx=20, pady=(5, 0))
        
        tk.Label(info_frame, text=data["label"], font=("Segoe UI", 12, "bold"),
                bg="#1C1C1E", fg="#8E8E93").pack(side="left")
        tk.Label(info_frame, text=f" • {data['subtext']}", font=("Segoe UI", 10),
                bg="#1C1C1E", fg="#5E5E60").pack(side="left")
        
        return card
        
    def create_activity_item(self, parent, activity):
        """Crée un élément d'activité"""
        item = tk.Frame(parent, bg="#2C2C2E", relief="flat")
        item.pack(fill="x", pady=5)
        
        content = tk.Frame(item, bg="#2C2C2E")
        content.pack(fill="x", padx=15, pady=12)
        
        # Icône
        tk.Label(content, text=activity["icon"], font=("Segoe UI", 14),
                bg="#2C2C2E", fg="#007AFF").pack(side="left", padx=(0, 10))
        
        # Texte
        tk.Label(content, text=activity["text"], font=("Segoe UI", 11),
                bg="#2C2C2E", fg="white").pack(side="left")
        
        # Temps
        tk.Label(content, text=activity["time"], font=("Segoe UI", 10),
                bg="#2C2C2E", fg="#8E8E93").pack(side="right")
        
    def show_user_management(self):
        """Affiche l'interface de gestion des utilisateurs avec un design moderne"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="Gestion des Utilisateurs", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack(side="left", padx=30)
        
        # Boutons d'action
        action_frame = tk.Frame(header_content, bg="#0A0A0A")
        action_frame.pack(side="right", padx=30)
        
        ModernButton(action_frame, text="Nouvel utilisateur", command=self.new_user, 
                    icon="➕", style="primary").pack(side="left", padx=5)
        ModernButton(action_frame, text="Actualiser", command=self.refresh_users, 
                    icon="🔄", style="secondary").pack(side="left", padx=5)
        
        # Statistiques
        stats_frame = tk.Frame(self.content_area, bg="#000000")
        stats_frame.pack(fill="x", padx=30, pady=20)
        
        self.user_stats = {
            "total": tk.StringVar(value="0"),
            "admins": tk.StringVar(value="0"),
            "editors": tk.StringVar(value="0"),
            "visitors": tk.StringVar(value="0")
        }
        
        stats = [
            {"label": "Total", "var": self.user_stats["total"], "color": "#007AFF"},
            {"label": "Admins", "var": self.user_stats["admins"], "color": "#FF9500"},
            {"label": "Éditeurs", "var": self.user_stats["editors"], "color": "#34C759"},
            {"label": "Visiteurs", "var": self.user_stats["visitors"], "color": "#5856D6"}
        ]
        
        for stat in stats:
            self.create_stat_card(stats_frame, stat["label"], stat["var"], stat["color"]).pack(side="left", padx=10)
        
        # Table des utilisateurs
        table_frame = tk.Frame(self.content_area, bg="#1C1C1E")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Barre de recherche
        search_frame = tk.Frame(table_frame, bg="#1C1C1E")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        self.user_search_entry = ModernEntry(search_frame, placeholder="🔍 Rechercher un utilisateur...")
        self.user_search_entry.pack(side="left", fill="x", expand=True)
        
        # Treeview
        tree_container = tk.Frame(table_frame, bg="#1C1C1E")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        # Treeview avec style moderne
        self.user_tree = ttk.Treeview(tree_container,
                                     columns=('ID', 'Username', 'Email', 'Nom complet', 'Rôle', 'Statut'),
                                     show='headings',
                                     yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set,
                                     height=15)
        
        vsb.config(command=self.user_tree.yview)
        hsb.config(command=self.user_tree.xview)
        
        # Configure columns
        columns = [
            ('ID', 60),
            ('Username', 150),
            ('Email', 250),
            ('Nom complet', 200),
            ('Rôle', 120),
            ('Statut', 100)
        ]
        
        for col, width in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=width)
        
        # Pack
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Tags pour les couleurs
        self.user_tree.tag_configure('admin', foreground='#FF9500')
        self.user_tree.tag_configure('editor', foreground='#34C759')
        self.user_tree.tag_configure('visitor', foreground='#5856D6')
        self.user_tree.tag_configure('inactive', foreground='#8E8E93')
        
        # Menu contextuel
        self.create_context_menu()
        
        # Bindings
        self.user_tree.bind('<Double-Button-1>', lambda e: self.edit_user())
        self.user_tree.bind('<Button-3>', self.show_context_menu)
        
        # Recherche en temps réel
        self.user_search_entry.entry.bind('<KeyRelease>', lambda e: self.filter_users(self.user_search_entry.get()))
        
        # Charger les utilisateurs
        self.refresh_users()
        
    def create_stat_card(self, parent, label, var, color):
        """Crée une carte de statistique"""
        card = tk.Frame(parent, bg="#1C1C1E", width=150, height=80)
        card.pack_propagate(False)
        
        tk.Label(card, textvariable=var, font=("Segoe UI", 24, "bold"),
                bg="#1C1C1E", fg=color).pack(pady=(10, 0))
        tk.Label(card, text=label, font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack()
        
        return card
        
    def create_context_menu(self):
        """Crée un menu contextuel pour le treeview"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#2C2C2E", fg="white",
                                   activebackground="#007AFF", activeforeground="white")
        self.context_menu.add_command(label="✏️  Modifier", command=self.edit_user)
        self.context_menu.add_command(label="📋  Dupliquer", command=self.duplicate_user)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️  Supprimer", command=self.delete_user)
        
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        item = self.user_tree.identify_row(event.y)
        if item:
            self.user_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def filter_users(self, query):
        """Filtre les utilisateurs selon la recherche"""
        # Effacer l'arbre actuel
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Filtrer et réafficher
        query_lower = query.lower()
        for user in self.all_users:
            # Recherche dans username, email et nom complet
            if (query_lower in user.get('username', '').lower() or 
                query_lower in user.get('email', '').lower() or 
                query_lower in f"{user.get('firstName', '')} {user.get('lastName', '')}".lower()):
                
                self.insert_user_to_tree(user)
                
    def insert_user_to_tree(self, user):
        """Insère un utilisateur dans le treeview"""
        role = user.get('role', '')
        tag = role.lower()
        
        # Statut avec emoji
        status = '🟢 Actif' if user.get('active', False) else '🔴 Inactif'
        if not user.get('active', False):
            tag = 'inactive'
            
        # Nom complet
        full_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        
        self.user_tree.insert('', 'end', values=(
            user.get('id', ''),
            user.get('username', ''),
            user.get('email', ''),
            full_name,
            role,
            status
        ), tags=(tag,))
        
    def duplicate_user(self):
        """Duplique l'utilisateur sélectionné"""
        selection = self.user_tree.selection()
        if not selection:
            return
            
        item = self.user_tree.item(selection[0])
        values = item['values']
        
        user_data = {
            'username': values[1] + "_copy",
            'email': "",
            'firstName': values[3].split()[0] if values[3] else "",
            'lastName': values[3].split()[1] if len(values[3].split()) > 1 else "",
            'role': values[4],
            'active': values[5] == '🟢 Actif'
        }
        
        self.open_user_dialog(user_data)
        
    def refresh_users(self):
        """Actualise la liste des utilisateurs via SOAP ou REST"""
        # Animation de chargement
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
            
        try:
            users = []
            
            # Essayer d'abord avec SOAP
            if self.soap_client:
                try:
                    # Utiliser le service SOAP pour lister les utilisateurs
                    soap_users = self.soap_client.service.listUsers(self.auth_token)
                    if soap_users:
                        users = soap_users
                except Exception as e:
                    print(f"Erreur SOAP, basculement vers REST: {e}")
                    
            # Si SOAP échoue, utiliser REST
            if not users:
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                response = requests.get(f"{self.base_url}/api/users", headers=headers)
                
                if response.status_code == 200:
                    users = response.json()
                    
            # Sauvegarder pour le filtrage
            self.all_users = users
                    
            # Stats
            stats = {"total": len(users), "admins": 0, "editors": 0, "visitors": 0}
            
            # Afficher les utilisateurs
            for user in users:
                role = user.get('role', '')
                
                # Compter pour les stats
                if role == 'ADMIN':
                    stats["admins"] += 1
                elif role == 'EDITOR':
                    stats["editors"] += 1
                elif role == 'VISITOR':
                    stats["visitors"] += 1
                    
                self.insert_user_to_tree(user)
                
            # Mettre à jour les statistiques
            for key, value in stats.items():
                self.user_stats[key].set(str(value))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
            
    def new_user(self):
        """Ouvre la fenêtre de création d'utilisateur"""
        self.open_user_dialog()
        
    def edit_user(self):
        """Ouvre la fenêtre de modification d'utilisateur"""
        selection = self.user_tree.selection()
        if not selection:
            return
            
        item = self.user_tree.item(selection[0])
        values = item['values']
        
        # Extraire le prénom et le nom
        full_name = values[3].split() if values[3] else []
        
        user_data = {
            'id': values[0],
            'username': values[1],
            'email': values[2],
            'firstName': full_name[0] if full_name else '',
            'lastName': ' '.join(full_name[1:]) if len(full_name) > 1 else '',
            'role': values[4],
            'active': values[5] == '🟢 Actif'
        }
        
        self.open_user_dialog(user_data)
        
    def open_user_dialog(self, user_data=None):
        """Ouvre la boîte de dialogue moderne pour créer/modifier un utilisateur"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel utilisateur" if user_data is None else "Modifier utilisateur")
        dialog.geometry("500x650")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (650 // 2)
        dialog.geometry(f"500x650+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="👤", font=("Segoe UI", 32),
                bg="#0A0A0A", fg="#007AFF").pack()
        tk.Label(header_content, text="Nouvel utilisateur" if not user_data else "Modifier utilisateur",
                font=("Segoe UI", 16, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Form container
        form_container = tk.Frame(dialog, bg="#1C1C1E")
        form_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Variables
        vars = {}
        
        # Champs du formulaire
        fields = [
            {"name": "username", "label": "Nom d'utilisateur", "type": "entry", 
             "value": user_data.get('username', '') if user_data else ''},
            {"name": "email", "label": "Email", "type": "entry",
             "value": user_data.get('email', '') if user_data else ''},
            {"name": "password", "label": "Mot de passe", "type": "password"},
            {"name": "firstName", "label": "Prénom", "type": "entry",
             "value": user_data.get('firstName', '') if user_data else ''},
            {"name": "lastName", "label": "Nom", "type": "entry",
             "value": user_data.get('lastName', '') if user_data else ''},
            {"name": "role", "label": "Rôle", "type": "combo",
             "values": ['VISITOR', 'EDITOR', 'ADMIN'],
             "value": user_data.get('role', 'VISITOR') if user_data else 'VISITOR'},
        ]
        
        for field in fields:
            # Label
            label_frame = tk.Frame(form_container, bg="#1C1C1E")
            label_frame.pack(fill="x", pady=(0, 5))
            
            tk.Label(label_frame, text=field["label"], font=("Segoe UI", 11),
                    bg="#1C1C1E", fg="#8E8E93").pack(anchor="w")
            
            # Input
            if field["type"] == "combo":
                vars[field["name"]] = tk.StringVar(value=field["value"])
                combo = ttk.Combobox(form_container, textvariable=vars[field["name"]],
                                   values=field["values"], state="readonly",
                                   font=("Segoe UI", 11))
                combo.pack(fill="x", pady=(0, 15))
                
            elif field["type"] == "password":
                entry = ModernEntry(form_container, placeholder="••••••••", show="•")
                entry.pack(fill="x", pady=(0, 15))
                vars[field["name"]] = entry
                
                if user_data:
                    hint = tk.Label(form_container, text="Laisser vide pour conserver le mot de passe actuel",
                                  font=("Segoe UI", 9, "italic"), bg="#1C1C1E", fg="#8E8E93")
                    hint.pack(anchor="w", pady=(0, 15))
                    
            else:
                entry = ModernEntry(form_container)
                entry.pack(fill="x", pady=(0, 15))
                entry.set(field.get("value", ""))
                vars[field["name"]] = entry
                
                # Désactiver le username en modification
                if field["name"] == "username" and user_data:
                    entry.entry.configure(state="disabled", fg="#8E8E93")
                    
        # Checkbox actif
        active_var = tk.BooleanVar(value=user_data.get('active', True) if user_data else True)
        vars['active'] = active_var
        
        check_frame = tk.Frame(form_container, bg="#1C1C1E")
        check_frame.pack(fill="x", pady=20)
        
        check = tk.Checkbutton(check_frame, text="Compte actif", variable=active_var,
                             font=("Segoe UI", 11), bg="#1C1C1E", fg="white",
                             selectcolor="#1C1C1E", activebackground="#1C1C1E",
                             activeforeground="white")
        check.pack(anchor="w")
        
        # Boutons
        button_frame = tk.Frame(dialog, bg="#1C1C1E")
        button_frame.pack(fill="x", padx=40, pady=(0, 30))
        
        def save_user():
            # Validation
            username = vars['username'].get() if hasattr(vars['username'], 'get') else vars['username'].entry.get()
            email = vars['email'].get()
            
            if not username or not email:
                messagebox.showerror("Erreur", "Le nom d'utilisateur et l'email sont obligatoires")
                return
                
            password = vars['password'].get()
            if not user_data and not password:
                messagebox.showerror("Erreur", "Le mot de passe est obligatoire pour un nouvel utilisateur")
                return
                
            try:
                user_obj = {
                    'username': username,
                    'email': email,
                    'firstName': vars['firstName'].get(),
                    'lastName': vars['lastName'].get(),
                    'role': vars['role'].get(),
                    'active': vars['active'].get()
                }
                
                if password:
                    user_obj['password'] = password
                    
                # Essayer d'abord avec SOAP
                success = False
                if self.soap_client:
                    try:
                        if user_data:
                            # Modification via SOAP
                            success = self.soap_client.service.updateUser(
                                self.auth_token, user_data['id'], user_obj
                            )
                        else:
                            # Création via SOAP
                            result = self.soap_client.service.addUser(
                                self.auth_token, user_obj
                            )
                            success = result is not None
                    except Exception as e:
                        print(f"Erreur SOAP: {e}")
                        
                # Si SOAP échoue, utiliser REST
                if not success:
                    headers = {'Authorization': f'Bearer {self.jwt_token}'}
                    
                    if user_data:
                        response = requests.put(f"{self.base_url}/api/users/{user_data['id']}", 
                                              json=user_obj, headers=headers)
                    else:
                        response = requests.post(f"{self.base_url}/api/users", 
                                               json=user_obj, headers=headers)
                        
                    success = response.status_code in [200, 201]
                    
                if success:
                    dialog.destroy()
                    self.refresh_users()
                    self.show_notification("✅ Utilisateur enregistré avec succès", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'enregistrement")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
        ModernButton(button_frame, text="Enregistrer", command=save_user,
                    style="primary", icon="💾").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
    def delete_user(self):
        """Supprime l'utilisateur sélectionné avec confirmation moderne"""
        selection = self.user_tree.selection()
        if not selection:
            return
            
        item = self.user_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # Dialogue de confirmation moderne
        confirm_dialog = tk.Toplevel(self.root)
        confirm_dialog.title("Confirmation")
        confirm_dialog.geometry("400x200")
        confirm_dialog.configure(bg="#1C1C1E")
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()
        
        # Centrer
        confirm_dialog.update_idletasks()
        x = (confirm_dialog.winfo_screenwidth() // 2) - 200
        y = (confirm_dialog.winfo_screenheight() // 2) - 100
        confirm_dialog.geometry(f"400x200+{x}+{y}")
        
        # Contenu
        content = tk.Frame(confirm_dialog, bg="#1C1C1E")
        content.pack(expand=True)
        
        tk.Label(content, text="⚠️", font=("Segoe UI", 48),
                bg="#1C1C1E", fg="#FF3B30").pack()
        tk.Label(content, text=f"Supprimer l'utilisateur '{username}' ?",
                font=("Segoe UI", 14), bg="#1C1C1E", fg="white").pack(pady=10)
        tk.Label(content, text="Cette action est irréversible",
                font=("Segoe UI", 10), bg="#1C1C1E", fg="#8E8E93").pack()
        
        # Boutons
        button_frame = tk.Frame(content, bg="#1C1C1E")
        button_frame.pack(pady=20)
        
        def load():
            category = category_entry.get()
            if category:
                self.show_loading("Chargement...")
                try:
                    headers = {'Accept': f'application/{self.format_var.get().lower()}'}
                    response = requests.get(f"{self.base_url}/api/rest/articles/category/{category}", 
                                          headers=headers)
                    
                    self.hide_loading()
                    
                    if response.status_code == 200:
                        self.display_rest_response(response.text, self.format_var.get())
                        dialog.destroy()
                        self.show_notification(f"✅ Articles de '{category}' chargés", "success")
                    else:
                        self.show_notification("❌ Catégorie non trouvée", "error")
                        
                except Exception as e:
                    self.hide_loading()
                    self.show_notification("❌ Erreur de connexion", "error")
                    
        ModernButton(button_frame, text="Charger", command=load,
                    style="primary").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
        category_entry.entry.bind('<Return>', lambda e: load())
        
    def load_grouped_articles(self):
        """Charge les articles groupés par catégorie via REST"""
        self.show_loading("Chargement des articles groupés...")
        
        try:
            headers = {'Accept': f'application/{self.format_var.get().lower()}'}
            response = requests.get(f"{self.base_url}/api/rest/articles/grouped", headers=headers)
            
            self.hide_loading()
            
            if response.status_code == 200:
                self.display_rest_response(response.text, self.format_var.get())
                self.show_notification("✅ Articles groupés chargés", "success")
            else:
                self.show_notification("❌ Erreur lors du chargement", "error")
                
        except Exception as e:
            self.hide_loading()
            self.show_notification("❌ Erreur de connexion", "error")
            
    def display_rest_response(self, content, format_type):
        """Affiche la réponse REST avec coloration syntaxique"""
        self.rest_text.config(state="normal")
        self.rest_text.delete(1.0, tk.END)
        
        if format_type == "JSON":
            try:
                # Pretty print JSON avec coloration
                data = json.loads(content)
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                
                # Insérer le texte
                self.rest_text.insert(1.0, formatted)
                
                # Appliquer la coloration syntaxique
                self.apply_json_syntax_highlighting()
                
            except Exception as e:
                self.rest_text.insert(1.0, content)
        else:
            # Pretty print XML
            try:
                root = ET.fromstring(content)
                formatted = self.prettify_xml(root)
                self.rest_text.insert(1.0, formatted)
                
                # Appliquer la coloration syntaxique XML
                self.apply_xml_syntax_highlighting()
                
            except Exception as e:
                self.rest_text.insert(1.0, content)
                
        self.rest_text.config(state="disabled")
        
    def apply_json_syntax_highlighting(self):
        """Applique la coloration syntaxique JSON"""
        # Tags de coloration
        self.rest_text.tag_configure("key", foreground="#FF9500")
        self.rest_text.tag_configure("string", foreground="#34C759")
        self.rest_text.tag_configure("number", foreground="#007AFF")
        self.rest_text.tag_configure("boolean", foreground="#FF3B30")
        self.rest_text.tag_configure("null", foreground="#8E8E93")
        
        # Patterns
        import re
        
        content = self.rest_text.get(1.0, tk.END)
        
        # Clés JSON (entre guillemets suivis de :)
        for match in re.finditer(r'"([^"]+)"\s*:', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()-1}c"
            self.rest_text.tag_add("key", start_idx, end_idx)
        
        # Chaînes (entre guillemets, mais pas les clés)
        for match in re.finditer(r':\s*"([^"]*)"', content):
            start_idx = f"1.0+{match.start() + match.group().index('"')}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("string", start_idx, end_idx)
        
        # Nombres
        for match in re.finditer(r':\s*(-?\d+\.?\d*)', content):
            start_idx = f"1.0+{match.start() + match.group().index(match.group(1))}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("number", start_idx, end_idx)
        
        # Booléens
        for match in re.finditer(r':\s*(true|false)', content):
            start_idx = f"1.0+{match.start() + match.group().index(match.group(1))}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("boolean", start_idx, end_idx)
        
        # Null
        for match in re.finditer(r':\s*(null)', content):
            start_idx = f"1.0+{match.start() + match.group().index('null')}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("null", start_idx, end_idx)
            
    def apply_xml_syntax_highlighting(self):
        """Applique la coloration syntaxique XML"""
        # Tags de coloration
        self.rest_text.tag_configure("tag", foreground="#007AFF")
        self.rest_text.tag_configure("attribute", foreground="#FF9500")
        self.rest_text.tag_configure("value", foreground="#34C759")
        self.rest_text.tag_configure("comment", foreground="#8E8E93", font=("Consolas", 11, "italic"))
        
        import re
        
        content = self.rest_text.get(1.0, tk.END)
        
        # Tags XML
        for match in re.finditer(r'</?[^>]+>', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("tag", start_idx, end_idx)
        
        # Attributs et valeurs
        for match in re.finditer(r'(\w+)="([^"]*)"', content):
            # Attribut
            attr_start = f"1.0+{match.start(1)}c"
            attr_end = f"1.0+{match.end(1)}c"
            self.rest_text.tag_add("attribute", attr_start, attr_end)
            
            # Valeur
            val_start = f"1.0+{match.start(2)-1}c"
            val_end = f"1.0+{match.end(2)+1}c"
            self.rest_text.tag_add("value", val_start, val_end)
        
        # Commentaires
        for match in re.finditer(r'<!--.*?-->', content, re.DOTALL):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.rest_text.tag_add("comment", start_idx, end_idx)
            
    def prettify_xml(self, elem, level=0):
        """Formate le XML pour l'affichage"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.prettify_xml(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return ET.tostring(elem, encoding='unicode')
        
    def logout(self):
        """Déconnecte l'utilisateur avec animation"""
        # Animation de déconnexion
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Message de déconnexion
        logout_frame = tk.Frame(self.content_area, bg="#000000")
        logout_frame.pack(fill="both", expand=True)
        
        logout_label = tk.Label(logout_frame, text="À bientôt! 👋",
                              font=("Segoe UI", 36, "bold"), bg="#000000", fg="#007AFF")
        logout_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Reset des variables
        self.jwt_token = None
        self.auth_token = None
        self.current_user = None
        self.soap_client = None
        self.all_users = []
        self.all_articles = []
        self.all_categories = []
        
        # Retour à l'écran de connexion après animation
        self.root.after(1500, self.setup_login_screen)
        

def main():
    """Point d'entrée principal de l'application"""
    # Création de la fenêtre principale
    root = tk.Tk()
    
    # Configuration de la fenêtre principale
    root.title("News Platform Admin")
    root.configure(bg="#000000")
    
    # Icône de l'application (si disponible)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    # Configuration du redimensionnement
    root.resizable(True, True)
    root.minsize(1200, 700)
    
    # Créer l'application
    app = NewsAdminApp(root)
    
    # Gestionnaire de fermeture
    def on_closing():
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Lancer la boucle principale
    root.mainloop()
    

if __name__ == "__main__":

        
        def confirm_delete():
            try:
                # Essayer d'abord avec SOAP
                success = False
                if self.soap_client:
                    try:
                        success = self.soap_client.service.deleteUser(self.auth_token, user_id)
                    except Exception as e:
                        print(f"Erreur SOAP: {e}")
                        
                # Si SOAP échoue, utiliser REST
                if not success:
                    headers = {'Authorization': f'Bearer {self.jwt_token}'}
                    response = requests.delete(f"{self.base_url}/api/users/{user_id}", headers=headers)
                    success = response.status_code == 204
                    
                if success:
                    confirm_dialog.destroy()
                    self.refresh_users()
                    self.show_notification("✅ Utilisateur supprimé", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la suppression")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
        ModernButton(button_frame, text="Supprimer", command=confirm_delete,
                    style="danger").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=confirm_dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
                    
    def show_notification(self, message, type="info"):
        """Affiche une notification temporaire"""
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.configure(bg="#2C2C2E")
        
        # Style selon le type
        colors = {
            "success": "#34C759",
            "error": "#FF3B30",
            "info": "#007AFF",
            "warning": "#FF9500"
        }
        
        color = colors.get(type, colors["info"])
        
        frame = tk.Frame(notif, bg="#2C2C2E", highlightbackground=color, highlightthickness=2)
        frame.pack(padx=2, pady=2)
        
        tk.Label(frame, text=message, font=("Segoe UI", 12), bg="#2C2C2E", 
                fg="white", padx=20, pady=10).pack()
        
        # Position en haut à droite
        notif.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() - notif.winfo_width() - 20
        y = self.root.winfo_y() + 50
        notif.geometry(f"+{x}+{y}")
        
        # Animation de disparition
        notif.after(3000, notif.destroy)
        
    def show_article_management(self):
        """Affiche la gestion complète des articles"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="Gestion des Articles", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack(side="left", padx=30)
        
        # Boutons d'action
        action_frame = tk.Frame(header_content, bg="#0A0A0A")
        action_frame.pack(side="right", padx=30)
        
        ModernButton(action_frame, text="Nouvel article", command=self.new_article, 
                    icon="➕", style="primary").pack(side="left", padx=5)
        ModernButton(action_frame, text="Actualiser", command=self.refresh_articles, 
                    icon="🔄", style="secondary").pack(side="left", padx=5)
        
        # Table des articles
        table_frame = tk.Frame(self.content_area, bg="#1C1C1E")
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Filtres
        filter_frame = tk.Frame(table_frame, bg="#1C1C1E")
        filter_frame.pack(fill="x", padx=20, pady=20)
        
        # Recherche
        self.article_search_entry = ModernEntry(filter_frame, placeholder="🔍 Rechercher un article...")
        self.article_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        
        # Filtre par catégorie
        tk.Label(filter_frame, text="Catégorie:", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="white").pack(side="left", padx=(0, 10))
        
        self.category_filter = ttk.Combobox(filter_frame, state="readonly", width=20)
        self.category_filter.pack(side="left")
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_articles())
        
        # Treeview pour les articles
        tree_container = tk.Frame(table_frame, bg="#1C1C1E")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        self.article_tree = ttk.Treeview(tree_container,
                                       columns=('ID', 'Titre', 'Catégorie', 'Auteur', 'Date', 'Statut'),
                                       show='headings',
                                       yscrollcommand=vsb.set,
                                       xscrollcommand=hsb.set,
                                       height=15)
        
        vsb.config(command=self.article_tree.yview)
        hsb.config(command=self.article_tree.xview)
        
        # Configure columns
        columns = [
            ('ID', 60),
            ('Titre', 300),
            ('Catégorie', 150),
            ('Auteur', 150),
            ('Date', 150),
            ('Statut', 100)
        ]
        
        for col, width in columns:
            self.article_tree.heading(col, text=col)
            self.article_tree.column(col, width=width)
        
        # Pack
        self.article_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Tags pour les couleurs
        self.article_tree.tag_configure('published', foreground='#34C759')
        self.article_tree.tag_configure('draft', foreground='#FF9500')
        self.article_tree.tag_configure('archived', foreground='#8E8E93')
        
        # Menu contextuel
        self.create_article_context_menu()
        
        # Bindings
        self.article_tree.bind('<Double-Button-1>', lambda e: self.edit_article())
        self.article_tree.bind('<Button-3>', self.show_article_context_menu)
        
        # Recherche en temps réel
        self.article_search_entry.entry.bind('<KeyRelease>', lambda e: self.filter_articles())
        
        # Charger les articles
        self.refresh_articles()
        
    def create_article_context_menu(self):
        """Menu contextuel pour les articles"""
        self.article_context_menu = tk.Menu(self.root, tearoff=0, bg="#2C2C2E", fg="white",
                                          activebackground="#007AFF", activeforeground="white")
        self.article_context_menu.add_command(label="👁️  Prévisualiser", command=self.preview_article)
        self.article_context_menu.add_command(label="✏️  Modifier", command=self.edit_article)
        self.article_context_menu.add_command(label="📋  Dupliquer", command=self.duplicate_article)
        self.article_context_menu.add_separator()
        self.article_context_menu.add_command(label="📤  Publier", command=self.publish_article)
        self.article_context_menu.add_command(label="📥  Archiver", command=self.archive_article)
        self.article_context_menu.add_separator()
        self.article_context_menu.add_command(label="🗑️  Supprimer", command=self.delete_article)
        
    def show_article_context_menu(self, event):
        """Affiche le menu contextuel des articles"""
        item = self.article_tree.identify_row(event.y)
        if item:
            self.article_tree.selection_set(item)
            self.article_context_menu.post(event.x_root, event.y_root)
            
    def refresh_articles(self):
        """Actualise la liste des articles"""
        # Clear tree
        for item in self.article_tree.get_children():
            self.article_tree.delete(item)
            
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/articles", headers=headers)
            
            if response.status_code == 200:
                articles = response.json()
                self.all_articles = articles
                
                # Charger aussi les catégories pour le filtre
                self.load_categories_for_filter()
                
                # Afficher les articles
                for article in articles:
                    self.insert_article_to_tree(article)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des articles: {str(e)}")
            
    def insert_article_to_tree(self, article):
        """Insère un article dans le treeview"""
        status = article.get('status', 'draft')
        tag = status.lower()
        
        # Format de la date
        date_str = article.get('publishedDate', article.get('createdDate', ''))
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            except:
                pass
                
        # Statut avec emoji
        status_display = {
            'published': '🟢 Publié',
            'draft': '🟡 Brouillon',
            'archived': '📦 Archivé'
        }.get(status, status)
        
        self.article_tree.insert('', 'end', values=(
            article.get('id', ''),
            article.get('title', ''),
            article.get('categoryName', article.get('category', '')),
            article.get('authorName', article.get('author', '')),
            date_str,
            status_display
        ), tags=(tag,))
        
    def load_categories_for_filter(self):
        """Charge les catégories pour le filtre"""
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/categories", headers=headers)
            
            if response.status_code == 200:
                categories = response.json()
                category_names = ['Toutes'] + [cat.get('name', '') for cat in categories]
                self.category_filter['values'] = category_names
                self.category_filter.set('Toutes')
        except:
            pass
            
    def filter_articles(self):
        """Filtre les articles selon la recherche et la catégorie"""
        # Clear tree
        for item in self.article_tree.get_children():
            self.article_tree.delete(item)
            
        query = self.article_search_entry.get().lower()
        category = self.category_filter.get()
        
        for article in self.all_articles:
            # Filtre par recherche
            if query and not any(query in str(val).lower() for val in [
                article.get('title', ''),
                article.get('content', ''),
                article.get('authorName', '')
            ]):
                continue
                
            # Filtre par catégorie
            if category != 'Toutes' and article.get('categoryName', '') != category:
                continue
                
            self.insert_article_to_tree(article)
            
    def new_article(self):
        """Crée un nouvel article"""
        self.open_article_dialog()
        
    def edit_article(self):
        """Modifie l'article sélectionné"""
        selection = self.article_tree.selection()
        if not selection:
            return
            
        item = self.article_tree.item(selection[0])
        article_id = item['values'][0]
        
        # Récupérer les détails complets de l'article
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/articles/{article_id}", headers=headers)
            
            if response.status_code == 200:
                article = response.json()
                self.open_article_dialog(article)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'article: {str(e)}")
            
    def open_article_dialog(self, article_data=None):
        """Dialogue pour créer/modifier un article"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel article" if article_data is None else "Modifier article")
        dialog.geometry("800x700")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 400
        y = (dialog.winfo_screenheight() // 2) - 350
        dialog.geometry(f"800x700+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="📄", font=("Segoe UI", 32),
                bg="#0A0A0A", fg="#007AFF").pack()
        tk.Label(header_content, text="Nouvel article" if not article_data else "Modifier article",
                font=("Segoe UI", 16, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Form avec scrollbar
        form_frame = tk.Frame(dialog, bg="#1C1C1E")
        form_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(form_frame, bg="#1C1C1E", highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1C1C1E")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form container
        form_container = tk.Frame(scrollable_frame, bg="#1C1C1E")
        form_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Variables
        vars = {}
        
        # Titre
        tk.Label(form_container, text="Titre", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        title_entry = ModernEntry(form_container)
        title_entry.pack(fill="x", pady=(0, 20))
        if article_data:
            title_entry.set(article_data.get('title', ''))
        vars['title'] = title_entry
        
        # Catégorie
        tk.Label(form_container, text="Catégorie", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_container, textvariable=category_var,
                                    state="readonly", font=("Segoe UI", 11))
        category_combo.pack(fill="x", pady=(0, 20))
        vars['category'] = category_var
        
        # Charger les catégories
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/categories", headers=headers)
            if response.status_code == 200:
                categories = response.json()
                category_names = [cat.get('name', '') for cat in categories]
                category_combo['values'] = category_names
                if article_data and article_data.get('categoryName'):
                    category_var.set(article_data['categoryName'])
                elif category_names:
                    category_var.set(category_names[0])
        except:
            pass
            
        # Description courte
        tk.Label(form_container, text="Description courte", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        desc_entry = ModernEntry(form_container)
        desc_entry.pack(fill="x", pady=(0, 20))
        if article_data:
            desc_entry.set(article_data.get('summary', ''))
        vars['summary'] = desc_entry
        
        # Contenu
        tk.Label(form_container, text="Contenu", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        content_frame = tk.Frame(form_container, bg="#2C2C2E", highlightbackground="#3A3A3C", 
                               highlightthickness=1)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        content_text = tk.Text(content_frame, bg="#1C1C1E", fg="white", font=("Segoe UI", 11),
                             border=0, padx=10, pady=8, wrap=tk.WORD, height=10)
        content_text.pack(fill="both", expand=True)
        
        if article_data:
            content_text.insert("1.0", article_data.get('content', ''))
        vars['content'] = content_text
        
        # Statut
        tk.Label(form_container, text="Statut", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        status_var = tk.StringVar(value=article_data.get('status', 'draft') if article_data else 'draft')
        status_frame = tk.Frame(form_container, bg="#1C1C1E")
        status_frame.pack(fill="x", pady=(0, 20))
        
        statuses = [
            ("Brouillon", "draft"),
            ("Publié", "published"),
            ("Archivé", "archived")
        ]
        
        for text, value in statuses:
            rb = tk.Radiobutton(status_frame, text=text, variable=status_var,
                              value=value, font=("Segoe UI", 11), bg="#1C1C1E",
                              fg="white", selectcolor="#1C1C1E")
            rb.pack(side="left", padx=10)
        vars['status'] = status_var
        
        # Boutons
        button_frame = tk.Frame(dialog, bg="#1C1C1E")
        button_frame.pack(fill="x", padx=40, pady=20)
        
        def save_article():
            # Validation
            if not vars['title'].get():
                messagebox.showerror("Erreur", "Le titre est obligatoire")
                return
                
            try:
                article_obj = {
                    'title': vars['title'].get(),
                    'summary': vars['summary'].get(),
                    'content': vars['content'].get("1.0", "end-1c"),
                    'categoryName': vars['category'].get(),
                    'status': vars['status'].get(),
                    'authorId': self.current_user['id']
                }
                
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                
                if article_data:
                    response = requests.put(f"{self.base_url}/api/articles/{article_data['id']}", 
                                          json=article_obj, headers=headers)
                else:
                    response = requests.post(f"{self.base_url}/api/articles", 
                                           json=article_obj, headers=headers)
                    
                if response.status_code in [200, 201]:
                    dialog.destroy()
                    self.refresh_articles()
                    self.show_notification("✅ Article enregistré", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'enregistrement")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
        ModernButton(button_frame, text="Enregistrer", command=save_article,
                    style="primary", icon="💾").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
    def preview_article(self):
        """Prévisualise l'article sélectionné"""
        selection = self.article_tree.selection()
        if not selection:
            return
            
        item = self.article_tree.item(selection[0])
        article_id = item['values'][0]
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/articles/{article_id}", headers=headers)
            
            if response.status_code == 200:
                article = response.json()
                self.show_article_preview(article)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def show_article_preview(self, article):
        """Affiche la prévisualisation d'un article"""
        preview = tk.Toplevel(self.root)
        preview.title("Prévisualisation")
        preview.geometry("700x600")
        preview.configure(bg="#1C1C1E")
        preview.transient(self.root)
        
        # Centrer
        preview.update_idletasks()
        x = (preview.winfo_screenwidth() // 2) - 350
        y = (preview.winfo_screenheight() // 2) - 300
        preview.geometry(f"700x600+{x}+{y}")
        
        # Contenu
        content_frame = tk.Frame(preview, bg="#1C1C1E")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Titre
        tk.Label(content_frame, text=article.get('title', ''), 
                font=("Segoe UI", 24, "bold"), bg="#1C1C1E", fg="white",
                wraplength=640).pack(anchor="w", pady=(0, 10))
        
        # Méta
        meta_frame = tk.Frame(content_frame, bg="#1C1C1E")
        meta_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(meta_frame, text=f"📁 {article.get('categoryName', '')}",
                font=("Segoe UI", 10), bg="#1C1C1E", fg="#007AFF").pack(side="left", padx=(0, 20))
        tk.Label(meta_frame, text=f"✍️ {article.get('authorName', '')}",
                font=("Segoe UI", 10), bg="#1C1C1E", fg="#8E8E93").pack(side="left", padx=(0, 20))
        tk.Label(meta_frame, text=f"📅 {article.get('publishedDate', '')[:10]}",
                font=("Segoe UI", 10), bg="#1C1C1E", fg="#8E8E93").pack(side="left")
        
        # Description
        if article.get('summary'):
            tk.Label(content_frame, text=article['summary'],
                    font=("Segoe UI", 12, "italic"), bg="#1C1C1E", fg="#8E8E93",
                    wraplength=640, justify="left").pack(anchor="w", pady=(0, 20))
        
        # Contenu avec scrollbar
        text_frame = tk.Frame(content_frame, bg="#2C2C2E")
        text_frame.pack(fill="both", expand=True)
        
        text_widget = tk.Text(text_frame, bg="#2C2C2E", fg="white", font=("Segoe UI", 11),
                            wrap=tk.WORD, padx=20, pady=20, relief="flat")
        text_scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        
        text_widget.pack(side="left", fill="both", expand=True)
        text_scrollbar.pack(side="right", fill="y")
        
        text_widget.config(yscrollcommand=text_scrollbar.set)
        text_widget.insert("1.0", article.get('content', ''))
        text_widget.config(state="disabled")
        
        # Bouton fermer
        ModernButton(content_frame, text="Fermer", command=preview.destroy,
                    style="secondary").pack(pady=(20, 0))
        
    def duplicate_article(self):
        """Duplique l'article sélectionné"""
        selection = self.article_tree.selection()
        if not selection:
            return
            
        item = self.article_tree.item(selection[0])
        article_id = item['values'][0]
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/articles/{article_id}", headers=headers)
            
            if response.status_code == 200:
                article = response.json()
                article['title'] = article['title'] + " (Copie)"
                article['status'] = 'draft'
                del article['id']
                self.open_article_dialog(article)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def publish_article(self):
        """Publie l'article sélectionné"""
        self.update_article_status('published')
        
    def archive_article(self):
        """Archive l'article sélectionné"""
        self.update_article_status('archived')
        
    def update_article_status(self, status):
        """Met à jour le statut d'un article"""
        selection = self.article_tree.selection()
        if not selection:
            return
            
        item = self.article_tree.item(selection[0])
        article_id = item['values'][0]
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.patch(f"{self.base_url}/api/articles/{article_id}/status", 
                                    json={'status': status}, headers=headers)
            
            if response.status_code == 200:
                self.refresh_articles()
                status_text = {'published': 'publié', 'archived': 'archivé'}.get(status, status)
                self.show_notification(f"✅ Article {status_text}", "success")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la mise à jour")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def delete_article(self):
        """Supprime l'article sélectionné"""
        selection = self.article_tree.selection()
        if not selection:
            return
            
        item = self.article_tree.item(selection[0])
        article_id = item['values'][0]
        title = item['values'][1]
        
        if messagebox.askyesno("Confirmation", f"Supprimer l'article '{title}' ?"):
            try:
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                response = requests.delete(f"{self.base_url}/api/articles/{article_id}", headers=headers)
                
                if response.status_code == 204:
                    self.refresh_articles()
                    self.show_notification("✅ Article supprimé", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la suppression")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
    def show_categories(self):
        """Affiche la gestion complète des catégories"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="Gestion des Catégories", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack(side="left", padx=30)
        
        # Boutons d'action
        action_frame = tk.Frame(header_content, bg="#0A0A0A")
        action_frame.pack(side="right", padx=30)
        
        ModernButton(action_frame, text="Nouvelle catégorie", command=self.new_category, 
                    icon="➕", style="primary").pack(side="left", padx=5)
        ModernButton(action_frame, text="Actualiser", command=self.refresh_categories, 
                    icon="🔄", style="secondary").pack(side="left", padx=5)
        
        # Table des catégories
        table_frame = tk.Frame(self.content_area, bg="#1C1C1E")
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Treeview pour les catégories
        tree_container = tk.Frame(table_frame, bg="#1C1C1E")
        tree_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        
        self.category_tree = ttk.Treeview(tree_container,
                                         columns=('ID', 'Nom', 'Description', 'Articles'),
                                         show='headings',
                                         yscrollcommand=vsb.set,
                                         height=15)
        
        vsb.config(command=self.category_tree.yview)
        
        # Configure columns
        columns = [
            ('ID', 60),
            ('Nom', 200),
            ('Description', 400),
            ('Articles', 100)
        ]
        
        for col, width in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=width)
        
        self.category_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Menu contextuel
        self.create_category_context_menu()
        
        # Bindings
        self.category_tree.bind('<Double-Button-1>', lambda e: self.edit_category())
        self.category_tree.bind('<Button-3>', self.show_category_context_menu)
        
        # Charger les catégories
        self.refresh_categories()
        
    def create_category_context_menu(self):
        """Crée un menu contextuel pour les catégories"""
        self.category_context_menu = tk.Menu(self.root, tearoff=0, bg="#2C2C2E", fg="white",
                                           activebackground="#007AFF", activeforeground="white")
        self.category_context_menu.add_command(label="✏️  Modifier", command=self.edit_category)
        self.category_context_menu.add_command(label="📄  Voir les articles", command=self.view_category_articles)
        self.category_context_menu.add_separator()
        self.category_context_menu.add_command(label="🗑️  Supprimer", command=self.delete_category)
        
    def show_category_context_menu(self, event):
        """Affiche le menu contextuel des catégories"""
        item = self.category_tree.identify_row(event.y)
        if item:
            self.category_tree.selection_set(item)
            self.category_context_menu.post(event.x_root, event.y_root)
            
    def refresh_categories(self):
        """Actualise la liste des catégories"""
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/categories", headers=headers)
            
            if response.status_code == 200:
                categories = response.json()
                self.all_categories = categories
                
                for category in categories:
                    # Compter les articles de la catégorie
                    article_count = len([a for a in self.all_articles 
                                       if a.get('categoryName') == category.get('name')])
                    
                    self.category_tree.insert('', 'end', values=(
                        category.get('id', ''),
                        category.get('name', ''),
                        category.get('description', ''),
                        article_count
                    ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des catégories: {str(e)}")
            
    def new_category(self):
        """Ouvre la fenêtre de création de catégorie"""
        self.open_category_dialog()
        
    def edit_category(self):
        """Modifie une catégorie"""
        selection = self.category_tree.selection()
        if not selection:
            return
            
        item = self.category_tree.item(selection[0])
        values = item['values']
        
        category_data = {
            'id': values[0],
            'name': values[1],
            'description': values[2]
        }
        
        self.open_category_dialog(category_data)
        
    def open_category_dialog(self, category_data=None):
        """Dialogue pour créer/modifier une catégorie"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvelle catégorie" if category_data is None else "Modifier catégorie")
        dialog.geometry("500x400")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="🏷️", font=("Segoe UI", 32),
                bg="#0A0A0A", fg="#007AFF").pack()
        tk.Label(header_content, text="Nouvelle catégorie" if not category_data else "Modifier catégorie",
                font=("Segoe UI", 16, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Form
        form_container = tk.Frame(dialog, bg="#1C1C1E")
        form_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Nom
        tk.Label(form_container, text="Nom", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        name_entry = ModernEntry(form_container)
        name_entry.pack(fill="x", pady=(0, 20))
        if category_data:
            name_entry.set(category_data.get('name', ''))
        
        # Description
        tk.Label(form_container, text="Description", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        desc_frame = tk.Frame(form_container, bg="#2C2C2E", highlightbackground="#3A3A3C", 
                             highlightthickness=1)
        desc_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        desc_text = tk.Text(desc_frame, bg="#1C1C1E", fg="white", font=("Segoe UI", 11),
                           border=0, padx=10, pady=8, wrap=tk.WORD)
        desc_text.pack(fill="both", expand=True)
        
        if category_data:
            desc_text.insert("1.0", category_data.get('description', ''))
        
        # Boutons
        button_frame = tk.Frame(dialog, bg="#1C1C1E")
        button_frame.pack(fill="x", padx=40, pady=(0, 30))
        
        def save_category():
            name = name_entry.get()
            description = desc_text.get("1.0", "end-1c")
            
            if not name:
                messagebox.showerror("Erreur", "Le nom est obligatoire")
                return
            
            try:
                category_obj = {
                    'name': name,
                    'description': description
                }
                
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                
                if category_data:
                    response = requests.put(f"{self.base_url}/api/categories/{category_data['id']}", 
                                          json=category_obj, headers=headers)
                else:
                    response = requests.post(f"{self.base_url}/api/categories", 
                                           json=category_obj, headers=headers)
                
                if response.status_code in [200, 201]:
                    dialog.destroy()
                    self.refresh_categories()
                    self.show_notification("✅ Catégorie enregistrée", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'enregistrement")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
        ModernButton(button_frame, text="Enregistrer", command=save_category,
                    style="primary", icon="💾").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
    def delete_category(self):
        """Supprime une catégorie"""
        selection = self.category_tree.selection()
        if not selection:
            return
            
        item = self.category_tree.item(selection[0])
        category_id = item['values'][0]
        category_name = item['values'][1]
        article_count = item['values'][3]
        
        if article_count > 0:
            messagebox.showwarning("Attention", 
                                 f"Cette catégorie contient {article_count} article(s). "
                                 "Veuillez d'abord déplacer ou supprimer ces articles.")
            return
        
        if messagebox.askyesno("Confirmation", f"Supprimer la catégorie '{category_name}' ?"):
            try:
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                response = requests.delete(f"{self.base_url}/api/categories/{category_id}", headers=headers)
                
                if response.status_code == 204:
                    self.refresh_categories()
                    self.show_notification("✅ Catégorie supprimée", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la suppression")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
    def view_category_articles(self):
        """Affiche les articles d'une catégorie"""
        selection = self.category_tree.selection()
        if not selection:
            return
            
        item = self.category_tree.item(selection[0])
        category_name = item['values'][1]
        
        # Basculer vers la vue articles avec filtre
        self.show_article_management()
        self.category_filter.set(category_name)
        self.filter_articles()
        
    def show_token_management(self):
        """Affiche la gestion des jetons d'authentification"""
        if self.current_user['role'] != 'ADMIN':
            messagebox.showerror("Accès refusé", "Cette fonctionnalité est réservée aux administrateurs")
            return
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="Gestion des Jetons API", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack(side="left", padx=30)
        
        # Boutons d'action
        action_frame = tk.Frame(header_content, bg="#0A0A0A")
        action_frame.pack(side="right", padx=30)
        
        ModernButton(action_frame, text="Nouveau jeton", command=self.generate_token, 
                    icon="🔑", style="primary").pack(side="left", padx=5)
        ModernButton(action_frame, text="Actualiser", command=self.refresh_tokens, 
                    icon="🔄", style="secondary").pack(side="left", padx=5)
        
        # Instructions
        info_frame = tk.Frame(self.content_area, bg="#1C1C1E")
        info_frame.pack(fill="x", padx=30, pady=20)
        
        info_text = """Les jetons d'authentification permettent d'accéder aux services web SOAP. 
Chaque jeton a une durée de validité limitée et peut être révoqué à tout moment."""
        
        tk.Label(info_frame, text="ℹ️ " + info_text, font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93", wraplength=1000, justify="left").pack(padx=20, pady=15)
        
        # Table des jetons
        table_frame = tk.Frame(self.content_area, bg="#1C1C1E")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Treeview pour les jetons
        tree_container = tk.Frame(table_frame, bg="#1C1C1E")
        tree_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        
        self.token_tree = ttk.Treeview(tree_container,
                                      columns=('ID', 'Jeton', 'Description', 'Créé le', 'Expire le', 'Statut'),
                                      show='headings',
                                      yscrollcommand=vsb.set,
                                      height=15)
        
        vsb.config(command=self.token_tree.yview)
        
        # Configure columns
        columns = [
            ('ID', 60),
            ('Jeton', 300),
            ('Description', 200),
            ('Créé le', 150),
            ('Expire le', 150),
            ('Statut', 100)
        ]
        
        for col, width in columns:
            self.token_tree.heading(col, text=col)
            self.token_tree.column(col, width=width)
        
        self.token_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Tags pour les couleurs
        self.token_tree.tag_configure('active', foreground='#34C759')
        self.token_tree.tag_configure('expired', foreground='#FF3B30')
        self.token_tree.tag_configure('revoked', foreground='#8E8E93')
        
        # Menu contextuel
        self.create_token_context_menu()
        
        # Bindings
        self.token_tree.bind('<Button-3>', self.show_token_context_menu)
        
        # Charger les jetons
        self.refresh_tokens()
        
    def create_token_context_menu(self):
        """Menu contextuel pour les jetons"""
        self.token_context_menu = tk.Menu(self.root, tearoff=0, bg="#2C2C2E", fg="white",
                                        activebackground="#007AFF", activeforeground="white")
        self.token_context_menu.add_command(label="📋  Copier le jeton", command=self.copy_token)
        self.token_context_menu.add_separator()
        self.token_context_menu.add_command(label="🗑️  Révoquer", command=self.revoke_token)
        
    def show_token_context_menu(self, event):
        """Affiche le menu contextuel des jetons"""
        item = self.token_tree.identify_row(event.y)
        if item:
            self.token_tree.selection_set(item)
            self.token_context_menu.post(event.x_root, event.y_root)
            
    def generate_token(self):
        """Génère un nouveau jeton"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouveau jeton API")
        dialog.geometry("500x350")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 175
        dialog.geometry(f"500x350+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="🔑", font=("Segoe UI", 32),
                bg="#0A0A0A", fg="#007AFF").pack()
        tk.Label(header_content, text="Nouveau jeton API",
                font=("Segoe UI", 16, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Form
        form_container = tk.Frame(dialog, bg="#1C1C1E")
        form_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        tk.Label(form_container, text="Description du jeton", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        desc_entry = ModernEntry(form_container, placeholder="Ex: Service SOAP Production")
        desc_entry.pack(fill="x", pady=(0, 20))
        
        tk.Label(form_container, text="Durée de validité", font=("Segoe UI", 11),
                bg="#1C1C1E", fg="#8E8E93").pack(anchor="w", pady=(0, 5))
        
        duration_var = tk.StringVar(value="30")
        duration_frame = tk.Frame(form_container, bg="#1C1C1E")
        duration_frame.pack(fill="x", pady=(0, 20))
        
        durations = [("7 jours", "7"), ("30 jours", "30"), ("90 jours", "90"), ("1 an", "365")]
        for text, value in durations:
            rb = tk.Radiobutton(duration_frame, text=text, variable=duration_var,
                              value=value, font=("Segoe UI", 11), bg="#1C1C1E",
                              fg="white", selectcolor="#1C1C1E")
            rb.pack(side="left", padx=10)
        
        # Boutons
        button_frame = tk.Frame(dialog, bg="#1C1C1E")
        button_frame.pack(fill="x", padx=40, pady=(0, 30))
        
        def create_token():
            description = desc_entry.get()
            if not description:
                messagebox.showerror("Erreur", "La description est obligatoire")
                return
            
            try:
                token_data = {
                    'description': description,
                    'validityDays': int(duration_var.get())
                }
                
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                response = requests.post(f"{self.base_url}/api/tokens", json=token_data, headers=headers)
                
                if response.status_code == 201:
                    result = response.json()
                    dialog.destroy()
                    self.refresh_tokens()
                    
                    # Afficher le jeton généré
                    self.show_generated_token(result['token'])
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la génération du jeton")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
        ModernButton(button_frame, text="Générer", command=create_token,
                    style="primary", icon="🔑").pack(side="left", padx=5)
        ModernButton(button_frame, text="Annuler", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
    def show_generated_token(self, token):
        """Affiche le jeton généré"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Jeton généré")
        dialog.geometry("600x350")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 175
        dialog.geometry(f"600x350+{x}+{y}")
        
        # Contenu
        content = tk.Frame(dialog, bg="#1C1C1E")
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        tk.Label(content, text="✅ Jeton généré avec succès", font=("Segoe UI", 16, "bold"),
                bg="#1C1C1E", fg="#34C759").pack(pady=(0, 20))
        
        tk.Label(content, text="⚠️ IMPORTANT: Copiez ce jeton maintenant, il ne sera plus affiché!",
                font=("Segoe UI", 11, "bold"), bg="#1C1C1E", fg="#FF9500").pack(pady=(0, 20))
        
        # Zone de texte pour le jeton
        token_frame = tk.Frame(content, bg="#2C2C2E", highlightbackground="#3A3A3C", 
                              highlightthickness=1)
        token_frame.pack(fill="x", pady=(0, 20))
        
        token_text = tk.Text(token_frame, bg="#1C1C1E", fg="#34C759", font=("Consolas", 11),
                            height=4, wrap=tk.WORD, padx=10, pady=10, relief="flat")
        token_text.pack(fill="both")
        token_text.insert("1.0", token)
        token_text.config(state="disabled")
        
        # Boutons
        button_frame = tk.Frame(content, bg="#1C1C1E")
        button_frame.pack()
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(token)
            self.show_notification("✅ Jeton copié dans le presse-papier", "success")
        
        ModernButton(button_frame, text="Copier", command=copy_to_clipboard,
                    style="primary", icon="📋").pack(side="left", padx=5)
        ModernButton(button_frame, text="Fermer", command=dialog.destroy,
                    style="secondary").pack(side="left", padx=5)
        
    def refresh_tokens(self):
        """Actualise la liste des jetons"""
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/tokens", headers=headers)
            
            if response.status_code == 200:
                tokens = response.json()
                
                for token in tokens:
                    # Déterminer le statut
                    if token.get('revoked', False):
                        status = '🔴 Révoqué'
                        tag = 'revoked'
                    elif token.get('expired', False):
                        status = '⏰ Expiré'
                        tag = 'expired'
                    else:
                        status = '🟢 Actif'
                        tag = 'active'
                    
                    # Formater les dates
                    created_date = token.get('createdAt', '')
                    expires_date = token.get('expiresAt', '')
                    
                    if created_date:
                        try:
                            date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            created_date = date_obj.strftime("%d/%m/%Y")
                        except:
                            pass
                            
                    if expires_date:
                        try:
                            date_obj = datetime.fromisoformat(expires_date.replace('Z', '+00:00'))
                            expires_date = date_obj.strftime("%d/%m/%Y")
                        except:
                            pass
                    
                    self.token_tree.insert('', 'end', values=(
                        token.get('id', ''),
                        token.get('token', '')[:50] + '...',
                        token.get('description', ''),
                        created_date,
                        expires_date,
                        status
                    ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des jetons: {str(e)}")
            
    def copy_token(self):
        """Copie le jeton sélectionné"""
        selection = self.token_tree.selection()
        if not selection:
            return
            
        item = self.token_tree.item(selection[0])
        token_id = item['values'][0]
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(f"{self.base_url}/api/tokens/{token_id}", headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.root.clipboard_clear()
                self.root.clipboard_append(token_data['token'])
                self.show_notification("✅ Jeton copié dans le presse-papier", "success")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def revoke_token(self):
        """Révoque le jeton sélectionné"""
        selection = self.token_tree.selection()
        if not selection:
            return
            
        item = self.token_tree.item(selection[0])
        token_id = item['values'][0]
        
        if messagebox.askyesno("Confirmation", "Révoquer ce jeton ? Cette action est irréversible."):
            try:
                headers = {'Authorization': f'Bearer {self.jwt_token}'}
                response = requests.delete(f"{self.base_url}/api/tokens/{token_id}", headers=headers)
                
                if response.status_code == 204:
                    self.refresh_tokens()
                    self.show_notification("✅ Jeton révoqué", "success")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la révocation")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
    def show_rest_services(self):
        """Affiche la section des services REST"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.content_area, bg="#0A0A0A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#0A0A0A")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="Services REST - Tests API", 
                font=("Segoe UI", 24, "bold"), bg="#0A0A0A", fg="white").pack()
        
        # Container principal
        main_container = tk.Frame(self.content_area, bg="#000000")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Contrôles
        control_frame = tk.Frame(main_container, bg="#1C1C1E")
        control_frame.pack(fill="x", pady=(0, 20))
        
        control_content = tk.Frame(control_frame, bg="#1C1C1E")
        control_content.pack(padx=20, pady=20)
        
        # Format selection
        tk.Label(control_content, text="Format de sortie:", font=("Segoe UI", 12),
                bg="#1C1C1E", fg="white").pack(side="left", padx=(0, 10))
        
        self.format_var = tk.StringVar(value="JSON")
        for format_type in ["JSON", "XML"]:
            rb = tk.Radiobutton(control_content, text=format_type, variable=self.format_var,
                              value=format_type, font=("Segoe UI", 11), bg="#1C1C1E",
                              fg="white", selectcolor="#1C1C1E", activebackground="#1C1C1E",
                              activeforeground="white")
            rb.pack(side="left", padx=10)
            
        # Boutons d'action
        button_frame = tk.Frame(control_content, bg="#1C1C1E")
        button_frame.pack(side="right", padx=(40, 0))
        
        ModernButton(button_frame, text="Tous les articles", command=self.load_all_articles,
                    icon="📄", style="primary").pack(side="left", padx=5)
        ModernButton(button_frame, text="Par catégorie", command=self.load_articles_by_category,
                    icon="🏷️", style="secondary").pack(side="left", padx=5)
        ModernButton(button_frame, text="Articles groupés", command=self.load_grouped_articles,
                    icon="📊", style="warning").pack(side="left", padx=5)
        
        # Zone de résultats
        result_frame = tk.Frame(main_container, bg="#1C1C1E")
        result_frame.pack(fill="both", expand=True)
        
        # Header de la zone de résultats
        result_header = tk.Frame(result_frame, bg="#2C2C2E")
        result_header.pack(fill="x")
        
        tk.Label(result_header, text="📋 Résultats API", font=("Segoe UI", 14, "bold"),
                bg="#2C2C2E", fg="white").pack(side="left", padx=20, pady=10)
        
        # Zone de texte avec style moderne
        text_frame = tk.Frame(result_frame, bg="#1C1C1E")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.rest_text = tk.Text(text_frame, wrap=tk.WORD, bg="#0A0A0A", fg="white",
                               font=("Consolas", 11), insertbackground="white",
                               selectbackground="#007AFF", selectforeground="white",
                               padx=20, pady=20, relief="flat")
        self.rest_text.pack(side="left", fill="both", expand=True)
        
        # Scrollbar moderne
        scrollbar = ttk.Scrollbar(text_frame, command=self.rest_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.rest_text.config(yscrollcommand=scrollbar.set)
        
        # Message par défaut
        self.rest_text.insert("1.0", "Cliquez sur un bouton ci-dessus pour tester les services REST...")
        self.rest_text.config(state="disabled")
        
    def load_all_articles(self):
        """Charge tous les articles via REST"""
        self.show_loading("Chargement des articles...")
        
        try:
            headers = {'Accept': f'application/{self.format_var.get().lower()}'}
            response = requests.get(f"{self.base_url}/api/rest/articles", headers=headers)
            
            self.hide_loading()
            
            if response.status_code == 200:
                self.display_rest_response(response.text, self.format_var.get())
                self.show_notification("✅ Articles chargés avec succès", "success")
            else:
                self.show_notification("❌ Erreur lors du chargement", "error")
                
        except Exception as e:
            self.hide_loading()
            self.show_notification("❌ Erreur de connexion", "error")
            
    def load_articles_by_category(self):
        """Charge les articles d'une catégorie via REST"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sélectionner une catégorie")
        dialog.geometry("400x200")
        dialog.configure(bg="#1C1C1E")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Contenu
        content = tk.Frame(dialog, bg="#1C1C1E")
        content.pack(expand=True)
        
        tk.Label(content, text="🏷️", font=("Segoe UI", 32),
                bg="#1C1C1E", fg="#007AFF").pack()
        tk.Label(content, text="Nom de la catégorie", font=("Segoe UI", 14),
                bg="#1C1C1E", fg="white").pack(pady=10)
        
        category_entry = ModernEntry(content, placeholder="Ex: Technologie")
        category_entry.pack(fill="x", padx=40, pady=10)
        category_entry.entry.focus()
        
        # Boutons
        button_frame = tk.Frame(content, bg="#1C1C1E")
        button_frame.pack(pady=