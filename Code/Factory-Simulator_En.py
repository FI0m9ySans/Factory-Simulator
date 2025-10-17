import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import random

# 添加分辨率配置
class ResolutionConfig:
    """分辨率配置类"""
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
        """获取当前分辨率尺寸"""
        return self.resolutions[self.current_resolution]
    
    def set_resolution(self, resolution_name):
        """设置分辨率"""
        if resolution_name in self.resolutions:
            self.current_resolution = resolution_name
            return True
        return False
    
    def get_scale_factor(self):
        """获取缩放因子"""
        return self.resolutions[self.current_resolution]["scale"]
    
    def get_available_resolutions(self):
        """获取可用的分辨率列表"""
        return list(self.resolutions.keys())

class Product:
    """产品类"""
    def __init__(self, name: str, production_time: int, sale_price: float):
        self.name = name
        self.production_time = production_time  # 生产所需时间(分钟)
        self.sale_price = sale_price  # 销售价格
        self.materials_required = {}  # 所需原材料 {材料名称: 数量}
        self.products_required = {}  # 所需产品 {产品名称: 数量}
        self.is_craftable = False  # 是否可通过合成获得
        
    def add_material_requirement(self, material_name: str, quantity: int):
        """添加原材料需求"""
        self.materials_required[material_name] = quantity
        
    def add_product_requirement(self, product_name: str, quantity: int):
        """添加产品需求"""
        self.products_required[product_name] = quantity
        self.is_craftable = True
        
    def remove_material_requirement(self, material_name: str):
        """移除原材料需求"""
        if material_name in self.materials_required:
            del self.materials_required[material_name]
            
    def remove_product_requirement(self, product_name: str):
        """移除产品需求"""
        if product_name in self.products_required:
            del self.products_required[product_name]
            
    def get_total_material_cost(self, materials_dict):
        """计算总材料成本"""
        total_cost = 0
        for material_name, quantity in self.materials_required.items():
            if material_name in materials_dict:
                material = materials_dict[material_name]
                total_cost += material.cost * quantity
        return total_cost
        
    def to_dict(self):
        """转换为字典，用于JSON序列化"""
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
        """从字典创建产品"""
        product = cls(
            name=data["name"],
            production_time=data["production_time"],
            sale_price=data["sale_price"]
        )
        # 加载原材料需求
        product.materials_required = data.get("materials_required", {})
        # 加载产品需求
        product.products_required = data.get("products_required", {})
        product.is_craftable = data.get("is_craftable", False)
        return product
        
    def __str__(self):
        materials_str = ", ".join([f"{name}×{qty}" for name, qty in self.materials_required.items()])
        products_str = ", ".join([f"{name}×{qty}" for name, qty in self.products_required.items()])
        
        if materials_str and products_str:
            return f"{self.name} (Selling price:¥{self.sale_price}, Production time:{self.production_time}minute, Material:{materials_str}, Component:{products_str})"
        elif materials_str:
            return f"{self.name} (Selling price:¥{self.sale_price}, Production time:{self.production_time}minute, Material:{materials_str})"
        elif products_str:
            return f"{self.name} (Selling price:¥{self.sale_price}, Production time:{self.production_time}minute, Component:{products_str})"
        else:
            return f"{self.name} (Selling price:¥{self.sale_price}, Production time:{self.production_time}minute)"

class Material:
    """原材料类"""
    def __init__(self, name: str, cost: float, unit: str):
        self.name = name
        self.cost = cost  # 单价
        self.unit = unit  # 单位
        self.is_craftable = False  # 是否可通过合成获得
        self.materials_required = {}  # 所需原材料 {材料名称: 数量}
        self.products_required = {}  # 所需产品 {产品名称: 数量}
        
    def add_material_requirement(self, material_name: str, quantity: int):
        """添加原材料需求"""
        self.materials_required[material_name] = quantity
        self.is_craftable = True
        
    def add_product_requirement(self, product_name: str, quantity: int):
        """添加产品需求"""
        self.products_required[product_name] = quantity
        self.is_craftable = True
        
    def remove_material_requirement(self, material_name: str):
        """移除原材料需求"""
        if material_name in self.materials_required:
            del self.materials_required[material_name]
            
    def remove_product_requirement(self, product_name: str):
        """移除产品需求"""
        if product_name in self.products_required:
            del self.products_required[product_name]
        
    def to_dict(self):
        """转换为字典，用于JSON序列化"""
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
        """从字典创建原材料"""
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
                return f"{self.name} (¥{self.cost}/{self.unit}, Can be synthesized, Material:{materials_str}, Component:{products_str})"
            elif materials_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, Can be synthesized, Material:{materials_str})"
            elif products_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, Can be synthesized, Component:{products_str})"
        else:
            return f"{self.name} (¥{self.cost}/{self.unit})"

class CraftingStation:
    """合成站类"""
    def __init__(self, station_id: int, name: str, capacity: int):
        self.station_id = station_id
        self.name = name
        self.capacity = capacity  # 最大产能
        self.current_recipe = None  # 当前合成配方（产品名或材料名）
        self.is_recipe_product = True  # True: 合成产品, False: 合成材料
        self.crafting_progress = 0
        self.assigned_worker = None
        self.is_active = False
        
    def assign_worker(self, worker):
        """分配工人到合成站"""
        self.assigned_worker = worker
        worker.is_working = True
        self.is_active = True
        
    def assign_recipe(self, recipe_name: str, is_product: bool):
        """分配合成配方到合成站"""
        self.current_recipe = recipe_name
        self.is_recipe_product = is_product
        self.crafting_progress = 0
        
    def update_crafting(self):
        """更新合成进度"""
        if self.is_active and self.current_recipe and self.assigned_worker:
            # 技能等级影响合成效率
            efficiency = 1 + (self.assigned_worker.skill_level - 1) * 0.2
            self.crafting_progress += efficiency
            
            if self.crafting_progress >= 60:  # 合成固定需要60分钟
                # 合成完成
                self.crafting_progress = 0
                completed_item = self.current_recipe
                self.current_recipe = None
                return completed_item, self.is_recipe_product
        return None, None
        
    def get_progress_percentage(self):
        """获取合成进度百分比"""
        return min(100, int((self.crafting_progress / 60) * 100))
        
    def __str__(self):
        status = "Running" if self.is_active else "Stop"
        recipe_name = self.current_recipe if self.current_recipe else "None"
        recipe_type = "Product" if self.is_recipe_product else "Material"
        worker_name = self.assigned_worker.name if self.assigned_worker else "None"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"{self.name} {self.station_id} (State:{status}, Formula:{recipe_name}({recipe_type}), Worker:{worker_name}, Progress:{progress})"

class Worker:
    """工人类"""
    def __init__(self, name: str, skill_level: int, salary: float):
        self.name = name
        self.skill_level = skill_level  # 技能等级(1-5)
        self.salary = salary  # 日薪
        self.is_working = False
        self.current_task = None
        
    def to_dict(self):
        """转换为字典，用于JSON序列化"""
        return {
            "name": self.name,
            "skill_level": self.skill_level,
            "salary": self.salary
        }
        
    @classmethod
    def from_dict(cls, data):
        """从字典创建工人"""
        return cls(
            name=data["name"],
            skill_level=data["skill_level"],
            salary=data["salary"]
        )
        
    def __str__(self):
        status = "At work" if self.is_working else "Free"
        return f"{self.name} (Skill:{self.skill_level}, Salary:¥{self.salary}/day, State:{status})"

class ProductionLine:
    """生产线类"""
    def __init__(self, line_id: int, capacity: int):
        self.line_id = line_id
        self.capacity = capacity  # 最大产能
        self.current_product = None
        self.production_progress = 0
        self.assigned_worker = None
        self.is_active = False
        
    def assign_worker(self, worker: Worker):
        """分配工人到生产线"""
        self.assigned_worker = worker
        worker.is_working = True
        self.is_active = True
        
    def assign_product(self, product: Product):
        """分配产品到生产线"""
        self.current_product = product
        self.production_progress = 0
        
    def update_production(self):
        """更新生产进度"""
        if self.is_active and self.current_product and self.assigned_worker:
            # 技能等级影响生产效率
            efficiency = 1 + (self.assigned_worker.skill_level - 1) * 0.2
            self.production_progress += efficiency
            
            if self.production_progress >= self.current_product.production_time:
                # 生产完成
                self.production_progress = 0
                completed_product = self.current_product
                self.current_product = None
                return completed_product
        return None
        
    def get_progress_percentage(self):
        """获取生产进度百分比"""
        if self.current_product:
            return min(100, int((self.production_progress / self.current_product.production_time) * 100))
        return 0
        
    def __str__(self):
        status = "Running" if self.is_active else "Stop"
        product_name = self.current_product.name if self.current_product else "None"
        worker_name = self.assigned_worker.name if self.assigned_worker else "None"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"Production line {self.line_id} (State:{status}, Product:{product_name}, Worker:{worker_name}, Progress:{progress})"

