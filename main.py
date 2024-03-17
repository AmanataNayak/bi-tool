import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# For DataBase
import pandas as pd
import pymysql
import psycopg2

#For Cloud
import boto3  # For AWS
from azure.storage.blob import BlobServiceClient  # For Azure
from google.cloud import storage  # For GCP

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class VisualizationFrame(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.selected_column = tk.StringVar()
        self.selected_plot_type = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        columns_to_plot = self.data.columns.tolist()

        ttk.Label(self, text="Select Column to Plot:").pack()
        self.column_dropdown = ttk.Combobox(self, textvariable=self.selected_column, values=columns_to_plot)
        self.column_dropdown.pack()

        ttk.Label(self, text="Select Plot Type:").pack()
        self.plot_type_dropdown = ttk.Combobox(self, textvariable=self.selected_plot_type, values=["Bar", "Line", "Scatter", "Pie", "Histogram", "Box"])
        self.plot_type_dropdown.pack()

        self.column_dropdown.bind("<<ComboboxSelected>>", self.plot_selected_column)
        self.plot_type_dropdown.bind("<<ComboboxSelected>>", self.plot_selected_column)

        self.back_button = ttk.Button(self, text="Back", command=self.back_to_previous_frame)
        self.back_button.pack()

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_selected_column(self, event=None):
        self.ax.clear()

        selected_column = self.selected_column.get()
        plot_type = self.selected_plot_type.get()
        if selected_column and plot_type and self.data is not None:
            if plot_type == "Bar":
                self.ax.bar(self.data.index, self.data[selected_column])
            elif plot_type == "Line":
                self.ax.plot(self.data.index, self.data[selected_column])
            elif plot_type == "Scatter":
                self.ax.scatter(self.data.index, self.data[selected_column])
            elif plot_type == 'Pie':
                try:
                    self.ax.pie(self.data[selected_column].unique(), labels=self.data[selected_column].unique())
                except Exception as e:
                    messagebox.showerror('Error in plotting', f'{e}')
            elif plot_type == 'Histogram':
                self.ax.hist(self.data[selected_column], bins=10)
            elif plot_type == 'Box':
                self.ax.boxplot(self.data[selected_column])
            self.ax.set_xlabel('X Label')
            self.ax.set_ylabel('Y Label')
            self.ax.set_title(f'{plot_type} Plot of {selected_column}')

        self.canvas.draw()

    def back_to_previous_frame(self):
        self.pack_forget()
        self.master.label.pack(pady=5)
        self.master.combobox.pack(pady=5)
        self.master.select_button.pack(pady=5)
        self.master.create_frames()

class ProcessDataFrame(tk.Frame):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.data = self.load_data_from_file(self.file_path)
        if self.data is not None:
            self.create_widgets()
            self.display_dataframe("Data", self.data)
        else:
            self.display_file_load_error("Failed to load data from file. Please check the file path.")

    def load_data_from_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path)
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path)
            else:
                messagebox.showerror("File Format Error", "Unsupported file format. Please choose a CSV, JSON, or Excel file.")
                return None
            return data
        except Exception as e:
            print(f"Error loading data from file: {e}")
            return None

    def display_file_load_error(self, error_message):
        pass


    def create_widgets(self):
        self.treeview = ttk.Treeview(self)
        self.treeview.pack(side="top", fill='both',expand=True)

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side="left", fill="both",expand=True)

        self.data_info_label = ttk.Label(self.info_frame, text="Data Info:")
        self.data_info_label.pack( anchor="w")

        self.data_info_text = tk.Text(self.info_frame, wrap="word")
        self.data_info_text.pack(fill="both",)

        self.clean_button = ttk.Button(self, text="Clean Data", command=self.clean_data)
        self.clean_button.pack(side="right",anchor='center')

        self.back_button = ttk.Button(self, text="Back", command=self.go_back)
        self.back_button.pack(side="right", anchor='center')

        self.visualize_button = ttk.Button(self, text="Hii", command=self.go_to_visualization)
        self.visualize_button.pack(side="bottom")
            
        self.download_csv_button = ttk.Button(self, text="Download CSV", command=self.download_csv)
        self.download_csv_button.pack(side="bottom", anchor='center')

        self.download_json_button = ttk.Button(self, text="Download JSON", command=self.download_json)
        self.download_json_button.pack(side="bottom", anchor='center')

        self.download_excel_button = ttk.Button(self, text="Download Excel", command=self.download_excel)
        self.download_excel_button.pack(side="bottom", anchor='center')

    def download_csv(self):
        self.download_data(".csv")

    def download_json(self):
        self.download_data(".json")

    def download_excel(self):
        self.download_data(".xlsx")

    def download_data(self, extension):
        if self.data is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=extension, filetypes=[(extension.upper()[1:] + " files", "*" + extension)])
            if save_path:
                try:
                    if extension == ".csv":
                        self.data.to_csv(save_path, index=False)
                    elif extension == ".json":
                        self.data.to_json(save_path, orient="records", lines=True)
                    elif extension == ".xlsx":
                        self.data.to_excel(save_path, index=False)
                    messagebox.showinfo("Download Successful", f"Data has been successfully downloaded as {extension} format.")
                except Exception as e:
                    messagebox.showerror("Download Error", f"An error occurred while downloading: {str(e)}")
        else:
            messagebox.showerror("Download Error", "No data to download.")

    def replace_outliers_with_mean(self, df, column):
        mean = df[column].mean()
        std_dev = df[column].std()
        threshold = 2.5
        outliers = (df[column] - mean).abs() > threshold * std_dev
        df.loc[outliers, column] = mean

    def clean_data(self):
        try:
            self.data.dropna(inplace=True)
            numeric_columns = self.data.select_dtypes(include='number').columns
            for col in numeric_columns:
                self.replace_outliers_with_mean(self.data, col)
            messagebox.showinfo("Data Cleaning", "Data cleaned successfully.")
            self.update_treeview()  
        except Exception as e:
            messagebox.showerror("Data Cleaning Error", f"An error occurred during data cleaning: {str(e)}")

    def update_treeview(self):
        if self.data is not None:
            for child in self.treeview.get_children():
                self.treeview.delete(child)

            self.display_dataframe("Cleaned Data", self.data)

            self.update_data_info()
        else:
            messagebox.showinfo("Data Information", "No data loaded.")

    def display_dataframe(self, title, dataframe):
        self.treeview['columns'] = dataframe.columns.tolist()
        self.treeview.heading("#0", text=title)

        for col in dataframe.columns:
            if col in dataframe.columns:
                self.treeview.heading(col, text=col)
            
        for i, row in dataframe.iterrows():
            self.treeview.insert('', 'end', text=i, values=row.tolist())
        
        self.update_data_info()

    def update_data_info(self):
        if self.data is not None:
            info_str = f"Number of rows: {len(self.data)}\n"
            info_str += f"Number of columns: {len(self.data.columns)}\n"
            info_str += f"Column names: {', '.join(self.data.columns)}\n"
            info_str += f"Data types:\n{self.data.dtypes}\n\n"

            info_str += "Statistics:\n"
            for col in self.data.columns:
                info_str += f"{col}:\n"
                if np.issubdtype(self.data[col].dtype, np.number):  
                    info_str += f"Mean: {self.data[col].mean()}\n"
                    info_str += f"Median: {self.data[col].median()}\n"
                    info_str += f"Mode: {self.data[col].mode().iloc[0]}\n"
                    info_str += f"Standard Deviation: {self.data[col].std()}\n"
                    info_str += f"Variance: {self.data[col].var()}\n"
                    info_str += f"Min: {self.data[col].min()}\n"
                    info_str += f"Max: {self.data[col].max()}\n"
                    info_str += f"Q1 (First Quartile): {self.data[col].quantile(0.25)}\n"
                    info_str += f"Q3 (Third Quartile): {self.data[col].quantile(0.75)}\n\n"
                else:  
                    info_str += f"Mode: {self.data[col].mode().iloc[0]}\n"
                    info_str += f"Min: {self.data[col].min()}\n"
                    info_str += f"Max: {self.data[col].max()}\n\n"

            self.data_info_text.config(state="normal")
            self.data_info_text.delete("1.0", tk.END)
            self.data_info_text.insert(tk.END, info_str)
            self.data_info_text.config(state="disabled")
        else:
            messagebox.showinfo("Data Information", "No data loaded.")

    def go_back(self):        
        self.pack_forget()
        self.master.label.pack(pady=5)
        self.master.combobox.pack(pady=5)
        self.master.select_button.pack(pady=5)
        self.master.create_frames()

    def go_to_visualization(self):
        if self.data is not None:
            self.pack_forget()
            visualization_frame = VisualizationFrame(self.master, self.data)
            visualization_frame.pack(pady=10)
        else:
            messagebox.showinfo("Data Information", "No data loaded.")

class DatabaseConnectionFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_source = tk.StringVar()
        
        
        self.db_type = tk.StringVar()
        self.host = tk.StringVar()
        self.port = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.database_name = tk.StringVar()
        
        self.label_db_type = ttk.Label(self, text="Database Type:")
        self.label_db_type.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_db_type = ttk.Entry(self, textvariable=self.db_type)
        self.entry_db_type.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_host = ttk.Label(self, text="Host:")
        self.label_host.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_host = ttk.Entry(self, textvariable=self.host)
        self.entry_host.grid(row=1, column=1, padx=5, pady=5)
        
        self.label_port = ttk.Label(self, text="Port:")
        self.label_port.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_port = ttk.Entry(self, textvariable=self.port)
        self.entry_port.grid(row=2, column=1, padx=5, pady=5)
        
        self.label_username = ttk.Label(self, text="Username:")
        self.label_username.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_username = ttk.Entry(self, textvariable=self.username)
        self.entry_username.grid(row=3, column=1, padx=5, pady=5)
        
        self.label_password = ttk.Label(self, text="Password:")
        self.label_password.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_password = ttk.Entry(self, textvariable=self.password, show="*")
        self.entry_password.grid(row=4, column=1, padx=5, pady=5)
        
        self.label_database_name = ttk.Label(self, text="Database Name:")
        self.label_database_name.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entry_database_name = ttk.Entry(self, textvariable=self.database_name)
        self.entry_database_name.grid(row=5, column=1, padx=5, pady=5)
        
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect_to_database)
        self.connect_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        
    def connect_to_database(self):
        db_type = self.db_type.get()
        host = self.host.get()
        port = self.port.get()
        username = self.username.get()
        password = self.password.get()
        database_name = self.database_name.get()
        
        try:
            if db_type == "MySQL":
                connection = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database_name
                )
                tk.messagebox.showinfo("Database Connection", "Connected to MySQL database successfully.")
                connection.close()
            elif db_type == "PostgreSQL":
                connection = psycopg2.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database_name
                )
                tk.messagebox.showinfo("Database Connection", "Connected to PostgreSQL database successfully.")
                connection.close()
            else:
                tk.messagebox.showerror("Database Connection", "Unsupported database type.")
        except Exception as e:
            tk.messagebox.showerror("Database Connection", f"Failed to connect: {str(e)}")

class CloudServiceConnectionFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_source = tk.StringVar()
        
        
        self.service_type = tk.StringVar()
        self.access_key = tk.StringVar()
        self.secret_key = tk.StringVar()
        
        self.label_service_type = ttk.Label(self, text="Service Type:")
        self.label_service_type.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_service_type = ttk.Entry(self, textvariable=self.service_type)
        self.entry_service_type.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_access_key = ttk.Label(self, text="Access Key:")
        self.label_access_key.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_access_key = ttk.Entry(self, textvariable=self.access_key)
        self.entry_access_key.grid(row=1, column=1, padx=5, pady=5)
        
        self.label_secret_key = ttk.Label(self, text="Secret Key:")
        self.label_secret_key.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_secret_key = ttk.Entry(self, textvariable=self.secret_key, show="*")
        self.entry_secret_key.grid(row=2, column=1, padx=5, pady=5)
        
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect_to_cloud_service)
        self.connect_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
    def connect_to_cloud_service(self):
        service_type = self.service_type.get()
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()
        
        try:
            if service_type == "AWS":
                session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
                s3 = session.client('s3')
                buckets = s3.list_buckets()
                print("S3 Buckets:")
                for bucket in buckets['Buckets']:
                    print(bucket['Name'])
                tk.messagebox.showinfo("Cloud Service Connection", "Connected to AWS successfully.")
            elif service_type == "Azure":
                connect_str = f"DefaultEndpointsProtocol=https;AccountName={access_key};AccountKey={secret_key};EndpointSuffix=core.windows.net"
                blob_service_client = BlobServiceClient.from_connection_string(connect_str)
                containers = blob_service_client.list_containers()
                print("Azure Containers:")
                for container in containers:
                    print(container['name'])
                tk.messagebox.showinfo("Cloud Service Connection", "Connected to Azure successfully.")
            elif service_type == "GCP":
                client = storage.Client.from_service_account_json(access_key)
                buckets = client.list_buckets()
                print("GCP Buckets:")
                for bucket in buckets:
                    print(bucket.name)
                tk.messagebox.showinfo("Cloud Service Connection", "Connected to GCP successfully.")
            else:
                tk.messagebox.showerror("Cloud Service Connection", "Unsupported cloud service type.")
        except Exception as e:
            tk.messagebox.showerror("Cloud Service Connection", f"Failed to connect: {str(e)}")

class FileSelectionFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_source = tk.StringVar()
        
        self.file_path = None
        
        self.label = ttk.Label(self, text="Select File:")
        self.label.pack(pady=5)
        
        self.select_button = ttk.Button(self, text="Browse", command=self.select_file)
        self.select_button.pack(pady=5)
        
    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("JSON files", "*.json")])
        if self.file_path:
            self.pack_forget()
            self.parent.label.pack_forget()
            self.parent.combobox.pack_forget()
            self.parent.select_button.pack_forget()
            self.parent.create_process_frame(self.file_path)
        else:
            messagebox.showerror("File Selection Error", "No file selected. Please choose a file.")

class WebSourceConnectionFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_source = tk.StringVar()
        self.url = tk.StringVar()
        self.label_url = ttk.Label(self, text="URL:")
        self.label_url.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_url = ttk.Entry(self, textvariable=self.url, width=50)
        self.entry_url.grid(row=0, column=1, padx=5, pady=5)
        
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect_to_web_source)
        self.connect_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
    def connect_to_web_source(self):
        url = self.url.get()
        try:
            response = requests.get(url)
            if response.status_code == 200:

                tk.messagebox.showinfo("Web Source Connection", "Connected to web source successfully.")
            else:
                tk.messagebox.showerror("Web Source Connection", f"Failed to connect. Status code: {response.status_code}")
        except Exception as e:
            tk.messagebox.showerror("Web Source Connection", f"Failed to connect: {str(e)}")

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dynamic Data Source Connector")
        self.geometry("800x600")
        self.selected_source = tk.StringVar()
        
        
        self.label = ttk.Label(self, text="Select Data Source:")
        self.label.pack(pady=5)
        
        self.combobox = ttk.Combobox(self, textvariable=self.selected_source, values=["Database", "Cloud Service", "File", "Web Source"])
        self.combobox.pack(pady=5)
        
        self.select_button = ttk.Button(self, text="Select", command=self.select_data_source)
        self.select_button.pack(pady=5)
        
        self.frames = {}
        self.create_frames()
        self.frames["File"] = FileSelectionFrame(self)

    def create_frames(self):
        self.frames["Database"] = DatabaseConnectionFrame(self)
        self.frames["Cloud Service"] = CloudServiceConnectionFrame(self)
        self.frames["File"] = FileSelectionFrame(self)
        self.frames["Web Source"] = WebSourceConnectionFrame(self)

        for frame in self.frames.values():
            frame.pack_forget()

    def select_data_source(self):
        source_type = self.selected_source.get()

        if source_type in self.frames:
            for frame in self.frames.values():
                frame.pack_forget()
            if source_type == "File":
                self.frames[source_type].pack(pady=10)
                self.create_process_frame(self.frames[source_type].file_path)
            else:
                self.frames[source_type].pack(pady=10)
        else:
            messagebox.showerror("Error", "Invalid data source selected.")

    def create_process_frame(self, file_path):
        self.process_frame = self.process_frame = ProcessDataFrame(self, file_path)
        self.process_frame.pack(pady=10)


    def create_visualization_frame(self, data):
        self.frames["Visualization"] = VisualizationFrame(self, data)
        self.frames["Visualization"].pack(pady=10)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
