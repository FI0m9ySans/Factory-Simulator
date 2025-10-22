import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import random

# Add resolution configuration
class ResolutionConfig:
    """Resolution configuration class"""
    def __init__(self):
        self.resolutions = {
            "1920x1080": {"width": 1920, "height": 1080, "scale": 1.0},
            "1600x900": {"width": 1600, "height": 900, "scale": 0.9},
            "1360x768": {"width": 1360, "height": 768, "scale": 0.8},
            "1280x720": {"width": 1280, "height": 720, "scale": 0.75},
            "1024x768": {"width": 1024, "height": 768, "scale": 0.7}
        }
        self.current_resolution = "1920x1080"
        
    def get_current_size(self):
        """Get current resolution size"""
        return self.resolutions[self.current_resolution]
    
    def set_resolution(self, resolution_name):
        """Set resolution"""
        if resolution_name in self.resolutions:
            self.current_resolution = resolution_name
            return True
        return False
    
    def get_scale_factor(self):
        """Get scale factor"""
        return self.resolutions[self.current_resolution]["scale"]
    
    def get_available_resolutions(self):
        """Get available resolution list"""
        return list(self.resolutions.keys())

class Product:
    """Product class"""
    def __init__(self, name: str, production_time: int, sale_price: float):
        self.name = name
        self.production_time = production_time  # Production time required (minutes)
        self.sale_price = sale_price  # Sale price
        self.materials_required = {}  # Required materials {material_name: quantity}
        self.products_required = {}  # Required products {product_name: quantity}
        self.is_craftable = False  # Whether it can be crafted
        
    def add_material_requirement(self, material_name: str, quantity: int):
        """Add material requirement"""
        self.materials_required[material_name] = quantity
        
    def add_product_requirement(self, product_name: str, quantity: int):
        """Add product requirement"""
        self.products_required[product_name] = quantity
        self.is_craftable = True
        
    def remove_material_requirement(self, material_name: str):
        """Remove material requirement"""
        if material_name in self.materials_required:
            del self.materials_required[material_name]
            
    def remove_product_requirement(self, product_name: str):
        """Remove product requirement"""
        if product_name in self.products_required:
            del self.products_required[product_name]
            
    def get_total_material_cost(self, materials_dict):
        """Calculate total material cost"""
        total_cost = 0
        for material_name, quantity in self.materials_required.items():
            if material_name in materials_dict:
                material = materials_dict[material_name]
                total_cost += material.cost * quantity
        return total_cost
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "production_time": self.production_time,
            "sale_price": self.sale_price,
            "materials_required": self.materials_required,
            "products_required": self.products_required,
            "is_craftable": self.is_craftable
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create product from dictionary"""
        product = cls(
            name=data["name"],
            production_time=data["production_time"],
            sale_price=data["sale_price"]
        )
        # Load material requirements
        product.materials_required = data.get("materials_required", {})
        # Load product requirements
        product.products_required = data.get("products_required", {})
        product.is_craftable = data.get("is_craftable", False)
        return product
        
    def __str__(self):
        materials_str = ", ".join([f"{name}×{qty}" for name, qty in self.materials_required.items()])
        products_str = ", ".join([f"{name}×{qty}" for name, qty in self.products_required.items()])
        
        if materials_str and products_str:
            return f"{self.name} (Price:¥{self.sale_price}, Production Time:{self.production_time}min, Materials:{materials_str}, Components:{products_str})"
        elif materials_str:
            return f"{self.name} (Price:¥{self.sale_price}, Production Time:{self.production_time}min, Materials:{materials_str})"
        elif products_str:
            return f"{self.name} (Price:¥{self.sale_price}, Production Time:{self.production_time}min, Components:{products_str})"
        else:
            return f"{self.name} (Price:¥{self.sale_price}, Production Time:{self.production_time}min)"

class Material:
    """Material class"""
    def __init__(self, name: str, cost: float, unit: str):
        self.name = name
        self.cost = cost  # Unit price
        self.unit = unit  # Unit
        self.is_craftable = False  # Whether it can be crafted
        self.materials_required = {}  # Required materials {material_name: quantity}
        self.products_required = {}  # Required products {product_name: quantity}
        
    def add_material_requirement(self, material_name: str, quantity: int):
        """Add material requirement"""
        self.materials_required[material_name] = quantity
        self.is_craftable = True
        
    def add_product_requirement(self, product_name: str, quantity: int):
        """Add product requirement"""
        self.products_required[product_name] = quantity
        self.is_craftable = True
        
    def remove_material_requirement(self, material_name: str):
        """Remove material requirement"""
        if material_name in self.materials_required:
            del self.materials_required[material_name]
            
    def remove_product_requirement(self, product_name: str):
        """Remove product requirement"""
        if product_name in self.products_required:
            del self.products_required[product_name]
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "cost": self.cost,
            "unit": self.unit,
            "is_craftable": self.is_craftable,
            "materials_required": self.materials_required,
            "products_required": self.products_required
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create material from dictionary"""
        material = cls(
            name=data["name"],
            cost=data["cost"],
            unit=data["unit"]
        )
        material.is_craftable = data.get("is_craftable", False)
        material.materials_required = data.get("materials_required", {})
        material.products_required = data.get("products_required", {})
        return material
        
    def __str__(self):
        if self.is_craftable:
            materials_str = ", ".join([f"{name}×{qty}" for name, qty in self.materials_required.items()])
            products_str = ", ".join([f"{name}×{qty}" for name, qty in self.products_required.items()])
            
            if materials_str and products_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, Craftable, Materials:{materials_str}, Components:{products_str})"
            elif materials_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, Craftable, Materials:{materials_str})"
            elif products_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, Craftable, Components:{products_str})"
        else:
            return f"{self.name} (¥{self.cost}/{self.unit})"

class CraftingStation:
    """Crafting station class"""
    def __init__(self, station_id: int, name: str, capacity: int):
        self.station_id = station_id
        self.name = name
        self.capacity = capacity  # Maximum capacity
        self.current_recipe = None  # Current crafting recipe (product name or material name)
        self.is_recipe_product = True  # True: Crafting product, False: Crafting material
        self.crafting_progress = 0
        self.assigned_worker = None
        self.is_active = False
        
    def assign_worker(self, worker):
        """Assign worker to crafting station"""
        self.assigned_worker = worker
        worker.is_working = True
        self.is_active = True
        
    def assign_recipe(self, recipe_name: str, is_product: bool):
        """Assign crafting recipe to station"""
        self.current_recipe = recipe_name
        self.is_recipe_product = is_product
        self.crafting_progress = 0
        
    def update_crafting(self):
        """Update crafting progress"""
        if self.is_active and self.current_recipe and self.assigned_worker:
            # Skill level affects crafting efficiency
            efficiency = 1 + (self.assigned_worker.skill_level - 1) * 0.2
            self.crafting_progress += efficiency
            
            if self.crafting_progress >= 60:  # Crafting fixed at 60 minutes
                # Crafting completed
                self.crafting_progress = 0
                completed_item = self.current_recipe
                self.current_recipe = None
                return completed_item, self.is_recipe_product
        return None, None
        
    def get_progress_percentage(self):
        """Get crafting progress percentage"""
        return min(100, int((self.crafting_progress / 60) * 100))
        
    def __str__(self):
        status = "Running" if self.is_active else "Stopped"
        recipe_name = self.current_recipe if self.current_recipe else "None"
        recipe_type = "Product" if self.is_recipe_product else "Material"
        worker_name = self.assigned_worker.name if self.assigned_worker else "None"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"{self.name} {self.station_id} (Status:{status}, Recipe:{recipe_name}({recipe_type}), Worker:{worker_name}, Progress:{progress})"

class Worker:
    """Worker class"""
    def __init__(self, name: str, skill_level: int, salary: float):
        self.name = name
        self.skill_level = skill_level  # Skill level (1-5)
        self.salary = salary  # Daily salary
        self.is_working = False
        self.current_task = None
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "skill_level": self.skill_level,
            "salary": self.salary
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create worker from dictionary"""
        return cls(
            name=data["name"],
            skill_level=data["skill_level"],
            salary=data["salary"]
        )
        
    def __str__(self):
        status = "Working" if self.is_working else "Idle"
        return f"{self.name} (Skill:{self.skill_level}, Salary:¥{self.salary}/day, Status:{status})"

class ProductionLine:
    """Production line class"""
    def __init__(self, line_id: int, capacity: int):
        self.line_id = line_id
        self.capacity = capacity  # Maximum capacity
        self.current_product = None
        self.production_progress = 0
        self.assigned_worker = None
        self.is_active = False
        
    def assign_worker(self, worker: Worker):
        """Assign worker to production line"""
        self.assigned_worker = worker
        worker.is_working = True
        self.is_active = True
        
    def assign_product(self, product: Product):
        """Assign product to production line"""
        self.current_product = product
        self.production_progress = 0
        
    def update_production(self):
        """Update production progress"""
        if self.is_active and self.current_product and self.assigned_worker:
            # Skill level affects production efficiency
            efficiency = 1 + (self.assigned_worker.skill_level - 1) * 0.2
            self.production_progress += efficiency
            
            if self.production_progress >= self.current_product.production_time:
                # Production completed
                self.production_progress = 0
                completed_product = self.current_product
                self.current_product = None
                return completed_product
        return None
        
    def get_progress_percentage(self):
        """Get production progress percentage"""
        if self.current_product:
            return min(100, int((self.production_progress / self.current_product.production_time) * 100))
        return 0
        
    def __str__(self):
        status = "Running" if self.is_active else "Stopped"
        product_name = self.current_product.name if self.current_product else "None"
        worker_name = self.assigned_worker.name if self.assigned_worker else "None"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"Production Line {self.line_id} (Status:{status}, Product:{product_name}, Worker:{worker_name}, Progress:{progress})"

class Order:
    """Order class"""
    def __init__(self, order_id: int, product: Product, quantity: int, deadline: datetime):
        self.order_id = order_id
        self.product = product
        self.quantity = quantity
        self.deadline = deadline
        self.completed_quantity = 0
        self.is_completed = False
        
    def complete_quantity(self, amount: int):
        """Complete a certain quantity of products"""
        self.completed_quantity += amount
        if self.completed_quantity >= self.quantity:
            self.is_completed = True
            
    def is_overdue(self, current_time: datetime):
        """Check if order is overdue"""
        return current_time > self.deadline and not self.is_completed
        
    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"Order #{self.order_id}: {self.product.name} x{self.quantity} (Deadline:{self.deadline.strftime('%Y-%m-%d %H:%M')}, Status:{status})"

class Mod:
    """Mod class"""
    def __init__(self, name="", description="", author="", version="1.0"):
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.products = []
        self.materials = []
        self.initial_workers = []
        self.initial_balance = 0
        self.initial_materials = {}
        self.crafting_stations = []
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "initial_balance": self.initial_balance,
            "initial_materials": self.initial_materials,
            "products": [product.to_dict() for product in self.products],
            "materials": [material.to_dict() for material in self.materials],
            "initial_workers": [worker.to_dict() for worker in self.initial_workers],
            "crafting_stations": self.crafting_stations
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create mod from dictionary"""
        mod = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0")
        )
        mod.initial_balance = data.get("initial_balance", 0)
        mod.initial_materials = data.get("initial_materials", {})
        
        # Load materials
        mod.materials = [Material.from_dict(material_data) for material_data in data.get("materials", [])]
        
        # Load products
        mod.products = [Product.from_dict(product_data) for product_data in data.get("products", [])]
        
        # Load initial workers
        mod.initial_workers = [Worker.from_dict(worker_data) for worker_data in data.get("initial_workers", [])]
        
        # Load crafting stations
        mod.crafting_stations = data.get("crafting_stations", [])
        
        return mod
        
    def save_to_file(self, filename):
        """Save mod to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            
    @classmethod
    def load_from_file(cls, filename):
        """Load mod from file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls.from_dict(data)