class Order:
    """订单类"""
    def __init__(self, order_id: int, product: Product, quantity: int, deadline: datetime):
        self.order_id = order_id
        self.product = product
        self.quantity = quantity
        self.deadline = deadline
        self.completed_quantity = 0
        self.is_completed = False
        
    def complete_quantity(self, amount: int):
        """完成一定数量的产品"""
        self.completed_quantity += amount
        if self.completed_quantity >= self.quantity:
            self.is_completed = True
            
    def is_overdue(self, current_time: datetime):
        """检查订单是否逾期"""
        return current_time > self.deadline and not self.is_completed
        
    def __str__(self):
        status = "Completed" if self.is_completed else "In progress"
        return f"Order #{self.order_id}: {self.product.name} x{self.quantity} (Deadline:{self.deadline.strftime('%Y-%m-%d %H:%M')}, State:{status})"

class Mod:
    """模组类"""
    def __init__(self, name="", description="", author="", version="1.0"):
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.products = []
        self.materials = []
        self.initial_workers = []
        self.initial_balance = 10000
        self.initial_materials = {}
        self.crafting_stations = []
        
    def to_dict(self):
        """转换为字典，用于JSON序列化"""
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
        """从字典创建模组"""
        mod = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0")
        )
        mod.initial_balance = data.get("initial_balance", 10000)
        mod.initial_materials = data.get("initial_materials", {})
        
        # 加载原材料
        mod.materials = [Material.from_dict(material_data) for material_data in data.get("materials", [])]
        
        # 加载产品
        mod.products = [Product.from_dict(product_data) for product_data in data.get("products", [])]
        
        # 加载初始工人
        mod.initial_workers = [Worker.from_dict(worker_data) for worker_data in data.get("initial_workers", [])]
        
        # 加载合成站
        mod.crafting_stations = data.get("crafting_stations", [])
        
        return mod
        
    def save_to_file(self, filename):
        """保存模组到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            
    @classmethod
    def load_from_file(cls, filename):
        """从文件加载模组"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls.from_dict(data)

