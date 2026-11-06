import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RetailSalesDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Retail Sales Analytics Dashboard")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f4f6f9")

        self.df = None

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f4f6f9")
        self.style.configure("TLabel", background="#f4f6f9", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50", background="#f4f6f9")
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#3498db", foreground="white")
        self.style.map("TButton", background=[("active", "#2980b9")])

        # Header Frame
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)

        title = ttk.Label(header_frame, text=" Retail Sales Dashboard", style="Header.TLabel")
        title.pack(side=tk.LEFT, padx=10)

        load_btn = ttk.Button(header_frame, text="Load CSV File", command=self.load_csv)
        load_btn.pack(side=tk.RIGHT, padx=10)

        # Filters Frame
        self.filter_frame = ttk.LabelFrame(self.root, text=" Dashboard Controls & Filters ", padding=10)
        self.filter_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(self.filter_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_cb = ttk.Combobox(self.filter_frame, state="readonly", values=["All"])
        self.category_cb.current(0)
        self.category_cb.grid(row=0, column=1, padx=5, pady=5)
        self.category_cb.bind("<<ComboboxSelected>>", self.update_dashboard)

        ttk.Label(self.filter_frame, text="Region:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.region_cb = ttk.Combobox(self.filter_frame, state="readonly", values=["All"])
        self.region_cb.current(0)
        self.region_cb.grid(row=0, column=3, padx=5, pady=5)
        self.region_cb.bind("<<ComboboxSelected>>", self.update_dashboard)

        # Summary KPIs Frame
        self.kpi_frame = ttk.Frame(self.root, padding=5)
        self.kpi_frame.pack(fill=tk.X, padx=15, pady=5)

        self.kpi_total_sales = ttk.Label(self.kpi_frame, text="Total Sales: $0.00", font=("Segoe UI", 12, "bold"), foreground="#27ae60")
        self.kpi_total_sales.pack(side=tk.LEFT, expand=True)

        self.kpi_total_orders = ttk.Label(self.kpi_frame, text="Total Orders: 0", font=("Segoe UI", 12, "bold"), foreground="#2980b9")
        self.kpi_total_orders.pack(side=tk.LEFT, expand=True)

        self.kpi_avg_order = ttk.Label(self.kpi_frame, text="Avg Order Value: $0.00", font=("Segoe UI", 12, "bold"), foreground="#8e44ad")
        self.kpi_avg_order.pack(side=tk.LEFT, expand=True)

        # Matplotlib Figure Canvas
        self.fig, self.axs = plt.subplots(2, 2, figsize=(10, 5.5), dpi=100)
        self.fig.patch.set_facecolor('#f4f6f9')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Automatically check for sample data
        if os.path.exists("retail_sales_data.csv"):
            self.load_data("retail_sales_data.csv")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            self.load_data(file_path)

    def load_data(self, file_path):
        try:
            df = pd.read_csv(file_path)
            required_cols = {"Date", "Category", "Region", "Quantity", "UnitPrice", "TotalSales"}
            if not required_cols.issubset(set(df.columns)):
                # If TotalSales missing, calculate it
                if {"Quantity", "UnitPrice"}.issubset(set(df.columns)):
                    df["TotalSales"] = df["Quantity"] * df["UnitPrice"]
                else:
                    messagebox.showerror("Error", f"CSV must contain at least: {required_cols}")
                    return

            df["Date"] = pd.to_datetime(df["Date"])
            self.df = df

            # Populate filter dropdowns
            categories = ["All"] + sorted(list(df["Category"].astype(str).unique()))
            regions = ["All"] + sorted(list(df["Region"].astype(str).unique()))

            self.category_cb["values"] = categories
            self.region_cb["values"] = regions
            self.category_cb.current(0)
            self.region_cb.current(0)

            self.update_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")

    def update_dashboard(self, event=None):
        if self.df is None:
            return

        filtered_df = self.df.copy()

        cat = self.category_cb.get()
        reg = self.region_cb.get()

        if cat != "All":
            filtered_df = filtered_df[filtered_df["Category"] == cat]
        if reg != "All":
            filtered_df = filtered_df[filtered_df["Region"] == reg]

        # Update KPI values
        total_sales = filtered_df["TotalSales"].sum()
        total_orders = len(filtered_df)
        avg_order = filtered_df["TotalSales"].mean() if total_orders > 0 else 0

        self.kpi_total_sales.config(text=f"Total Sales: ${total_sales:,.2f}")
        self.kpi_total_orders.config(text=f"Total Orders: {total_orders:,}")
        self.kpi_avg_order.config(text=f"Avg Order Value: ${avg_order:,.2f}")

        # Clear existing plots
        for ax in self.axs.flat:
            ax.clear()
            ax.set_facecolor('#ffffff')

        if filtered_df.empty:
            self.canvas.draw()
            return

        # 1. Sales Trend over Time
        daily_sales = filtered_df.groupby("Date")["TotalSales"].sum().reset_index()
        self.axs[0, 0].plot(daily_sales["Date"], daily_sales["TotalSales"], color="#2980b9", linewidth=1.5)
        self.axs[0, 0].set_title("Sales Trend Over Time", fontsize=10, fontweight="bold", pad=8)
        self.axs[0, 0].tick_params(axis='x', rotation=30, labelsize=7)
        self.axs[0, 0].tick_params(axis='y', labelsize=7)
        self.axs[0, 0].grid(True, linestyle="--", alpha=0.5)

        # 2. Sales by Category
        cat_sales = filtered_df.groupby("Category")["TotalSales"].sum().sort_values()
        bars1 = self.axs[0, 1].barh(cat_sales.index, cat_sales.values, color="#27ae60", edgecolor="none")
        self.axs[0, 1].set_title("Sales by Category", fontsize=10, fontweight="bold", pad=8)
        self.axs[0, 1].tick_params(labelsize=8)
        self.axs[0, 1].grid(axis="x", linestyle="--", alpha=0.5)

        # 3. Sales by Region
        reg_sales = filtered_df.groupby("Region")["TotalSales"].sum()
        self.axs[1, 0].bar(reg_sales.index, reg_sales.values, color="#e67e22", edgecolor="none")
        self.axs[1, 0].set_title("Sales by Region", fontsize=10, fontweight="bold", pad=8)
        self.axs[1, 0].tick_params(labelsize=8)
        self.axs[1, 0].grid(axis="y", linestyle="--", alpha=0.5)

        # 4. Top Sold Quantity Products/Categories
        qty_cat = filtered_df.groupby("Category")["Quantity"].sum()
        self.axs[1, 1].pie(qty_cat.values, labels=qty_cat.index, autopct='%1.1f%%', 
                           colors=["#3498db", "#9b59b6", "#e74c3c", "#f1c40f", "#1abc9c"],
                           textprops={'fontsize': 7})
        self.axs[1, 1].set_title("Units Sold Share by Category", fontsize=10, fontweight="bold", pad=8)

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RetailSalesDashboard(root)
    root.mainloop()