class Factory:
    """Factory class"""
    def __init__(self, name: str, initial_balance: float):
        self.name = name
        self.balance = initial_balance
        self.production_lines = []
        self.crafting_stations = []
        self.workers = []
        self.products = {}
        self.materials = {}
        self.material_inventory = {}
        self.product_inventory = {}
        self.orders = []
        self.current_time = datetime.now()
        self.day = 1
        self.daily_costs = 0
        self.daily_income = 0
        
    def add_production_line(self, capacity: int):
        """Add production line"""
        line_id = len(self.production_lines) + 1
        new_line = ProductionLine(line_id, capacity)
        self.production_lines.append(new_line)
        return new_line
        
    def add_crafting_station(self, name: str, capacity: int):
        """Add crafting station"""
        station_id = len(self.crafting_stations) + 1
        new_station = CraftingStation(station_id, name, capacity)
        self.crafting_stations.append(new_station)
        return new_station
        
    def hire_worker(self, name: str, skill_level: int, salary: float):
        """Hire worker"""
        new_worker = Worker(name, skill_level, salary)
        self.workers.append(new_worker)
        return new_worker
        
    def add_product(self, product: Product):
        """Add product"""
        self.products[product.name] = product
        self.product_inventory[product.name] = 0
        return product
        
    def remove_product(self, name: str):
        """Remove product"""
        if name in self.products:
            del self.products[name]
            if name in self.product_inventory:
                del self.product_inventory[name]
            return True
        return False
        
    def add_material(self, name: str, cost: float, unit: str, initial_quantity: int = 0):
        """Add material"""
        new_material = Material(name, cost, unit)
        self.materials[name] = new_material
        self.material_inventory[name] = initial_quantity
        return new_material
        
    def remove_material(self, name: str):
        """Remove material"""
        if name in self.materials:
            del self.materials[name]
            if name in self.material_inventory:
                del self.material_inventory[name]
            return True
        return False
        
    def purchase_material(self, material_name: str, quantity: int):
        """Purchase material"""
        if material_name not in self.materials:
            return False, f"Error: Material {material_name} does not exist!"
            
        material = self.materials[material_name]
        cost = material.cost * quantity
        
        if cost > self.balance:
            return False, f"Error: Insufficient funds! Need ¥{cost}, current balance ¥{self.balance}"
            
        self.balance -= cost
        self.material_inventory[material_name] += quantity
        self.daily_costs += cost
        return True, f"Purchased {quantity}{material.unit} {material_name}, cost ¥{cost}"
        
    def create_order(self, product_name: str, quantity: int, days_until_deadline: int):
        """Create order"""
        if product_name not in self.products:
            return None, f"Error: Product {product_name} does not exist!"
            
        product = self.products[product_name]
        deadline = self.current_time + timedelta(days=days_until_deadline)
        order_id = len(self.orders) + 1
        new_order = Order(order_id, product, quantity, deadline)
        self.orders.append(new_order)
        return new_order, f"Created new order: {new_order}"
        
    def assign_worker_to_line(self, worker_name: str, line_id: int):
        """Assign worker to production line"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        
        if not worker:
            return False, f"Error: Worker {worker_name} does not exist!"
            
        if not line:
            return False, f"Error: Production line {line_id} does not exist!"
            
        # If worker is already working on another line, unassign first
        for other_line in self.production_lines:
            if other_line.assigned_worker == worker:
                other_line.assigned_worker = None
                other_line.is_active = False
                
        line.assign_worker(worker)
        return True, f"Worker {worker_name} assigned to production line {line_id}"
        
    def assign_worker_to_station(self, worker_name: str, station_id: int):
        """Assign worker to crafting station"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        
        if not worker:
            return False, f"Error: Worker {worker_name} does not exist!"
            
        if not station:
            return False, f"Error: Crafting station {station_id} does not exist!"
            
        # If worker is already working on another station, unassign first
        for other_station in self.crafting_stations:
            if other_station.assigned_worker == worker:
                other_station.assigned_worker = None
                other_station.is_active = False
                
        station.assign_worker(worker)
        return True, f"Worker {worker_name} assigned to crafting station {station_id}"
        
    def assign_product_to_line(self, product_name: str, line_id: int):
        """Assign product to production line"""
        if product_name not in self.products:
            return False, f"Error: Product {product_name} does not exist!"
            
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        if not line:
            return False, f"Error: Production line {line_id} does not exist!"
            
        if not line.assigned_worker:
            return False, f"Error: Production line {line_id} has no assigned worker!"
            
        product = self.products[product_name]
        
        # Check if all required materials are sufficient
        for material_name, quantity in product.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"Error: {material_name} insufficient! Need {quantity}, current stock {self.material_inventory.get(material_name, 0)}"
            
        # Check if all required products are sufficient
        for product_name_req, quantity in product.products_required.items():
            if self.product_inventory.get(product_name_req, 0) < quantity:
                return False, f"Error: {product_name_req} insufficient! Need {quantity}, current stock {self.product_inventory.get(product_name_req, 0)}"
            
        # Consume all required materials
        for material_name, quantity in product.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # Consume all required products
        for product_name_req, quantity in product.products_required.items():
            self.product_inventory[product_name_req] -= quantity
            
        line.assign_product(product)
        return True, f"Production line {line_id} started producing {product_name}"
        
    def assign_recipe_to_station(self, recipe_name: str, is_product: bool, station_id: int):
        """Assign crafting recipe to station"""
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        if not station:
            return False, f"Error: Crafting station {station_id} does not exist!"
            
        if not station.assigned_worker:
            return False, f"Error: Crafting station {station_id} has no assigned worker!"
            
        # Check if recipe exists
        if is_product:
            if recipe_name not in self.products:
                return False, f"Error: Product {recipe_name} does not exist!"
            recipe = self.products[recipe_name]
        else:
            if recipe_name not in self.materials:
                return False, f"Error: Material {recipe_name} does not exist!"
            recipe = self.materials[recipe_name]
            
        # Check if craftable
        if not recipe.is_craftable:
            return False, f"Error: {recipe_name} is not craftable!"
            
        # Check if all required materials are sufficient
        for material_name, quantity in recipe.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"Error: {material_name} insufficient! Need {quantity}, current stock {self.material_inventory.get(material_name, 0)}"
            
        # Check if all required products are sufficient
        for product_name, quantity in recipe.products_required.items():
            if self.product_inventory.get(product_name, 0) < quantity:
                return False, f"Error: {product_name} insufficient! Need {quantity}, current stock {self.product_inventory.get(product_name, 0)}"
            
        # Consume all required materials
        for material_name, quantity in recipe.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # Consume all required products
        for product_name, quantity in recipe.products_required.items():
            self.product_inventory[product_name] -= quantity
            
        station.assign_recipe(recipe_name, is_product)
        return True, f"Crafting station {station_id} started crafting {recipe_name}"
        
    def update_production(self):
        """Update all production lines progress"""
        completed_products = []
        for line in self.production_lines:
            if line.is_active and line.current_product:
                completed_product = line.update_production()
                if completed_product:
                    # Production completed, add to inventory
                    self.product_inventory[completed_product.name] += 1
                    completed_products.append(completed_product.name)
                    
                    # Check if any orders need completion
                    for order in self.orders:
                        if not order.is_completed and order.product.name == completed_product.name:
                            order.complete_quantity(1)
                            if order.is_completed:
                                # Order completed, get income
                                income = order.product.sale_price * order.quantity
                                self.balance += income
                                self.daily_income += income
        return completed_products
        
    def update_crafting(self):
        """Update all crafting stations progress"""
        completed_items = []
        for station in self.crafting_stations:
            if station.is_active and station.current_recipe:
                completed_item, is_product = station.update_crafting()
                if completed_item:
                    # Crafting completed, add to inventory
                    if is_product:
                        self.product_inventory[completed_item] += 1
                    else:
                        self.material_inventory[completed_item] += 1
                    completed_items.append((completed_item, is_product))
        return completed_items
                            
    def sell_from_inventory(self, product_name: str, quantity: int):
        """Sell from inventory"""
        if product_name not in self.product_inventory:
            return False, f"Error: Product {product_name} does not exist!"
            
        if self.product_inventory[product_name] < quantity:
            return False, f"Error: Insufficient stock! {product_name} only has {self.product_inventory[product_name]} units"
            
        product = self.products[product_name]
        income = product.sale_price * quantity
        self.product_inventory[product_name] -= quantity
        self.balance += income
        self.daily_income += income
        return True, f"Sold {quantity} units of {product_name}, earned ¥{income}"
        
    def pay_workers(self):
        """Pay worker salaries"""
        total_salary = sum(worker.salary for worker in self.workers)
        if total_salary > self.balance:
            return False, f"Warning: Insufficient funds to pay worker salaries! Need ¥{total_salary}, current balance ¥{self.balance}"
            
        self.balance -= total_salary
        self.daily_costs += total_salary
        return True, f"Paid worker salaries ¥{total_salary}"
        
    def advance_time(self, hours: int = 1):
        """Advance time"""
        self.current_time += timedelta(hours=hours)
        
        # Update production and crafting hourly
        completed_products = []
        completed_crafting = []
        for _ in range(hours):
            completed = self.update_production()
            completed_products.extend(completed)
            
            completed = self.update_crafting()
            completed_crafting.extend(completed)
            
        # Check overdue orders
        overdue_orders = []
        for order in self.orders:
            if order.is_overdue(self.current_time):
                overdue_orders.append(order.order_id)
                
        return completed_products, completed_crafting, overdue_orders
                
    def next_day(self):
        """Move to next day"""
        self.day += 1
        self.current_time = self.current_time.replace(hour=8, minute=0) + timedelta(days=1)
        
        # Pay worker salaries
        success, message = self.pay_workers()
        
        # Reset daily statistics
        daily_profit = self.daily_income - self.daily_costs
        
        self.daily_income = 0
        self.daily_costs = 0
        
        return success, message, daily_profit
        
    def get_status_text(self):
        """Get factory status text"""
        status_text = f"=== {self.name} Status (Day {self.day}) ===\n"
        status_text += f"Balance: ¥{self.balance}\n"
        status_text += f"Time: {self.current_time.strftime('%Y-%m-%d %H:%M')}\n"
        
        status_text += "\n--- Production Lines ---\n"
        for line in self.production_lines:
            status_text += f"  {line}\n"
            
        status_text += "\n--- Crafting Stations ---\n"
        for station in self.crafting_stations:
            status_text += f"  {station}\n"
            
        status_text += "\n--- Workers ---\n"
        for worker in self.workers:
            status_text += f"  {worker}\n"
            
        status_text += "\n--- Material Inventory ---\n"
        for material, quantity in self.material_inventory.items():
            unit = self.materials[material].unit if material in self.materials else "unit"
            status_text += f"  {material}: {quantity}{unit}\n"
            
        status_text += "\n--- Product Inventory ---\n"
        for product, quantity in self.product_inventory.items():
            status_text += f"  {product}: {quantity} units\n"
            
        status_text += "\n--- Orders ---\n"
        for order in self.orders:
            status = "Completed" if order.is_completed else "In Progress"
            overdue = " (Overdue!)" if order.is_overdue(self.current_time) else ""
            status_text += f"  {order}{overdue}\n"
            
        return status_text

    def load_mod(self, mod):
        """Load mod"""
        # Clear existing data
        self.products.clear()
        self.materials.clear()
        self.product_inventory.clear()
        self.material_inventory.clear()
        self.workers.clear()
        self.crafting_stations.clear()
        
        # Set initial balance
        self.balance = mod.initial_balance
        
        # Add materials
        for material in mod.materials:
            initial_quantity = mod.initial_materials.get(material.name, 0)
            self.add_material(
                material.name,
                material.cost,
                material.unit,
                initial_quantity
            )
            # Set material crafting requirements
            self.materials[material.name].is_craftable = material.is_craftable
            self.materials[material.name].materials_required = material.materials_required.copy()
            self.materials[material.name].products_required = material.products_required.copy()
            
        # Add products
        for product in mod.products:
            self.add_product(product)
            
        # Add workers
        for worker_data in mod.initial_workers:
            self.hire_worker(
                worker_data.name,
                worker_data.skill_level,
                worker_data.salary
            )
            
        # Add crafting stations
        for station_data in mod.crafting_stations:
            self.add_crafting_station(station_data["name"], station_data["capacity"])