class Factory:
    """工厂类"""
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
        """添加生产线"""
        line_id = len(self.production_lines) + 1
        new_line = ProductionLine(line_id, capacity)
        self.production_lines.append(new_line)
        return new_line
        
    def add_crafting_station(self, name: str, capacity: int):
        """添加合成站"""
        station_id = len(self.crafting_stations) + 1
        new_station = CraftingStation(station_id, name, capacity)
        self.crafting_stations.append(new_station)
        return new_station
        
    def hire_worker(self, name: str, skill_level: int, salary: float):
        """雇佣工人"""
        new_worker = Worker(name, skill_level, salary)
        self.workers.append(new_worker)
        return new_worker
        
    def add_product(self, product: Product):
        """添加产品"""
        self.products[product.name] = product
        self.product_inventory[product.name] = 0
        return product
        
    def remove_product(self, name: str):
        """删除产品"""
        if name in self.products:
            del self.products[name]
            if name in self.product_inventory:
                del self.product_inventory[name]
            return True
        return False
        
    def add_material(self, name: str, cost: float, unit: str, initial_quantity: int = 0):
        """添加原材料"""
        new_material = Material(name, cost, unit)
        self.materials[name] = new_material
        self.material_inventory[name] = initial_quantity
        return new_material
        
    def remove_material(self, name: str):
        """删除原材料"""
        if name in self.materials:
            del self.materials[name]
            if name in self.material_inventory:
                del self.material_inventory[name]
            return True
        return False
        
    def purchase_material(self, material_name: str, quantity: int):
        """购买原材料"""
        if material_name not in self.materials:
            return False, f"Error: Raw materials {material_name} Does not exist!"
            
        material = self.materials[material_name]
        cost = material.cost * quantity
        
        if cost > self.balance:
            return False, f"Error: Insufficient funds! ¥{cost} required, current balance ¥{self.balance}"
            
        self.balance -= cost
        self.material_inventory[material_name] += quantity
        self.daily_costs += cost
        return True, f"Purchased {quantity}{material.unit} of {material_name}, costing ¥{cost}"
        
    def create_order(self, product_name: str, quantity: int, days_until_deadline: int):
        """创建订单"""
        if product_name not in self.products:
            return None, f"Error: Product {product_name} does not exist!"
            
        product = self.products[product_name]
        deadline = self.current_time + timedelta(days=days_until_deadline)
        order_id = len(self.orders) + 1
        new_order = Order(order_id, product, quantity, deadline)
        self.orders.append(new_order)
        return new_order, f"Created a new order: {new_order}"
        
    def assign_worker_to_line(self, worker_name: str, line_id: int):
        """分配工人到生产线"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        
        if not worker:
            return False, f"Error: Worker {worker_name} does not exist!"
            
        if not line:
            return False, f"Error: Production line {line_id} does not exist!"
            
        # 如果工人已经在其他生产线上工作，先解除分配
        for other_line in self.production_lines:
            if other_line.assigned_worker == worker:
                other_line.assigned_worker = None
                other_line.is_active = False
                
        line.assign_worker(worker)
        return True, f"Worker {worker_name} was assigned to production line {line_id}"
        
    def assign_worker_to_station(self, worker_name: str, station_id: int):
        """分配工人到合成站"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        
        if not worker:
            return False, f"Error: Worker {worker_name} does not exist!"
            
        if not station:
            return False, f"Error: Synthesis station {station_id} does not exist!"
            
        # 如果工人已经在其他合成站工作，先解除分配
        for other_station in self.crafting_stations:
            if other_station.assigned_worker == worker:
                other_station.assigned_worker = None
                other_station.is_active = False
                
        station.assign_worker(worker)
        return True, f"Worker {worker_name} has been assigned to synthesis station {station_id}"
        
    def assign_product_to_line(self, product_name: str, line_id: int):
        """分配产品到生产线"""
        if product_name not in self.products:
            return False, f"Error: Product {product_name} does not exist!"
            
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        if not line:
            return False, f"Error: Production line {line_id} does not exist!"
            
        if not line.assigned_worker:
            return False, f"Error: No workers assigned to production line {line_id}!"
            
        product = self.products[product_name]
        
        # 检查所有所需原材料是否足够
        for material_name, quantity in product.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"Error: {material_name} is insufficient! {quantity} required, current stock is {self.material_inventory.get(material_name, 0)}"
            
        # 检查所有所需产品是否足够
        for product_name_req, quantity in product.products_required.items():
            if self.product_inventory.get(product_name_req, 0) < quantity:
                return False, f"Error: {product_name_req} is insufficient! {quantity} required, current stock {self.product_inventory.get(product_name_req, 0)}"
            
        # 消耗所有所需原材料
        for material_name, quantity in product.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # 消耗所有所需产品
        for product_name_req, quantity in product.products_required.items():
            self.product_inventory[product_name_req] -= quantity
            
        line.assign_product(product)
        return True, f"Production line {line_id} has started producing {product_name}"
        
    def assign_recipe_to_station(self, recipe_name: str, is_product: bool, station_id: int):
        """分配合成配方到合成站"""
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        if not station:
            return False, f"Error: Synthesis station {station_id} does not exist!"
            
        if not station.assigned_worker:
            return False, f"Error: Assembly station {station_id} has no assigned workers!"
            
        # 检查配方是否存在
        if is_product:
            if recipe_name not in self.products:
                return False, f"Error: Product {recipe_name} does not exist!"
            recipe = self.products[recipe_name]
        else:
            if recipe_name not in self.materials:
                return False, f"Error: Raw material {recipe_name} does not exist!"
            recipe = self.materials[recipe_name]
            
        # 检查是否是可合成物品
        if not recipe.is_craftable:
            return False, f"Error: {recipe_name} cannot be crafted!"
            
        # 检查所有所需原材料是否足够
        for material_name, quantity in recipe.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"Error: {material_name} is insufficient! {quantity} required, current stock is {self.material_inventory.get(material_name, 0)}"
            
        # 检查所有所需产品是否足够
        for product_name, quantity in recipe.products_required.items():
            if self.product_inventory.get(product_name, 0) < quantity:
                return False, f"Error: {product_name} is insufficient! {quantity} required, current stock is {self.product_inventory.get(product_name, 0)}"
            
        # 消耗所有所需原材料
        for material_name, quantity in recipe.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # 消耗所有所需产品
        for product_name, quantity in recipe.products_required.items():
            self.product_inventory[product_name] -= quantity
            
        station.assign_recipe(recipe_name, is_product)
        return True, f"Synthesis station {station_id} started synthesizing {recipe_name}"
        
    def update_production(self):
        """更新所有生产线的生产进度"""
        completed_products = []
        for line in self.production_lines:
            if line.is_active and line.current_product:
                completed_product = line.update_production()
                if completed_product:
                    # 生产完成，添加到库存
                    self.product_inventory[completed_product.name] += 1
                    completed_products.append(completed_product.name)
                    
                    # 检查是否有订单需要完成
                    for order in self.orders:
                        if not order.is_completed and order.product.name == completed_product.name:
                            order.complete_quantity(1)
                            if order.is_completed:
                                # 订单完成，获得收入
                                income = order.product.sale_price * order.quantity
                                self.balance += income
                                self.daily_income += income
        return completed_products
        
    def update_crafting(self):
        """更新所有合成站的合成进度"""
        completed_items = []
        for station in self.crafting_stations:
            if station.is_active and station.current_recipe:
                completed_item, is_product = station.update_crafting()
                if completed_item:
                    # 合成完成，添加到库存
                    if is_product:
                        self.product_inventory[completed_item] += 1
                    else:
                        self.material_inventory[completed_item] += 1
                    completed_items.append((completed_item, is_product))
        return completed_items
                            
    def sell_from_inventory(self, product_name: str, quantity: int):
        """从库存销售产品"""
        if product_name not in self.product_inventory:
            return False, f"Error: Product {product_name} does not exist!"
            
        if self.product_inventory[product_name] < quantity:
            return False, f"Error: Insufficient stock! {product_name} only has {self.product_inventory[product_name]} items"
            
        product = self.products[product_name]
        income = product.sale_price * quantity
        self.product_inventory[product_name] -= quantity
        self.balance += income
        self.daily_income += income
        return True, f"Sold {quantity} units of {product_name}, earning ¥{income}"
        
    def pay_workers(self):
        """支付工人工资"""
        total_salary = sum(worker.salary for worker in self.workers)
        if total_salary > self.balance:
            return False, f"Warning: Insufficient funds to pay workers' wages! ¥{total_salary} needed, current balance ¥{self.balance}"
            
        self.balance -= total_salary
        self.daily_costs += total_salary
        return True, f"Paid the workers' wages ¥{total_salary}"
        
    def advance_time(self, hours: int = 1):
        """推进时间"""
        self.current_time += timedelta(hours=hours)
        
        # 每小时更新生产和合成
        completed_products = []
        completed_crafting = []
        for _ in range(hours):
            completed = self.update_production()
            completed_products.extend(completed)
            
            completed = self.update_crafting()
            completed_crafting.extend(completed)
            
        # 检查逾期订单
        overdue_orders = []
        for order in self.orders:
            if order.is_overdue(self.current_time):
                overdue_orders.append(order.order_id)
                
        return completed_products, completed_crafting, overdue_orders
                
    def next_day(self):
        """进入下一天"""
        self.day += 1
        self.current_time = self.current_time.replace(hour=8, minute=0) + timedelta(days=1)
        
        # 支付工人工资
        success, message = self.pay_workers()
        
        # 重置每日统计
        daily_profit = self.daily_income - self.daily_costs
        
        self.daily_income = 0
        self.daily_costs = 0
        
        return success, message, daily_profit
        
    def get_status_text(self):
        """获取工厂状态文本"""
        status_text = f"=== {self.name} Status (Day {self.day}) ===\n"
        status_text += f"Funds: ¥{self.balance}\n"
        status_text += f"Time: {self.current_time.strftime('%Y-%m-%d %H:%M')}\n"
        
        status_text += "\n--- Production line ---\n"
        for line in self.production_lines:
            status_text += f"  {line}\n"
            
        status_text += "\n--- Synthesis Station ---\n"
        for station in self.crafting_stations:
            status_text += f"  {station}\n"
            
        status_text += "\n--- Worker ---\n"
        for worker in self.workers:
            status_text += f"  {worker}\n"
            
        status_text += "\n--- Raw material inventory ---\n"
        for material, quantity in self.material_inventory.items():
            unit = self.materials[material].unit if material in self.materials else "Unit"
            status_text += f"  {material}: {quantity}{unit}\n"
            
        status_text += "\n--- Product inventory ---\n"
        for product, quantity in self.product_inventory.items():
            status_text += f"  {product}: {quantity}pieces\n"
            
        status_text += "\n--- Order ---\n"
        for order in self.orders:
            status = "Completed" if order.is_completed else "In progress"
            overdue = "(Overdue!)" if order.is_overdue(self.current_time) else ""
            status_text += f"  {order}{overdue}\n"
            
        return status_text

    def load_mod(self, mod):
        """加载模组"""
        # 清空现有数据
        self.products.clear()
        self.materials.clear()
        self.product_inventory.clear()
        self.material_inventory.clear()
        self.workers.clear()
        self.crafting_stations.clear()
        
        # 设置初始余额
        self.balance = mod.initial_balance
        
        # 添加原材料
        for material in mod.materials:
            initial_quantity = mod.initial_materials.get(material.name, 0)
            self.add_material(
                material.name,
                material.cost,
                material.unit,
                initial_quantity
            )
            # 设置材料的合成需求
            self.materials[material.name].is_craftable = material.is_craftable
            self.materials[material.name].materials_required = material.materials_required.copy()
            self.materials[material.name].products_required = material.products_required.copy()
            
        # 添加产品
        for product in mod.products:
            self.add_product(product)
            
        # 添加工人
        for worker_data in mod.initial_workers:
            self.hire_worker(
                worker_data.name,
                worker_data.skill_level,
                worker_data.salary
            )
            
        # 添加合成站
        for station_data in mod.crafting_stations:
            self.add_crafting_station(station_data["name"], station_data["capacity"])

class FactorySimulatorGUI:
    """工厂模拟器GUI"""
    def __init__(self, root):
        self.root = root
        self.root.title("(Processing Plant Simulator - Synthesis System Edition)")
        self.root.geometry("1200x800")
        
        # 创建工厂实例
        self.factory = Factory("Efficient Factory", initial_balance=10000)
        self.setup_factory()
        
        # 当前模组
        self.current_mod = None
        
        # 是否正在运行模拟
        self.simulation_running = False
        
        # 创建GUI
        self.create_widgets()
        
        # 启动定时更新
        self.update_display()
        
