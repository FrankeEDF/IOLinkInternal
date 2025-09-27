#!/usr/bin/env python3
"""
RFID Modbus Test GUI
Testing tool for RFID functions over Modbus RTU communication
Based on ModbusSpecRFID_Add.md specification
"""

VERSION = "1.0.0"

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.factory import ClientDecoder
import serial.tools.list_ports
import struct


class LoggingModbusClient(ModbusSerialClient):
    """Custom Modbus client that logs raw data traffic"""

    def __init__(self, *args, **kwargs):
        self.raw_data_callback = kwargs.pop('raw_data_callback', None)
        super().__init__(*args, **kwargs)

    def _send(self, request):
        """Override to capture TX data"""
        raw_data = request
        if self.raw_data_callback and raw_data:
            self.raw_data_callback('TX', raw_data)
        return super()._send(request)

    def _recv(self, size):
        """Override to capture RX data"""
        raw_data = super()._recv(size)
        if self.raw_data_callback and raw_data:
            self.raw_data_callback('RX', raw_data)
        return raw_data


class RfidModbusTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"RFID Modbus Test GUI V{VERSION}")
        self.root.geometry("1200x900")

        # Modbus client
        self.client = None
        self.connected = False
        self.polling_active = False
        self.polling_thread = None

        # Raw data logging
        self.raw_logging_enabled = False
        self.raw_data_buffer = []
        self.max_raw_buffer_size = 1000  # Max lines to keep in buffer

        # RTU frame assembly for raw data
        self.rx_frame_buffer = bytearray()
        self.rx_frame_timer = None
        self.rtu_frame_timeout = 50  # ms timeout for RTU frame completion

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

    def read_and_display_last_error(self, operation_name="operation"):
        """Read lastError register (1026) and display/log the result"""
        if not self.connected:
            return

        try:
            # Read single register 1026 (returns list with one element)
            result = self.modbus_read_registers(1026, 1)
            last_error = result[0]

            # Extract Low and High bytes
            low_byte = last_error & 0xFF  # Low byte (bits 0-7)
            high_byte = (last_error >> 8) & 0xFF  # High byte (bits 8-15)

            # Update the GUI fields with hex values
            low_hex = f"0x{low_byte:02X}"
            high_hex = f"0x{high_byte:02X}"
            self.last_error_low_var.set(low_hex)
            self.last_error_high_var.set(high_hex)

            # Change color based on error status
            if last_error != 0:
                self.last_error_low_label.config(foreground="red")
                self.last_error_high_label.config(foreground="red")
                error_msg = f"LastError after {operation_name}: Low={low_hex} High={high_hex} (0x{last_error:04X})"
                self.log(error_msg)
                self.block_display.insert(tk.END, f"  ⚠️  {error_msg}\n")
                return last_error
            else:
                self.last_error_low_label.config(foreground="green")
                self.last_error_high_label.config(foreground="green")
                self.log(f"LastError after {operation_name}: Low={low_hex} High={high_hex} (Success)")
                return 0
        except Exception as err:
            self.last_error_low_var.set("ERR")
            self.last_error_high_var.set("ERR")
            self.last_error_low_label.config(foreground="red")
            self.last_error_high_label.config(foreground="red")
            self.log(f"Could not read lastError register: {err}")
            return None

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

    def bytes_to_registers(self, byte_array):
        """Convert byte array to Modbus registers (16-bit values).

        Modbus registers store data in little-endian within each register:
        - Register value = (byte[1] << 8) | byte[0]
        - This means: byte[0] goes to low byte, byte[1] goes to high byte

        Args:
            byte_array: Array of bytes to convert

        Returns:
            List of 16-bit register values
        """
        registers = []
        for i in range(0, len(byte_array), 2):
            if i + 1 < len(byte_array):
                # Two bytes available: second byte becomes high byte, first byte becomes low byte
                reg = (byte_array[i + 1] << 8) | byte_array[i]
            else:
                # Only one byte left: it becomes low byte, high byte is 0
                reg = byte_array[i]
            registers.append(reg)
        return registers

    def registers_to_bytes(self, registers, byte_count=None):
        """Convert Modbus registers to byte array.

        Modbus registers store data in little-endian within each register:
        - Low byte = register & 0xFF
        - High byte = (register >> 8) & 0xFF

        Args:
            registers: List of 16-bit register values
            byte_count: Optional number of bytes to extract (for trimming)

        Returns:
            Array of bytes
        """
        byte_array = []
        for reg in registers:
            byte_array.append(reg & 0xFF)          # Low byte first
            byte_array.append((reg >> 8) & 0xFF)   # High byte second

        # Trim to specified byte count if provided
        if byte_count is not None:
            byte_array = byte_array[:byte_count]

        return byte_array

    def registers_to_ascii_bytes(self, registers, byte_count=None):
        """Convert Modbus registers to byte array for ASCII strings.

        ASCII strings in firmware are stored with natural byte order:
        - High byte = (register >> 8) & 0xFF  (first character)
        - Low byte = register & 0xFF           (second character)

        Args:
            registers: List of 16-bit register values
            byte_count: Optional number of bytes to extract (for trimming)

        Returns:
            Array of bytes in ASCII order
        """
        byte_array = []
        for reg in registers:
            byte_array.append((reg >> 8) & 0xFF)   # High byte first for ASCII
            byte_array.append(reg & 0xFF)          # Low byte second

        # Trim to specified byte count if provided
        if byte_count is not None:
            byte_array = byte_array[:byte_count]

        return byte_array

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

    def update_key_selection_display(self):
        """Update display when key selection changes"""
        key_text = "Key B" if self.use_key_b_var.get() else "Key A"
        self.log(f"Selected {key_text} for authentication")

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

        ttk.Button(fb_btn_frame, text="Read Current FB", command=self.read_and_display_function_block).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(fb_btn_frame, text="Set Function Block", command=self.set_function_block).pack(side=tk.LEFT, padx=5)

        # Create notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(3, weight=3)  # Give more weight to notebook

        # Tab 1: Tag Information
        self.create_tag_info_tab(notebook)

        # Tab 2: Basic Data
        self.create_basic_data_tab(notebook)

        # Tab 3: MIFARE Operations
        self.create_mifare_tab(notebook)

        # Tab 4: LED Control (Funktionsbaustein 2)
        self.create_led_tab(notebook)

        # Tab 5: Tunnel Mode (Funktionsbaustein 3)
        self.create_tunnel_tab(notebook)

        # Tab 6: Manual Register Access
        self.create_manual_tab(notebook)

        # Tab 7: Log
        self.create_log_tab(notebook)

        # Raw Modbus Data Panel (collapsible)
        self.create_raw_data_panel(main_frame)

        # Configure main_frame grid weights properly
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Force geometry update
        self.root.update_idletasks()

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

    # Tunnel Mode Methods (Funktionsbaustein 3)
    def use_quick_command(self):
        """Use selected quick command in tunnel mode"""
        selection = self.quick_cmd_var.get()
        if selection:
            # Extract hex part after the colon
            hex_part = selection.split(": ", 1)[-1]
            self.tunnel_tx_display.delete(1.0, tk.END)
            self.tunnel_tx_display.insert(1.0, hex_part)

    def tunnel_send_data(self):
        """Send data through RFID tunnel mode"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # Parse hex data
            hex_data = self.tunnel_tx_display.get(1.0, tk.END).strip().replace(" ", "").replace("CRC", "").upper()

            # Validate hex characters
            if not all(c in '0123456789ABCDEF' for c in hex_data):
                raise ValueError("Invalid hex characters in TX data")

            if len(hex_data) % 2 != 0:
                raise ValueError("Hex data must have even number of characters")

            if len(hex_data) > 80:  # 40 bytes max
                raise ValueError("TX data too long (max 40 bytes = 80 hex chars)")

            # Convert to bytes
            tx_bytes = bytes.fromhex(hex_data)
            tx_length = len(tx_bytes)

            self.log(f"Tunnel: Sending {tx_length} bytes: {hex_data}")

            # Convert bytes to registers using central function
            tx_registers = self.bytes_to_registers(tx_bytes)

            # Prepare combined TX data: TX Length + TX Data
            combined_data = [tx_length] + tx_registers

            # Write TX length + data starting at 2200 (this executes immediately)
            self.modbus_write_registers(2200, combined_data)

            # Update status
            self.tunnel_tx_len_var.set(str(tx_length))

            self.log(f"Tunnel: TX data sent and executed")
            self.show_success("TX data sent to RFID and executed")

            # Auto-read response after short delay
            self.root.after(200, self.tunnel_read_response)

        except Exception as e:
            self.handle_error(e, "Tunnel send data")

    def tunnel_read_response(self):
        """Read response data from RFID tunnel mode"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # Read RX Length + Data starting at 2100
            # Always read at least 1 register for RX Length, + up to 20 for data
            max_read_count = 21  # 1 for RX Length + 20 for RX Data
            rx_all = self.modbus_read_registers(2100, max_read_count)

            # First register is RX Length
            rx_length = rx_all[0]
            self.tunnel_rx_len_var.set(str(rx_length))


            if rx_length == 0:
                self.tunnel_rx_display.insert(tk.END, "No response data available\n")
                return

            # Remaining registers are RX Data
            rx_registers = rx_all[1:]

            # Convert registers to bytes using central function
            rx_bytes = self.registers_to_bytes(rx_registers, rx_length)

            # Display response
            hex_str = ' '.join([f'{b:02X}' for b in rx_bytes])
            ascii_str = ''.join([chr(b) if 32 <= b < 127 else '.' for b in rx_bytes])

            timestamp = time.strftime("%H:%M:%S")
            response_text = f"[{timestamp}] RX ({rx_length} bytes): {hex_str}\n"
            response_text += f"               ASCII: {ascii_str}\n\n"

            self.tunnel_rx_display.insert(tk.END, response_text)
            self.tunnel_rx_display.see(tk.END)

            self.log(f"Tunnel: Received {rx_length} bytes: {hex_str}")

        except Exception as e:
            self.handle_error(e, "Tunnel read response")

    def clear_tunnel_rx(self):
        """Clear tunnel RX display"""
        self.tunnel_rx_display.delete(1.0, tk.END)
        self.tunnel_rx_len_var.set("0")

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

        # Auto-polling controls (moved from main window)
        poll_frame = ttk.LabelFrame(tab, text="Automatic Polling", padding="10")
        poll_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)

        self.poll_var = tk.BooleanVar(value=False)
        self.poll_check = ttk.Checkbutton(poll_frame, text="Auto-poll tag information",
                                          variable=self.poll_var, command=self.toggle_polling)
        self.poll_check.grid(row=0, column=0, padx=5)

        ttk.Label(poll_frame, text="Poll interval (ms):").grid(row=0, column=1, padx=5)
        self.poll_interval_var = tk.IntVar(value=500)
        poll_spin = ttk.Spinbox(poll_frame, from_=100, to=5000, increment=100,
                                textvariable=self.poll_interval_var, width=10)
        poll_spin.grid(row=0, column=2, padx=5)

    def create_basic_data_tab(self, notebook):
        """Create tab for Basic Data (read-only system information)"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Basic Data")

        # Main scrollable frame
        main_canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Basic device information
        device_frame = ttk.LabelFrame(scrollable_frame, text="Device Information", padding="10")
        device_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create grid of basic data fields
        row = 0

        # Firmware Revision (Register 10020)
        ttk.Label(device_frame, text="Firmware Revision (10020):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.fw_revision_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.fw_revision_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Hardware Revision (Register 10021)
        ttk.Label(device_frame, text="Hardware Revision (10021):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.hw_revision_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.hw_revision_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Module Serial Number (Register 10022-10027)
        ttk.Label(device_frame, text="Module Serial Number (10022-10027):").grid(row=row, column=0, sticky=tk.W, padx=5,
                                                                                 pady=2)
        self.module_serial_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.module_serial_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Product Name (Register 10028-10035)
        ttk.Label(device_frame, text="Product Name (10028-10035):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_name_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.product_name_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Product Order Type (Register 10036-10043)
        ttk.Label(device_frame, text="Product Order Type (10036-10043):").grid(row=row, column=0, sticky=tk.W, padx=5,
                                                                               pady=2)
        self.product_order_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.product_order_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # IO Link Device ID (Register 10044-10045)
        ttk.Label(device_frame, text="IO Link Device ID (10044-10045):").grid(row=row, column=0, sticky=tk.W, padx=5,
                                                                              pady=2)
        self.iolink_id_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.iolink_id_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # System Firmware Version (Register 10046-10053)
        ttk.Label(device_frame, text="System Firmware Version (10046-10053):").grid(row=row, column=0, sticky=tk.W,
                                                                                    padx=5, pady=2)
        self.sys_fw_version_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.sys_fw_version_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # System Serial Number (Register 10054-10059)
        ttk.Label(device_frame, text="System Serial Number (10054-10059):").grid(row=row, column=0, sticky=tk.W, padx=5,
                                                                                 pady=2)
        self.sys_serial_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.sys_serial_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Personal Number (Register 10060-10061)
        ttk.Label(device_frame, text="Personal Number (10060-10061):").grid(row=row, column=0, sticky=tk.W, padx=5,
                                                                            pady=2)
        self.personal_num_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.personal_num_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # System Hardware Version (Register 10062-10069)
        ttk.Label(device_frame, text="System Hardware Version (10062-10069):").grid(row=row, column=0, sticky=tk.W,
                                                                                    padx=5, pady=2)
        self.sys_hw_version_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.sys_hw_version_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Product ID (Register 10070-10077)
        ttk.Label(device_frame, text="Product ID (10070-10077):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_id_var = tk.StringVar(value="--")
        ttk.Label(device_frame, textvariable=self.product_id_var, font=("Courier", 10), width=25).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1

        # Buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill="x", padx=5, pady=10)

        ttk.Button(btn_frame, text="Read All Basic Data", command=self.read_basic_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_basic_data).pack(side=tk.LEFT, padx=5)

        # Enable mousewheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        main_canvas.bind("<MouseWheel>", on_mousewheel)

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
        block_frame.columnconfigure(3, weight=1)

        ttk.Label(block_frame, text="Block Number (1016):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.block_num_var = tk.IntVar(value=4)
        block_spin = ttk.Spinbox(block_frame, from_=0, to=255, textvariable=self.block_num_var, width=10,
                                 command=self.update_block_info)
        block_spin.grid(row=0, column=1, padx=5, pady=2)

        # Add key selection checkbox (for high byte bit 0 of register 1016)
        self.use_key_b_var = tk.BooleanVar(value=False)
        key_select_check = ttk.Checkbutton(block_frame, text="Use Key B",
                                           variable=self.use_key_b_var,
                                           command=self.update_key_selection_display)
        key_select_check.grid(row=0, column=2, padx=5, pady=2)

        # Add block type info label with fixed width
        self.block_info_var = tk.StringVar()
        self.block_info_label = ttk.Label(block_frame, textvariable=self.block_info_var,
                                          font=("Arial", 9), foreground="blue", width=35)
        self.block_info_label.grid(row=0, column=3, sticky=tk.W, padx=10, pady=2)

        # Bind variable change to update block info
        self.block_num_var.trace_add('write', self.update_block_info)

        ttk.Label(block_frame, text="Block Data (1018-1025):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.block_data_var = tk.StringVar(value="00000000000000000000000000000000")
        block_data_entry = ttk.Entry(block_frame, textvariable=self.block_data_var, width=40, font=("Courier", 10))
        block_data_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=2)

        # Add event handler to auto-pad with FF when focus is lost
        block_data_entry.bind('<FocusOut>', self.auto_pad_block_data)

        # Info label about auto-padding and block validation
        ttk.Label(block_frame, text="(Auto-pads with FF if less than 32 hex characters)",
                  font=("Arial", 8), foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(block_frame, text="⚠️ Write only allowed for Data Blocks (Read allows all blocks)",
                  font=("Arial", 8), foreground="red").grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=5)

        # Buttons
        btn_frame = ttk.Frame(block_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Read Block", command=self.read_mifare_block).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Write Block", command=self.write_mifare_block).grid(
            row=0, column=1, padx=5
        )

        # LastError display
        error_frame = ttk.Frame(block_frame)
        error_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))

        ttk.Label(error_frame, text="LastError (1026):").grid(row=0, column=0, sticky=tk.W, padx=5)

        # Low Byte display
        ttk.Label(error_frame, text="Low:").grid(row=0, column=1, sticky=tk.W, padx=(10, 2))
        self.last_error_low_var = tk.StringVar(value="0x00")
        self.last_error_low_label = ttk.Label(error_frame, textvariable=self.last_error_low_var,
                                              font=("Courier", 10, "bold"), foreground="green", width=5)
        self.last_error_low_label.grid(row=0, column=2, padx=2)

        # High Byte display
        ttk.Label(error_frame, text="High:").grid(row=0, column=3, sticky=tk.W, padx=(10, 2))
        self.last_error_high_var = tk.StringVar(value="0x00")
        self.last_error_high_label = ttk.Label(error_frame, textvariable=self.last_error_high_var,
                                               font=("Courier", 10, "bold"), foreground="green", width=5)
        self.last_error_high_label.grid(row=0, column=4, padx=2)

        ttk.Label(error_frame, text="(Updated after each Block Read/Write)",
                  font=("Arial", 8), foreground="gray").grid(row=0, column=5, padx=(10, 5))

        # Data display
        data_frame = ttk.LabelFrame(tab, text="Block Data Display", padding="10")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        tab.rowconfigure(2, weight=1)

        self.block_display = scrolledtext.ScrolledText(data_frame, width=60, height=10, font=("Courier", 9))
        self.block_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.rowconfigure(0, weight=1)
        data_frame.columnconfigure(0, weight=1)

    def create_led_tab(self, notebook):
        """Create LED Control tab (Funktionsbaustein 2)"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="LED Control (FB2)")

        # Main LED Control frame
        main_led_frame = ttk.LabelFrame(tab, text="External LED Ring Control (LR22K5DUO_BG_619)", padding="15")
        main_led_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        tab.columnconfigure(0, weight=1)

        # LED Control Settings
        settings_frame = ttk.LabelFrame(main_led_frame, text="LED Settings", padding="15")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Make sure the settings frame expands properly
        settings_frame.columnconfigure(1, weight=1)

        # LED Selection
        ttk.Label(settings_frame, text="LED Color:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(5, 15), pady=10)
        self.led_selection_var = tk.StringVar(value="Off")
        led_combo = ttk.Combobox(settings_frame, textvariable=self.led_selection_var, width=20, state="readonly", font=("Arial", 10))
        led_combo['values'] = ("Off", "Grün", "Blau", "Türkis")
        led_combo.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        # LED Duration - Mit mehr Abstand und größerer Combobox
        ttk.Label(settings_frame, text="Duration:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(5, 15), pady=10)
        self.led_duration_var = tk.StringVar(value="Dauerlicht")
        duration_combo = ttk.Combobox(settings_frame, textvariable=self.led_duration_var, width=20, state="readonly", font=("Arial", 10))
        
        # Erweiterte Duration-Auswahl in 50ms Schritten
        duration_values = []
        for i in range(1, 21):  # 1-20 entspricht 50ms-1000ms
            duration_values.append(f"{i*50}ms")
        duration_values.extend(["1.5s", "2s", "2.5s", "3s", "5s", "10s", "Dauerlicht"])
        duration_combo['values'] = tuple(duration_values)
        duration_combo.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Debug: Print values to console and log  
        print(f"DEBUG: Duration combo created with {len(duration_values)} values")
        print(f"DEBUG: First 5 values: {duration_values[:5]}")
        print(f"DEBUG: Last 5 values: {duration_values[-5:]}")
        
        # Control buttons
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="Set LED", command=self.control_external_led, 
                   style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="LED Off", command=self.led_off_quick).pack(side=tk.LEFT, padx=5)

    def create_tunnel_tab(self, notebook):
        """Create Tunnel Mode tab (Funktionsbaustein 3)"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Tunnel Mode (FB3)")

        # TX Data frame
        tx_frame = ttk.LabelFrame(tab, text="TX Data (Send to RFID)", padding="10")
        tx_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        ttk.Label(tx_frame, text="Hex Data (max 80 chars = 40 bytes):").pack(anchor=tk.W)
        self.tunnel_tx_display = scrolledtext.ScrolledText(tx_frame, width=80, height=6, font=("Courier", 9))
        self.tunnel_tx_display.pack(fill=tk.BOTH, expand=True, pady=2)
        self.tunnel_tx_display.insert(tk.END, "50 00 05 22 01 00 CRC")

        # TX buttons
        tx_btn_frame = ttk.Frame(tx_frame)
        tx_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(tx_btn_frame, text="Send to RFID", command=self.tunnel_send_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tx_btn_frame, text="Clear TX", command=lambda: self.tunnel_tx_display.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

        # Common RFID commands dropdown
        ttk.Label(tx_btn_frame, text="Quick Commands:").pack(side=tk.LEFT, padx=(20, 5))
        self.quick_cmd_var = tk.StringVar()
        quick_cmds = ttk.Combobox(tx_btn_frame, textvariable=self.quick_cmd_var, width=25, state="readonly")
        quick_cmds['values'] = (
            "Get UID: 50 00 02 22 10 26 46",
            "Get Version: 50 00 00 04 54",
            "LED Blue: 50 00 03 03 FF 07 04 AC",
            "LED Grün: 50 00 03 03 FF 07 01 A9",
            "LED Off: 50 00 03 03 FF 07 00 A8"
        )
        quick_cmds.pack(side=tk.LEFT, padx=5)
        ttk.Button(tx_btn_frame, text="Use", command=self.use_quick_command).pack(side=tk.LEFT, padx=(5, 0))

        # RX Data frame
        rx_frame = ttk.LabelFrame(tab, text="RX Data (Response from RFID)", padding="10")
        rx_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tab.rowconfigure(1, weight=1)  # Same weight as TX frame

        # RX display
        self.tunnel_rx_display = scrolledtext.ScrolledText(rx_frame, width=80, height=6, font=("Courier", 9))
        self.tunnel_rx_display.pack(fill=tk.BOTH, expand=True, pady=2)

        # RX buttons
        rx_btn_frame = ttk.Frame(rx_frame)
        rx_btn_frame.pack(fill=tk.X, pady=(5, 0), side=tk.BOTTOM)
        ttk.Button(rx_btn_frame, text="Read Response", command=self.tunnel_read_response).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rx_btn_frame, text="Clear RX", command=self.clear_tunnel_rx).pack(side=tk.LEFT, padx=5)

        # Status frame (kompakter)
        status_frame = ttk.LabelFrame(tab, text="Status", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.pack(fill=tk.X)

        ttk.Label(status_info_frame, text="TX Length:").pack(side=tk.LEFT)
        self.tunnel_tx_len_var = tk.StringVar(value="0")
        ttk.Label(status_info_frame, textvariable=self.tunnel_tx_len_var, width=6).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(status_info_frame, text="RX Length:").pack(side=tk.LEFT)
        self.tunnel_rx_len_var = tk.StringVar(value="0")
        ttk.Label(status_info_frame, textvariable=self.tunnel_rx_len_var, width=6).pack(side=tk.LEFT, padx=(5, 20))


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

    def create_raw_data_panel(self, parent):
        """Create collapsible panel for displaying raw Modbus RTU data"""
        # Container for the entire raw data section
        self.raw_data_container = ttk.Frame(parent)
        self.raw_data_container.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # Don't give weight initially since panel is collapsed

        # Control bar (always visible)
        control_bar = ttk.Frame(self.raw_data_container)
        control_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.raw_data_container.columnconfigure(0, weight=1)

        # Enable/disable raw logging checkbox (also controls collapse)
        self.raw_logging_var = tk.BooleanVar(value=False)
        self.raw_logging_check = ttk.Checkbutton(control_bar, text="▶ Enable Raw Modbus Data Logging",
                                                 variable=self.raw_logging_var,
                                                 command=self.toggle_raw_panel)
        self.raw_logging_check.grid(row=0, column=0, padx=5)

        # Statistics (always visible)
        self.raw_stats_var = tk.StringVar(value="TX: 0 bytes, RX: 0 bytes")
        ttk.Label(control_bar, textvariable=self.raw_stats_var).grid(row=0, column=1, padx=20, sticky=tk.E)
        control_bar.columnconfigure(1, weight=1)

        # Collapsible frame for raw data display
        self.raw_panel_frame = ttk.Frame(self.raw_data_container)
        # Initially hidden
        self.raw_panel_expanded = False

        # Create the content but don't grid it yet
        self.create_raw_panel_content()

    def create_raw_panel_content(self):
        """Create the content of the raw data panel"""
        # Control frame within the panel
        control_frame = ttk.Frame(self.raw_panel_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Button(control_frame, text="Clear Raw Data",
                   command=self.clear_raw_data).grid(row=0, column=0, padx=5)

        # Display format options
        ttk.Label(control_frame, text="Display:").grid(row=0, column=1, padx=(20, 5))
        self.raw_format_var = tk.StringVar(value="hex")
        format_combo = ttk.Combobox(control_frame, textvariable=self.raw_format_var,
                                    width=15, state="readonly")
        format_combo['values'] = ('Hex Only', 'Hex + ASCII', 'Hex + Decode')
        format_combo.set('Hex + Decode')
        format_combo.grid(row=0, column=2, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self.refresh_raw_display)

        # Raw data display
        display_frame = ttk.LabelFrame(self.raw_panel_frame, text="Raw Modbus RTU Traffic", padding="5")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.raw_panel_frame.rowconfigure(1, weight=1)
        self.raw_panel_frame.columnconfigure(0, weight=1)

        # Create text widget with monospace font (smaller height for panel)
        self.raw_display = scrolledtext.ScrolledText(display_frame, width=100, height=12,
                                                     font=("Courier", 9), wrap=tk.NONE)
        self.raw_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.rowconfigure(0, weight=1)
        display_frame.columnconfigure(0, weight=1)

        # Configure tags for coloring
        self.raw_display.tag_configure("tx", foreground="blue")
        self.raw_display.tag_configure("rx", foreground="green")
        self.raw_display.tag_configure("error", foreground="red")
        self.raw_display.tag_configure("crc", foreground="purple")
        self.raw_display.tag_configure("timestamp", foreground="gray")
        self.raw_display.tag_configure("info", foreground="black")

        # Horizontal scrollbar for long lines
        h_scrollbar = ttk.Scrollbar(display_frame, orient="horizontal",
                                    command=self.raw_display.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.raw_display.config(xscrollcommand=h_scrollbar.set)

    def toggle_raw_panel(self):
        """Toggle the raw data panel expansion and logging"""
        self.raw_logging_enabled = self.raw_logging_var.get()

        if self.raw_logging_enabled:
            # Expand panel
            if not self.raw_panel_expanded:
                # First update the container to allow expansion
                self.raw_data_container.grid(row=4, column=0, columnspan=2,
                                             sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
                # Get parent and configure row weight
                parent = self.raw_data_container.master
                parent.rowconfigure(4, weight=1)

                # Now show the panel frame
                self.raw_panel_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
                self.raw_data_container.rowconfigure(1, weight=1)
                self.raw_panel_expanded = True
                self.raw_logging_check.config(text="▼ Disable Raw Modbus Data Logging")

                # Force update of the window
                self.root.update_idletasks()

            self.log("Raw Modbus data logging enabled")
            self.raw_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ", "timestamp")
            self.raw_display.insert(tk.END, "Raw data logging started\n", "info")
        else:
            # Collapse panel
            if self.raw_panel_expanded:
                self.raw_panel_frame.grid_forget()
                self.raw_data_container.rowconfigure(1, weight=0)

                # Reset container to non-expanding
                self.raw_data_container.grid(row=4, column=0, columnspan=2,
                                             sticky=(tk.W, tk.E), pady=5)
                # Remove row weight
                parent = self.raw_data_container.master
                parent.rowconfigure(4, weight=0)

                self.raw_panel_expanded = False
                self.raw_logging_check.config(text="▶ Enable Raw Modbus Data Logging")

                # Force update of the window
                self.root.update_idletasks()

            # Clean up frame assembly
            if self.rx_frame_timer:
                self.root.after_cancel(self.rx_frame_timer)
                self.rx_frame_timer = None
            self.rx_frame_buffer.clear()

            self.log("Raw Modbus data logging disabled")
            if hasattr(self, 'raw_display'):
                self.raw_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ", "timestamp")
                self.raw_display.insert(tk.END, "Raw data logging stopped\n", "info")

        if hasattr(self, 'raw_display'):
            self.raw_display.see(tk.END)

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

                self.client = LoggingModbusClient(
                    port=port,
                    baudrate=baudrate,
                    parity='E',
                    method='rtu',
                    timeout=0.5,
                    raw_data_callback=self.handle_raw_data
                )

                if self.client.connect():
                    self.connected = True
                    self.connect_btn.config(text="Disconnect")
                    self.status_label.config(text="Connected", foreground="green")
                    self.log(f"Connected to {port} at {baudrate} baud")

                    # Reset LastError display on connect
                    self.last_error_low_var.set("0x00")
                    self.last_error_high_var.set("0x00")
                    self.last_error_low_label.config(foreground="green")
                    self.last_error_high_label.config(foreground="green")

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

    def clear_raw_data(self):
        """Clear raw data display"""
        self.raw_display.delete(1.0, tk.END)
        self.raw_data_buffer.clear()
        self._tx_total = 0
        self._rx_total = 0
        self.update_raw_stats()

    def refresh_raw_display(self, event=None):
        """Refresh raw data display with current format"""
        # Re-display all buffered data with new format
        self.raw_display.delete(1.0, tk.END)
        for entry in self.raw_data_buffer:
            self.display_raw_entry(entry)

    def update_raw_stats(self, tx_bytes=None, rx_bytes=None):
        """Update raw data statistics"""
        if not hasattr(self, '_tx_total'):
            self._tx_total = 0
            self._rx_total = 0

        if tx_bytes is not None:
            self._tx_total += tx_bytes
        if rx_bytes is not None:
            self._rx_total += rx_bytes

        self.raw_stats_var.set(f"TX: {self._tx_total} bytes, RX: {self._rx_total} bytes")

    def handle_raw_data(self, direction, data):
        """Callback for raw Modbus data from custom client"""
        if not self.raw_logging_enabled:
            return

        # Convert data to bytes
        if isinstance(data, (bytes, bytearray)):
            data_bytes = data
        else:
            data_bytes = b''

        if not data_bytes:
            return

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        if direction == 'TX':
            # TX frames are usually complete, display immediately
            self.display_frame(timestamp, direction, data_bytes)
            self.update_raw_stats(tx_bytes=len(data_bytes))
        else:
            # RX frames might come in fragments, need to assemble
            self.handle_rx_frame(timestamp, data_bytes)

    def handle_rx_frame(self, timestamp, data_bytes):
        """Handle RX frame assembly"""
        # Cancel previous timer
        if self.rx_frame_timer:
            self.root.after_cancel(self.rx_frame_timer)
            self.rx_frame_timer = None

        # Add new data to buffer
        self.rx_frame_buffer.extend(data_bytes)

        # Check if frame looks complete
        if self.is_frame_complete(self.rx_frame_buffer):
            # Display complete frame
            self.display_frame(timestamp, 'RX', bytes(self.rx_frame_buffer))
            self.update_raw_stats(rx_bytes=len(self.rx_frame_buffer))
            self.rx_frame_buffer.clear()
        else:
            # Set timer to flush incomplete frame after timeout
            self.rx_frame_timer = self.root.after(self.rtu_frame_timeout,
                                                  lambda: self.flush_rx_frame(timestamp))

    def is_frame_complete(self, frame_data):
        """Check if Modbus RTU frame appears complete"""
        if len(frame_data) < 4:  # Minimum: slave_id, function, data, 2 CRC bytes
            return False

        try:
            slave_id = frame_data[0]
            function = frame_data[1]

            # For read response (function 0x03), check expected length
            if function == 0x03 and len(frame_data) >= 3:
                byte_count = frame_data[2]
                expected_length = 3 + byte_count + 2  # slave + func + count + data + CRC
                return len(frame_data) >= expected_length

            # For other responses, assume complete if we have reasonable length and valid CRC
            if len(frame_data) >= 5:  # At least slave + func + 1 data + 2 CRC
                return self.has_valid_crc(frame_data)

        except:
            pass

        return False

    def has_valid_crc(self, frame_data):
        """Check if frame has valid CRC"""
        if len(frame_data) < 4:
            return False

        try:
            # Calculate CRC for all but last 2 bytes
            calculated_crc = self.calculate_modbus_crc(frame_data[:-2])
            # Get received CRC (little endian)
            received_crc = (frame_data[-1] << 8) | frame_data[-2]
            return calculated_crc == received_crc
        except:
            return False

    def flush_rx_frame(self, timestamp):
        """Flush incomplete RX frame after timeout"""
        if self.rx_frame_buffer:
            self.display_frame(timestamp, 'RX', bytes(self.rx_frame_buffer))
            self.update_raw_stats(rx_bytes=len(self.rx_frame_buffer))
            self.rx_frame_buffer.clear()
        self.rx_frame_timer = None

    def display_frame(self, timestamp, direction, frame_data):
        """Display a complete frame"""
        hex_data = ' '.join([f'{b:02X}' for b in frame_data])

        # Store in buffer
        entry = {
            'timestamp': timestamp,
            'direction': direction,
            'hex_data': hex_data,
            'raw_bytes': frame_data
        }

        self.raw_data_buffer.append(entry)
        if len(self.raw_data_buffer) > self.max_raw_buffer_size:
            self.raw_data_buffer.pop(0)

        # Display the entry
        self.display_raw_entry(entry)

    def display_raw_entry(self, entry):
        """Display a single raw data entry in the chosen format"""
        format_mode = self.raw_format_var.get()

        # Timestamp
        self.raw_display.insert(tk.END, f"[{entry['timestamp']}] ", "timestamp")

        # Direction
        tag = "tx" if entry['direction'] == 'TX' else "rx"
        self.raw_display.insert(tk.END, f"{entry['direction']}: ", tag)

        # Hex data
        self.raw_display.insert(tk.END, entry['hex_data'], tag)

        # Additional formatting based on mode
        if format_mode == 'Hex + ASCII':
            # Add ASCII representation
            ascii_str = ""
            for hex_byte in entry['hex_data'].split():
                try:
                    byte_val = int(hex_byte, 16)
                    ascii_str += chr(byte_val) if 32 <= byte_val < 127 else '.'
                except:
                    ascii_str += '.'
            self.raw_display.insert(tk.END, f"  |{ascii_str}|", "info")

        elif format_mode == 'Hex + Decode':
            # Try to decode Modbus frame
            decoded = self.decode_modbus_frame(entry['raw_bytes'], entry['direction'])
            if decoded:
                self.raw_display.insert(tk.END, f"  | {decoded}", "info")

        self.raw_display.insert(tk.END, "\n")
        self.raw_display.see(tk.END)

    def decode_modbus_frame(self, data, direction):
        """Decode Modbus RTU frame"""
        if not data or len(data) < 4:
            return ""

        try:
            slave_id = data[0]
            function = data[1]

            # Common function codes
            func_names = {
                0x03: "Read Holding Registers",
                0x06: "Write Single Register",
                0x10: "Write Multiple Registers",
                0x04: "Read Input Registers"
            }

            func_name = func_names.get(function, f"Function 0x{function:02X}")

            if len(data) >= 4:
                # Calculate and verify CRC
                crc_received = (data[-1] << 8) | data[-2]
                crc_calculated = self.calculate_modbus_crc(data[:-2])
                crc_ok = crc_received == crc_calculated
                crc_status = "OK" if crc_ok else "ERROR"

                result = f"Slave:{slave_id} {func_name}"

                # Decode based on function code and direction
                if function == 0x03 and direction == 'TX' and len(data) >= 8:
                    # Read request
                    addr = (data[2] << 8) | data[3]
                    count = (data[4] << 8) | data[5]
                    result += f" Addr:{addr} Count:{count}"
                elif function == 0x03 and direction == 'RX' and len(data) >= 5:
                    # Read response
                    byte_count = data[2]
                    result += f" Bytes:{byte_count}"
                elif function == 0x10 and direction == 'TX' and len(data) >= 9:
                    # Write multiple request
                    addr = (data[2] << 8) | data[3]
                    count = (data[4] << 8) | data[5]
                    byte_count = data[6]
                    result += f" Addr:{addr} Count:{count} Bytes:{byte_count}"

                result += f" CRC:{crc_status}"
                return result

            return f"Slave:{slave_id} {func_name}"

        except Exception as e:
            return f"Decode error: {e}"

    def calculate_modbus_crc(self, data):
        """Calculate Modbus RTU CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

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
            # Extract UID registers (2011-2015)
            uid_registers = regs[1:6]  # 5 registers containing up to 10 bytes
            # Convert registers to bytes using central function
            uid_bytes = self.registers_to_bytes(uid_registers)

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

            # Convert registers to bytes using ASCII function for version string (34 bytes total)
            version_bytes = self.registers_to_ascii_bytes(regs)

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

            # Convert Key A registers to bytes using central function
            key_a_bytes = self.registers_to_bytes(key_a_regs, 6)
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

            # Convert Key B registers to bytes using central function
            key_b_bytes = self.registers_to_bytes(key_b_regs, 6)
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

            # Convert bytes to registers using central function
            key_a_regs = self.bytes_to_registers(key_a_bytes)

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

            # Convert bytes to registers using central function
            key_b_regs = self.bytes_to_registers(key_b_bytes)

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

    def read_basic_data(self):
        """Read all basic data from device"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # Read all basic data registers from base module (address 10000+)
            basic_data = {}

            # Read registers 10020-10021 (Firmware/Hardware Revision)
            regs = self.modbus_read_registers(10020, 2)
            basic_data[20] = regs[0]  # Firmware Revision
            basic_data[21] = regs[1]  # Hardware Revision

            # Read registers 10022-10077 (all other basic data)
            regs = self.modbus_read_registers(10022, 56)  # 10022 to 10077 = 56 registers
            for i, reg_value in enumerate(regs):
                basic_data[22 + i] = reg_value

            # Convert and display the data
            self.display_basic_data(basic_data)

            self.log("Basic data read successfully")
            self.show_success("Basic data updated")

        except Exception as e:
            self.handle_error(e, "Read basic data")

    def display_basic_data(self, data):
        """Display basic data in the GUI fields"""

        # Firmware Revision (Register 20) - 2 bytes ASCII
        if 20 in data:
            fw_rev = self.register_to_ascii([data[20]])
            self.fw_revision_var.set(fw_rev)

        # Hardware Revision (Register 21) - 2 bytes ASCII
        if 21 in data:
            hw_rev = self.register_to_ascii([data[21]])
            self.hw_revision_var.set(hw_rev)

        # Module Serial Number (Registers 22-27) - 12 bytes ASCII
        if all(reg in data for reg in range(22, 28)):
            module_serial = self.register_to_ascii([data[reg] for reg in range(22, 28)])
            self.module_serial_var.set(module_serial)

        # Product Name (Registers 28-35) - 16 bytes ASCII
        if all(reg in data for reg in range(28, 36)):
            product_name = self.register_to_ascii([data[reg] for reg in range(28, 36)])
            self.product_name_var.set(product_name)

        # Product Order Type (Registers 36-43) - 16 bytes ASCII
        if all(reg in data for reg in range(36, 44)):
            product_order = self.register_to_ascii([data[reg] for reg in range(36, 44)])
            self.product_order_var.set(product_order)

        # IO Link Device ID (Registers 44-45) - 3 bytes (special handling)
        if all(reg in data for reg in range(44, 46)):
            # Extract 3 bytes from 2 registers using central function
            id_regs = [data[44], data[45]]
            id_bytes = self.registers_to_bytes(id_regs)
            # Only use first 3 bytes for the IO Link ID
            iolink_id = f"0x{id_bytes[0]:02X}{id_bytes[1]:02X}{id_bytes[2]:02X}"
            self.iolink_id_var.set(iolink_id)

        # System Firmware Version (Registers 46-53) - 16 bytes ASCII
        if all(reg in data for reg in range(46, 54)):
            sys_fw_ver = self.register_to_ascii([data[reg] for reg in range(46, 54)])
            self.sys_fw_version_var.set(sys_fw_ver)

        # System Serial Number (Registers 54-59) - 12 bytes ASCII
        if all(reg in data for reg in range(54, 60)):
            sys_serial = self.register_to_ascii([data[reg] for reg in range(54, 60)])
            self.sys_serial_var.set(sys_serial)

        # Personal Number (Registers 60-61) - 4 bytes ASCII
        if all(reg in data for reg in range(60, 62)):
            personal_num = self.register_to_ascii([data[reg] for reg in range(60, 62)])
            self.personal_num_var.set(personal_num)

        # System Hardware Version (Registers 62-69) - 16 bytes ASCII
        if all(reg in data for reg in range(62, 70)):
            sys_hw_ver = self.register_to_ascii([data[reg] for reg in range(62, 70)])
            self.sys_hw_version_var.set(sys_hw_ver)

        # Product ID (Registers 70-77) - 16 bytes ASCII
        if all(reg in data for reg in range(70, 78)):
            product_id = self.register_to_ascii([data[reg] for reg in range(70, 78)])
            self.product_id_var.set(product_id)

    def register_to_ascii(self, registers):
        """Convert list of 16-bit registers to ASCII string"""
        # Convert registers to bytes using ASCII-specific function (High-Low order)
        bytes_data = self.registers_to_ascii_bytes(registers)

        ascii_chars = []
        for byte_val in bytes_data:
            # Convert to ASCII, replace non-printable chars with spaces
            if 32 <= byte_val <= 126:
                ascii_chars.append(chr(byte_val))
            else:
                ascii_chars.append(' ')

        return ''.join(ascii_chars).strip()

    def clear_basic_data(self):
        """Clear all basic data fields"""
        self.clear_error()
        self.fw_revision_var.set("--")
        self.hw_revision_var.set("--")
        self.module_serial_var.set("--")
        self.product_name_var.set("--")
        self.product_order_var.set("--")
        self.iolink_id_var.set("--")
        self.sys_fw_version_var.set("--")
        self.sys_serial_var.set("--")
        self.personal_num_var.set("--")
        self.sys_hw_version_var.set("--")
        self.product_id_var.set("--")

    def read_mifare_block(self):
        """Read MIFARE block data"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            block_num = self.block_num_var.get()

            # Combine block number with key selection
            # Low byte: block number, High byte bit 0: key selection (0=Key A, 1=Key B)
            use_key_b = self.use_key_b_var.get()
            register_value = block_num | (0x0100 if use_key_b else 0x0000)

            # Log the key being used
            key_text = "Key B" if use_key_b else "Key A"
            self.log(f"Reading block {block_num} using {key_text}")

            # First write the block number with key selection
            self.modbus_write_register(1016, register_value)

            # Wait a bit for the operation
            time.sleep(0.1)

            # Read block data (registers 1018-1025, 8 registers = 16 bytes)
            regs = self.modbus_read_registers(1018, 8)

            # Convert registers to bytes using central function
            block_bytes = self.registers_to_bytes(regs, 16)

            hex_str = ''.join([f'{b:02X}' for b in block_bytes])
            self.block_data_var.set(hex_str)

            # Display in block display
            display_str = f"Block {block_num:02d}: {hex_str}\n"
            display_str += f"  ASCII: {''.join([chr(b) if 32 <= b < 127 else '.' for b in block_bytes])}\n"
            self.block_display.insert(tk.END, display_str)
            self.block_display.see(tk.END)

            self.log(f"Read block {block_num}: {hex_str}")

        except Exception as e:
            self.handle_error(e, "Read MIFARE block")

        finally:
            # ALWAYS read lastError after any block operation attempt - regardless of success/failure
            self.read_and_display_last_error("block read")
            self.block_display.insert(tk.END, "\n")
            self.block_display.see(tk.END)

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

            # Log the key being used
            use_key_b = self.use_key_b_var.get()
            key_text = "Key B" if use_key_b else "Key A"
            self.log(f"Writing to {self.get_block_info(block_num)} using {key_text}")

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

            # Convert bytes to registers using central function
            block_regs = self.bytes_to_registers(block_bytes)

            # Write block number with key selection
            # Low byte: block number, High byte bit 0: key selection (0=Key A, 1=Key B)
            register_value = block_num | (0x0100 if use_key_b else 0x0000)
            self.modbus_write_register(1016, register_value)

            # Write block data (registers 1018-1025)
            self.modbus_write_registers(1018, block_regs)

            self.log(f"Wrote block {block_num}: {block_hex}")
            self.show_success(f"Block {block_num} written successfully")

        except Exception as e:
            self.handle_error(e, "Write MIFARE block")

        finally:
            # ALWAYS read lastError after any block operation attempt - regardless of success/failure
            last_error = self.read_and_display_last_error("block write")
            # Override success message if there was an error
            if last_error and last_error != 0:
                self.show_error(f"Block {block_num} written but with error: 0x{last_error:04X}")

    def control_external_led(self):
        """Control external LED via registers 1027-1028 (nur FB2)"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # Get LED selection and duration values
            led_selection = self.led_selection_var.get()
            led_duration = self.led_duration_var.get()

            # Map LED selection to register values (from documentation)
            led_selection_map = {
                "Off": 0x00,      # Alle LEDs AUS
                "Grün": 0x01,     # Grün
                "Blau": 0x04,     # Blau  
                "Türkis": 0x05    # Mischfarbe Blau/Grün
            }

            # Map duration to register values (50ms steps)
            if led_duration == "Dauerlicht":
                duration_value = 0xFF
            elif led_duration.endswith("ms"):
                # Extract number from strings like "50ms", "100ms", etc.
                duration_ms = int(led_duration.replace("ms", ""))
                duration_value = duration_ms // 50  # Convert to 50ms steps
            elif led_duration.endswith("s"):
                # Handle seconds values like "1.5s", "2s", etc.
                duration_s = float(led_duration.replace("s", ""))
                duration_ms = int(duration_s * 1000)
                duration_value = min(duration_ms // 50, 254)  # Cap at 254 (0xFE)
            else:
                duration_value = 0xFF  # Default to Dauerlicht for unknown values

            # Build register values according to documentation:
            # Register 1027 Low: LED Duration
            # Register 1027 High: LED Enable (0x07)
            # Register 1028 Low: LED Selection
            # Register 1028 High: Unused (0x00)
            reg1027_value = duration_value | (0x07 << 8)  # Duration in low byte, Enable=0x07 in high byte
            reg1028_value = led_selection_map[led_selection]  # Selection in low byte, high byte=0x00

            self.log(f"Setting LED: {led_selection}, Duration: {led_duration}")
            self.log(f"Duration value: {duration_value} (0x{duration_value:02X}) = {duration_value * 50}ms")
            self.log(f"Register values: 1027=0x{reg1027_value:04X}, 1028=0x{reg1028_value:04X}")

            # Use Multi-Register Write (FC16) as required by documentation
            # MUST write both registers together as WriteSequence
            self.modbus_write_registers(1027, [reg1027_value, reg1028_value])

            self.show_success(f"LED set to {led_selection} with {led_duration}")

        except Exception as e:
            self.handle_error(e, "Control External LED")

    def led_off_quick(self):
        """Quick function to turn off LED - sends LED Off telegram but keeps dropdown selection"""
        self.clear_error()
        if not self.check_connection():
            return

        try:
            # For LED Off, always use Dauerlicht (0xFF) regardless of duration dropdown
            duration_value = 0xFF

            # Always send LED Off (0x00) with Dauerlicht duration
            reg1027_value = duration_value | (0x07 << 8)  # Dauerlicht (0xFF) + Enable (0x07)
            reg1028_value = 0x00  # LED Off selection

            self.log(f"LED Off command (keeping GUI selection: {self.led_selection_var.get()})")
            self.log(f"Duration: Dauerlicht (0xFF), Selection: Off (0x00)")
            self.log(f"Register values: 1027=0x{reg1027_value:04X}, 1028=0x{reg1028_value:04X}")
            self.log(f"Expected RFID telegram: 50 00 03 03 FF 07 00 A8")

            # Send LED Off command
            self.modbus_write_registers(1027, [reg1027_value, reg1028_value])

            self.show_success("LED turned off")

        except Exception as e:
            self.handle_error(e, "LED Off Quick")

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