class FactoryAI:
    """AI Player class for automatic factory management"""
    
    def __init__(self, app):
        self.app = app
        self.factory = app.factory
        self.running = False
        self.strategy = "balanced"  # balanced, aggressive, conservative
        self.last_decision_day = 0
        self.decision_interval = 1  # Decision interval (hours)
        self.last_decision_time = self.factory.current_time
        
    def start(self):
        """Start AI player"""
        self.running = True
        self.last_decision_time = self.factory.current_time
        self.app.log_event("AI Player started")
        # Immediately make one decision
        self.make_continuous_decisions()
        
    def stop(self):
        """Stop AI player"""
        self.running = False
        self.app.log_event("AI Player stopped")
        
    def make_continuous_decisions(self):
        """Make continuous decisions"""
        if not self.running:
            return
            
        current_time = self.factory.current_time
        time_diff = (current_time - self.last_decision_time).total_seconds() / 3600  # Convert to hours
        
        # Make decisions at regular intervals
        if time_diff >= self.decision_interval:
            self.last_decision_time = current_time
            self.app.log_event(f"AI Player made decisions at {current_time.strftime('%H:%M')}")
            
            try:
                # Make decisions based on strategy
                if self.strategy == "balanced":
                    self.balanced_strategy()
                elif self.strategy == "aggressive":
                    self.aggressive_strategy()
                elif self.strategy == "conservative":
                    self.conservative_strategy()
                    
                self.app.update_display()
            except Exception as e:
                self.app.log_event(f"AI decision error: {str(e)}")
        
        # Schedule next decision check
        if self.running:
            # Check every 5 seconds if decisions need to be made
            self.app.root.after(5000, self.make_continuous_decisions)
        
    def make_daily_decisions(self):
        """Make daily decisions (compatible with existing interface)"""
        if not self.running or self.factory.day <= self.last_decision_day:
            return
            
        self.last_decision_day = self.factory.day
        self.app.log_event(f"AI Player made decisions on Day {self.factory.day}")
        
        try:
            # Make decisions based on strategy
            if self.strategy == "balanced":
                self.balanced_strategy()
            elif self.strategy == "aggressive":
                self.aggressive_strategy()
            elif self.strategy == "conservative":
                self.conservative_strategy()
                
            self.app.update_display()
            self.app.log_event("AI decisions executed")
        except Exception as e:
            self.app.log_event(f"AI decision error: {str(e)}")
        
    def balanced_strategy(self):
        """Balanced development strategy"""
        self.app.log_event("Executing balanced development strategy")
        
        # 1. Assign workers to idle production lines
        self.assign_workers_to_lines()
        
        # 2. Assign products to staffed production lines
        self.assign_products_to_lines()
        
        # 3. Assign workers to idle crafting stations
        self.assign_workers_to_stations()
        
        # 4. Assign recipes to crafting stations
        self.assign_recipes_to_stations()
        
        # 5. Purchase necessary materials
        self.purchase_needed_materials()
        
        # 6. Create some orders
        if len(self.factory.orders) < 2:
            self.create_random_orders()
            
    def aggressive_strategy(self):
        """Aggressive expansion strategy"""
        self.app.log_event("Executing aggressive expansion strategy")
        
        # 1. Hire as many workers as possible
        if len(self.factory.workers) < 5 and self.factory.balance > 500:
            self.hire_worker(f"AI Worker{len(self.factory.workers)+1}", 3, 120)
            
        # 2. Add more production lines
        if len(self.factory.production_lines) < 4 and self.factory.balance > 1000:
            self.factory.add_production_line(10)
            self.app.log_event("AI added new production line")
            self.app.update_progress_bars()
            
        # 3. Add more crafting stations
        if len(self.factory.crafting_stations) < 3 and self.factory.balance > 800:
            self.factory.add_crafting_station("AI Crafting Station", 5)
            self.app.log_event("AI added new crafting station")
            self.app.update_progress_bars()
            
        # 4. Basic decisions from balanced strategy
        self.balanced_strategy()
        
    def conservative_strategy(self):
        """Conservative operation strategy"""
        self.app.log_event("Executing conservative operation strategy")
        
        # Only ensure basic operations
        self.assign_workers_to_lines()
        self.assign_products_to_lines()
        
        # Only purchase most necessary materials
        critical_materials = ["Wood", "Metal", "Screws"]
        for material in critical_materials:
            if material in self.factory.materials:
                current_stock = self.factory.material_inventory.get(material, 0)
                if current_stock < 50 and self.factory.balance > 100:
                    # Purchase enough materials
                    needed = 100 - current_stock
                    affordable = min(needed, int(self.factory.balance / self.factory.materials[material].cost / 2))
                    if affordable > 0:
                        success, message = self.factory.purchase_material(material, affordable)
                        if success:
                            self.app.log_event(message)
                
    def assign_workers_to_lines(self):
        """Assign workers to production lines"""
        available_workers = [w for w in self.factory.workers if not w.is_working]
        unstaffed_lines = [l for l in self.factory.production_lines if not l.assigned_worker]
        
        for worker, line in zip(available_workers, unstaffed_lines):
            success, message = self.factory.assign_worker_to_line(worker.name, line.line_id)
            if success:
                self.app.log_event(f"AI assigned {worker.name} to production line {line.line_id}")
                
    def assign_workers_to_stations(self):
        """Assign workers to crafting stations"""
        available_workers = [w for w in self.factory.workers if not w.is_working]
        unstaffed_stations = [s for s in self.factory.crafting_stations if not s.assigned_worker]
        
        for worker, station in zip(available_workers, unstaffed_stations):
            success, message = self.factory.assign_worker_to_station(worker.name, station.station_id)
            if success:
                self.app.log_event(f"AI assigned {worker.name} to crafting station {station.station_id}")
                
    def assign_products_to_lines(self):
        """Assign products to production lines"""
        staffed_lines = [l for l in self.factory.production_lines if l.assigned_worker and not l.current_product]
        
        for line in staffed_lines:
            # Try to assign different products
            for product_name, product in self.factory.products.items():
                can_produce = True
                
                # Check if materials are sufficient
                for material, quantity in product.materials_required.items():
                    if material not in self.factory.material_inventory or self.factory.material_inventory[material] < quantity:
                        can_produce = False
                        break
                        
                # Check if required products are sufficient
                for prod_req, quantity in product.products_required.items():
                    if prod_req not in self.factory.product_inventory or self.factory.product_inventory[prod_req] < quantity:
                        can_produce = False
                        break
                        
                if can_produce:
                    success, message = self.factory.assign_product_to_line(product_name, line.line_id)
                    if success:
                        self.app.log_event(f"AI started producing {product_name} on production line {line.line_id}")
                        break
                        
    def assign_recipes_to_stations(self):
        """Assign recipes to crafting stations"""
        staffed_stations = [s for s in self.factory.crafting_stations if s.assigned_worker and not s.current_recipe]
        
        for station in staffed_stations:
            # Try to assign craftable products
            for product_name, product in self.factory.products.items():
                if product.is_craftable:
                    can_craft = True
                    
                    # Check if materials are sufficient
                    for material, quantity in product.materials_required.items():
                        if material not in self.factory.material_inventory or self.factory.material_inventory[material] < quantity:
                            can_craft = False
                            break
                            
                    # Check if required products are sufficient
                    for prod_req, quantity in product.products_required.items():
                        if prod_req not in self.factory.product_inventory or self.factory.product_inventory[prod_req] < quantity:
                            can_craft = False
                            break
                            
                    if can_craft:
                        success, message = self.factory.assign_recipe_to_station(product_name, True, station.station_id)
                        if success:
                            self.app.log_event(f"AI started crafting {product_name} on crafting station {station.station_id}")
                            break
                    
    def purchase_needed_materials(self):
        """Purchase needed materials"""
        for material_name, material in self.factory.materials.items():
            current_stock = self.factory.material_inventory.get(material_name, 0)
            
            # If stock below threshold and sufficient funds, purchase
            if current_stock < 100 and self.factory.balance > material.cost * 50:
                quantity = min(200, int(self.factory.balance / material.cost / 2))
                success, message = self.factory.purchase_material(material_name, quantity)
                if success:
                    self.app.log_event(f"AI purchased {quantity} units of {material_name}")
                    
    def create_random_orders(self):
        """Create random orders"""
        import random
        available_products = list(self.factory.products.keys())
        if available_products:
            product = random.choice(available_products)
            quantity = random.randint(3, 10)
            days = random.randint(2, 5)
            
            order, message = self.factory.create_order(product, quantity, days)
            if order:
                self.app.log_event(f"AI created order: {product} x{quantity}, deliver within {days} days")
                
    def hire_worker(self, name, skill_level, salary):
        """Hire worker"""
        if self.factory.balance >= salary:
            worker = self.factory.hire_worker(name, skill_level, salary)
            self.app.log_event(f"AI hired worker {name}")
            return worker
        return None
        
    def analyze_factory(self):
        """Analyze factory status"""
        analysis = "=== AI Analysis Report ===\n\n"
        
        # Financial analysis
        analysis += f"Financial Status: ¥{self.factory.balance}\n"
        if self.factory.balance < 200:
            analysis += "Warning: Insufficient funds!\n"
        elif self.factory.balance > 1000:
            analysis += "Good: Sufficient funds\n"
        else:
            analysis += "Normal: Good financial status\n"
            
        analysis += "\n"
        
        # Production line analysis
        active_lines = sum(1 for line in self.factory.production_lines if line.is_active)
        total_lines = len(self.factory.production_lines)
        analysis += f"Production Lines: {active_lines}/{total_lines} running\n"
        
        if active_lines < total_lines:
            analysis += "Suggestion: Assign more workers to production lines\n"
            
        analysis += "\n"
        
        # Inventory analysis
        low_stock_materials = []
        for material, quantity in self.factory.material_inventory.items():
            if quantity < 50:
                low_stock_materials.append(material)
                
        if low_stock_materials:
            analysis += f"Low stock materials: {', '.join(low_stock_materials)}\n"
            analysis += "Suggestion: Restock inventory\n"
        else:
            analysis += "Material inventory: Sufficient\n"
            
        analysis += "\n"
        
        # Order analysis
        active_orders = sum(1 for order in self.factory.orders if not order.is_completed)
        analysis += f"Active orders: {active_orders}\n"
        
        if active_orders < 2:
            analysis += "Suggestion: Create more orders\n"
            
        return analysis

