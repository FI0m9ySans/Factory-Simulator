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
            return f"{self.name} (售价:¥{self.sale_price}, 生产时间:{self.production_time}分钟, 材料:{materials_str}, 组件:{products_str})"
        elif materials_str:
            return f"{self.name} (售价:¥{self.sale_price}, 生产时间:{self.production_time}分钟, 材料:{materials_str})"
        elif products_str:
            return f"{self.name} (售价:¥{self.sale_price}, 生产时间:{self.production_time}分钟, 组件:{products_str})"
        else:
            return f"{self.name} (售价:¥{self.sale_price}, 生产时间:{self.production_time}分钟)"

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
                return f"{self.name} (¥{self.cost}/{self.unit}, 可合成, 材料:{materials_str}, 组件:{products_str})"
            elif materials_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, 可合成, 材料:{materials_str})"
            elif products_str:
                return f"{self.name} (¥{self.cost}/{self.unit}, 可合成, 组件:{products_str})"
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
        status = "运行中" if self.is_active else "停止"
        recipe_name = self.current_recipe if self.current_recipe else "无"
        recipe_type = "产品" if self.is_recipe_product else "材料"
        worker_name = self.assigned_worker.name if self.assigned_worker else "无"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"{self.name} {self.station_id} (状态:{status}, 配方:{recipe_name}({recipe_type}), 工人:{worker_name}, 进度:{progress})"

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
        status = "工作中" if self.is_working else "空闲"
        return f"{self.name} (技能:{self.skill_level}, 薪资:¥{self.salary}/天, 状态:{status})"

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
        status = "运行中" if self.is_active else "停止"
        product_name = self.current_product.name if self.current_product else "无"
        worker_name = self.assigned_worker.name if self.assigned_worker else "无"
        progress = f"{self.get_progress_percentage()}%"
        
        return f"生产线 {self.line_id} (状态:{status}, 产品:{product_name}, 工人:{worker_name}, 进度:{progress})"

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
        status = "已完成" if self.is_completed else "进行中"
        return f"订单 #{self.order_id}: {self.product.name} x{self.quantity} (截止:{self.deadline.strftime('%Y-%m-%d %H:%M')}, 状态:{status})"

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
        self.initial_balance = 0
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
        mod.initial_balance = data.get("initial_balance", 0)
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
            return False, f"错误: 原材料 {material_name} 不存在!"
            
        material = self.materials[material_name]
        cost = material.cost * quantity
        
        if cost > self.balance:
            return False, f"错误: 资金不足! 需要 ¥{cost}, 当前余额 ¥{self.balance}"
            
        self.balance -= cost
        self.material_inventory[material_name] += quantity
        self.daily_costs += cost
        return True, f"购买了 {quantity}{material.unit} {material_name}, 花费 ¥{cost}"
        
    def create_order(self, product_name: str, quantity: int, days_until_deadline: int):
        """创建订单"""
        if product_name not in self.products:
            return None, f"错误: 产品 {product_name} 不存在!"
            
        product = self.products[product_name]
        deadline = self.current_time + timedelta(days=days_until_deadline)
        order_id = len(self.orders) + 1
        new_order = Order(order_id, product, quantity, deadline)
        self.orders.append(new_order)
        return new_order, f"创建了新订单: {new_order}"
        
    def assign_worker_to_line(self, worker_name: str, line_id: int):
        """分配工人到生产线"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        
        if not worker:
            return False, f"错误: 工人 {worker_name} 不存在!"
            
        if not line:
            return False, f"错误: 生产线 {line_id} 不存在!"
            
        # 如果工人已经在其他生产线上工作，先解除分配
        for other_line in self.production_lines:
            if other_line.assigned_worker == worker:
                other_line.assigned_worker = None
                other_line.is_active = False
                
        line.assign_worker(worker)
        return True, f"工人 {worker_name} 被分配到生产线 {line_id}"
        
    def assign_worker_to_station(self, worker_name: str, station_id: int):
        """分配工人到合成站"""
        worker = next((w for w in self.workers if w.name == worker_name), None)
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        
        if not worker:
            return False, f"错误: 工人 {worker_name} 不存在!"
            
        if not station:
            return False, f"错误: 合成站 {station_id} 不存在!"
            
        # 如果工人已经在其他合成站工作，先解除分配
        for other_station in self.crafting_stations:
            if other_station.assigned_worker == worker:
                other_station.assigned_worker = None
                other_station.is_active = False
                
        station.assign_worker(worker)
        return True, f"工人 {worker_name} 被分配到合成站 {station_id}"
        
    def assign_product_to_line(self, product_name: str, line_id: int):
        """分配产品到生产线"""
        if product_name not in self.products:
            return False, f"错误: 产品 {product_name} 不存在!"
            
        line = next((l for l in self.production_lines if l.line_id == line_id), None)
        if not line:
            return False, f"错误: 生产线 {line_id} 不存在!"
            
        if not line.assigned_worker:
            return False, f"错误: 生产线 {line_id} 没有分配工人!"
            
        product = self.products[product_name]
        
        # 检查所有所需原材料是否足够
        for material_name, quantity in product.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"错误: {material_name} 不足! 需要 {quantity}, 当前库存 {self.material_inventory.get(material_name, 0)}"
            
        # 检查所有所需产品是否足够
        for product_name_req, quantity in product.products_required.items():
            if self.product_inventory.get(product_name_req, 0) < quantity:
                return False, f"错误: {product_name_req} 不足! 需要 {quantity}, 当前库存 {self.product_inventory.get(product_name_req, 0)}"
            
        # 消耗所有所需原材料
        for material_name, quantity in product.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # 消耗所有所需产品
        for product_name_req, quantity in product.products_required.items():
            self.product_inventory[product_name_req] -= quantity
            
        line.assign_product(product)
        return True, f"生产线 {line_id} 开始生产 {product_name}"
        
    def assign_recipe_to_station(self, recipe_name: str, is_product: bool, station_id: int):
        """分配合成配方到合成站"""
        station = next((s for s in self.crafting_stations if s.station_id == station_id), None)
        if not station:
            return False, f"错误: 合成站 {station_id} 不存在!"
            
        if not station.assigned_worker:
            return False, f"错误: 合成站 {station_id} 没有分配工人!"
            
        # 检查配方是否存在
        if is_product:
            if recipe_name not in self.products:
                return False, f"错误: 产品 {recipe_name} 不存在!"
            recipe = self.products[recipe_name]
        else:
            if recipe_name not in self.materials:
                return False, f"错误: 原材料 {recipe_name} 不存在!"
            recipe = self.materials[recipe_name]
            
        # 检查是否是可合成物品
        if not recipe.is_craftable:
            return False, f"错误: {recipe_name} 不可合成!"
            
        # 检查所有所需原材料是否足够
        for material_name, quantity in recipe.materials_required.items():
            if self.material_inventory.get(material_name, 0) < quantity:
                return False, f"错误: {material_name} 不足! 需要 {quantity}, 当前库存 {self.material_inventory.get(material_name, 0)}"
            
        # 检查所有所需产品是否足够
        for product_name, quantity in recipe.products_required.items():
            if self.product_inventory.get(product_name, 0) < quantity:
                return False, f"错误: {product_name} 不足! 需要 {quantity}, 当前库存 {self.product_inventory.get(product_name, 0)}"
            
        # 消耗所有所需原材料
        for material_name, quantity in recipe.materials_required.items():
            self.material_inventory[material_name] -= quantity
            
        # 消耗所有所需产品
        for product_name, quantity in recipe.products_required.items():
            self.product_inventory[product_name] -= quantity
            
        station.assign_recipe(recipe_name, is_product)
        return True, f"合成站 {station_id} 开始合成 {recipe_name}"
        
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
            return False, f"错误: 产品 {product_name} 不存在!"
            
        if self.product_inventory[product_name] < quantity:
            return False, f"错误: 库存不足! {product_name} 只有 {self.product_inventory[product_name]} 件"
            
        product = self.products[product_name]
        income = product.sale_price * quantity
        self.product_inventory[product_name] -= quantity
        self.balance += income
        self.daily_income += income
        return True, f"售出 {quantity} 件 {product_name}, 获得收入 ¥{income}"
        
    def pay_workers(self):
        """支付工人工资"""
        total_salary = sum(worker.salary for worker in self.workers)
        if total_salary > self.balance:
            return False, f"警告: 资金不足支付工人工资! 需要 ¥{total_salary}, 当前余额 ¥{self.balance}"
            
        self.balance -= total_salary
        self.daily_costs += total_salary
        return True, f"支付了工人工资 ¥{total_salary}"
        
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
        status_text = f"=== {self.name} 状态 (第 {self.day} 天) ===\n"
        status_text += f"资金: ¥{self.balance}\n"
        status_text += f"时间: {self.current_time.strftime('%Y-%m-%d %H:%M')}\n"
        
        status_text += "\n--- 生产线 ---\n"
        for line in self.production_lines:
            status_text += f"  {line}\n"
            
        status_text += "\n--- 合成站 ---\n"
        for station in self.crafting_stations:
            status_text += f"  {station}\n"
            
        status_text += "\n--- 工人 ---\n"
        for worker in self.workers:
            status_text += f"  {worker}\n"
            
        status_text += "\n--- 原材料库存 ---\n"
        for material, quantity in self.material_inventory.items():
            unit = self.materials[material].unit if material in self.materials else "单位"
            status_text += f"  {material}: {quantity}{unit}\n"
            
        status_text += "\n--- 产品库存 ---\n"
        for product, quantity in self.product_inventory.items():
            status_text += f"  {product}: {quantity}件\n"
            
        status_text += "\n--- 订单 ---\n"
        for order in self.orders:
            status = "已完成" if order.is_completed else "进行中"
            overdue = " (逾期!)" if order.is_overdue(self.current_time) else ""
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
        self.root.title("加工厂模拟器 - 合成系统版")
        self.root.geometry("1200x800")
        
        # 创建工厂实例
        self.factory = Factory("高效加工厂", initial_balance=240)
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
        self.window.title("设置")
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
        resolution_frame = ttk.LabelFrame(main_frame, text="分辨率设置", padding="10")
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="选择分辨率:").pack(anchor=tk.W, pady=5)
        
        self.resolution_var = tk.StringVar(value=self.app.resolution_config.current_resolution)
        resolution_combo = ttk.Combobox(
            resolution_frame, 
            textvariable=self.resolution_var,
            values=self.app.resolution_config.get_available_resolutions(),
            state="readonly"
        )
        resolution_combo.pack(fill=tk.X, pady=5)
        
        # 窗口模式
        window_frame = ttk.LabelFrame(main_frame, text="窗口模式", padding="10")
        window_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.window_mode_var = tk.StringVar(value=self.app.window_mode)
        ttk.Radiobutton(
            window_frame, 
            text="窗口模式", 
            variable=self.window_mode_var, 
            value="windowed"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            window_frame, 
            text="全屏模式", 
            variable=self.window_mode_var, 
            value="fullscreen"
        ).pack(anchor=tk.W, pady=2)
        
        # 缩放设置
        scale_frame = ttk.LabelFrame(main_frame, text="界面缩放", padding="10")
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
        
        scale_value_label = ttk.Label(scale_frame, text=f"缩放因子: {self.scale_var.get():.1f}")
        scale_value_label.pack(anchor=tk.W)
        
        def update_scale_label(*args):
            scale_value_label.config(text=f"缩放因子: {self.scale_var.get():.1f}")
        
        self.scale_var.trace('w', update_scale_label)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="应用设置", 
            command=self.apply_settings
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="恢复默认", 
            command=self.reset_to_default
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="取消", 
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
        
        messagebox.showinfo("成功", "设置已应用，部分设置需要重启程序才能完全生效。")
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
        self.root.title("加工厂模拟器 - 合成系统版")
        
        # 初始化分辨率配置
        self.resolution_config = ResolutionConfig()
        self.window_mode = "windowed"  # windowed 或 fullscreen
        self.scale_factor = 1.0
        
        # 设置窗口初始大小和位置
        self.setup_window()
        
        # 创建工厂实例
        self.factory = Factory("高效加工厂", initial_balance=420)
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
        self.factory.add_material("木材", cost=1, unit="单位", initial_quantity=100)
        self.factory.add_material("金属", cost=2, unit="单位", initial_quantity=50)
        self.factory.add_material("塑料", cost=0.5, unit="单位", initial_quantity=200)
        self.factory.add_material("螺丝", cost=0.1, unit="个", initial_quantity=500)
        
        # 添加产品
        chair = Product("木椅", production_time=60, sale_price=20)
        chair.add_material_requirement("木材", 5)
        self.factory.add_product(chair)
        
        table = Product("木桌", production_time=120, sale_price=40)
        table.add_material_requirement("木材", 10)
        self.factory.add_product(table)
        
        cabinet = Product("木柜", production_time=180, sale_price=60)
        cabinet.add_material_requirement("木材", 15)
        cabinet.add_material_requirement("金属", 2)
        self.factory.add_product(cabinet)
        
        # 添加可合成的产品和材料
        # 合成材料：金属板（由2金属合成）
        metal_plate = Material("金属板", cost=3, unit="块")
        metal_plate.add_material_requirement("金属", 2)
        self.factory.add_material(metal_plate.name, metal_plate.cost, metal_plate.unit, 0)
        self.factory.materials["金属板"].is_craftable = True
        self.factory.materials["金属板"].materials_required = metal_plate.materials_required.copy()
        
        # 合成产品：高级椅子（由木椅和金属板合成）
        premium_chair = Product("高级椅子", production_time=90, sale_price=50)
        premium_chair.add_product_requirement("木椅", 1)
        premium_chair.add_material_requirement("金属板", 1)
        premium_chair.add_material_requirement("螺丝", 4)
        self.factory.add_product(premium_chair)
        
        # 添加生产线
        self.factory.add_production_line(capacity=10)
        self.factory.add_production_line(capacity=10)
        
        # 添加合成站
        self.factory.add_crafting_station("基础合成台", capacity=5)
        self.factory.add_crafting_station("高级合成台", capacity=3)
        
        # 雇佣工人
        
        # 分配工人到生产线和合成站
        
        # 创建订单

        
        # 购买更多原材料
        self.factory.purchase_material("木材", 200)
        self.factory.purchase_material("金属", 50)
        self.factory.purchase_material("螺丝", 200)
        
        # 开始生产
        self.factory.assign_product_to_line("木椅", 1)
        self.factory.assign_product_to_line("木桌", 2)
        
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
        title_label = ttk.Label(main_frame, text="加工厂模拟器 - 合成系统版", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 创建左右分栏的框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(content_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 右侧状态显示
        status_frame = ttk.LabelFrame(content_frame, text="工厂状态", padding="10")
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 控制面板内容
        self.create_control_panel(control_frame)
        
        # 状态显示内容
        self.create_status_display(status_frame)
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="事件日志", padding="10")
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
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存游戏", command=self.save_game)
        file_menu.add_command(label="加载游戏", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="显示设置", command=self.open_settings)
        settings_menu.add_separator()
        
        # 分辨率子菜单
        resolution_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="分辨率", menu=resolution_menu)
        
        for resolution in self.resolution_config.get_available_resolutions():
            resolution_menu.add_command(
                label=resolution, 
                command=lambda r=resolution: self.change_resolution(r)
            )
        
        # 窗口模式子菜单
        window_mode_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="窗口模式", menu=window_mode_menu)
        window_mode_menu.add_command(
            label="窗口模式", 
            command=lambda: self.set_window_mode("windowed")
        )
        window_mode_menu.add_command(
            label="全屏模式", 
            command=lambda: self.set_window_mode("fullscreen")
        )
        
        # 模组菜单
        mod_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模组", menu=mod_menu)
        mod_menu.add_command(label="模组制作器", command=self.open_mod_creator)
        mod_menu.add_command(label="导入模组", command=self.import_mod)
        mod_menu.add_command(label="导出当前模组", command=self.export_current_mod)
        mod_menu.add_separator()
        mod_menu.add_command(label="重置为默认", command=self.reset_to_default)
        
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
            title="保存游戏",
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
                    
                messagebox.showinfo("成功", f"游戏已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存游戏失败: {str(e)}")
                
    def load_game(self):
        """加载游戏"""
        filename = filedialog.askopenfilename(
            title="加载游戏",
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
                messagebox.showinfo("成功", f"游戏已从 {filename} 加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载游戏失败: {str(e)}")
    
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
        mod_frame = ttk.LabelFrame(self.scrollable_frame, text="当前模组", padding="5")
        mod_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mod_label = ttk.Label(mod_frame, text="")
        self.mod_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 时间控制
        time_frame = ttk.LabelFrame(self.scrollable_frame, text="时间控制", padding="5")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        time_btn_frame = ttk.Frame(time_frame)
        time_btn_frame.pack(fill=tk.X)
        
        ttk.Button(time_btn_frame, text="推进1小时", command=self.advance_one_hour).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="推进8小时", command=self.advance_eight_hours).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(time_btn_frame, text="下一天", command=self.next_day).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 自动模拟控制
        auto_frame = ttk.LabelFrame(self.scrollable_frame, text="自动模拟", padding="5")
        auto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sim_speed = tk.StringVar(value="1")
        speed_frame = ttk.Frame(auto_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="速度:").pack(side=tk.LEFT)
        ttk.Radiobutton(speed_frame, text="慢", variable=self.sim_speed, value="0.5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="正常", variable=self.sim_speed, value="1").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(speed_frame, text="快", variable=self.sim_speed, value="2").pack(side=tk.LEFT, padx=5)
        
        self.auto_btn = ttk.Button(auto_frame, text="开始自动模拟", command=self.toggle_auto_simulation)
        self.auto_btn.pack(fill=tk.X, pady=5)
        
        # 工厂管理
        manage_frame = ttk.LabelFrame(self.scrollable_frame, text="工厂管理", padding="5")
        manage_frame.pack(fill=tk.X, pady=(0, 10))
        
        manage_btn_frame = ttk.Frame(manage_frame)
        manage_btn_frame.pack(fill=tk.X)
        
        ttk.Button(manage_btn_frame, text="购买原材料", command=self.purchase_material).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="创建订单", command=self.create_order).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="销售库存", command=self.sell_inventory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(manage_btn_frame, text="雇佣工人", command=self.hire_worker).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 生产线管理
        line_frame = ttk.LabelFrame(self.scrollable_frame, text="生产线管理", padding="5")
        line_frame.pack(fill=tk.X, pady=(0, 10))
        
        line_btn_frame = ttk.Frame(line_frame)
        line_btn_frame.pack(fill=tk.X)
        
        ttk.Button(line_btn_frame, text="分配工人", command=self.assign_worker_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="分配产品", command=self.assign_product_to_line).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(line_btn_frame, text="添加生产线", command=self.add_production_line).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 合成站管理
        craft_frame = ttk.LabelFrame(self.scrollable_frame, text="合成站管理", padding="5")
        craft_frame.pack(fill=tk.X, pady=(0, 10))
        
        craft_btn_frame = ttk.Frame(craft_frame)
        craft_btn_frame.pack(fill=tk.X)
        
        ttk.Button(craft_btn_frame, text="分配工人", command=self.assign_worker_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="分配配方", command=self.assign_recipe_to_station).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(craft_btn_frame, text="添加合成站", command=self.add_crafting_station).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 进度条显示
        progress_frame = ttk.LabelFrame(self.scrollable_frame, text="生产进度", padding="5")
        progress_frame.pack(fill=tk.X)
        
        # 生产线进度条
        ttk.Label(progress_frame, text="生产线:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.progress_bars = {}
        for line in self.factory.production_lines:
            line_frame = ttk.Frame(progress_frame)
            line_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(line_frame, text=f"生产线 {line.line_id}:").pack(side=tk.LEFT)
            progress_bar = ttk.Progressbar(line_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
            self.progress_bars[line.line_id] = progress_bar
            
        # 合成站进度条
        ttk.Label(progress_frame, text="合成站:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 2))
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
            self.log_event(f"完成了 {product} 的生产!")
            
        for item, is_product in completed_crafting:
            item_type = "产品" if is_product else "材料"
            self.log_event(f"合成了 {item} {item_type}!")
            
        for order_id in overdue_orders:
            self.log_event(f"警告: 订单 {order_id} 已逾期!")
            
        self.update_display()
    
    def advance_eight_hours(self):
        """推进8小时"""
        for _ in range(8):
            completed_products, completed_crafting, overdue_orders = self.factory.advance_time(1)
            
            for product in completed_products:
                self.log_event(f"完成了 {product} 的生产!")
                
            for item, is_product in completed_crafting:
                item_type = "产品" if is_product else "材料"
                self.log_event(f"合成了 {item} {item_type}!")
                
            for order_id in overdue_orders:
                self.log_event(f"警告: 订单 {order_id} 已逾期!")
                
        self.update_display()
    
    def next_day(self):
        """进入下一天"""
        success, message, daily_profit = self.factory.next_day()
        self.log_event(message)
        self.log_event(f"昨日利润: ¥{daily_profit}")
        self.update_display()
    
    def toggle_auto_simulation(self):
        """切换自动模拟状态"""
        if self.simulation_running:
            self.simulation_running = False
            self.auto_btn.config(text="开始自动模拟")
        else:
            self.simulation_running = True
            self.auto_btn.config(text="停止自动模拟")
            self.auto_advance_time()
    
    def auto_advance_time(self):
        """自动推进时间"""
        if self.simulation_running:
            self.advance_one_hour()
    
    def purchase_material(self):
        """购买原材料对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("购买原材料")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="原材料名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        material_var = tk.StringVar(value=list(self.factory.materials.keys())[0] if self.factory.materials else "")
        material_combo = ttk.Combobox(dialog, textvariable=material_var, values=list(self.factory.materials.keys()))
        material_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="数量:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数量!")
        
        ttk.Button(dialog, text="购买", command=do_purchase).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def create_order(self):
        """创建订单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("创建订单")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="产品:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="数量:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar(value="5")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="交货天数:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字!")
        
        ttk.Button(dialog, text="创建订单", command=do_create_order).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def sell_inventory(self):
        """销售库存对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("销售库存")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="产品:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="数量:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数量!")
        
        ttk.Button(dialog, text="销售", command=do_sell).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def hire_worker(self):
        """雇佣工人对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("雇佣工人")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="技能等级 (1-5):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        skill_var = tk.StringVar(value="3")
        skill_entry = ttk.Entry(dialog, textvariable=skill_var)
        skill_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="日薪:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        salary_var = tk.StringVar(value="100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_hire():
            try:
                skill = int(skill_var.get())
                salary = float(salary_var.get())
                if not name_var.get():
                    messagebox.showerror("错误", "请输入工人姓名!")
                    return
                    
                worker = self.factory.hire_worker(name_var.get(), skill, salary)
                self.log_event(f"雇佣了工人 {worker.name} (技能:{skill}, 薪资:¥{salary}/天)")
                self.update_display()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字!")
        
        ttk.Button(dialog, text="雇佣", command=do_hire).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_line(self):
        """分配工人到生产线对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("分配工人到生产线")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="工人:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="生产线:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的生产线ID!")
        
        ttk.Button(dialog, text="分配", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_worker_to_station(self):
        """分配工人到合成站对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("分配工人到合成站")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="工人:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        worker_var = tk.StringVar()
        worker_combo = ttk.Combobox(dialog, textvariable=worker_var, 
                                   values=[w.name for w in self.factory.workers])
        worker_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="合成站:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的合成站ID!")
        
        ttk.Button(dialog, text="分配", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_product_to_line(self):
        """分配产品到生产线对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("分配产品到生产线")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="产品:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var, 
                                    values=list(self.factory.products.keys()))
        product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="生产线:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
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
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的生产线ID!")
        
        ttk.Button(dialog, text="分配", command=do_assign).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def assign_recipe_to_station(self):
        """分配配方到合成站对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("分配配方到合成站")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="配方类型:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        type_var = tk.StringVar(value="产品")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["产品", "材料"])
        type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="配方名称:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        recipe_var = tk.StringVar()
        
        def update_recipe_options(*args):
            if type_var.get() == "产品":
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
        
        ttk.Label(dialog, text="合成站:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        station_var = tk.StringVar()
        station_combo = ttk.Combobox(dialog, textvariable=station_var, 
                                   values=[s.station_id for s in self.factory.crafting_stations])
        station_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def do_assign():
            try:
                station_id = int(station_var.get())
                is_product = (type_var.get() == "产品")
                success, message = self.factory.assign_recipe_to_station(recipe_var.get(), is_product, station_id)
                if success:
                    self.log_event(message)
                    self.update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", message)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的合成站ID!")
        
        ttk.Button(dialog, text="分配", command=do_assign).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def add_production_line(self):
        """添加生产线"""
        capacity = 10  # 默认产能
        line = self.factory.add_production_line(capacity)
        self.log_event(f"添加了新的生产线 {line.line_id} (产能:{capacity})")
        
        # 更新进度条显示
        self.update_progress_bars()
        self.update_display()
    
    def add_crafting_station(self):
        """添加合成站"""
        capacity = 5  # 默认产能
        station = self.factory.add_crafting_station("合成台", capacity)
        self.log_event(f"添加了新的合成站 {station.station_id} (产能:{capacity})")
        
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
        ttk.Label(progress_frame, text="生产线:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        for i, line in enumerate(self.factory.production_lines):
            ttk.Label(progress_frame, text=f"生产线 {line.line_id}:").grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=150, mode="determinate")
            progress_bar.grid(row=i+1, column=1, padx=5, pady=2)
            self.progress_bars[line.line_id] = progress_bar
            
        # 重新创建合成站进度条
        craft_start_row = len(self.factory.production_lines) + 2
        ttk.Label(progress_frame, text="合成站:", font=("Arial", 9, "bold")).grid(row=craft_start_row, column=0, sticky=tk.W, padx=5, pady=2)
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
            title="选择模组文件",
            filetypes=[("LAUN Mod Files", "*.launmod"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                mod = Mod.load_from_file(filename)
                self.current_mod = mod
                self.factory.load_mod(mod)
                self.mod_label.config(text=f"{mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"已加载模组: {mod.name} v{mod.version} by {mod.author}")
                self.log_event(f"模组描述: {mod.description}")
                self.update_progress_bars()
                self.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"加载模组失败: {str(e)}")
    
    def export_current_mod(self):
        """导出当前模组"""
        if not self.current_mod:
            messagebox.showwarning("警告", "没有加载任何模组，无法导出!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存模组文件",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.current_mod.save_to_file(filename)
                messagebox.showinfo("成功", f"模组已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存模组失败: {str(e)}")
    
    def reset_to_default(self):
        """重置为默认模组"""
        self.setup_factory()
        self.current_mod = None
        self.mod_label.config(text="默认模组")
        self.log_event("已重置为默认模组")
        self.update_progress_bars()
        self.update_display()

class ModCreator:
    """模组制作器"""
    def __init__(self, parent, app):
        self.app = app
        self.mod = Mod()
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("模组制作器")
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
        notebook.add(info_tab, text="基本信息")
        self.create_info_tab(info_tab)
        
        # 原材料标签页
        material_tab = ttk.Frame(notebook)
        notebook.add(material_tab, text="原材料")
        self.create_material_tab(material_tab)
        
        # 产品标签页
        product_tab = ttk.Frame(notebook)
        notebook.add(product_tab, text="产品")
        self.create_product_tab(product_tab)
        
        # 合成配方标签页
        recipe_tab = ttk.Frame(notebook)
        notebook.add(recipe_tab, text="合成配方")
        self.create_recipe_tab(recipe_tab)
        
        # 工人标签页
        worker_tab = ttk.Frame(notebook)
        notebook.add(worker_tab, text="工人")
        self.create_worker_tab(worker_tab)
        
        # 操作按钮
        action_frame = ttk.Frame(self.window)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="保存模组", command=self.save_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="加载模组", command=self.load_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="应用模组", command=self.apply_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def create_info_tab(self, parent):
        """创建基本信息标签页"""
        info_frame = ttk.LabelFrame(parent, text="模组基本信息", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="模组名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="描述:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="作者:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.author_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="版本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(info_frame, textvariable=self.version_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(info_frame, text="初始资金:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.balance_var = tk.StringVar(value="0")
        ttk.Entry(info_frame, textvariable=self.balance_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 合成站设置
        station_frame = ttk.LabelFrame(parent, text="合成站设置", padding="10")
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
        
        ttk.Button(station_btn_frame, text="添加合成站", command=self.add_station_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(station_btn_frame, text="删除合成站", command=self.delete_station).pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(material_btn_frame, text="添加原材料", command=self.add_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="编辑原材料", command=self.edit_material_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="删除原材料", command=self.delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(material_btn_frame, text="设置合成配方", command=self.set_material_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(product_btn_frame, text="添加产品", command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="编辑产品", command=self.edit_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="删除产品", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_btn_frame, text="设置合成配方", command=self.set_product_recipe_dialog).pack(side=tk.LEFT, padx=5)
        
        # 初始化列表
        self.update_product_list()
    
    def create_recipe_tab(self, parent):
        """创建合成配方标签页"""
        # 配方列表
        recipe_frame = ttk.LabelFrame(parent, text="合成配方", padding="10")
        recipe_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview来显示配方
        columns = ("类型", "名称", "材料需求", "产品需求")
        self.recipe_tree = ttk.Treeview(recipe_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.recipe_tree.heading(col, text=col)
            if col == "名称":
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
        
        ttk.Button(recipe_btn_frame, text="刷新配方列表", command=self.update_recipe_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(recipe_btn_frame, text="删除配方", command=self.delete_recipe).pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(worker_btn_frame, text="添加工人", command=self.add_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="编辑工人", command=self.edit_worker_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(worker_btn_frame, text="删除工人", command=self.delete_worker).pack(side=tk.LEFT, padx=5)
        
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
                self.recipe_tree.insert("", "end", values=("材料", material.name, materials_str, products_str))
                
        # 添加可合成的产品
        for product in self.mod.products:
            if product.is_craftable:
                materials_str = ", ".join([f"{name}×{qty}" for name, qty in product.materials_required.items()])
                products_str = ", ".join([f"{name}×{qty}" for name, qty in product.products_required.items()])
                self.recipe_tree.insert("", "end", values=("产品", product.name, materials_str, products_str))
    
    def add_station_dialog(self):
        """添加合成站对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title("添加合成站")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="合成站名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value="合成台")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="产能:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        capacity_var = tk.StringVar(value="5")
        capacity_entry = ttk.Entry(dialog, textvariable=capacity_var)
        capacity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def add_station():
            try:
                name = name_var.get()
                capacity = int(capacity_var.get())
                
                if not name:
                    messagebox.showerror("错误", "请输入合成站名称!")
                    return
                
                self.mod.crafting_stations.append({"name": name, "capacity": capacity})
                self.station_listbox.insert(tk.END, f"{name} (产能:{capacity})")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的产能!")
        
        ttk.Button(dialog, text="添加", command=add_station).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_station(self):
        """删除合成站"""
        selection = self.station_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个合成站!")
            return
            
        index = selection[0]
        self.mod.crafting_stations.pop(index)
        self.station_listbox.delete(index)
    
    def add_material_dialog(self):
        """添加原材料对话框"""
        self.material_dialog("添加原材料")
    
    def edit_material_dialog(self):
        """编辑原材料对话框"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个原材料!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.material_dialog("编辑原材料", material, index)
    
    def material_dialog(self, title, material=None, index=None):
        """原材料对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="原材料名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=material.name if material else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="单价:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        cost_var = tk.StringVar(value=material.cost if material else "1")
        cost_entry = ttk.Entry(dialog, textvariable=cost_var)
        cost_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="单位:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        unit_var = tk.StringVar(value=material.unit if material else "单位")
        unit_entry = ttk.Entry(dialog, textvariable=unit_var)
        unit_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="初始数量:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
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
                    messagebox.showerror("错误", "请输入原材料名称!")
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
                messagebox.showerror("错误", "请输入有效的数字!")
        
        ttk.Button(dialog, text="保存", command=save_material).grid(row=4, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_material_recipe_dialog(self):
        """设置材料合成配方对话框"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个原材料!")
            return
            
        index = selection[0]
        material = self.mod.materials[index]
        self.recipe_dialog("设置材料合成配方", material, False)
    
    def add_product_dialog(self):
        """添加产品对话框"""
        self.product_dialog("添加产品")
    
    def edit_product_dialog(self):
        """编辑产品对话框"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个产品!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.product_dialog("编辑产品", product, index)
    
    def product_dialog(self, title, product=None, index=None):
        """产品对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="产品名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=product.name if product else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="生产时间(分钟):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        time_var = tk.StringVar(value=product.production_time if product else "60")
        time_entry = ttk.Entry(dialog, textvariable=time_var)
        time_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="销售价格:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        price_var = tk.StringVar(value=product.sale_price if product else "20")
        price_entry = ttk.Entry(dialog, textvariable=price_var)
        price_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_product():
            try:
                name = name_var.get()
                production_time = int(time_var.get())
                sale_price = float(price_var.get())
                
                if not name:
                    messagebox.showerror("错误", "请输入产品名称!")
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
                messagebox.showerror("错误", "请输入有效的数字!")
        
        ttk.Button(dialog, text="保存", command=save_product).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def set_product_recipe_dialog(self):
        """设置产品合成配方对话框"""
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个产品!")
            return
            
        index = selection[0]
        product = self.mod.products[index]
        self.recipe_dialog("设置产品合成配方", product, True)
    
    def recipe_dialog(self, title, item, is_product):
        """合成配方对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("500x640")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 基本信息
        info_frame = ttk.LabelFrame(dialog, text="基本信息", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        item_type = "产品" if is_product else "材料"
        ttk.Label(info_frame, text=f"{item_type}名称: {item.name}").pack(anchor=tk.W)
        
        # 材料需求
        materials_frame = ttk.LabelFrame(dialog, text="材料需求", padding="10")
        materials_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 材料需求列表
        materials_list_frame = ttk.Frame(materials_frame)
        materials_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview来显示材料需求
        columns = ("材料", "数量")
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
        
        ttk.Button(materials_btn_frame, text="添加材料需求", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "material")).pack(side=tk.LEFT, padx=5)
        ttk.Button(materials_btn_frame, text="删除材料需求", 
                  command=lambda: self.delete_requirement(self.materials_tree)).pack(side=tk.LEFT, padx=5)
        
        # 产品需求
        products_frame = ttk.LabelFrame(dialog, text="产品需求", padding="10")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 产品需求列表
        products_list_frame = ttk.Frame(products_frame)
        products_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview来显示产品需求
        columns = ("产品", "数量")
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
        
        ttk.Button(products_btn_frame, text="添加产品需求", 
                  command=lambda: self.add_requirement_dialog(dialog, item, "product")).pack(side=tk.LEFT, padx=5)
        ttk.Button(products_btn_frame, text="删除产品需求", 
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
            
            messagebox.showinfo("成功", "合成配方已保存!")
        
        def save_and_close():
            save_recipe()
            dialog.destroy()
        
        ttk.Button(btn_frame, text="保存配方", command=save_recipe).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存并关闭", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def add_requirement_dialog(self, parent_dialog, item, requirement_type):
        """添加需求对话框"""
        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"添加{requirement_type}需求")
        dialog.geometry("300x150")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        requirement_name = "材料" if requirement_type == "material" else "产品"
        
        ttk.Label(dialog, text=f"{requirement_name}:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        
        if requirement_type == "material":
            name_combo = ttk.Combobox(dialog, textvariable=name_var, 
                                     values=[m.name for m in self.mod.materials])
        else:
            name_combo = ttk.Combobox(dialog, textvariable=name_var, 
                                     values=[p.name for p in self.mod.products])
        name_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="数量:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def add_requirement():
            try:
                name = name_var.get()
                quantity = int(quantity_var.get())
                
                if not name:
                    messagebox.showerror("错误", f"请选择{requirement_name}!")
                    return
                
                # 检查是否已存在该需求
                if requirement_type == "material":
                    tree = self.materials_tree
                else:
                    tree = self.products_tree
                    
                for tree_item in tree.get_children():
                    values = tree.item(tree_item, "values")
                    if values[0] == name:
                        messagebox.showwarning("警告", f"该{requirement_name}需求已存在!")
                        return
                
                # 添加到列表
                tree.insert("", "end", values=(name, quantity))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数量!")
        
        ttk.Button(dialog, text="添加", command=add_requirement).grid(row=2, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_requirement(self, tree):
        """删除需求"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个需求!")
            return
            
        for item in selection:
            tree.delete(item)
    
    def delete_material(self):
        """删除原材料"""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个原材料!")
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
            messagebox.showwarning("警告", "请先选择一个产品!")
            return
            
        index = selection[0]
        self.mod.products.pop(index)
        self.update_product_list()
        self.update_recipe_list()
    
    def delete_recipe(self):
        """删除配方"""
        selection = self.recipe_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个配方!")
            return
            
        for item in selection:
            values = self.recipe_tree.item(item, "values")
            item_type, name = values[0], values[1]
            
            if item_type == "材料":
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
        self.worker_dialog("添加工人")
    
    def edit_worker_dialog(self):
        """编辑工人对话框"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工人!")
            return
            
        index = selection[0]
        worker = self.mod.initial_workers[index]
        self.worker_dialog("编辑工人", worker, index)
    
    def worker_dialog(self, title, worker=None, index=None):
        """工人对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="工人姓名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=worker.name if worker else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="技能等级 (1-5):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        skill_var = tk.StringVar(value=worker.skill_level if worker else "3")
        skill_entry = ttk.Entry(dialog, textvariable=skill_var)
        skill_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="日薪:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        salary_var = tk.StringVar(value=worker.salary if worker else "100")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var)
        salary_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def save_worker():
            try:
                name = name_var.get()
                skill_level = int(skill_var.get())
                salary = float(salary_var.get())
                
                if not name:
                    messagebox.showerror("错误", "请输入工人姓名!")
                    return
                
                new_worker = Worker(name, skill_level, salary)
                
                if worker:  # 编辑模式
                    self.mod.initial_workers[index] = new_worker
                else:  # 添加模式
                    self.mod.initial_workers.append(new_worker)
                
                self.update_worker_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字!")
        
        ttk.Button(dialog, text="保存", command=save_worker).grid(row=3, column=0, columnspan=2, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_worker(self):
        """删除工人"""
        selection = self.worker_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工人!")
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
            messagebox.showerror("错误", "初始资金必须是有效的数字!")
            return
        
        if not self.mod.name:
            messagebox.showerror("错误", "请输入模组名称!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存模组文件",
            defaultextension=".launmod",
            filetypes=[("LAUN Mod Files", "*.launmod")]
        )
        
        if filename:
            try:
                self.mod.save_to_file(filename)
                messagebox.showinfo("成功", f"模组已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存模组失败: {str(e)}")
    
    def load_mod(self):
        """加载模组"""
        filename = filedialog.askopenfilename(
            title="选择模组文件",
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
                    self.station_listbox.insert(tk.END, f"{station['name']} (产能:{station['capacity']})")
                
                self.update_material_list()
                self.update_product_list()
                self.update_worker_list()
                self.update_recipe_list()
                
                messagebox.showinfo("成功", f"已加载模组: {self.mod.name}")
            except Exception as e:
                messagebox.showerror("错误", f"加载模组失败: {str(e)}")
    
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
            messagebox.showerror("错误", "初始资金必须是有效的数字!")
            return
        
        if not self.mod.name:
            messagebox.showerror("错误", "请输入模组名称!")
            return
        
        self.app.current_mod = self.mod
        self.app.factory.load_mod(self.mod)
        self.app.mod_label.config(text=f"{self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"已加载模组: {self.mod.name} v{self.mod.version} by {self.mod.author}")
        self.app.log_event(f"模组描述: {self.mod.description}")
        self.app.update_progress_bars()
        self.app.update_display()
        
        messagebox.showinfo("成功", "模组已应用到游戏!")
        self.window.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = FactorySimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":

    main()
