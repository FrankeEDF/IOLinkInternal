#!/usr/bin/env python3
"""
RFID Modbus Test GUI
Testing tool for RFID functions over Modbus RTU communication
Based on ModbusSpecRFID_Add.md specification
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
import serial.tools.list_ports


class RfidModbusTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Modbus Test GUI")
        self.root.geometry("1200x850")

        # Modbus client
        self.client = None
        self.connected = False
        self.polling_active = False
        self.polling_thread = None

        # Error display timer
        self.error_clear_timer = None

        # RFID tag types for reference
        self.tag_types = {
            0x0004: "MIFARE Classic 1K",
            0x0002: "MIFARE Classic 4K",
            0x0044: "MIFARE Ultralight",
            0x0344: "MIFARE DESFire EV1"
        }

        self.sak_types = {
            0x08: "MIFARE Classic 1K",
            0x18: "MIFARE Classic 4K",
            0x00: "MIFARE Ultralight",
            0x20: "MIFARE DESFire EV1"
        }

        self.create_widgets()
        self.refresh_ports()

    def is_data_block(self, block_num):
        """Check if block number is a standard data block (not UID block or trailer block)"""
        # Block 0 is UID/manufacturer block (read-only)
        if block_num == 0:
            return False
        
        # Trailer blocks: 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63
        # Formula: block_num % 4 == 3 for blocks 0-63 (MIFARE 1K range)
        if block_num <= 63 and (block_num % 4 == 3):
            return False
        
        # For MIFARE 4K (blocks 64-255), different structure:
        # Blocks 64-127: Groups of 16, trailer blocks at 79, 95, 111, 127
        # Blocks 128-255: Groups of 16, trailer blocks at 143, 159, ..., 255
        if block_num > 63:
            # MIFARE 4K sectors 16-31 (blocks 64-127): 16 blocks per sector
            if 64 <= block_num <= 127:
                sector_start = ((block_num - 64) // 16) * 16 + 64
                if block_num == sector_start + 15:  # Last block of sector is trailer
                    return False
            # MIFARE 4K sectors 32-39 (blocks 128-255): 16 blocks per sector  
            elif 128 <= block_num <= 255:
                sector_start = ((block_num - 128) // 16) * 16 + 128
                if block_num == sector_start + 15:  # Last block of sector is trailer
                    return False
        
        return True

    def is_read_only_block(self, block_num):
        """Check if block is read-only (UID/manufacturer block)"""
        return block_num == 0

    def get_block_info(self, block_num):
        """Get human-readable info about block type"""
        if block_num == 0:
            return "UID/Manufacturer Block (Read-Only)"
        elif not self.is_data_block(block_num):
            return "Trailer Block (Keys & Access Bits)"
        else:
            # Calculate sector number
            if block_num <= 63:
                sector = block_num // 4
                block_in_sector = block_num % 4
            elif block_num <= 127:
                sector = 16 + (block_num - 64) // 16
                block_in_sector = (block_num - 64) % 16
            else:
                sector = 32 + (block_num - 128) // 16
                block_in_sector = (block_num - 128) % 16
            return f"Data Block (Sector {sector}, Block {block_in_sector})"

    def update_block_info(self, *args):
        """Update block info label when block number changes"""
        try:
            block_num = self.block_num_var.get()
            block_info = self.get_block_info(block_num)
            self.block_info_var.set(block_info)
            
            # Update label color based on block type
            if block_num == 0:
                self.block_info_label.config(foreground="red")  # Read-only
            elif not self.is_data_block(block_num):
                self.block_info_label.config(foreground="orange")  # Trailer block
            else:
                self.block_info_label.config(foreground="green")  # Data block
        except tk.TclError:
            # Handle case when variable is being initialized
            pass

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Error Display Frame (at the top)
        self.create_error_display(main_frame)

        # Connection Frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(conn_frame, text="COM Port:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=5)

        ttk.Button(conn_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5)

        ttk.Label(conn_frame, text="Baudrate:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.baud_var = tk.StringVar(value="57600")
        baud_combo = ttk.Combobox(conn_frame, textvariable=self.baud_var, width=10)
        baud_combo['values'] = ('9600', '19200', '38400', '57600', '115200')
        baud_combo.grid(row=0, column=4, padx=5)

        ttk.Label(conn_frame, text="Slave ID:").grid(row=0, column=5, sticky=tk.W, padx=5)
        self.slave_id_var = tk.IntVar(value=1)
        slave_spin = ttk.Spinbox(conn_frame, from_=1, to=247, textvariable=self.slave_id_var, width=8)
        slave_spin.grid(row=0, column=6, padx=5)

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=7, padx=10)

        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=8, padx=10)

        # Function Block Selection Frame
        fb_frame = ttk.LabelFrame(main_frame, text="RFID Function Block (Register 1009)", padding="10")
        fb_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.fb_var = tk.IntVar(value=1)
        fb_options = [
            (0, "FB0: RFID Off (Standby)"),
            (1, "FB1: Read UID"),
            (2, "FB2: Read UID + MIFARE Classic R/W"),
            (3, "FB3: Read UID + Direct Commands")
        ]

        for value, text in fb_options:
            ttk.Radiobutton(fb_frame, text=text, variable=self.fb_var, value=value).grid(
                row=0, column=value, sticky=tk.W, padx=10
            )

        # Function block buttons
        fb_btn_frame = ttk.Frame(fb_frame)
        fb_btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(fb_btn_frame, text="Read Current FB", command=self.read_and_display_function_block).pack(side=tk.LEFT, padx=5)
        ttk.Button(fb_btn_frame, text="Set Function Block", command=self.set_function_block).pack(side=tk.LEFT, padx=5)

        # Create notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(3, weight=1)

        # Tab 1: Tag Information
        self.create_tag_info_tab(notebook)

        # Tab 2: MIFARE Operations
        self.create_mifare_tab(notebook)

        # Tab 3: Manual Register Access
        self.create_manual_tab(notebook)

        # Tab 4: Log
        self.create_log_tab(notebook)

        # Polling control
        poll_frame = ttk.Frame(main_frame)
        poll_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.poll_var = tk.BooleanVar(value=False)
        self.poll_check = ttk.Checkbutton(poll_frame, text="Auto-poll tag information",
                                          variable=self.poll_var, command=self.toggle_polling)
        self.poll_check.grid(row=0, column=0, padx=5)

        ttk.Label(poll_frame, text="Poll interval (ms):").grid(row=0, column=1, padx=5)
        self.poll_interval_var = tk.IntVar(value=500)
        poll_spin = ttk.Spinbox(poll_frame, from_=100, to=5000, increment=100,
                                textvariable=self.poll_interval_var, width=10)
        poll_spin.grid(row=0, column=2, padx=5)
        
        # Initialize block info display
        self.update_block_info()

    def create_error_display(self, parent):
        """Create non-modal error display frame with fixed height"""
        self.error_frame = ttk.Frame(parent, height=30)  # Fixed height
        self.error_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.error_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Error text display
        self.error_var = tk.StringVar()
        self.error_label = ttk.Label(self.error_frame, textvariable=self.error_var,
                                    foreground="red", font=("Arial", 10, "bold"))
        self.error_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.error_frame.columnconfigure(0, weight=1)
        self.error_frame.rowconfigure(0, weight=1)
        
        # Initially empty but visible (reserving space)
        self.error_var.set("")

    def show_error(self, message):
        """Display error message in non-modal way"""
        self.error_var.set(f"ERROR: {message}")
        self.error_label.config(foreground="red")

        # Cancel previous timer if exists
        if self.error_clear_timer:
            self.root.after_cancel(self.error_clear_timer)

        # Auto-clear error after 5 seconds
        self.error_clear_timer = self.root.after(5000, self.clear_error)

        # Also log the error
        self.log(f"Error: {message}")

    def clear_error(self):
        """Clear error display"""
        self.error_var.set("")
        if self.error_clear_timer:
            self.root.after_cancel(self.error_clear_timer)
            self.error_clear_timer = None

    def handle_error(self, error_msg, operation_name=""):
        """Common error handler for all operations"""
        # Stop auto-polling if active
        if self.polling_active:
            self.stop_polling_on_error()

        # Show error in non-modal display
        if operation_name:
            self.show_error(f"{operation_name}: {error_msg}")
        else:
            self.show_error(str(error_msg))

    def stop_polling_on_error(self):
        """Stop polling when error occurs"""
        self.polling_active = False
        self.poll_var.set(False)
        self.log("Auto-polling disabled due to error")

    def check_connection(self):
        """Check if connected, show error if not"""
        if not self.connected:
            self.show_error("Not connected to Modbus device")
            return False
        return True

    def create_tag_info_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Tag Information")

        # Create grid of tag information
        info_frame = ttk.LabelFrame(tab, text="Current Tag Data", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)

        # UID Length
        ttk.Label(info_frame, text="UID Length (2010):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.uid_length_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.uid_length_var, font=("Courier", 10)).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )

        # UID
        ttk.Label(info_frame, text="UID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.uid_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.uid_var, font=("Courier", 10)).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )

        # ATQA
        ttk.Label(info_frame, text="ATQA (2016):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.atqa_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.atqa_var, font=("Courier", 10)).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=2
        )

        # SAK
        ttk.Label(info_frame, text="SAK (2017):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.sak_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.sak_var, font=("Courier", 10)).grid(
            row=3, column=1, sticky=tk.W, padx=5, pady=2
        )

        # Tag Type
        ttk.Label(info_frame, text="Tag Type:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.tag_type_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.tag_type_var, font=("Courier", 10)).grid(
            row=4, column=1, sticky=tk.W, padx=5, pady=2
        )

        # Reader Version
        ttk.Label(info_frame, text="Reader Version:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.reader_version_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.reader_version_var, font=("Courier", 10)).grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=2
        )

        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)

        ttk.Button(btn_frame, text="Read Tag Info", command=self.read_tag_info).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Read Reader Version", command=self.read_reader_version).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_tag_info).grid(
            row=0, column=2, padx=5
        )

    def create_mifare_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="MIFARE Operations")

        # Key configuration
        key_frame = ttk.LabelFrame(tab, text="MIFARE Keys", padding="10")
        key_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(key_frame, text="Key A (1010-1012):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.key_a_var = tk.StringVar(value="FFFFFFFFFFFF")
        key_a_entry = ttk.Entry(key_frame, textvariable=self.key_a_var, width=20, font=("Courier", 10))
        key_a_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(key_frame, text="Key B (1013-1015):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.key_b_var = tk.StringVar(value="FFFFFFFFFFFF")
        key_b_entry = ttk.Entry(key_frame, textvariable=self.key_b_var, width=20, font=("Courier", 10))
        key_b_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(key_frame, text="Read Keys", command=self.read_mifare_keys).grid(
            row=0, column=2, rowspan=2, padx=10, pady=5
        )
        
        ttk.Button(key_frame, text="Write Keys", command=self.write_mifare_keys).grid(
            row=0, column=3, rowspan=2, padx=10, pady=5
        )

        # Block operations
        block_frame = ttk.LabelFrame(tab, text="Block Operations", padding="10")
        block_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Configure grid weights for stable layout
        block_frame.columnconfigure(2, weight=1)

        ttk.Label(block_frame, text="Block Number (1016):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.block_num_var = tk.IntVar(value=4)
        block_spin = ttk.Spinbox(block_frame, from_=0, to=255, textvariable=self.block_num_var, width=10,
                                command=self.update_block_info)
        block_spin.grid(row=0, column=1, padx=5, pady=2)
        
        # Add block type info label with fixed width
        self.block_info_var = tk.StringVar()
        self.block_info_label = ttk.Label(block_frame, textvariable=self.block_info_var, 
                                         font=("Arial", 9), foreground="blue", width=35)
        self.block_info_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)
        
        # Bind variable change to update block info
        self.block_num_var.trace_add('write', self.update_block_info)

        ttk.Label(block_frame, text="Block Data (1018-1025):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.block_data_var = tk.StringVar(value="00000000000000000000000000000000")
        block_data_entry = ttk.Entry(block_frame, textvariable=self.block_data_var, width=40, font=("Courier", 10))
        block_data_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2)
        
        # Add event handler to auto-pad with FF when focus is lost
        block_data_entry.bind('<FocusOut>', self.auto_pad_block_data)
        
        # Info label about auto-padding and block validation
        ttk.Label(block_frame, text="(Auto-pads with FF if less than 32 hex characters)", 
                 font=("Arial", 8), foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(block_frame, text="⚠️ Write only allowed for Data Blocks (Read allows all blocks)", 
                 font=("Arial", 8), foreground="red").grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)

        # Buttons
        btn_frame = ttk.Frame(block_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Read Block", command=self.read_mifare_block).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Write Block", command=self.write_mifare_block).grid(
            row=0, column=1, padx=5
        )

        # Data display
        data_frame = ttk.LabelFrame(tab, text="Block Data Display", padding="10")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        tab.rowconfigure(2, weight=1)

        self.block_display = scrolledtext.ScrolledText(data_frame, width=60, height=10, font=("Courier", 9))
        self.block_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.rowconfigure(0, weight=1)
        data_frame.columnconfigure(0, weight=1)

    def create_manual_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Manual Register Access")

        # Read registers
        read_frame = ttk.LabelFrame(tab, text="Read Registers", padding="10")
        read_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(read_frame, text="Start Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.read_addr_var = tk.IntVar(value=2000)
        read_addr_spin = ttk.Spinbox(read_frame, from_=0, to=65535, textvariable=self.read_addr_var, width=10)
        read_addr_spin.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(read_frame, text="Count:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.read_count_var = tk.IntVar(value=10)
        read_count_spin = ttk.Spinbox(read_frame, from_=1, to=125, textvariable=self.read_count_var, width=10)
        read_count_spin.grid(row=0, column=3, padx=5, pady=2)

        ttk.Button(read_frame, text="Read", command=self.manual_read).grid(row=0, column=4, padx=10)

        # Write registers
        write_frame = ttk.LabelFrame(tab, text="Write Registers", padding="10")
        write_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(write_frame, text="Start Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.write_addr_var = tk.IntVar(value=999)
        write_addr_spin = ttk.Spinbox(write_frame, from_=0, to=65535, textvariable=self.write_addr_var, width=10)
        write_addr_spin.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(write_frame, text="Values (hex, space separated):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.write_values_var = tk.StringVar(value="0000")
        write_values_entry = ttk.Entry(write_frame, textvariable=self.write_values_var, width=50)
        write_values_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=2)

        ttk.Button(write_frame, text="Write", command=self.manual_write).grid(row=1, column=4, padx=10)

        # Results display
        result_frame = ttk.LabelFrame(tab, text="Results", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        tab.rowconfigure(2, weight=1)

        self.manual_display = scrolledtext.ScrolledText(result_frame, width=70, height=15, font=("Courier", 9))
        self.manual_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

    def create_log_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Communication Log")

        # Log display
        log_frame = ttk.Frame(tab)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        self.log_display = scrolledtext.ScrolledText(log_frame, width=80, height=25, font=("Courier", 9))
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        # Control buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=0, padx=5)

        self.autoscroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_frame, text="Auto-scroll", variable=self.autoscroll_var).grid(row=0, column=1, padx=5)

    def refresh_ports(self):
        """Refresh available COM ports"""
        self.clear_error()  # Clear any error when action is taken
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def toggle_connection(self):
        """Connect or disconnect Modbus client"""
        self.clear_error()  # Clear any error when action is taken

        if not self.connected:
            try:
                port = self.port_var.get()
                baudrate = int(self.baud_var.get())

                self.client = ModbusSerialClient(
                    port=port,
                    baudrate=baudrate,
                    parity='E',
                    method='rtu',
                    timeout=0.5
                )

                if self.client.connect():
                    self.connected = True
                    self.connect_btn.config(text="Disconnect")
                    self.status_label.config(text="Connected", foreground="green")
                    self.log(f"Connected to {port} at {baudrate} baud")
                    
                    # Read current function block from device
                    self.read_current_function_block()
                else:
                    raise Exception("Failed to connect")

            except Exception as e:
                self.handle_error(e, "Connection")
        else:
            # Stop polling if active
            if self.polling_active:
                self.polling_active = False
                self.poll_var.set(False)
                self.log("Stopped polling due to disconnection")

            if self.client:
                self.client.close()

            self.connected = False
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Disconnected", foreground="red")
            self.log("Disconnected")

    def log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_display.insert(tk.END, f"[{timestamp}] {message}\n")
        if self.autoscroll_var.get():
            self.log_display.see(tk.END)

    def clear_log(self):
        """Clear log display"""
        self.log_display.delete(1.0, tk.END)

    def modbus_read_registers(self, address, count, unit_id=None):
        """Helper function for Modbus read with error handling"""
        if unit_id is None:
            unit_id = self.slave_id_var.get()

        result = self.client.read_holding_registers(address, count, unit=unit_id)
        if result.isError():
            raise Exception(f"Modbus error: {result}")
        return result.registers

    def modbus_write_register(self, address, value, unit_id=None):
        """Helper function for single register write using FC 0x10 (Write Multiple Registers)"""
        if unit_id is None:
            unit_id = self.slave_id_var.get()

        # Use write_registers (FC 0x10) instead of write_register (FC 0x06)
        # to comply with device that only supports FC 0x03 and 0x10
        result = self.client.write_registers(address, [value], unit=unit_id)
        if result.isError():
            raise Exception(f"Modbus error: {result}")
        return result

    def modbus_write_registers(self, address, values, unit_id=None):
        """Helper function for multiple register write with error handling"""
        if unit_id is None:
            unit_id = self.slave_id_var.get()

        result = self.client.write_registers(address, values, unit=unit_id)
        if result.isError():
            raise Exception(f"Modbus error: {result}")
        return result

    def read_current_function_block(self):
        """Read current function block from device and update GUI (used on connect)"""
        try:
            # Read register 1009 to get current function block
            regs = self.modbus_read_registers(1009, 1)
            current_fb = regs[0] & 0xFF  # Only low byte is used
            
            # Update GUI radio button
            if current_fb in [0, 1, 2, 3]:  # Valid FB values
                self.fb_var.set(current_fb)
                self.log(f"Current function block: FB{current_fb}")
                
                # Show info message
                fb_names = {
                    0: "RFID Off (Standby)",
                    1: "Read UID",
                    2: "Read UID + MIFARE R/W",
                    3: "Read UID + Direct Commands"
                }
                self.show_success(f"Device is in FB{current_fb}: {fb_names.get(current_fb, 'Unknown')}")
            else:
                self.log(f"Unknown function block value: {current_fb}")
                
        except Exception as e:
            # Don't use handle_error here to avoid stopping the connection process
            self.log(f"Could not read function block: {e}")
            # Set default to FB1
            self.fb_var.set(1)
    
    def read_and_display_function_block(self):
        """Read current function block when user clicks button"""
        self.clear_error()
        if not self.check_connection():
            return
            
        try:
            # Read register 1009 to get current function block
            regs = self.modbus_read_registers(1009, 1)
            current_fb = regs[0] & 0xFF  # Only low byte is used
            
            # Update GUI radio button
            if current_fb in [0, 1, 2, 3]:  # Valid FB values
                self.fb_var.set(current_fb)
                
                # Show info message
                fb_names = {
                    0: "RFID Off (Standby)",
                    1: "Read UID",
                    2: "Read UID + MIFARE R/W",
                    3: "Read UID + Direct Commands"
                }
                self.log(f"Current function block: FB{current_fb} - {fb_names.get(current_fb, 'Unknown')}")
                self.show_success(f"Device is in FB{current_fb}: {fb_names.get(current_fb, 'Unknown')}")
            else:
                self.log(f"Unknown function block value: {current_fb}")
                self.show_error(f"Unknown function block value: {current_fb}")
                
        except Exception as e:
            self.handle_error(e, "Read function block")
    
    def set_function_block(self):
        """Set RFID function block"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            fb_value = self.fb_var.get()
            self.modbus_write_register(1009, fb_value)
            self.log(f"Set function block to {fb_value}")
            self.show_success(f"Function block set to FB{fb_value}")

        except Exception as e:
            self.handle_error(e, "Set function block")

    def show_success(self, message):
        """Show success message briefly in status area"""
        # Use the error display for success messages too, but in green
        self.error_var.set(f"SUCCESS: {message}")
        self.error_label.config(foreground="green")

        # Cancel previous timer if exists
        if self.error_clear_timer:
            self.root.after_cancel(self.error_clear_timer)

        # Auto-clear after 3 seconds
        self.error_clear_timer = self.root.after(3000, self.clear_error)

        # Restore red color for errors
        self.root.after(3100, lambda: self.error_label.config(foreground="red"))

    def read_tag_info(self):
        """Read tag information from registers 2010-2017"""
        if not self.check_connection():
            return

        try:
            # Read registers 2010-2017 (8 registers)
            regs = self.modbus_read_registers(2010, 8)

            # Parse UID length
            uid_length = regs[0] & 0xFF
            self.uid_length_var.set(str(uid_length))

            # Parse UID (up to 10 bytes from registers 2011-2015)
            uid_bytes = []
            for i in range(1, 6):  # Registers 2011-2015
                uid_bytes.append((regs[i] >> 8) & 0xFF)
                uid_bytes.append(regs[i] & 0xFF)

            # Format UID based on length
            if uid_length > 0:
                uid_hex = ' '.join([f'{b:02X}' for b in uid_bytes[:uid_length]])
                self.uid_var.set(uid_hex)
            else:
                self.uid_var.set("No tag detected")

            # Parse ATQA
            atqa = regs[6]
            self.atqa_var.set(f"0x{atqa:04X}")

            # Parse SAK
            sak = regs[7] & 0xFF
            self.sak_var.set(f"0x{sak:02X}")

            # Determine tag type
            if uid_length > 0:
                tag_type = self.tag_types.get(atqa, "Unknown")
                sak_type = self.sak_types.get(sak, "Unknown")
                if tag_type == sak_type:
                    self.tag_type_var.set(tag_type)
                else:
                    self.tag_type_var.set(f"{tag_type} / {sak_type}")
            else:
                self.tag_type_var.set("--")

            self.log("Tag information read successfully")

        except Exception as e:
            self.handle_error(e, "Read tag info")

    def clear_tag_info(self):
        """Clear tag information display"""
        self.clear_error()
        self.uid_length_var.set("--")
        self.uid_var.set("--")
        self.atqa_var.set("--")
        self.sak_var.set("--")
        self.tag_type_var.set("--")

    def read_reader_version(self):
        """Read RFID reader software version"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # Read 17 registers (0x22 = 34 bytes) for version string as per spec
            regs = self.modbus_read_registers(2030, 17)

            # Convert registers to bytes (34 bytes total)
            version_bytes = []
            for reg in regs:
                version_bytes.append((reg >> 8) & 0xFF)
                version_bytes.append(reg & 0xFF)

            # Convert to string, handling mixed ASCII and binary data
            version_parts = []
            current_ascii = ""

            for i, b in enumerate(version_bytes):
                if 32 <= b < 127:  # Printable ASCII
                    current_ascii += chr(b)
                else:
                    # Non-ASCII byte
                    if current_ascii:
                        version_parts.append(current_ascii)
                        current_ascii = ""
                    if b != 0:  # Don't show null bytes
                        version_parts.append(f"0x{b:02X}")

            # Add any remaining ASCII
            if current_ascii:
                version_parts.append(current_ascii)

            if version_parts:
                version_str = " ".join(version_parts)
                self.reader_version_var.set(version_str)
                self.log(f"Reader version: {version_str}")

                # Also log raw hex for debugging
                hex_str = " ".join([f"{b:02X}" for b in version_bytes])
                self.log(f"Reader version (raw): {hex_str}")
            else:
                self.reader_version_var.set("No readable data")
                hex_str = " ".join([f"{b:02X}" for b in version_bytes])
                self.log(f"Reader version (hex only): {hex_str}")

        except Exception as e:
            self.handle_error(e, "Read reader version")

    def read_mifare_key_a(self):
        """Read MIFARE Key A from registers"""
        try:
            # Clear the display field to show reading is in progress
            self.key_a_var.set("------------")
            self.root.update_idletasks()  # Force GUI update to show the dashes
            
            # Read Key A (registers 1010-1012, 3 registers = 6 bytes)
            key_a_regs = self.modbus_read_registers(1010, 3)
            
            # Convert Key A registers to hex string
            key_a_bytes = []
            for reg in key_a_regs:
                key_a_bytes.append((reg >> 8) & 0xFF)
                key_a_bytes.append(reg & 0xFF)
            key_a_hex = ''.join([f'{b:02X}' for b in key_a_bytes])
            
            # Update the GUI field
            self.key_a_var.set(key_a_hex)
            self.log(f"Read Key A: {key_a_hex}")
            return True
            
        except Exception as e:
            self.key_a_var.set("ERROR")
            self.log(f"Failed to read Key A: {e}")
            return False

    def read_mifare_key_b(self):
        """Read MIFARE Key B from registers"""
        try:
            # Clear the display field to show reading is in progress
            self.key_b_var.set("------------")
            self.root.update_idletasks()  # Force GUI update to show the dashes
            
            # Read Key B (registers 1013-1015, 3 registers = 6 bytes)
            key_b_regs = self.modbus_read_registers(1013, 3)
            
            # Convert Key B registers to hex string
            key_b_bytes = []
            for reg in key_b_regs:
                key_b_bytes.append((reg >> 8) & 0xFF)
                key_b_bytes.append(reg & 0xFF)
            key_b_hex = ''.join([f'{b:02X}' for b in key_b_bytes])
            
            # Update the GUI field
            self.key_b_var.set(key_b_hex)
            self.log(f"Read Key B: {key_b_hex}")
            return True
            
        except Exception as e:
            self.key_b_var.set("ERROR")
            self.log(f"Failed to read Key B: {e}")
            return False

    def read_mifare_keys(self):
        """Read MIFARE keys from registers"""
        self.clear_error()
        if not self.check_connection():
            return

        # Read both keys separately
        success_a = self.read_mifare_key_a()
        success_b = self.read_mifare_key_b()
        
        # Show error if both failed
        if not success_a and not success_b:
            self.handle_error("Failed to read both keys", "Read MIFARE keys")
        elif not success_a:
            self.show_error("Failed to read Key A")
        elif not success_b:
            self.show_error("Failed to read Key B")

    def write_mifare_key_a(self):
        """Write MIFARE Key A to registers"""
        try:
            # Parse Key A
            key_a_hex = self.key_a_var.get().replace(" ", "")
            if len(key_a_hex) != 12:
                raise ValueError("Key A must be 6 bytes (12 hex characters)")
            key_a_bytes = bytes.fromhex(key_a_hex)

            # Convert to registers (3 registers)
            key_a_regs = [
                (key_a_bytes[0] << 8) | key_a_bytes[1],
                (key_a_bytes[2] << 8) | key_a_bytes[3],
                (key_a_bytes[4] << 8) | key_a_bytes[5]
            ]

            # Write Key A (registers 1010-1012)
            self.modbus_write_registers(1010, key_a_regs)
            
            self.log(f"Written Key A: {key_a_hex}")
            return True
            
        except ValueError as e:
            self.log(f"Invalid Key A format: {e}")
            return False
        except Exception as e:
            self.log(f"Failed to write Key A: {e}")
            return False

    def write_mifare_key_b(self):
        """Write MIFARE Key B to registers"""
        try:
            # Parse Key B
            key_b_hex = self.key_b_var.get().replace(" ", "")
            if len(key_b_hex) != 12:
                raise ValueError("Key B must be 6 bytes (12 hex characters)")
            key_b_bytes = bytes.fromhex(key_b_hex)

            # Convert to registers (3 registers)
            key_b_regs = [
                (key_b_bytes[0] << 8) | key_b_bytes[1],
                (key_b_bytes[2] << 8) | key_b_bytes[3],
                (key_b_bytes[4] << 8) | key_b_bytes[5]
            ]

            # Write Key B (registers 1013-1015)
            self.modbus_write_registers(1013, key_b_regs)
            
            self.log(f"Written Key B: {key_b_hex}")
            return True
            
        except ValueError as e:
            self.log(f"Invalid Key B format: {e}")
            return False
        except Exception as e:
            self.log(f"Failed to write Key B: {e}")
            return False

    def write_mifare_keys(self):
        """Write MIFARE keys to registers"""
        self.clear_error()
        if not self.check_connection():
            return

        # Write both keys separately
        success_a = self.write_mifare_key_a()
        success_b = self.write_mifare_key_b()
        
        # Show appropriate message
        if success_a and success_b:
            self.log("MIFARE keys written successfully")
            self.show_success("Both MIFARE keys written")
        elif not success_a and not success_b:
            self.handle_error("Failed to write both keys", "Write MIFARE keys")
        elif not success_a:
            self.show_error("Failed to write Key A (Key B written)")
        elif not success_b:
            self.show_error("Failed to write Key B (Key A written)")

    def read_mifare_block(self):
        """Read MIFARE block data"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            block_num = self.block_num_var.get()

            # First write the block number
            self.modbus_write_register(1016, block_num)

            # Wait a bit for the operation
            time.sleep(0.1)

            # Read block data (registers 1018-1025, 8 registers = 16 bytes)
            regs = self.modbus_read_registers(1018, 8)

            # Convert to hex string
            block_bytes = []
            for reg in regs:
                block_bytes.append((reg >> 8) & 0xFF)
                block_bytes.append(reg & 0xFF)

            hex_str = ''.join([f'{b:02X}' for b in block_bytes])
            self.block_data_var.set(hex_str)

            # Display in block display
            display_str = f"Block {block_num:02d}: {hex_str}\n"
            display_str += f"  ASCII: {''.join([chr(b) if 32 <= b < 127 else '.' for b in block_bytes])}\n"
            self.block_display.insert(tk.END, display_str + "\n")
            self.block_display.see(tk.END)

            self.log(f"Read block {block_num}: {hex_str}")

        except Exception as e:
            self.handle_error(e, "Read MIFARE block")

    def auto_pad_block_data(self, event=None):
        """Auto-pad block data with FF to make it 32 hex characters"""
        try:
            # Get current value and remove spaces
            block_hex = self.block_data_var.get().replace(" ", "").upper()
            
            # Validate hex characters
            if block_hex and not all(c in '0123456789ABCDEF' for c in block_hex):
                return  # Don't modify if invalid hex
            
            # If empty, set to all FF
            if not block_hex:
                block_hex = "FF" * 16  # 32 hex characters
            # If too long, truncate to 32 hex characters
            elif len(block_hex) > 32:
                block_hex = block_hex[:32]
            # If too short, pad with FF to reach 32 hex characters
            elif len(block_hex) < 32:
                # Simply pad with F until we have 32 characters
                padding_needed = 32 - len(block_hex)
                block_hex += "F" * padding_needed
            
            # Update the field with padded value
            self.block_data_var.set(block_hex)
            
        except Exception:
            pass  # Silently ignore errors in auto-padding

    def write_mifare_block(self):
        """Write MIFARE block data"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            block_num = self.block_num_var.get()
            
            # Validate that only standard data blocks can be written
            if not self.is_data_block(block_num):
                if block_num == 0:
                    raise ValueError("Block 0 is the UID/Manufacturer block and cannot be written!\n" +
                                   "Writing to this block would make the transponder unusable.")
                else:
                    raise ValueError(f"Block {block_num} is a Trailer Block containing keys and access bits!\n" +
                                   "Writing to trailer blocks can lock the sector permanently.\n" +
                                   "Use the Key A/B fields instead to modify keys safely.")
            
            self.log(f"Writing to {self.get_block_info(block_num)}")
            
            # Parse and auto-pad block data
            block_hex = self.block_data_var.get().replace(" ", "").upper()
            
            # Validate hex characters
            if not all(c in '0123456789ABCDEF' for c in block_hex):
                raise ValueError("Block data must contain only hexadecimal characters (0-9, A-F)")
            
            # Auto-pad with F if less than 32 hex characters
            if len(block_hex) < 32:
                padding_needed = 32 - len(block_hex)
                block_hex += "F" * padding_needed
                self.log(f"Auto-padded block data with {padding_needed} hex character(s) 'F'")
                # Update the input field to show the padded value
                self.block_data_var.set(block_hex)
            elif len(block_hex) > 32:
                # Truncate if too long
                block_hex = block_hex[:32]
                self.log("Truncated block data to 32 hex characters")
                self.block_data_var.set(block_hex)
            
            # Now block_hex should be exactly 32 hex characters
            if len(block_hex) != 32:
                raise ValueError("Internal error: Block data is not 32 hex characters after padding")
            
            block_bytes = bytes.fromhex(block_hex)

            # Convert to registers (8 registers = 16 bytes)
            block_regs = []
            for i in range(0, 16, 2):
                reg = (block_bytes[i] << 8) | block_bytes[i+1]
                block_regs.append(reg)

            # Write block number
            self.modbus_write_register(1016, block_num)

            # Write block data (registers 1018-1025)
            self.modbus_write_registers(1018, block_regs)

            self.log(f"Wrote block {block_num}: {block_hex}")
            self.show_success(f"Block {block_num} written successfully")

        except Exception as e:
            self.handle_error(e, "Write MIFARE block")

    def manual_read(self):
        """Manual read of Modbus registers"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            start_addr = self.read_addr_var.get()
            count = self.read_count_var.get()

            regs = self.modbus_read_registers(start_addr, count)

            # Format output
            output = f"Read {count} registers from address {start_addr}:\n"
            output += "-" * 60 + "\n"
            output += "Addr    Dec     Hex    Binary            ASCII\n"
            output += "-" * 60 + "\n"

            for i, value in enumerate(regs):
                addr = start_addr + i
                high_byte = (value >> 8) & 0xFF
                low_byte = value & 0xFF
                ascii_str = ""
                if 32 <= high_byte < 127:
                    ascii_str += chr(high_byte)
                else:
                    ascii_str += "."
                if 32 <= low_byte < 127:
                    ascii_str += chr(low_byte)
                else:
                    ascii_str += "."

                output += f"{addr:5d}  {value:5d}  {value:04X}   {value:016b}  {ascii_str}\n"

            self.manual_display.delete(1.0, tk.END)
            self.manual_display.insert(1.0, output)

            self.log(f"Read {count} registers from address {start_addr}")

        except Exception as e:
            self.handle_error(e, "Manual read")

    def manual_write(self):
        """Manual write of Modbus registers"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            start_addr = self.write_addr_var.get()

            # Parse values
            values_str = self.write_values_var.get().strip()
            values = []
            for val_str in values_str.split():
                if val_str.startswith("0x") or val_str.startswith("0X"):
                    values.append(int(val_str, 16))
                else:
                    # Assume hex without prefix
                    values.append(int(val_str, 16))

            # Always use write_registers (FC 0x10) even for single values
            # because device only supports FC 0x03 and 0x10
            if len(values) == 1:
                self.modbus_write_register(start_addr, values[0])  # This now uses FC 0x10 internally
            else:
                self.modbus_write_registers(start_addr, values)

            self.log(f"Wrote {len(values)} register(s) to address {start_addr}: {[hex(v) for v in values]}")
            self.show_success(f"Successfully wrote {len(values)} register(s)")

        except Exception as e:
            self.handle_error(e, "Manual write")

    def toggle_polling(self):
        """Toggle automatic polling of tag information"""
        self.clear_error()
        if self.poll_var.get() and self.connected:
            self.polling_active = True
            self.polling_thread = threading.Thread(target=self.polling_worker, daemon=True)
            self.polling_thread.start()
            self.log("Started polling")
        else:
            self.polling_active = False
            self.poll_var.set(False)
            self.log("Stopped polling")

    def polling_worker(self):
        """Worker thread for polling tag information"""
        error_count = 0
        max_errors = 3  # Stop polling after 3 consecutive errors

        while self.polling_active and self.connected:
            try:
                # Use threading to avoid blocking GUI
                self.root.after(0, self.read_tag_info)
                error_count = 0  # Reset error count on successful read
                time.sleep(self.poll_interval_var.get() / 1000.0)
            except Exception as e:
                error_count += 1
                self.log(f"Polling error ({error_count}/{max_errors}): {e}")

                if error_count >= max_errors:
                    self.log(f"Auto-polling stopped after {max_errors} consecutive errors")
                    self.polling_active = False
                    self.root.after(0, lambda: self.poll_var.set(False))
                    break

                # Wait a bit longer before retrying after an error
                time.sleep(1.0)


def main():
    root = tk.Tk()
    app = RfidModbusTestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