class SettingsDialog:
    """Settings Dialog"""
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x410")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        self.create_widgets()
        
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create settings interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Resolution settings
        resolution_frame = ttk.LabelFrame(main_frame, text="Resolution Settings", padding="10")
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="Select Resolution:").pack(anchor=tk.W, pady=5)
        
        self.resolution_var = tk.StringVar(value=self.app.resolution_config.current_resolution)
        resolution_combo = ttk.Combobox(
            resolution_frame, 
            textvariable=self.resolution_var,
            values=self.app.resolution_config.get_available_resolutions(),
            state="readonly"
        )
        resolution_combo.pack(fill=tk.X, pady=5)
        
        # Window mode
        window_frame = ttk.LabelFrame(main_frame, text="Window Mode", padding="10")
        window_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.window_mode_var = tk.StringVar(value=self.app.window_mode)
        ttk.Radiobutton(
            window_frame, 
            text="Windowed", 
            variable=self.window_mode_var, 
            value="windowed"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            window_frame, 
            text="Fullscreen", 
            variable=self.window_mode_var, 
            value="fullscreen"
        ).pack(anchor=tk.W, pady=2)
        
        # Scale settings
        scale_frame = ttk.LabelFrame(main_frame, text="Interface Scale", padding="10")
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.scale_var = tk.DoubleVar(value=self.app.scale_factor)
        scale_slider = ttk.Scale(
            scale_frame,
            from_=0.5,
            to=2.0,
            variable=self.scale_var,
            orient=tk.HORIZONTAL
        )
        scale_slider.pack(fill=tk.X, pady=5)
        
        scale_value_label = ttk.Label(scale_frame, text=f"Scale Factor: {self.scale_var.get():.1f}")
        scale_value_label.pack(anchor=tk.W)
        
        def update_scale_label(*args):
            scale_value_label.config(text=f"Scale Factor: {self.scale_var.get():.1f}")
        
        self.scale_var.trace('w', update_scale_label)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Apply Settings", 
            command=self.apply_settings
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Restore Defaults", 
            command=self.reset_to_default
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.window.destroy
        ).pack(side=tk.RIGHT)
        
    def apply_settings(self):
        """Apply settings"""
        # Update resolution
        new_resolution = self.resolution_var.get()
        if new_resolution != self.app.resolution_config.current_resolution:
            self.app.resolution_config.set_resolution(new_resolution)
            self.app.apply_resolution()
        
        # Update window mode
        new_window_mode = self.window_mode_var.get()
        if new_window_mode != self.app.window_mode:
            self.app.set_window_mode(new_window_mode)
        
        # Update scale factor
        new_scale = self.scale_var.get()
        if new_scale != self.app.scale_factor:
            self.app.set_scale_factor(new_scale)
        
        messagebox.showinfo("Success", "Settings applied. Some settings require restart to take full effect.")
        self.window.destroy()
        
    def reset_to_default(self):
        """Restore default settings"""
        self.resolution_var.set("1920x1080")
        self.window_mode_var.set("windowed")
        self.scale_var.set(1.0)