class SettingsDialog:
    """设置对话框"""
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x410")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        self.create_widgets()
        
    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """创建设置界面"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分辨率设置
        resolution_frame = ttk.LabelFrame(main_frame, text="Resolution settings", padding="10")
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="Choose resolution:").pack(anchor=tk.W, pady=5)
        
        self.resolution_var = tk.StringVar(value=self.app.resolution_config.current_resolution)
        resolution_combo = ttk.Combobox(
            resolution_frame, 
            textvariable=self.resolution_var,
            values=self.app.resolution_config.get_available_resolutions(),
            state="readonly"
        )
        resolution_combo.pack(fill=tk.X, pady=5)
        
        # 窗口模式
        window_frame = ttk.LabelFrame(main_frame, text="Windowed mode", padding="10")
        window_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.window_mode_var = tk.StringVar(value=self.app.window_mode)
        ttk.Radiobutton(
            window_frame, 
            text="Windowed mode", 
            variable=self.window_mode_var, 
            value="windowed"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            window_frame, 
            text="Full screen mode", 
            variable=self.window_mode_var, 
            value="fullscreen"
        ).pack(anchor=tk.W, pady=2)
        
        # 缩放设置
        scale_frame = ttk.LabelFrame(main_frame, text="Interface scaling", padding="10")
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
        
        scale_value_label = ttk.Label(scale_frame, text=f"Scaling factor: {self.scale_var.get():.1f}")
        scale_value_label.pack(anchor=tk.W)
        
        def update_scale_label(*args):
            scale_value_label.config(text=f"Scaling factor: {self.scale_var.get():.1f}")
        
        self.scale_var.trace('w', update_scale_label)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="App Settings", 
            command=self.apply_settings
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Restore default", 
            command=self.reset_to_default
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.window.destroy
        ).pack(side=tk.RIGHT)
        
    def apply_settings(self):
        """应用设置"""
        # 更新分辨率
        new_resolution = self.resolution_var.get()
        if new_resolution != self.app.resolution_config.current_resolution:
            self.app.resolution_config.set_resolution(new_resolution)
            self.app.apply_resolution()
        
        # 更新窗口模式
        new_window_mode = self.window_mode_var.get()
        if new_window_mode != self.app.window_mode:
            self.app.set_window_mode(new_window_mode)
        
        # 更新缩放因子
        new_scale = self.scale_var.get()
        if new_scale != self.app.scale_factor:
            self.app.set_scale_factor(new_scale)
        
        messagebox.showinfo("Success", "Settings applied. Some changes require restarting the program to take full effect.")
        self.window.destroy()
        
    def reset_to_default(self):
        """恢复默认设置"""
        self.resolution_var.set("1920x1080")
        self.window_mode_var.set("windowed")
        self.scale_var.set(1.0)

class FactorySimulatorGUI:
    """工厂模拟器GUI"""
    def __init__(self, root):
        self.root = root
        self.root.title("Processing Plant Simulator - Synthesis System Edition")
        
        # 初始化分辨率配置
        self.resolution_config = ResolutionConfig()
        self.window_mode = "windowed"  # windowed 或 fullscreen
        self.scale_factor = 1.0
        
        # 设置窗口初始大小和位置
        self.setup_window()
        
        # 创建工厂实例
        self.factory = Factory("Efficient Factory", initial_balance=10000)
        self.setup_factory()
        
        # 当前模组
        self.current_mod = None
        
        # 是否正在运行模拟
        self.simulation_running = False
        
        # 创建GUI
        self.create_widgets()
        
        # 启动定时更新
        self.update_display()
        
    def setup_window(self):
        """设置窗口属性"""
        # 获取当前分辨率设置
        resolution = self.resolution_config.get_current_size()
        
        # 设置窗口大小
        if self.window_mode == "fullscreen":
            self.root.attributes('-fullscreen', True)
        else:
            # 窗口模式，设置为分辨率的大小
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            # 居中显示
            self.center_window()
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
        # 绑定退出全屏快捷键
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def toggle_fullscreen(self, event=None):
        """切换全屏模式"""
        if self.window_mode == "fullscreen":
            self.set_window_mode("windowed")
        else:
            self.set_window_mode("fullscreen")
            
    def set_window_mode(self, mode):
        """设置窗口模式"""
        self.window_mode = mode
        if mode == "fullscreen":
            self.root.attributes('-fullscreen', True)
        else:
            self.root.attributes('-fullscreen', False)
            # 恢复窗口大小
            resolution = self.resolution_config.get_current_size()
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            self.center_window()
    
    def apply_resolution(self):
        """应用新的分辨率设置"""
        resolution = self.resolution_config.get_current_size()
        if self.window_mode == "windowed":
            self.root.geometry(f"{resolution['width']}x{resolution['height']}")
            self.center_window()
    
    def set_scale_factor(self, scale_factor):
        """设置界面缩放因子"""
        self.scale_factor = scale_factor
        # 这里可以添加更新界面样式的代码
        # 由于tkinter的缩放支持有限，这里主要影响字体大小和组件尺寸

    def setup_factory(self):
        """初始化工厂数据"""
        # 添加原材料
        self.factory.add_material("Wood", cost=1, unit="Unit", initial_quantity=100)
        self.factory.add_material("Metal", cost=2, unit="Unit", initial_quantity=50)
        self.factory.add_material("Plastic", cost=0.5, unit="Unit", initial_quantity=200)
        self.factory.add_material("Screw", cost=0.1, unit="pieces", initial_quantity=500)
        
        # 添加产品
        chair = Product("Wooden chair", production_time=60, sale_price=20)
        chair.add_material_requirement("Wood", 5)
        self.factory.add_product(chair)
        
        table = Product("Wooden table", production_time=120, sale_price=40)
        table.add_material_requirement("Wood", 10)
        self.factory.add_product(table)
        
        cabinet = Product("Wooden cabinet", production_time=180, sale_price=60)
        cabinet.add_material_requirement("Wood", 15)
        cabinet.add_material_requirement("Metal", 2)
        self.factory.add_product(cabinet)
        
        # 添加可合成的产品和材料
        # 合成材料：金属板（由2金属合成）
        metal_plate = Material("Metal plate", cost=3, unit="block")
        metal_plate.add_material_requirement("Metal", 2)
        self.factory.add_material(metal_plate.name, metal_plate.cost, metal_plate.unit, 0)
        self.factory.materials["Metal plate"].is_craftable = True
        self.factory.materials["Metal plate"].materials_required = metal_plate.materials_required.copy()
        
        # 合成产品：高级椅子（由木椅和金属板合成）
        premium_chair = Product("High-end chair", production_time=90, sale_price=50)
        premium_chair.add_product_requirement("Wooden chair", 1)
        premium_chair.add_material_requirement("Metal plate", 1)
        premium_chair.add_material_requirement("Screw", 4)
        self.factory.add_product(premium_chair)
        
        # 添加生产线
        self.factory.add_production_line(capacity=10)
        self.factory.add_production_line(capacity=10)
        
        # 添加合成站
        self.factory.add_crafting_station("Basic crafting table", capacity=5)
        self.factory.add_crafting_station("Advanced Synthesizer", capacity=3)
        
        # 雇佣工人
        
        # 分配工人到生产线和合成站
        
        # 创建订单

        
        # 购买更多原材料
        self.factory.purchase_material("Wood", 200)
        self.factory.purchase_material("Metal", 50)
        self.factory.purchase_material("Screw", 200)
        
        # 开始生产
        self.factory.assign_product_to_line("Wooden chair", 1)
        self.factory.assign_product_to_line("Wooden table", 2)
        
    def create_widgets(self):
        """创建GUI组件"""
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重 - 使用pack布局替代grid以便更好地适应缩放
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Processing Plant Simulator - Synthesis System Edition", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 创建左右分栏的框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(content_frame, text="Control Panel", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 右侧状态显示
        status_frame = ttk.LabelFrame(content_frame, text="Factory condition", padding="10")
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 控制面板内容
        self.create_control_panel(control_frame)
        
        # 状态显示内容
        self.create_status_display(status_frame)
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="Event Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Document", menu=file_menu)
        file_menu.add_command(label="Save game", command=self.save_game)
        file_menu.add_command(label="Load Game", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Display Settings", command=self.open_settings)
        settings_menu.add_separator()
        
        # 分辨率子菜单
        resolution_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Resolution", menu=resolution_menu)
        
        for resolution in self.resolution_config.get_available_resolutions():
            resolution_menu.add_command(
                label=resolution, 
                command=lambda r=resolution: self.change_resolution(r)
            )
        
        # 窗口模式子菜单
        window_mode_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Windowed mode", menu=window_mode_menu)
        window_mode_menu.add_command(
            label="Windowed mode", 
            command=lambda: self.set_window_mode("windowed")
        )
        window_mode_menu.add_command(
            label="Full screen mode", 
            command=lambda: self.set_window_mode("fullscreen")
        )
        
        # 模组菜单
        mod_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="mod", menu=mod_menu)
        mod_menu.add_command(label="Mod Maker", command=self.open_mod_creator)
        mod_menu.add_command(label="Import module", command=self.import_mod)
        mod_menu.add_command(label="Export current module", command=self.export_current_mod)
        mod_menu.add_separator()
        mod_menu.add_command(label="Reset to default", command=self.reset_to_default)
        
    def change_resolution(self, resolution):
        """改变分辨率"""
        if self.resolution_config.set_resolution(resolution):
            self.apply_resolution()
            
    def open_settings(self):
        """打开设置对话框"""
        SettingsDialog(self.root, self)
        
    def save_game(self):
        """保存游戏"""
        filename = filedialog.asksaveasfilename(
            title="Save game",
            defaultextension=".factorysave",
            filetypes=[("Factory Save Files", "*.factorysave")]
        )
        
        if filename:
            try:
                # 保存游戏状态到文件
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
                    
                messagebox.showinfo("Success", f"The game has been saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Failure", f"Failed to save the game: {str(e)}")
                
    def load_game(self):
        """加载游戏"""
        filename = filedialog.askopenfilename(
            title="Load Game",
            filetypes=[("Factory Save Files", "*.factorysave")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
                
                # 恢复工厂状态
                factory_data = game_state["factory"]
                self.factory.name = factory_data["name"]
                self.factory.balance = factory_data["balance"]
                self.factory.day = factory_data["day"]
                self.factory.current_time = datetime.fromisoformat(factory_data["current_time"])
                self.factory.material_inventory = factory_data["material_inventory"]
                self.factory.product_inventory = factory_data["product_inventory"]
                self.factory.daily_costs = factory_data["daily_costs"]
                self.factory.daily_income = factory_data["daily_income"]
                
                # 恢复设置
                settings_data = game_state["settings"]
                self.resolution_config.set_resolution(settings_data["resolution"])
                self.set_window_mode(settings_data["window_mode"])
                self.set_scale_factor(settings_data["scale_factor"])
                
                self.update_display()
                messagebox.showinfo("Success", f"The game has been loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Failure", f"Failed to load game: {str(e)}")
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 使用ScrolledFrame来支持滚动
        from tkinter.scrolledtext import ScrolledText
        
        # 创建滚动框架
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
        
        # 模组信息
        mod_frame = ttk.LabelFrame(self.scrollable_frame, text="Current module", padding="5")
        mod_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mod_label = ttk.Label(mod_frame, text="Default mod")
        self.mod_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 时间控制
        time_frame = ttk.LabelFrame(self.scrollable_frame, text="Time control", padding="5")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        time_btn_frame = ttk.Frame(time_frame)
        time_btn_frame.pack(fill=tk.X)
        
        ttk.Button(time_btn_frame, text="Move forward 1 hour", command=self.advance_one_hour).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="Move forward 8 hour", command=self.advance_eight_hours).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="The next day", command=self.next_day).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 自动模拟控制
        auto_frame = ttk.LabelFrame(self.scrollable_frame, text="Automatic simulation", padding="5")
        auto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sim_speed = tk.StringVar(value="1")
        speed_frame = ttk.Frame(auto_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        ttk.Radiobutton(speed_frame, text="slow", variable=self.sim_speed, value="0.5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="Normal", variable=self.sim_speed, value="1").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="fast", variable=self.sim_speed, value="2").pack(side=tk.LEFT, padx=5)
        
        self.auto_btn = ttk.Button(auto_frame, text="Start automatic simulation", command=self.toggle_auto_simulation)
        self.auto_btn.pack(fill=tk.X, pady=5)
        
        # 工厂管理
        manage_frame = ttk.LabelFrame(self.scrollable_frame, text="Factory Management", padding="5")
        manage_frame.pack(fill=tk.X, pady=(0, 10))
        
        manage_btn_frame = ttk.Frame(manage_frame)
        manage_btn_frame.pack(fill=tk.X)
        
        ttk.Button(manage_btn_frame, text="Purchase raw materials", command=self.purchase_material).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Create order", command=self.create_order).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Sales inventory", command=self.sell_inventory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="Hire workers", command=self.hire_worker).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 生产线管理
        line_frame = ttk.LabelFrame(self.scrollable_frame, text="Production line management", padding="5")
        line_frame.pack(fill=tk.X, pady=(0, 10))
        
        line_btn_frame = ttk.Frame(line_frame)
        line_btn_frame.pack(fill=tk.X)
        
        ttk.Button(line_btn_frame, text="Assign workers", command=self.assign_worker_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="Distribute products", command=self.assign_product_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="Add production line", command=self.add_production_line).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 合成站管理
        craft_frame = ttk.LabelFrame(self.scrollable_frame, text="Synthesis Station Management", padding="5")
        craft_frame.pack(fill=tk.X, pady=(0, 10))
        
        craft_btn_frame = ttk.Frame(craft_frame)
        craft_btn_frame.pack(fill=tk.X)
        
        ttk.Button(craft_btn_frame, text="Assign workers", command=self.assign_worker_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="Assign recipes", command=self.assign_recipe_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="Add synthesis station", command=self.add_crafting_station).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 进度条显示
        progress_frame = ttk.LabelFrame(self.scrollable_frame, text="Production progress", padding="5")
        progress_frame.pack(fill=tk.X)
        
        # 生产线进度条
        ttk.Label(progress_frame, text="Production line:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.progress_bars = {}
        for line in self.factory.production_lines:
            line_frame = ttk.Frame(progress_frame)
            line_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(line_frame, text=f"Production line {line.line_id}:").pack(side=tk.LEFT)
            progress_bar = ttk.Progressbar(line_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
            self.progress_bars[line.line_id] = progress_bar
            
        # 合成站进度条
        ttk.Label(progress_frame, text="Synthesis Station:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 2))
        self.craft_progress_bars = {}
        for station in self.factory.crafting_stations:
            station_frame = ttk.Frame(progress_frame)
            station_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(station_frame, text=f"{station.name}:").pack(side=tk.LEFT)
            progress_bar = ttk.Progressbar(station_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
            self.craft_progress_bars[station.station_id] = progress_bar
        
    def create_status_display(self, parent):
        """创建状态显示区域"""
        # 使用ScrolledText来支持滚动
        from tkinter.scrolledtext import ScrolledText
        
        self.status_text = ScrolledText(parent, height=20, width=60)
        self.status_text.pack(fill=tk.BOTH, expand=True)        
    def update_display(self):
        """更新显示"""
        # 更新状态文本
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, self.factory.get_status_text())
        
        # 更新生产线进度条
        for line in self.factory.production_lines:
            if line.line_id in self.progress_bars:
                progress = line.get_progress_percentage()
                self.progress_bars[line.line_id]['value'] = progress
                
        # 更新合成站进度条
        for station in self.factory.crafting_stations:
            if station.station_id in self.craft_progress_bars:
                progress = station.get_progress_percentage()
                self.craft_progress_bars[station.station_id]['value'] = progress
        
        # 如果自动模拟正在运行，安排下一次更新
        if self.simulation_running:
            speed = float(self.sim_speed.get())
            delay = int(1000 / speed)  # 转换为毫秒
            self.root.after(delay, self.auto_advance_time)
    
    def log_event(self, message):
        """记录事件到日志"""
        self.log_text.insert(tk.END, f"{self.factory.current_time.strftime('%H:%M')} - {message}\n")
        self.log_text.see(tk.END)
    
    def advance_one_hour(self):
        """推进1小时"""
        completed_products, completed_crafting, overdue_orders = self.factory.advance_time(1)
        
        for product in completed_products:
            self.log_event(f"The production of {product} has been completed!")
            
        for item, is_product in completed_crafting:
            item_type = "Product" if is_product else "Material"
            self.log_event(f"synthesized {item} {item_type}!")
            
        for order_id in overdue_orders:
            self.log_event(f"Warning: Order {order_id} is overdue!")
            
        self.update_display()
    
    def advance_eight_hours(self):
        """推进8小时"""
        for _ in range(8):
            completed_products, completed_crafting, overdue_orders = self.factory.advance_time(1)
            
            for product in completed_products:
                self.log_event(f"The production of {product} has been completed!")
                
            for item, is_product in completed_crafting:
                item_type = "Product" if is_product else "Material"
                self.log_event(f"synthesized {item} {item_type}!")
                
            for order_id in overdue_orders:
                self.log_event(f"Warning: Order {order_id} is overdue!")
                
        self.update_display()
    
    def next_day(self):
        """进入下一天"""
        success, message, daily_profit = self.factory.next_day()
        self.log_event(message)
        self.log_event(f"Yesterday's profit: ¥{daily_profit}")
        self.update_display()
    
    def toggle_auto_simulation(self):
        """切换自动模拟状态"""
        if self.simulation_running:
            self.simulation_running = False
            self.auto_btn.config(text="Start automatic simulation")
        else:
            self.simulation_running = True
            self.auto_btn.config(text="Stop automatic simulation")
            self.auto_advance_time()
    
    def auto_advance_time(self):
        """自动推进时间"""
        if self.simulation_running:
            self.advance_one_hour()
    
    def purchase_material(self):
        """购买原材料对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Purchase raw materials")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name of raw material:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
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
        """创建订单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create order")
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
        
        ttk.Label(dialog, text="Delivery days:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
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
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(dialog, text="Create order", command=do_create_order).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def sell_inventory(self):
        """销售库存对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sales inventory")
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
        
        ttk.Button(dialog, text="Sales", command=do_sell).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def hire_worker(self):
        """雇佣工人对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Hire workers")
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
        
        ttk.Label(dialog, text="Daily wage:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        salary_var = tk.StringVar(value="100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_hire():
            try:
                skill = int(skill_var.get())
                salary = float(salary_var.get())
                if not name_var.get():
                    messagebox.showerror("Error", "Please enter the worker's name!")
                    return
                    
                worker = self.factory.hire_worker(name_var.get(), skill, salary)
                self.log_event(f"Hired worker {worker.name} (Skill: {skill}, Salary: ¥{salary}/day)")
                self.update_display()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid skill level!")
        
        ttk.Button(dialog, text="Hire", command=do_hire).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_line(self):
        """分配工人到生产线对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign workers to the production line")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Worker:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Production line:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
        
        ttk.Button(dialog, text="Allocate", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_station(self):
        """分配工人到合成站对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign workers to the assembly station")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Worker:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Synthesis Station:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                messagebox.showerror("Error", "Please enter a valid synthesis station ID!")
        
        ttk.Button(dialog, text="Allocate", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_product_to_line(self):
        """分配产品到生产线对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign products to the production line")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, 
                                    values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Production line:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
        
        ttk.Button(dialog, text="distribute", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_recipe_to_station(self):
        """分配配方到合成站对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign recipe to synthesis station")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Formula type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        type_var = tk.StringVar(value="Product")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Product", "Material"])
        type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Recipe Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        recipe_var = tk.StringVar()
        
        def update_recipe_options(*args):
            if type_var.get() == "Product":
                # 只显示可合成的产品
                craftable_products = [p for p in self.factory.products.values() if p.is_craftable]
                recipe_combo['values'] = [p.name for p in craftable_products]
            else:
                # 只显示可合成的材料
                craftable_materials = [m for m in self.factory.materials.values() if m.is_craftable]
                recipe_combo['values'] = [m.name for m in craftable_materials]
        
        type_var.trace('w', update_recipe_options)
        recipe_combo = ttk.Combobox(dialog, textvariable=recipe_var)
        recipe_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        update_recipe_options()  # 初始化选项
        
        ttk.Label(dialog, text="Synthesis Station:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
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
                messagebox.showerror("Error", "Please enter a valid synthesis station ID!")
        
        ttk.Button(dialog, text="distribute", command=do_assign).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def add_production_line(self):
        """添加生产线"""
        capacity = 10  # 默认产能
        line = self.factory.add_production_line(capacity)
        self.log_event(f"Added a new production line {line.line_id} (Capacity: {capacity})")
        
        # 更新进度条显示
        self.update_progress_bars()
        self.update_display()
    
    def add_crafting_station(self):
        """添加合成站"""
        capacity = 5  # 默认产能
        station = self.factory.add_crafting_station("Synthesis Bench", capacity)
        self.log_event(f"Added a new synthesis station {station.station_id} (Capacity: {capacity})")
        
        # 更新进度条显示
        self.update_progress_bars()
        self.update_display()
    
    def update_progress_bars(self):
        """更新进度条显示"""
        # 清除现有进度条
        for widget in self.progress_bars.values():
            widget.destroy()
        for widget in self.craft_progress_bars.values():
            widget.destroy()
            
        self.progress_bars = {}
        self.craft_progress_bars = {}
        
        # 获取进度条框架
        progress_frame = self.auto_btn.master.master.master  # 获取进度条所在的框架
        
        # 重新创建生产线进度条
        ttk.Label(progress_frame, text="Production line:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        for i, line in enumerate(self.factory.production_lines):
            ttk.Label(progress_frame, text=f"Production line {line.line_id}:").grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=150, mode="determinate")
            progress_bar.grid(row=i+1, column=1, padx=5, pady=2)
            self.progress_bars[line.line_id] = progress_bar
            
        # 重新创建合成站进度条
        craft_start_row = len(self.factory.production_lines) + 2
        ttk.Label(progress_frame, text="Synthesis Station:", font=("Arial", 9, "bold")).grid(row=craft_start_row, column=0, sticky=tk.W, padx=5, pady=2)
        for i, station in enumerate(self.factory.crafting_stations):
            ttk.Label(progress_frame, text=f"{station.name}:").grid(row=craft_start_row+i+1, column=0, sticky=tk.W, padx=5, pady=2)
            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=150, mode="determinate")
            progress_bar.grid(row=craft_start_row+i+1, column=1, padx=5, pady=2)
            self.craft_progress_bars[station.station_id] = progress_bar
    
    def open_mod_creator(self):
        """打开模组制作器"""
        ModCreator(self.root, self)
    
    def import_mod(self):
        """导入模组"""
        filename = filedialog.askopenfilename(
            title="Select module file",
            filetypes=[("LAUN Mod Files", "*.launmod"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                mod = Mod.load_from_file(filename)
                self.current_mod = mod
                self.factory.load_mod(mod)
                self.mod_label.config(text=f"{mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"Mod loaded: {mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"Module Description: {mod.description}")
                self.update_progress_bars()
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load the mod: {str(e)}")
    
    def export_current_mod(self):
        """导出当前模组"""
        if not self.current_mod:
            messagebox.showwarning("Warning", "No mods loaded, unable to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save mod file",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.current_mod.save_to_file(filename)
                messagebox.showinfo("Success", f"Module has been saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Failure", f"Failed to save the mod: {str(e)}")
    
    def reset_to_default(self):
        """重置为默认模组"""
        self.setup_factory()
        self.current_mod = None
        self.mod_label.config(text="Default mod")
        self.log_event("Reset to default module")
        self.update_progress_bars()
        self.update_display()

class ModCreator:
    """模组制作器"""
    def __init__(self, parent, app):
        self.app = app
        self.mod = Mod()
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("Mod Maker")
        self.window.geometry("600x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建模组制作器界面"""
        # 创建笔记本控件
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 基本信息标签页
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Basic Information")
        self.create_info_tab(info_tab)
        
        # 原材料标签页
        material_tab = ttk.Frame(notebook)
        notebook.add(material_tab, text="Raw materials")
        self.create_material_tab(material_tab)
        
        # 产品标签页
        product_tab = ttk.Frame(notebook)
        notebook.add(product_tab, text="Product")
        self.create_product_tab(product_tab)
        
        # 合成配方标签页
        recipe_tab = ttk.Frame(notebook)
        notebook.add(recipe_tab, text="Synthesis Recipe")
        self.create_recipe_tab(recipe_tab)
        
        # 工人标签页
        worker_tab = ttk.Frame(notebook)
        notebook.add(worker_tab, text="Worker")
        self.create_worker_tab(worker_tab)
        
        # 操作按钮
        action_frame = ttk.Frame(self.window)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="Save mod", command=self.save_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Load mod", command=self.load_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Application Module", command=self.apply_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def create_info_tab(self, parent):
        """创建基本信息标签页"""
        info_frame = ttk.LabelFrame(parent, text="Mod Basic Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Module Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="describe:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.author_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Version:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(info_frame, textvariable=self.version_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="Initial capital:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.balance_var = tk.StringVar(value="10000")
        ttk.Entry(info_frame, textvariable=self.balance_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 合成站设置
        station_frame = ttk.LabelFrame(parent, text="Synthesis Station Settings", padding="10")
        station_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 合成站列表
        station_list_frame = ttk.Frame(station_frame)
        station_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.station_listbox = tk.Listbox(station_list_frame, height=4)
        station_scrollbar = ttk.Scrollbar(station_list_frame, orient="vertical", command=self.station_listbox.yview)
        self.station_listbox.configure(yscrollcommand=station_scrollbar.set)
        self.station_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        station_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 合成站按钮
        station_btn_frame = ttk.Frame(station_frame)
        station_btn_frame.pack(fill=tk.X)
        
        ttk.Button(station_btn_frame, text="Add synthesis station", command=self.add_station_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(station_btn_frame, text="Delete synthesis station", command=self.delete_station).pack(side=tk.LEFT, padx=5)
        
        info_frame.columnconfigure(1, weight=1)
        
    def create_material_tab(self, parent):
        """创建原材料标签页"""
        # 原材料列表
        material_list_frame = ttk.Frame(parent)
        material_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.material_listbox = tk.Listbox(material_list_frame)
        material_scrollbar = ttk.Scrollbar(material_list_frame, orient="vertical", command=self.material_listbox.yview)
        self.material_listbox.configure(yscrollcommand=material_scrollbar.set)
        self.material_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        material_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 原材料按钮
        material_btn_frame = ttk.Frame(parent)
        material_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(material_btn_frame, text="Add raw materials", command=self.add_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Edit raw materials", command=self.edit_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Delete raw materials", command=self.delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="Set synthesis recipe", command=self.set_material_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
        # 初始化列表
        self.update_material_list()
    
    def create_product_tab(self, parent):
        """创建产品标签页"""
        # 产品列表
        product_list_frame = ttk.Frame(parent)
        product_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.product_listbox = tk.Listbox(product_list_frame)
        product_scrollbar = ttk.Scrollbar(product_list_frame, orient="vertical", command=self.product_listbox.yview)
        self.product_listbox.configure(yscrollcommand=product_scrollbar.set)
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 产品按钮
        product_btn_frame = ttk.Frame(parent)
        product_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(product_btn_frame, text="Add Product", command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Edit Product", command=self.edit_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Delete product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="Set synthesis recipe", command=self.set_product_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
        # 初始化列表
        self.update_product_list()
    
    def create_recipe_tab(self, parent):
        """创建合成配方标签页"""
        # 配方列表
        recipe_frame = ttk.LabelFrame(parent, text="Synthesis Recipe", padding="10")
        recipe_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview来显示配方
        columns = ("Type", "Name", "Material Requirements", "Product Requirements")
        self.recipe_tree = ttk.Treeview(recipe_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.recipe_tree.heading(col, text=col)
            if col == "title":
                self.recipe_tree.column(col, width=150)
            else:
                self.recipe_tree.column(col, width=100)
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(recipe_frame, orient="vertical", command=self.recipe_tree.yview)
        self.recipe_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.recipe_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配方按钮
        recipe_btn_frame = ttk.Frame(parent)
        recipe_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(recipe_btn_frame, text="Refresh recipe list", command=self.update_recipe_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(recipe_btn_frame, text="Delete recipe", command=self.delete_recipe).pack(side=tk.LEFT, padx=5)
        
        # 初始化列表
        self.update_recipe_list()
    
    def create_worker_tab(self, parent):
        """创建工人标签页"""
        # 工人列表
        worker_list_frame = ttk.Frame(parent)
        worker_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.worker_listbox = tk.Listbox(worker_list_frame, height=15)
        worker_scrollbar = ttk.Scrollbar(worker_list_frame, orient="vertical", command=self.worker_listbox.yview)
        self.worker_listbox.configure(yscrollcommand=worker_scrollbar.set)
        self.worker_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        worker_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 工人按钮
        worker_btn_frame = ttk.Frame(parent)
        worker_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(worker_btn_frame, text="Add Worker", command=self.add_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="Editing worker", command=self.edit_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="Delete worker", command=self.delete_worker).pack(side=tk.LEFT, padx=5)
        
        # 初始化列表
        self.update_worker_list()
    
    def update_material_list(self):
        """更新原材料列表"""
        self.material_listbox.delete(0, tk.END)
        for material in self.mod.materials:
            self.material_listbox.insert(tk.END, str(material))
    
    def update_product_list(self):
        """更新产品列表"""
        self.product_listbox.delete(0, tk.END)
        for product in self.mod.products:
            self.product_listbox.insert(tk.END, str(product))
    
    def update_worker_list(self):
        """更新工人列表"""
        self.worker_listbox.delete(0, tk.END)
        for worker in self.mod.initial_workers:
            self.worker_listbox.insert(tk.END, str(worker))
    
    def update_recipe_list(self):
        """更新配方列表"""
        self.recipe_tree.delete(*self.recipe_tree.get_children())
        
        # 添加可合成的材料
        for material in self.mod.materials:
            if material.is_craftable:
                materials_str = ", ".join([f"{name}×{qty}" for name, qty in material.materials_required.items()])
                products_str = ", ".join([f"{name}×{qty}" for name, qty in material.products_required.items()])
                self.recipe_tree.insert("", "end", values=("Material", material.name, materials_str, products_str))
                
        # 添加可合成的产品
        for product in self.mod.products:
            if product.is_craftable:
                materials_str = ", ".join([f"{name}×{qty}" for name, qty in product.materials_required.items()])
                products_str = ", ".join([f"{name}×{qty}" for name, qty in product.products_required.items()])
                self.recipe_tree.insert("", "end", values=("Product", product.name, materials_str, products_str))
    
    def add_station_dialog(self):
        """添加合成站对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add synthesis station")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Synthesis Station Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value="Synthesis Bench")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Production capacity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        capacity_var = tk.StringVar(value="5")
        capacity_entry = ttk.Entry(dialog, textvariable=capacity_var)
        capacity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def add_station():
            try:
                name = name_var.get()
                capacity = int(capacity_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter the name of the synthesis station!")
                    return
                
                self.mod.crafting_stations.append({"name": name, "capacity": capacity})
                self.station_listbox.insert(tk.END, f"{name} (Production capacity:{capacity})")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid capacity!")
        
        ttk.Button(dialog, text="Add", command=add_station).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_station(self):
        """删除合成站"""
        selection = self.station_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a synthesis station first!")
            return
            
        index = selection[0]
        self.mod.crafting_stations.pop(index)
        self.station_listbox.delete(index)
    
    def add_material_dialog(self):
        """添加原材料对话框"""
        self.material_dialog("Add raw materials")
    
    def edit_material_dialog(self):
        """编辑原材料对话框"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a raw material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.material_dialog("Edit raw materials", material, index)
    
    def material_dialog(self, title, material=None, index=None):
        """原材料对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name of raw material:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=material.name if material else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Unit price:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        cost_var = tk.StringVar(value=material.cost if material else "1")
        cost_entry = ttk.Entry(dialog, textvariable=cost_var)
        cost_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="unit:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
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
                    messagebox.showerror("Error", "Please enter the name of the raw material!")
                    return
                
                new_material = Material(name, cost, unit)
                
                if material:  # 编辑模式
                    # 更新初始库存
                    if material.name in self.mod.initial_materials:
                        del self.mod.initial_materials[material.name]
                    self.mod.initial_materials[name] = quantity
                    
                    # 保留合成配方
                    new_material.is_craftable = material.is_craftable
                    new_material.materials_required = material.materials_required.copy()
                    new_material.products_required = material.products_required.copy()
                    
                    self.mod.materials[index] = new_material
                else:  # 添加模式
                    self.mod.initial_materials[name] = quantity
                    self.mod.materials.append(new_material)
                
                self.update_material_list()
                self.update_recipe_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
        
        ttk.Button(dialog, text="Save", command=save_material).grid(row=4, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_material_recipe_dialog(self):
        """设置材料合成配方对话框"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a raw material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.recipe_dialog("Set material synthesis recipe", material, False)
    
    def add_product_dialog(self):
        """添加产品对话框"""
        self.product_dialog("Add Product")
    
    def edit_product_dialog(self):
        """编辑产品对话框"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.product_dialog("Edit Product", product, index)
    
    def product_dialog(self, title, product=None, index=None):
        """产品对话框"""
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
        
        ttk.Label(dialog, text="Sales price:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        price_var = tk.StringVar(value=product.sale_price if product else "20")
        price_entry = ttk.Entry(dialog, textvariable=price_var)
        price_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_product():
            try:
                name = name_var.get()
                production_time = int(time_var.get())
                sale_price = float(price_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter the product name!")
                    return
                
                new_product = Product(name, production_time, sale_price)
                
                if product:  # 编辑模式
                    # 保留材料需求和合成配方
                    new_product.materials_required = product.materials_required.copy()
                    new_product.products_required = product.products_required.copy()
                    new_product.is_craftable = product.is_craftable
                    
                    self.mod.products[index] = new_product
                else:  # 添加模式
                    self.mod.products.append(new_product)
                
                self.update_product_list()
                self.update_recipe_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
        
        ttk.Button(dialog, text="Save", command=save_product).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_product_recipe_dialog(self):
        """设置产品合成配方对话框"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.recipe_dialog("Set product synthesis recipe", product, True)
    
    def recipe_dialog(self, title, item, is_product):
        """合成配方对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("500x640")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 基本信息
        info_frame = ttk.LabelFrame(dialog, text="Basic Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        item_type = "Product" if is_product else "Material"
        ttk.Label(info_frame, text=f"{item_type}Name: {item.name}").pack(anchor=tk.W)
        
        # 材料需求
        materials_frame = ttk.LabelFrame(dialog, text="Material Requirements", padding="10")
        materials_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 材料需求列表
        materials_list_frame = ttk.Frame(materials_frame)
        materials_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview来显示材料需求
        columns = ("Meterial", "Quantity")
        self.materials_tree = ttk.Treeview(materials_list_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题
        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(materials_list_frame, orient="vertical", command=self.materials_tree.yview)
        self.materials_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 材料需求按钮
        materials_btn_frame = ttk.Frame(materials_frame)
        materials_btn_frame.pack(fill=tk.X)
        
        ttk.Button(materials_btn_frame, text="Add material requirements", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "material")).pack(side=tk.LEFT, padx=5)
        ttk.Button(materials_btn_frame, text="Delete material request", 
                  command=lambda: self.delete_requirement(self.materials_tree)).pack(side=tk.LEFT, padx=5)
        
        # 产品需求
        products_frame = ttk.LabelFrame(dialog, text="Product Requirements", padding="10")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 产品需求列表
        products_list_frame = ttk.Frame(products_frame)
        products_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview来显示产品需求
        columns = ("Product", "Quantity")
        self.products_tree = ttk.Treeview(products_list_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # 添加滚动条
        tree_scrollbar2 = ttk.Scrollbar(products_list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=tree_scrollbar2.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 产品需求按钮
        products_btn_frame = ttk.Frame(products_frame)
        products_btn_frame.pack(fill=tk.X)
        
        ttk.Button(products_btn_frame, text="Add product requirements", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "product")).pack(side=tk.LEFT, padx=5)
        ttk.Button(products_btn_frame, text="Delete product requirements", 
                  command=lambda: self.delete_requirement(self.products_tree)).pack(side=tk.LEFT, padx=5)
        
        # 加载现有需求
        for material_name, quantity in item.materials_required.items():
            self.materials_tree.insert("", "end", values=(material_name, quantity))
            
        for product_name, quantity in item.products_required.items():
            self.products_tree.insert("", "end", values=(product_name, quantity))
        
        # 按钮框架
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_recipe():
            # 更新材料需求
            item.materials_required.clear()
            for material_item in self.materials_tree.get_children():
                values = self.materials_tree.item(material_item, "values")
                material_name = values[0]
                quantity = int(values[1])
                item.add_material_requirement(material_name, quantity)
                
            # 更新产品需求
            item.products_required.clear()
            for product_item in self.products_tree.get_children():
                values = self.products_tree.item(product_item, "values")
                product_name = values[0]
                quantity = int(values[1])
                item.add_product_requirement(product_name, quantity)
                
            # 标记为可合成
            item.is_craftable = True
            
            if is_product:
                self.update_product_list()
            else:
                self.update_material_list()
            self.update_recipe_list()
            
            messagebox.showinfo("Success", "The synthesis formula has been saved!")
        
        def save_and_close():
            save_recipe()
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save recipe", command=save_recipe).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save the recipe and close this window", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close this window", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def add_requirement_dialog(self, parent_dialog, item, requirement_type):
        """添加需求对话框"""
        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Add {requirement_type} requirement")
        dialog.geometry("300x150")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        requirement_name = "Meterial" if requirement_type == "material" else "Product"
        
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
                    messagebox.showerror("Error", f"Please select{requirement_name}!")
                    return
                
                # 检查是否已存在该需求
                if requirement_type == "material":
                    tree = self.materials_tree
                else:
                    tree = self.products_tree
                    
                for tree_item in tree.get_children():
                    values = tree.item(tree_item, "values")
                    if values[0] == name:
                        messagebox.showwarning("Warning", f"The {requirement_name} requirement already exists!")
                        return
                
                # 添加到列表
                tree.insert("", "end", values=(name, quantity))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(dialog, text="Add", command=add_requirement).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_requirement(self, tree):
        """删除需求"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a requirement first!")
            return
            
        for item in selection:
            tree.delete(item)
    
    def delete_material(self):
        """删除原材料"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a raw material first!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        
        # 删除初始库存
        if material.name in self.mod.initial_materials:
            del self.mod.initial_materials[material.name]
            
        self.mod.materials.pop(index)
        self.update_material_list()
        self.update_recipe_list()
    
    def delete_product(self):
        """删除产品"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
            
        index = selection[0]
        self.mod.products.pop(index)
        self.update_product_list()
        self.update_recipe_list()
    
    def delete_recipe(self):
        """删除配方"""
        selection = self.recipe_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recipe first!")
            return
            
        for item in selection:
            values = self.recipe_tree.item(item, "values")
            item_type, name = values[0], values[1]
            
            if item_type == "Meterial":
                # 找到对应的材料并清除合成配方
                for material in self.mod.materials:
                    if material.name == name:
                        material.is_craftable = False
                        material.materials_required.clear()
                        material.products_required.clear()
                        break
                self.update_material_list()
            else:
                # 找到对应的产品并清除合成配方
                for product in self.mod.products:
                    if product.name == name:
                        product.is_craftable = False
                        product.products_required.clear()
                        # 注意：不清除材料需求，因为产品可能还需要材料生产
                        break
                self.update_product_list()
                
            self.recipe_tree.delete(item)
    
    def add_worker_dialog(self):
        """添加工人对话框"""
        self.worker_dialog("Add Worker")
    
    def edit_worker_dialog(self):
        """编辑工人对话框"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker first!")
            return
            
        index = selection[0]
        worker = self.mod.initial_workers[index]
        self.worker_dialog("Edit Worker", worker, index)
    
    def worker_dialog(self, title, worker=None, index=None):
        """工人对话框"""
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
        
        ttk.Label(dialog, text="Daily wage:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        salary_var = tk.StringVar(value=worker.salary if worker else "100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_worker():
            try:
                name = name_var.get()
                skill_level = int(skill_var.get())
                salary = float(salary_var.get())
                
                if not name:
                    messagebox.showerror("Error", "Please enter the worker's name!")
                    return
                
                new_worker = Worker(name, skill_level, salary)
                
                if worker:  # 编辑模式
                    self.mod.initial_workers[index] = new_worker
                else:  # 添加模式
                    self.mod.initial_workers.append(new_worker)
                
                self.update_worker_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
        
        ttk.Button(dialog, text="Save", command=save_worker).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_worker(self):
        """删除工人"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker first!")
            return
            
        index = selection[0]
        self.mod.initial_workers.pop(index)
        self.update_worker_list()
    
    def save_mod(self):
        """保存模组"""
        # 更新模组基本信息
        self.mod.name = self.name_var.get()
        self.mod.description = self.desc_var.get()
        self.mod.author = self.author_var.get()
        self.mod.version = self.version_var.get()
        
        try:
            self.mod.initial_balance = float(self.balance_var.get())
        except ValueError:
            messagebox.showerror("Error", "The initial funds must be a valid number!")
            return
        
        if not self.mod.name:
            messagebox.showerror("Error", "Please enter the module name!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save mod file",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.mod.save_to_file(filename)
                messagebox.showinfo("Success", f"Module has been saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Failure", f"Failed to save the mod: {str(e)}")
    
    def load_mod(self):
        """加载模组"""
        filename = filedialog.askopenfilename(
            title="Select module file",
            filetypes=[("LAUN Mod Files", "*.launmod"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.mod = Mod.load_from_file(filename)
                
                # 更新界面
                self.name_var.set(self.mod.name)
                self.desc_var.set(self.mod.description)
                self.author_var.set(self.mod.author)
                self.version_var.set(self.mod.version)
                self.balance_var.set(str(self.mod.initial_balance))
                
                # 更新合成站列表
                self.station_listbox.delete(0, tk.END)
                for station in self.mod.crafting_stations:
                    self.station_listbox.insert(tk.END, f"{station['name']} (Production capacity:{station['capacity']})")
                
                self.update_material_list()
                self.update_product_list()
                self.update_worker_list()
                self.update_recipe_list()
                
                messagebox.showinfo("Success", f"Mod loaded: {self.mod.name}")
            except Exception as e:
                messagebox.showerror("Failure", f"Failed to load the mod: {str(e)}")
    
    def apply_mod(self):
        """应用模组到游戏"""
        # 更新模组基本信息
        self.mod.name = self.name_var.get()
        self.mod.description = self.desc_var.get()
        self.mod.author = self.author_var.get()
        self.mod.version = self.version_var.get()
        
        try:
            self.mod.initial_balance = float(self.balance_var.get())
        except ValueError:
            messagebox.showerror("Error", "The initial capital must be a valid number!")
            return
        
        if not self.mod.name:
            messagebox.showerror("Error", "Please enter the module name!")
            return
        
        self.app.current_mod = self.mod
        self.app.factory.load_mod(self.mod)
        self.app.mod_label.config(text=f"{self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"Mod loaded: {self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"Module Description: {self.mod.description}")
        self.app.update_progress_bars()
        self.app.update_display()
        
        messagebox.showinfo("Success", "The mod has been applied to the game!")
        self.window.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = FactorySimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