class FactorySimulatorGUI:
    """Factory Simulator GUI"""
    def __init__(self, root):
        self.root = root
        self.root.title("Factory Simulator - Crafting System Edition")
        
        # Initialize resolution configuration
        self.resolution_config = ResolutionConfig()
        self.window_mode = "windowed"  # windowed or fullscreen
        self.scale_factor = 1.0
        
        # Set window initial size and position
        self.setup_window()
        
        # Create factory instance
        self.factory = Factory("Efficient Factory", initial_balance=420)
        self.setup_factory()
        
        # Current mod
        self.current_mod = None
        
        # Whether simulation is running
        self.simulation_running = False

        # Create AI player
        self.ai_player = FactoryAI(self)
        
        # Create GUI
        self.create_widgets()
        
        # Start periodic update
        self.update_display()

    def check_ai_decision(self):
        """Check and execute AI decisions"""
        if hasattr(self, 'ai_player') and self.ai_player.running:
            self.ai_player.make_daily_decisions()

    def toggle_ai_player(self):
        """Toggle AI player running status"""
        if self.ai_player.running:
            self.ai_player.stop()
            self.ai_start_button.config(text="Start AI Player")
            self.ai_status_label.config(text="AI Status: Stopped", foreground="red")
        else:
            self.ai_player.strategy = self.ai_strategy_var.get()
            self.ai_player.start()
            self.ai_start_button.config(text="Stop AI Player")
            self.ai_status_label.config(text="AI Status: Running", foreground="green")

    def on_ai_strategy_change(self):
        """Callback when AI strategy changes"""
        if self.ai_player.running:
            self.ai_player.strategy = self.ai_strategy_var.get()
            self.log_event(f"AI strategy switched to: {self.ai_strategy_var.get()}")

    def ai_single_step(self):
        """AI single step execution"""
        if not self.ai_player.running:
            self.ai_player.strategy = self.ai_strategy_var.get()
            self.ai_player.make_daily_decisions()
            self.update_display()
            self.log_event("AI executed single step decision")

    def show_ai_analysis(self):
        """Show AI analysis"""
        analysis = self.ai_player.analyze_factory()
        messagebox.showinfo("AI Analysis Report", analysis)        

    def setup_window(self):
        """Set window properties"""
        # Get current resolution settings
        resolution = self.resolution_config.get_current_size()
        
        # Set window size
        if self.window_mode == "fullscreen":
            self.root.attributes('-fullscreen', True)
        else:
            # Window mode, set to resolution size
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            # Center on screen
            self.center_window()
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Bind exit fullscreen shortcuts
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        if self.window_mode == "fullscreen":
            self.set_window_mode("windowed")
        else:
            self.set_window_mode("fullscreen")
            
    def set_window_mode(self, mode):
        """Set window mode"""
        self.window_mode = mode
        if mode == "fullscreen":
            self.root.attributes('-fullscreen', True)
        else:
            self.root.attributes('-fullscreen', False)
            # Restore window size
            resolution = self.resolution_config.get_current_size()
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            self.center_window()
    
    def apply_resolution(self):
        """Apply new resolution settings"""
        resolution = self.resolution_config.get_current_size()
        if self.window_mode == "windowed":
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            self.center_window()
    
    def set_scale_factor(self, scale_factor):
        """Set interface scale factor"""
        self.scale_factor = scale_factor
        # Can add code to update interface styles here
        # Since tkinter scaling support is limited, this mainly affects font sizes and component dimensions

    def setup_factory(self):
        """Initialize factory data"""
        # Add materials
        self.factory.add_material("Wood", cost=1, unit="unit", initial_quantity=100)
        self.factory.add_material("Metal", cost=2, unit="unit", initial_quantity=50)
        self.factory.add_material("Plastic", cost=0.5, unit="unit", initial_quantity=200)
        self.factory.add_material("Screws", cost=0.1, unit="pcs", initial_quantity=500)
        
        # Add products
        chair = Product("Wooden Chair", production_time=60, sale_price=20)
        chair.add_material_requirement("Wood", 5)
        self.factory.add_product(chair)
        
        table = Product("Wooden Table", production_time=120, sale_price=40)
        table.add_material_requirement("Wood", 10)
        self.factory.add_product(table)
        
        cabinet = Product("Wooden Cabinet", production_time=180, sale_price=60)
        cabinet.add_material_requirement("Wood", 15)
        cabinet.add_material_requirement("Metal", 2)
        self.factory.add_product(cabinet)
        
        # Add craftable products and materials
        # Crafted material: Metal Plate (crafted from 2 Metal)
        metal_plate = Material("Metal Plate", cost=3, unit="sheet")
        metal_plate.add_material_requirement("Metal", 2)
        self.factory.add_material(metal_plate.name, metal_plate.cost, metal_plate.unit, 0)
        self.factory.materials["Metal Plate"].is_craftable = True
        self.factory.materials["Metal Plate"].materials_required = metal_plate.materials_required.copy()
        
        # Crafted product: Premium Chair (crafted from Wooden Chair and Metal Plate)
        premium_chair = Product("Premium Chair", production_time=90, sale_price=50)
        premium_chair.add_product_requirement("Wooden Chair", 1)
        premium_chair.add_material_requirement("Metal Plate", 1)
        premium_chair.add_material_requirement("Screws", 4)
        self.factory.add_product(premium_chair)
        
        # Add production lines
        self.factory.add_production_line(capacity=10)
        self.factory.add_production_line(capacity=10)
        
        # Add crafting stations
        self.factory.add_crafting_station("Basic Crafting Station", capacity=5)
        self.factory.add_crafting_station("Advanced Crafting Station", capacity=3)
        
        # Hire workers
        self.factory.hire_worker("Worker A", 3, 100)
        self.factory.hire_worker("Worker B", 2, 80)
        self.factory.hire_worker("Worker C", 4, 120)
        self.factory.hire_worker("Worker D", 3, 100)
        
        # Assign workers to production lines and crafting stations
        
        # Create orders
        
        # Purchase more materials
        self.factory.purchase_material("Wood", 200)
        self.factory.purchase_material("Metal", 50)
        self.factory.purchase_material("Screws", 200)
        
        # Start production
        self.factory.assign_product_to_line("Wooden Chair", 1)
        self.factory.assign_product_to_line("Wooden Table", 2)
        
    def create_widgets(self):
        """Create GUI components"""
        # Create menu bar
        self.create_menu()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights - use pack layout instead of grid for better scaling
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Factory Simulator - Crafting System Edition", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create left-right split frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left control panel
        control_frame = ttk.LabelFrame(content_frame, text="Control Panel", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right status display
        status_frame = ttk.LabelFrame(content_frame, text="Factory Status", padding="10")
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control panel content
        self.create_control_panel(control_frame)
        
        # Status display content
        self.create_status_display(status_frame)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Event Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Game", command=self.save_game)
        file_menu.add_command(label="Load Game", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Display Settings", command=self.open_settings)
        settings_menu.add_separator()
        
        # Resolution submenu
        resolution_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Resolution", menu=resolution_menu)
        
        for resolution in self.resolution_config.get_available_resolutions():
            resolution_menu.add_command(
                label=resolution, 
                command=lambda r=resolution: self.change_resolution(r)
            )
        
        # Window mode submenu
        window_mode_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Window Mode", menu=window_mode_menu)
        window_mode_menu.add_command(
            label="Windowed", 
            command=lambda: self.set_window_mode("windowed")
        )
        window_mode_menu.add_command(
            label="Fullscreen", 
            command=lambda: self.set_window_mode("fullscreen")
        )
        
        # Mods menu
        mod_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Mods", menu=mod_menu)
        mod_menu.add_command(label="Mod Creator", command=self.open_mod_creator)
        mod_menu.add_command(label="Import Mod", command=self.import_mod)
        mod_menu.add_command(label="Export Current Mod", command=self.export_current_mod)
        mod_menu.add_separator()
        mod_menu.add_command(label="Reset to Default", command=self.reset_to_default)
        
    def change_resolution(self, resolution):
        """Change resolution"""
        if self.resolution_config.set_resolution(resolution):
            self.apply_resolution()
            
    def open_settings(self):
        """Open settings dialog"""
        SettingsDialog(self.root, self)
        
    def save_game(self):
        """Save game"""
        filename = filedialog.asksaveasfilename(
            title="Save Game",
            defaultextension=".factorysave",
            filetypes=[("Factory Save Files", "*.factorysave")]
        )
        
        if filename:
            try:
                # Save game state to file
                game_state = {
                    "factory": {
                        "name": self.factory.name,
                        "balance": self.factory.balance,
                        "day": self.factory.day,
                        "current_time": self.factory.current_time.isoformat(),
                        "material_inventory": self.factory.material_inventory,
                        "product_inventory": self.factory.product_inventory,
                        "daily_costs": self.factory.daily_costs,
                        "daily_income": self.factory.daily_income
                    },
                    "settings": {
                        "resolution": self.resolution_config.current_resolution,
                        "window_mode": self.window_mode,
                        "scale_factor": self.scale_factor
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(game_state, f, indent=4, ensure_ascii=False)
                    
                messagebox.showinfo("Success", f"Game saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save game: {str(e)}")
                
    def load_game(self):
        """Load game"""
        filename = filedialog.askopenfilename(
            title="Load Game",
            filetypes=[("Factory Save Files", "*.factorysave")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
                
                # Restore factory state
                factory_data = game_state["factory"]
                self.factory.name = factory_data["name"]
                self.factory.balance = factory_data["balance"]
                self.factory.day = factory_data["day"]
                self.factory.current_time = datetime.fromisoformat(factory_data["current_time"])
                self.factory.material_inventory = factory_data["material_inventory"]
                self.factory.product_inventory = factory_data["product_inventory"]
                self.factory.daily_costs = factory_data["daily_costs"]
                self.factory.daily_income = factory_data["daily_income"]
                
                # Restore settings
                settings_data = game_state["settings"]
                self.resolution_config.set_resolution(settings_data["resolution"])
                self.set_window_mode(settings_data["window_mode"])
                self.set_scale_factor(settings_data["scale_factor"])
                
                self.update_display()
                messagebox.showinfo("Success", f"Game loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load game: {str(e)}")
    
    def create_control_panel(self, parent):
        """Create control panel"""
        # Use ScrolledFrame to support scrolling
        from tkinter.scrolledtext import ScrolledText
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== Add AI Control Panel =====
        ai_frame = ttk.LabelFrame(self.scrollable_frame, text="AI Player Control", padding="10")
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Strategy selection
        strategy_frame = ttk.Frame(ai_frame)
        strategy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strategy_frame, text="AI Strategy:").pack(side=tk.LEFT)
        
        self.ai_strategy_var = tk.StringVar(value="balanced")
        strategies = [("Balanced Development", "balanced"), ("Aggressive Expansion", "aggressive"), ("Conservative Operation", "conservative")]
        
        for text, value in strategies:
            ttk.Radiobutton(strategy_frame, text=text, variable=self.ai_strategy_var, 
                       value=value, command=self.on_ai_strategy_change).pack(side=tk.LEFT, padx=10)
    
        # Control buttons
        button_frame = ttk.Frame(ai_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.ai_start_button = ttk.Button(button_frame, text="Start AI Player", command=self.toggle_ai_player)
        self.ai_start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Single Step", command=self.ai_single_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="AI Analysis", command=self.show_ai_analysis).pack(side=tk.LEFT, padx=5)
    
        # Status display
        status_frame = ttk.Frame(ai_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.ai_status_label = ttk.Label(status_frame, text="AI Status: Not Started", foreground="red")
        self.ai_status_label.pack(side=tk.LEFT)
        # ===== AI Control Panel End =====
    
        # Mod information
        mod_frame = ttk.LabelFrame(self.scrollable_frame, text="Current Mod", padding="5")
        mod_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mod_label = ttk.Label(mod_frame, text="")
        self.mod_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Time control
        time_frame = ttk.LabelFrame(self.scrollable_frame, text="Time Control", padding="5")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        time_btn_frame = ttk.Frame(time_frame)
        time_btn_frame.pack(fill=tk.X)
        
        ttk.Button(time_btn_frame, text="Advance 1 Hour", command=self.advance_one_hour).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="Advance 8 Hours", command=self.advance_eight_hours).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="Next Day", command=self.next_day).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Auto simulation control
        auto_frame = ttk.LabelFrame(self.scrollable_frame, text="Auto Simulation", padding="5")
        auto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sim_speed = tk.StringVar(value="1")
        speed_frame = ttk.Frame(auto_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        ttk.Radiobutton(speed_frame, text="Slow", variable=self.sim_speed, value="0.5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="Normal", variable=self.sim_speed, value="1").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="Fast", variable=self.sim_speed, value="2").pack(side=tk.LEFT, padx=5)
        
        self.auto_btn = ttk.Button(auto_frame, text="Start Auto Simulation", command=self.toggle_auto_simulation)
        self.auto_btn.pack(fill=tk.X, pady=5)
        
        # Factory management
        manage_frame = ttk.LabelFrame(self.scrollable_frame, text="Factory Management", padding="5")
        manage_frame.pack(fill=tk.X, pady=(0, 10))
        
        manage_btn_frame = ttk.Frame(manage_frame)
        manage_btn_frame.pack(fill=tk.X)
        
        ttk.Button(manage_btn_frame, text="Purchase Materials", command=self.purchase_material).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Create Order", command=self.create_order).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Sell Inventory", command=self.sell_inventory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Hire Worker", command=self.hire_worker).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Production line management
        line_frame = ttk.LabelFrame(self.scrollable_frame, text="Production Line Management", padding="5")
        line_frame.pack(fill=tk.X, pady=(0, 10))
        
        line_btn_frame = ttk.Frame(line_frame)
        line_btn_frame.pack(fill=tk.X)
        
        ttk.Button(line_btn_frame, text="Assign Worker", command=self.assign_worker_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="Assign Product", command=self.assign_product_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="Add Production Line", command=self.add_production_line).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Crafting station management
        craft_frame = ttk.LabelFrame(self.scrollable_frame, text="Crafting Station Management", padding="5")
        craft_frame.pack(fill=tk.X, pady=(0, 10))
        
        craft_btn_frame = ttk.Frame(craft_frame)
        craft_btn_frame.pack(fill=tk.X)
        
        ttk.Button(craft_btn_frame, text="Assign Worker", command=self.assign_worker_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="Assign Recipe", command=self.assign_recipe_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="Add Crafting Station", command=self.add_crafting_station).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Progress bar display
        progress_frame = ttk.LabelFrame(self.scrollable_frame, text="Production Progress", padding="5")
        progress_frame.pack(fill=tk.X)
        
        # Production line progress bars
        ttk.Label(progress_frame, text="Production Lines:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.progress_bars = {}
        for line in self.factory.production_lines:
            line_frame = ttk.Frame(progress_frame)
            line_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(line_frame, text=f"Production Line {line.line_id}:").pack(side=tk.LEFT)
            progress_bar = ttk.Progressbar(line_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
            self.progress_bars[line.line_id] = progress_bar
            
        # Crafting station progress bars
        ttk.Label(progress_frame, text="Crafting Stations:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 2))
        self.craft_progress_bars = {}
        for station in self.factory.crafting_stations:
            station_frame = ttk.Frame(progress_frame)
            station_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(station_frame, text=f"{station.name}:").pack(side=tk.LEFT)
            progress_bar = ttk.Progressbar(station_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
            self.craft_progress_bars[station.station_id] = progress_bar
        
    def create_status_display(self, parent):
        """Create status display area"""
        # Use ScrolledText to support scrolling
        from tkinter.scrolledtext import ScrolledText
        
        self.status_text = ScrolledText(parent, height=20, width=60)
        self.status_text.pack(fill=tk.BOTH, expand=True)        
    def update_display(self):
        """Update display"""
        # Update status text
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, self.factory.get_status_text())
        
        # Update production line progress bars
        for line in self.factory.production_lines:
            if line.line_id in self.progress_bars:
                progress = line.get_progress_percentage()
                self.progress_bars[line.line_id]['value'] = progress
                
        # Update crafting station progress bars
        for station in self.factory.crafting_stations:
            if station.station_id in self.craft_progress_bars:
                progress = station.get_progress_percentage()
                self.craft_progress_bars[station.station_id]['value'] = progress
        
        # If auto simulation is running, schedule next update
        if self.simulation_running:
            speed = float(self.sim_speed.get())
            delay = int(1000 / speed)  # Convert to milliseconds
            self.root.after(delay, self.auto_advance_time)
    
    def log_event(self, message):
        """Log event to log"""
        self.log_text.insert(tk.END, f"{self.factory.current_time.strftime('%H:%M')} - {message}\n")
        self.log_text.see(tk.END)
    
    def advance_one_hour(self):
        """Advance 1 hour"""
        completed_products, completed_crafting, overdue_orders = self.factory.advance_time(1)
        
        for product in completed_products:
            self.log_event(f"Completed production of {product}!")
            
        for item, is_product in completed_crafting:
            item_type = "Product" if is_product else "Material"
            self.log_event(f"Crafted {item} {item_type}!")
            
        for order_id in overdue_orders:
            self.log_event(f"Warning: Order {order_id} is overdue!")
            
        # Check AI decisions
        self.check_ai_decision()
            
        self.update_display()
    
    def advance_eight_hours(self):
        """Advance 8 hours"""
        for _ in range(8):
            completed_products, completed_crafting, overdue_orders = self.factory.advance_time(1)
            
            for product in completed_products:
                self.log_event(f"Completed production of {product}!")
                
            for item, is_product in completed_crafting:
                item_type = "Product" if is_product else "Material"
                self.log_event(f"Crafted {item} {item_type}!")
                
            for order_id in overdue_orders:
                self.log_event(f"Warning: Order {order_id} is overdue!")
                
        # Check AI decisions
        self.check_ai_decision()
                
        self.update_display()
    
    def next_day(self):
        """Move to next day"""
        success, message, daily_profit = self.factory.next_day()
        self.log_event(message)
        self.log_event(f"Yesterday's Profit: ¥{daily_profit}")
        
        # Trigger AI decisions
        self.check_ai_decision()
        
        self.update_display()
    
    def toggle_auto_simulation(self):
        """Toggle auto simulation status"""
        if self.simulation_running:
            self.simulation_running = False
            self.auto_btn.config(text="Start Auto Simulation")
        else:
            self.simulation_running = True
            self.auto_btn.config(text="Stop Auto Simulation")
            self.auto_advance_time()
    
    def auto_advance_time(self):
        """Auto advance time"""
        if self.simulation_running:
            self.advance_one_hour()
    
    def purchase_material(self):
        """Purchase material dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Purchase Materials")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Material Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        material_var = tk.StringVar(value=list(self.factory.materials.keys())[0] if self.factory.materials else "")
        material_combo = ttk.Combobox(dialog, textvariable=material_var, values=list(self.factory.materials.keys()))
        material_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar(value="100")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_purchase():
            try:
                quantity = int(quantity_var.get())
                success, message = self.factory.purchase_material(material_var.get(), quantity)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(dialog, text="Purchase", command=do_purchase).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def create_order(self):
        """Create order dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Order")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar(value="5")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Delivery Days:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        days_var = tk.StringVar(value="3")
        days_entry = ttk.Entry(dialog, textvariable=days_var)
        days_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_create_order():
            try:
                quantity = int(quantity_var.get())
                days = int(days_var.get())
                order, message = self.factory.create_order(product_var.get(), quantity, days)
                if order:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(dialog, text="Create Order", command=do_create_order).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def sell_inventory(self):
        """Sell inventory dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sell Inventory")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_sell():
            try:
                quantity = int(quantity_var.get())
                success, message = self.factory.sell_from_inventory(product_var.get(), quantity)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(dialog, text="Sell", command=do_sell).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def hire_worker(self):
        """Hire worker dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Hire Worker")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Skill Level (1-5):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        skill_var = tk.StringVar(value="3")
        skill_entry = ttk.Entry(dialog, textvariable=skill_var)
        skill_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Daily Salary:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        salary_var = tk.StringVar(value="100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_hire():
            try:
                skill = int(skill_var.get())
                salary = float(salary_var.get())
                if not name_var.get():
                    messagebox.showerror("Error", "Please enter worker name!")
                    return
                    
                worker = self.factory.hire_worker(name_var.get(), skill, salary)
                self.log_event(f"Hired worker {worker.name} (Skill:{skill}, Salary:¥{salary}/day)")
                self.update_display()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(dialog, text="Hire", command=do_hire).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_line(self):
        """Assign worker to production line dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Worker to Production Line")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Worker:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Production Line:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        line_var = tk.StringVar()
        line_combo = ttk.Combobox(dialog, textvariable=line_var, 
                                 values=[l.line_id for l in self.factory.production_lines])
        line_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_assign():
            try:
                line_id = int(line_var.get())
                success, message = self.factory.assign_worker_to_line(worker_var.get(), line_id)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid production line ID!")
        
        ttk.Button(dialog, text="Assign", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_station(self):
        """Assign worker to crafting station dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Worker to Crafting Station")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Worker:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Crafting Station:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        station_var = tk.StringVar()
        station_combo = ttk.Combobox(dialog, textvariable=station_var, 
                                   values=[s.station_id for s in self.factory.crafting_stations])
        station_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_assign():
            try:
                station_id = int(station_var.get())
                success, message = self.factory.assign_worker_to_station(worker_var.get(), station_id)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid crafting station ID!")
        
        ttk.Button(dialog, text="Assign", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_product_to_line(self):
        """Assign product to production line dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Product to Production Line")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, 
                                    values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Production Line:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        line_var = tk.StringVar()
        line_combo = ttk.Combobox(dialog, textvariable=line_var, 
                                 values=[l.line_id for l in self.factory.production_lines])
        line_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_assign():
            try:
                line_id = int(line_var.get())
                success, message = self.factory.assign_product_to_line(product_var.get(), line_id)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid production line ID!")
        
        ttk.Button(dialog, text="Assign", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_recipe_to_station(self):
        """Assign recipe to crafting station dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Recipe to Crafting Station")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Recipe Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        type_var = tk.StringVar(value="Product")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Product", "Material"])
        type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Recipe Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        recipe_var = tk.StringVar()
        
        def update_recipe_options(*args):
            if type_var.get() == "Product":
                # Only show craftable products
                craftable_products = [p for p in self.factory.products.values() if p.is_craftable]
                recipe_combo['values'] = [p.name for p in craftable_products]
            else:
                # Only show craftable materials
                craftable_materials = [m for m in self.factory.materials.values() if m.is_craftable]
                recipe_combo['values'] = [m.name for m in craftable_materials]
        
        type_var.trace('w', update_recipe_options)
        recipe_combo = ttk.Combobox(dialog, textvariable=recipe_var)
        recipe_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        update_recipe_options()  # Initialize options
        
        ttk.Label(dialog, text="Crafting Station:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        station_var = tk.StringVar()
        station_combo = ttk.Combobox(dialog, textvariable=station_var, 
                                   values=[s.station_id for s in self.factory.crafting_stations])
        station_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_assign():
            try:
                station_id = int(station_var.get())
                is_product = (type_var.get() == "Product")
                success, message = self.factory.assign_recipe_to_station(recipe_var.get(), is_product, station_id)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid crafting station ID!")
        
        ttk.Button(dialog, text="Assign", command=do_assign).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def add_production_line(self):
        """Add production line"""
        capacity = 10  # Default capacity
        line = self.factory.add_production_line(capacity)
        self.log_event(f"Added new production line {line.line_id} (Capacity:{capacity})")
        
        # Update progress bar display
        self.update_progress_bars()
        self.update_display()
    
    def add_crafting_station(self):
        """Add crafting station"""
        capacity = 5  # Default capacity
        station = self.factory.add_crafting_station("Crafting Station", capacity)
        self.log_event(f"Added new crafting station {station.station_id} (Capacity:{capacity})")
        
        # Update progress bar display
        self.update_progress_bars()
        self.update_display()
    
    def update_progress_bars(self):
        """Update progress bar display"""
        # Clear existing progress bars
        for widget in self.progress_bars.values():
            widget.destroy()
        for widget in self.craft_progress_bars.values():
            widget.destroy()
            
        self.progress_bars = {}
        self.craft_progress_bars = {}
        
        # Get progress bar frame
        progress_frame = self.auto_btn.master.master.master  # Get the frame containing progress bars
        
        # Recreate production line progress bars
        ttk.Label(progress_frame, text="Production Lines:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        for i, line in enumerate(self.factory.production_lines):
            ttk.Label(progress_frame, text=f"Production Line {line.line_id}:").grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=150, mode="determinate")
            progress_bar.grid(row=i+1, column=1, padx=5, pady=2)
            self.progress_bars[line.line_id] = progress_bar
            
        # Recreate crafting station progress bars
        craft_start_row = len(self.factory.production_lines) + 2
        ttk.Label(progress_frame, text="Crafting Stations:", font=("Arial", 9, "bold")).grid(row=craft_start_row, column=0, sticky=tk.W, padx=5, pady=2)
        for i, station in enumerate(self.factory.crafting_stations):
            ttk.Label(progress_frame, text=f"{station.name}:").grid(row=craft_start_row+i+1, column=0, sticky=tk.W, padx=5, pady=2)
            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=150, mode="determinate")
            progress_bar.grid(row=craft_start_row+i+1, column=1, padx=5, pady=2)
            self.craft_progress_bars[station.station_id] = progress_bar
    
    def open_mod_creator(self):
        """Open mod creator"""
        ModCreator(self.root, self)
    
    def import_mod(self):
        """Import mod"""
        filename = filedialog.askopenfilename(
            title="Select Mod File",
            filetypes=[("LAUN Mod Files", "*.launmod"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                mod = Mod.load_from_file(filename)
                self.current_mod = mod
                self.factory.load_mod(mod)
                self.mod_label.config(text=f"{mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"Loaded mod: {mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"Mod description: {mod.description}")
                self.update_progress_bars()
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mod: {str(e)}")
    
    def export_current_mod(self):
        """Export current mod"""
        if not self.current_mod:
            messagebox.showwarning("Warning", "No mod loaded, cannot export!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Mod File",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.current_mod.save_to_file(filename)
                messagebox.showinfo("Success", f"Mod saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save mod: {str(e)}")
    
    def reset_to_default(self):
        """Reset to default mod"""
        self.setup_factory()
        self.current_mod = None
        self.mod_label.config(text="Default Mod")
        self.log_event("Reset to default mod")
        self.update_progress_bars()
        self.update_display()

class ModCreator:
    """Mod Creator"""
    def __init__(self, parent, app):
        self.app = app
        self.mod = Mod()
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Mod Creator")
        self.window.geometry("600x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create mod creator interface"""
        # Create notebook widget
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic info tab
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Basic Info")
        self.create_info_tab(info_tab)
        
        # Materials tab
        material_tab = ttk.Frame(notebook)
        notebook.add(material_tab, text="Materials")
        self.create_material_tab(material_tab)
        
        # Products tab
        product_tab = ttk.Frame(notebook)
        notebook.add(product_tab, text="Products")
        self.create_product_tab(product_tab)
        
        # Crafting recipes tab
        recipe_tab = ttk.Frame(notebook)
        notebook.add(recipe_tab, text="Crafting Recipes")
        self.create_recipe_tab(recipe_tab)
        
        # Workers tab
        worker_tab = ttk.Frame(notebook)
        notebook.add(worker_tab, text="Workers")
        self.create_worker_tab(worker_tab)
        
        # Action buttons
        action_frame = ttk.Frame(self.window)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="Save Mod", command=self.save_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Load Mod", command=self.load_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Apply Mod", command=self.apply_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def create_info_tab(self, parent):
        """Create basic info tab"""
        info_frame = ttk.LabelFrame(parent, text="Mod Basic Info", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Mod Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.author_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Version:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(info_frame, textvariable=self.version_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Initial Balance:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.balance_var = tk.StringVar(value="0")
        ttk.Entry(info_frame, textvariable=self.balance_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Crafting station settings
        station_frame = ttk.LabelFrame(parent, text="Crafting Station Settings", padding="10")
        station_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Crafting station list
        station_list_frame = ttk.Frame(station_frame)
        station_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.station_listbox = tk.Listbox(station_list_frame, height=4)
        station_scrollbar = ttk.Scrollbar(station_list_frame, orient="vertical", command=self.station_listbox.yview)
        self.station_listbox.configure(yscrollcommand=station_scrollbar.set)
        self.station_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        station_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Crafting station buttons
        station_btn_frame = ttk.Frame(station_frame)
        station_btn_frame.pack(fill=tk.X)
        
        ttk.Button(station_btn_frame, text="Add Crafting Station", command=self.add_station_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(station_btn_frame, text="Delete Crafting Station", command=self.delete_station).pack(side=tk.LEFT, padx=5)
        
        info_frame.columnconfigure(1, weight=1)
        
    def create_material_tab(self, parent):
        """Create materials tab"""
        # Materials list
        material_list_frame = ttk.Frame(parent)
        material_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.material_listbox = tk.Listbox(material_list_frame)
        material_scrollbar = ttk.Scrollbar(material_list_frame, orient="vertical", command=self.material_listbox.yview)
        self.material_listbox.configure(yscrollcommand=material_scrollbar.set)
        self.material_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        material_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Material buttons
        material_btn_frame = ttk.Frame(parent)
        material_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(material_btn_frame, text="Add Material", command=self.add_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Edit Material", command=self.edit_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Delete Material", command=self.delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Set Crafting Recipe", command=self.set_material_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
        # Initialize list
        self.update_material_list()
    
    def create_product_tab(self, parent):
        """Create products tab"""
        # Products list
        product_list_frame = ttk.Frame(parent)
        product_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.product_listbox = tk.Listbox(product_list_frame)
        product_scrollbar = ttk.Scrollbar(product_list_frame, orient="vertical", command=self.product_listbox.yview)
        self.product_listbox.configure(yscrollcommand=product_scrollbar.set)
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Product buttons
        product_btn_frame = ttk.Frame(parent)
        product_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(product_btn_frame, text="Add Product", command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Edit Product", command=self.edit_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Set Crafting Recipe", command=self.set_product_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
        # Initialize list
        self.update_product_list()
    
    def create_recipe_tab(self, parent):
        """Create crafting recipes tab"""
        # Recipe list
        recipe_frame = ttk.LabelFrame(parent, text="Crafting Recipes", padding="10")
        recipe_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview to display recipes
        columns = ("Type", "Name", "Material Requirements", "Product Requirements")
        self.recipe_tree = ttk.Treeview(recipe_frame, columns=columns, show="headings", height=15)
        
        # Set column headings
        for col in columns:
            self.recipe_tree.heading(col, text=col)
            if col == "Name":
                self.recipe_tree.column(col, width=150)
            else:
                self.recipe_tree.column(col, width=100)
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(recipe_frame, orient="vertical", command=self.recipe_tree.yview)
        self.recipe_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.recipe_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Recipe buttons
        recipe_btn_frame = ttk.Frame(parent)
        recipe_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(recipe_btn_frame, text="Refresh Recipe List", command=self.update_recipe_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(recipe_btn_frame, text="Delete Recipe", command=self.delete_recipe).pack(side=tk.LEFT, padx=5)
        
        # Initialize list
        self.update_recipe_list()
    
    def create_worker_tab(self, parent):
        """Create workers tab"""
        # Workers list
        worker_list_frame = ttk.Frame(parent)
        worker_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.worker_listbox = tk.Listbox(worker_list_frame, height=15)
        worker_scrollbar = ttk.Scrollbar(worker_list_frame, orient="vertical", command=self.worker_listbox.yview)
        self.worker_listbox.configure(yscrollcommand=worker_scrollbar.set)
        self.worker_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        worker_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Worker buttons
        worker_btn_frame = ttk.Frame(parent)
        worker_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(worker_btn_frame, text="Add Worker", command=self.add_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="Edit Worker", command=self.edit_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="Delete Worker", command=self.delete_worker).pack(side=tk.LEFT, padx=5)
        
        # Initialize list
        self.update_worker_list()
    
    def update_material_list(self):
        """Update materials list"""
        self.material_listbox.delete(0, tk.END)
        for material in self.mod.materials:
            self.material_listbox.insert(tk.END, str(material))
    
    def update_product_list(self):
        """Update products list"""
        self.product_listbox.delete(0, tk.END)
        for product in self.mod.products:
            self.product_listbox.insert(tk.END, str(product))
    
    def update_worker_list(self):
        """Update workers list"""
        self.worker_listbox.delete(0, tk.END)
        for worker in self.mod.initial_workers:
            self.worker_listbox.insert(tk.END, str(worker))
    
    def update_recipe_list(self):
        """Update recipes list"""
        self.recipe_tree.delete(*self.recipe_tree.get_children())
        
        # Add craftable materials
        for material in self.mod.materials:
            if material.is_craftable:
                materials_str = ", ".join([f"{name}×{qty}" for name, qty in material.materials_required.items()])
                products_str = ", ".join([f"{name}×{qty}" for name, qty in material.products_required.items()])
                self.recipe_tree.insert("", "end", values=("Material", material.name, materials_str, products_str))
                
        # Add craftable products
        for product in self.mod.products:
            if product.is_craftable:
                materials_str = ", ".join([f"{name}×{qty}" for name, qty in product.materials_required.items()])
                products_str = ", ".join([f"{name}×{qty}" for name, qty in product.products_required.items()])
                self.recipe_tree.insert("", "end", values=("Product", product.name, materials_str, products_str))
    
    def add_station_dialog(self):
        """Add crafting station dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Crafting Station")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Crafting Station Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value="Crafting Station")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Capacity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        capacity_var = tk.StringVar(value="5")
        capacity_entry = ttk.Entry(dialog, textvariable=capacity_var)
        capacity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def add_station():
            try:
                name = name_var.get()
                capacity = int(capacity_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter crafting station name!")
                    return
                
                self.mod.crafting_stations.append({"name": name, "capacity": capacity})
                self.station_listbox.insert(tk.END, f"{name} (Capacity:{capacity})")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid capacity!")
        
        ttk.Button(dialog, text="Add", command=add_station).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_station(self):
        """Delete crafting station"""
        selection = self.station_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a crafting station first!")
            return
            
        index = selection[0]
        self.mod.crafting_stations.pop(index)
        self.station_listbox.delete(index)
    
    def add_material_dialog(self):
        """Add material dialog"""
        self.material_dialog("Add Material")
    
    def edit_material_dialog(self):
        """Edit material dialog"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.material_dialog("Edit Material", material, index)
    
    def material_dialog(self, title, material=None, index=None):
        """Material dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Material Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=material.name if material else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Unit Price:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        cost_var = tk.StringVar(value=material.cost if material else "1")
        cost_entry = ttk.Entry(dialog, textvariable=cost_var)
        cost_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Unit:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        unit_var = tk.StringVar(value=material.unit if material else "unit")
        unit_entry = ttk.Entry(dialog, textvariable=unit_var)
        unit_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Initial Quantity:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_var = tk.StringVar(value=self.mod.initial_materials.get(material.name, 0) if material else "100")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_material():
            try:
                name = name_var.get()
                cost = float(cost_var.get())
                unit = unit_var.get()
                quantity = int(quantity_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter material name!")
                    return
                
                new_material = Material(name, cost, unit)
                
                if material:  # Edit mode
                    # Update initial stock
                    if material.name in self.mod.initial_materials:
                        del self.mod.initial_materials[material.name]
                    self.mod.initial_materials[name] = quantity
                    
                    # Preserve crafting recipe
                    new_material.is_craftable = material.is_craftable
                    new_material.materials_required = material.materials_required.copy()
                    new_material.products_required = material.products_required.copy()
                    
                    self.mod.materials[index] = new_material
                else:  # Add mode
                    self.mod.initial_materials[name] = quantity
                    self.mod.materials.append(new_material)
                
                self.update_material_list()
                self.update_recipe_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(dialog, text="Save", command=save_material).grid(row=4, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_material_recipe_dialog(self):
        """Set material crafting recipe dialog"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.recipe_dialog("Set Material Crafting Recipe", material, False)
    
    def add_product_dialog(self):
        """Add product dialog"""
        self.product_dialog("Add Product")
    
    def edit_product_dialog(self):
        """Edit product dialog"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.product_dialog("Edit Product", product, index)
    
    def product_dialog(self, title, product=None, index=None):
        """Product dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=product.name if product else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Production Time (minutes):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        time_var = tk.StringVar(value=product.production_time if product else "60")
        time_entry = ttk.Entry(dialog, textvariable=time_var)
        time_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Sale Price:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        price_var = tk.StringVar(value=product.sale_price if product else "20")
        price_entry = ttk.Entry(dialog, textvariable=price_var)
        price_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_product():
            try:
                name = name_var.get()
                production_time = int(time_var.get())
                sale_price = float(price_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter product name!")
                    return
                
                new_product = Product(name, production_time, sale_price)
                
                if product:  # Edit mode
                    # Preserve material requirements and crafting recipe
                    new_product.materials_required = product.materials_required.copy()
                    new_product.products_required = product.products_required.copy()
                    new_product.is_craftable = product.is_craftable
                    
                    self.mod.products[index] = new_product
                else:  # Add mode
                    self.mod.products.append(new_product)
                
                self.update_product_list()
                self.update_recipe_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(dialog, text="Save", command=save_product).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_product_recipe_dialog(self):
        """Set product crafting recipe dialog"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.recipe_dialog("Set Product Crafting Recipe", product, True)
    
    def recipe_dialog(self, title, item, is_product):
        """Crafting recipe dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("500x640")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Basic info
        info_frame = ttk.LabelFrame(dialog, text="Basic Info", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        item_type = "Product" if is_product else "Material"
        ttk.Label(info_frame, text=f"{item_type} Name: {item.name}").pack(anchor=tk.W)
        
        # Material requirements
        materials_frame = ttk.LabelFrame(dialog, text="Material Requirements", padding="10")
        materials_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Material requirements list
        materials_list_frame = ttk.Frame(materials_frame)
        materials_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview to display material requirements
        columns = ("Material", "Quantity")
        self.materials_tree = ttk.Treeview(materials_list_frame, columns=columns, show="headings", height=6)
        
        # Set column headings
        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(materials_list_frame, orient="vertical", command=self.materials_tree.yview)
        self.materials_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Material requirements buttons
        materials_btn_frame = ttk.Frame(materials_frame)
        materials_btn_frame.pack(fill=tk.X)
        
        ttk.Button(materials_btn_frame, text="Add Material Requirement", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "material")).pack(side=tk.LEFT, padx=5)
        ttk.Button(materials_btn_frame, text="Delete Material Requirement", 
                  command=lambda: self.delete_requirement(self.materials_tree)).pack(side=tk.LEFT, padx=5)
        
        # Product requirements
        products_frame = ttk.LabelFrame(dialog, text="Product Requirements", padding="10")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product requirements list
        products_list_frame = ttk.Frame(products_frame)
        products_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview to display product requirements
        columns = ("Product", "Quantity")
        self.products_tree = ttk.Treeview(products_list_frame, columns=columns, show="headings", height=6)
        
        # Set column headings
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Add scrollbar
        tree_scrollbar2 = ttk.Scrollbar(products_list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=tree_scrollbar2.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Product requirements buttons
        products_btn_frame = ttk.Frame(products_frame)
        products_btn_frame.pack(fill=tk.X)
        
        ttk.Button(products_btn_frame, text="Add Product Requirement", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "product")).pack(side=tk.LEFT, padx=5)
        ttk.Button(products_btn_frame, text="Delete Product Requirement", 
                  command=lambda: self.delete_requirement(self.products_tree)).pack(side=tk.LEFT, padx=5)
        
        # Load existing requirements
        for material_name, quantity in item.materials_required.items():
            self.materials_tree.insert("", "end", values=(material_name, quantity))
            
        for product_name, quantity in item.products_required.items():
            self.products_tree.insert("", "end", values=(product_name, quantity))
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_recipe():
            # Update material requirements
            item.materials_required.clear()
            for material_item in self.materials_tree.get_children():
                values = self.materials_tree.item(material_item, "values")
                material_name = values[0]
                quantity = int(values[1])
                item.add_material_requirement(material_name, quantity)
                
            # Update product requirements
            item.products_required.clear()
            for product_item in self.products_tree.get_children():
                values = self.products_tree.item(product_item, "values")
                product_name = values[0]
                quantity = int(values[1])
                item.add_product_requirement(product_name, quantity)
                
            # Mark as craftable
            item.is_craftable = True
            
            if is_product:
                self.update_product_list()
            else:
                self.update_material_list()
            self.update_recipe_list()
            
            messagebox.showinfo("Success", "Crafting recipe saved!")
        
        def save_and_close():
            save_recipe()
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save Recipe", command=save_recipe).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save and Close", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def add_requirement_dialog(self, parent_dialog, item, requirement_type):
        """Add requirement dialog"""
        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Add {requirement_type} Requirement")
        dialog.geometry("300x150")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        requirement_name = "Material" if requirement_type == "material" else "Product"
        
        ttk.Label(dialog, text=f"{requirement_name}:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        
        if requirement_type == "material":
            name_combo = ttk.Combobox(dialog, textvariable=name_var, 
                                     values=[m.name for m in self.mod.materials])
        else:
            name_combo = ttk.Combobox(dialog, textvariable=name_var, 
                                     values=[p.name for p in self.mod.products])
        name_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def add_requirement():
            try:
                name = name_var.get()
                quantity = int(quantity_var.get())
                
                if not name:
                    messagebox.showerror("Error", f"Please select {requirement_name}!")
                    return
                
                # Check if requirement already exists
                if requirement_type == "material":
                    tree = self.materials_tree
                else:
                    tree = self.products_tree
                    
                for tree_item in tree.get_children():
                    values = tree.item(tree_item, "values")
                    if values[0] == name:
                        messagebox.showwarning("Warning", f"This {requirement_name} requirement already exists!")
                        return
                
                # Add to list
                tree.insert("", "end", values=(name, quantity))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(dialog, text="Add", command=add_requirement).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_requirement(self, tree):
        """Delete requirement"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a requirement first!")
            return
            
        for item in selection:
            tree.delete(item)
    
    def delete_material(self):
        """Delete material"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        
        # Delete initial stock
        if material.name in self.mod.initial_materials:
            del self.mod.initial_materials[material.name]
            
        self.mod.materials.pop(index)
        self.update_material_list()
        self.update_recipe_list()
    
    def delete_product(self):
        """Delete product"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        self.mod.products.pop(index)
        self.update_product_list()
        self.update_recipe_list()
    
    def delete_recipe(self):
        """Delete recipe"""
        selection = self.recipe_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recipe first!")
            return
            
        for item in selection:
            values = self.recipe_tree.item(item, "values")
            item_type, name = values[0], values[1]
            
            if item_type == "Material":
                # Find corresponding material and clear crafting recipe
                for material in self.mod.materials:
                    if material.name == name:
                        material.is_craftable = False
                        material.materials_required.clear()
                        material.products_required.clear()
                        break
                self.update_material_list()
            else:
                # Find corresponding product and clear crafting recipe
                for product in self.mod.products:
                    if product.name == name:
                        product.is_craftable = False
                        product.products_required.clear()
                        # Note: Don't clear material requirements as product may still need materials for production
                        break
                self.update_product_list()
                
            self.recipe_tree.delete(item)
    
    def add_worker_dialog(self):
        """Add worker dialog"""
        self.worker_dialog("Add Worker")
    
    def edit_worker_dialog(self):
        """Edit worker dialog"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker first!")
            return
            
        index = selection[0]
        worker = self.mod.initial_workers[index]
        self.worker_dialog("Edit Worker", worker, index)
    
    def worker_dialog(self, title, worker=None, index=None):
        """Worker dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Worker Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=worker.name if worker else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Skill Level (1-5):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        skill_var = tk.StringVar(value=worker.skill_level if worker else "3")
        skill_entry = ttk.Entry(dialog, textvariable=skill_var)
        skill_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Daily Salary:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        salary_var = tk.StringVar(value=worker.salary if worker else "100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_worker():
            try:
                name = name_var.get()
                skill_level = int(skill_var.get())
                salary = float(salary_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter worker name!")
                    return
                
                new_worker = Worker(name, skill_level, salary)
                
                if worker:  # Edit mode
                    self.mod.initial_workers[index] = new_worker
                else:  # Add mode
                    self.mod.initial_workers.append(new_worker)
                
                self.update_worker_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(dialog, text="Save", command=save_worker).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_worker(self):
        """Delete worker"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker first!")
            return
            
        index = selection[0]
        self.mod.initial_workers.pop(index)
        self.update_worker_list()
    
    def save_mod(self):
        """Save mod"""
        # Update mod basic info
        self.mod.name = self.name_var.get()
        self.mod.description = self.desc_var.get()
        self.mod.author = self.author_var.get()
        self.mod.version = self.version_var.get()
        
        try:
            self.mod.initial_balance = float(self.balance_var.get())
        except ValueError:
            messagebox.showerror("Error", "Initial balance must be a valid number!")
            return
        
        if not self.mod.name:
            messagebox.showerror("Error", "Please enter mod name!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Mod File",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.mod.save_to_file(filename)
                messagebox.showinfo("Success", f"Mod saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save mod: {str(e)}")
    
    def load_mod(self):
        """Load mod"""
        filename = filedialog.askopenfilename(
            title="Select Mod File",
            filetypes=[("LAUN Mod Files", "*.launmod"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.mod = Mod.load_from_file(filename)
                
                # Update interface
                self.name_var.set(self.mod.name)
                self.desc_var.set(self.mod.description)
                self.author_var.set(self.mod.author)
                self.version_var.set(self.mod.version)
                self.balance_var.set(str(self.mod.initial_balance))
                
                # Update crafting station list
                self.station_listbox.delete(0, tk.END)
                for station in self.mod.crafting_stations:
                    self.station_listbox.insert(tk.END, f"{station['name']} (Capacity:{station['capacity']})")
                
                self.update_material_list()
                self.update_product_list()
                self.update_worker_list()
                self.update_recipe_list()
                
                messagebox.showinfo("Success", f"Loaded mod: {self.mod.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mod: {str(e)}")
    
    def apply_mod(self):
        """Apply mod to game"""
        # Update mod basic info
        self.mod.name = self.name_var.get()
        self.mod.description = self.desc_var.get()
        self.mod.author = self.author_var.get()
        self.mod.version = self.version_var.get()
        
        try:
            self.mod.initial_balance = float(self.balance_var.get())
        except ValueError:
            messagebox.showerror("Error", "Initial balance must be a valid number!")
            return
        
        if not self.mod.name:
            messagebox.showerror("Error", "Please enter mod name!")
            return
        
        self.app.current_mod = self.mod
        self.app.factory.load_mod(self.mod)
        self.app.mod_label.config(text=f"{self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"Loaded mod: {self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"Mod description: {self.mod.description}")
        self.app.update_progress_bars()
        self.app.update_display()
        
        messagebox.showinfo("Success", "Mod applied to game!")
        self.window.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = FactorySimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
