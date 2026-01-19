"""
CNC加工工具包 v2.9 - 手機版 (Kivy) - Google Colab 兼容版
開發者：Henry 老師傅
公司：歐盛珠寶股份有限公司 ERREPI TAIWAN
優化版本：2024年1月
"""

import os
import sys
import math
from os import environ
from functools import partial

# 必須在導入 Kivy 之前設置環境變量
environ['KIVY_NO_CONSOLELOG'] = '1'  # 關閉控制台日誌
environ['KIVY_NO_FILELOG'] = '1'     # 關閉文件日誌
environ['KIVY_LOG_MODE'] = 'PYTHON'  # 使用 Python 日誌系統

# 簡化 Android 平台檢測（Google Colab 中永遠為 False）
IS_ANDROID = False

# 非 Android 設備：設置窗口大小
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')

# 現在導入 Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle

# 檢查系統平台並設置字體
if sys.platform == 'win32':
    # Windows 系統字體
    font_paths = [
        "C:/Windows/Fonts/msjh.ttc",           # 微軟正黑體
        "C:/Windows/Fonts/msyh.ttc",           # 微軟雅黑
        "C:/Windows/Fonts/simhei.ttf",         # 黑體
        "C:/Windows/Fonts/simsun.ttc",         # 新宋體
    ]
elif sys.platform == 'darwin':
    # macOS/iOS 系統字體
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
else:
    # Linux 和其他系統（包括 Colab）
    font_paths = [
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

# 註冊中文字體
font_loaded = False
for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=font_path)
            print(f"已載入字體: {font_path}")
            font_loaded = True
            break
        except Exception as e:
            print(f"字體載入錯誤 {font_path}: {e}")

if not font_loaded:
    # 如果找不到中文字體，使用默認字體
    print("警告：找不到中文字體，將使用默認字體")
    try:
        LabelBase.register(name='ChineseFont', fn_regular='Roboto')
    except:
        print("使用 Kivy 默認字體")

class ValidatedTextInput(TextInput):
    """帶驗證的文本輸入框"""
    
    def __init__(self, **kwargs):
        # 設置默認輸入過濾器
        kwargs.setdefault('input_filter', self.float_filter)
        super().__init__(**kwargs)
        
    @staticmethod
    def float_filter(value, from_undo):
        """過濾器：只允許數字和小數點"""
        allowed_chars = '0123456789.'
        
        # 檢查是否已有一個小數點
        if '.' in value:
            parts = value.split('.')
            if len(parts) > 2:  # 多個小數點
                return ''
            elif len(parts) == 2 and len(parts[1]) > 3:  # 小數點後超過3位
                return '.'.join([parts[0], parts[1][:3]])
        
        # 過濾非法字符
        result = ''.join([char for char in value if char in allowed_chars])
        
        # 防止以多個0開頭（如 00123）
        if result.startswith('00') and len(result) > 1:
            result = '0' + result.lstrip('0')
            
        return result
    
    def validate_positive(self):
        """驗證輸入是否為正數"""
        try:
            value = float(self.text)
            return value > 0
        except ValueError:
            return False

# 創建自定義SpinnerOption來解決下拉選項的字體問題
class ChineseSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'ChineseFont'
        self.font_size = '16sp'
        self.background_color = (0.95, 0.95, 0.95, 1)
        self.color = (0.1, 0.1, 0.1, 1)

# 創建自定義Spinner來解決中文字體問題
class ChineseSpinner(Spinner):
    def __init__(self, **kwargs):
        # 確保有默認值
        if 'values' not in kwargs:
            kwargs['values'] = []
        
        # 設置字體和下拉選項樣式
        kwargs.setdefault('font_name', 'ChineseFont')
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('option_cls', ChineseSpinnerOption)
        kwargs.setdefault('background_color', (0.95, 0.95, 0.95, 1))
        kwargs.setdefault('color', (0.1, 0.1, 0.1, 1))
        
        super().__init__(**kwargs)

class CustomButton(Button):
    """自定義按鈕，帶有更好的反饋效果"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.font_name = 'ChineseFont'
        
    def on_press(self):
        """按壓效果"""
        original_color = self.background_color
        self.background_color = (original_color[0] * 0.8, 
                                original_color[1] * 0.8, 
                                original_color[2] * 0.8, 
                                original_color[3])
        Clock.schedule_once(self.reset_color, 0.1)
        
    def reset_color(self, dt):
        """恢復原始顏色"""
        if self.parent:  # 確保按鈕仍然存在
            original_color = self.background_color
            self.background_color = (original_color[0] / 0.8, 
                                    original_color[1] / 0.8, 
                                    original_color[2] / 0.8, 
                                    original_color[3])

class MainScreen(Screen):
    """主屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 主佈局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 標題
        title_label = Label(
            text='CNC加工工具包 v2.9',
            font_size='24sp',
            bold=True,
            size_hint_y=0.15,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont'
        )
        main_layout.add_widget(title_label)
        
        # 公司標題
        company_label = Label(
            text='歐盛珠寶股份有限公司\nERREPI TAIWAN',
            font_size='16sp',
            bold=True,
            size_hint_y=0.12,
            color=(1, 0.6, 0, 1),
            font_name='ChineseFont',
            halign='center'
        )
        company_label.bind(size=company_label.setter('text_size'))
        main_layout.add_widget(company_label)
        
        # 功能按鈕
        buttons = [
            ("刀具伸長計算", self.open_tool_calc, (0.93, 0.41, 0.19, 1)),
            ("球刀步距計算", self.open_ballmill_calc, (0.44, 0.68, 0.28, 1)),
            ("螺旋銑削計算", self.open_helical_calc, (0.27, 0.45, 0.77, 1)),
            ("切削條件計算", self.open_cutting_calc, (1, 0.6, 0, 1)),
            ("切削預留量計算", self.open_stock_calc, (0.61, 0.16, 0.69, 1))
        ]
        
        for text, callback, color in buttons:
            btn = CustomButton(
                text=text,
                size_hint_y=0.12,
                background_color=color,
                font_size='16sp',
                bold=True,
            )
            btn.bind(on_press=callback)
            main_layout.add_widget(btn)
        
        # 信息標籤
        info_text = """本工具包含5大計算功能：
• 刀具伸長優化計算
• 球刀步距計算
• 螺旋銑削計算
• 切削條件計算
• 切削預留量計算

版本: 2.9 (手機版)
優化: 輸入驗證、性能優化
開發者: Henry 老師傅
公司: 歐盛珠寶股份有限公司 ERREPI TAIWAN"""
        
        info_label = Label(
            text=info_text,
            font_size='12sp',
            size_hint_y=0.35,
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        info_label.bind(size=info_label.setter('text_size'))
        main_layout.add_widget(info_label)
        
        self.add_widget(main_layout)
    
    def open_tool_calc(self, instance):
        self.manager.current = 'tool_calc'
    
    def open_ballmill_calc(self, instance):
        self.manager.current = 'ballmill_calc'
    
    def open_helical_calc(self, instance):
        self.manager.current = 'helical_calc'
    
    def open_cutting_calc(self, instance):
        self.manager.current = 'cutting_calc'
    
    def open_stock_calc(self, instance):
        self.manager.current = 'stock_calc'

class ToolCalculator(Screen):
    """刀具伸長計算器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 主佈局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 標題和返回按鈕的佈局
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        # 返回按鈕
        back_btn = CustomButton(
            text='← 返回',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # 標題
        title = Label(
            text='刀具伸長計算器',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint=(0.8, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # 輸入區域
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.5)
        
        input_layout.add_widget(Label(text='刀具直徑 (mm):', font_size='16sp', font_name='ChineseFont'))
        self.diameter_input = ValidatedTextInput(text='10', multiline=False, font_size='16sp')
        input_layout.add_widget(self.diameter_input)
        
        input_layout.add_widget(Label(text='刀具材料:', font_size='16sp', font_name='ChineseFont'))
        self.material_spinner = ChineseSpinner(
            text='碳化鎢',
            values=['碳化鎢', '高速鋼', '陶瓷'],
            font_size='16sp',
            size_hint_y=None,
            height=dp(40)
        )
        input_layout.add_widget(self.material_spinner)
        
        input_layout.add_widget(Label(text='主軸轉速 (RPM):', font_size='16sp', font_name='ChineseFont'))
        self.speed_input = ValidatedTextInput(text='3000', multiline=False, font_size='16sp')
        input_layout.add_widget(self.speed_input)
        
        input_layout.add_widget(Label(text='進給速度 (mm/min):', font_size='16sp', font_name='ChineseFont'))
        self.feed_input = ValidatedTextInput(text='500', multiline=False, font_size='16sp')
        input_layout.add_widget(self.feed_input)
        
        input_layout.add_widget(Label(text='切削深度 (mm):', font_size='16sp', font_name='ChineseFont'))
        self.depth_input = ValidatedTextInput(text='2', multiline=False, font_size='16sp')
        input_layout.add_widget(self.depth_input)
        
        main_layout.add_widget(input_layout)
        
        # 計算按鈕
        calc_btn = CustomButton(
            text='計算最佳伸長',
            size_hint_y=0.1,
            background_color=(0.3, 0.7, 0.3, 1),
            font_size='18sp',
            bold=True,
        )
        calc_btn.bind(on_press=lambda x: Clock.schedule_once(self.calculate, 0))
        main_layout.add_widget(calc_btn)
        
        # 結果顯示
        self.result_label = Label(
            text='計算結果將顯示在這裡',
            font_size='14sp',
            size_hint_y=0.3,
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        main_layout.add_widget(self.result_label)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def calculate(self, dt):
        """計算最佳伸長（異步執行）"""
        try:
            # 驗證輸入
            if not all([self.diameter_input.validate_positive(),
                       self.speed_input.validate_positive(),
                       self.feed_input.validate_positive(),
                       self.depth_input.validate_positive()]):
                self.result_label.text = "錯誤：請輸入有效的正數"
                return
                
            diameter = float(self.diameter_input.text)
            speed = float(self.speed_input.text)
            feed = float(self.feed_input.text)
            depth = float(self.depth_input.text)
            
            # 檢查深度合理性
            if depth > diameter * 2:
                self.result_label.text = f"警告：切削深度({depth}mm)可能過大\n建議不超過刀具直徑的2倍"
                return
            
            material_factor = {"碳化鎢": 1.0, "高速鋼": 0.7, "陶瓷": 1.3}
            factor = material_factor.get(self.material_spinner.text, 1.0)
            
            # 計算最佳伸長
            optimal_length = diameter * 3 * factor * (1 - depth/10)
            optimal_length = max(diameter * 1.5, min(diameter * 5, optimal_length))  # 限制範圍
            
            result_text = f"""計算結果：
刀具直徑: {diameter} mm
最佳伸長: {optimal_length:.1f} mm
L/D比值: {optimal_length/diameter:.2f}
建議轉速: {int(speed * 0.9)} RPM
建議進給: {int(feed * 0.8)} mm/min

加工建議：
• 確保刀具夾持牢固
• 首次使用建議試切削
• 根據實際情況微調參數
• L/D比值應在1.5-5之間"""
            
            self.result_label.text = result_text
            
        except ValueError:
            self.result_label.text = "請輸入有效的數字"
        except Exception as e:
            self.result_label.text = f'計算錯誤: {str(e)}'

class BallMillCalculator(Screen):
    """球刀步距計算器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 參考步距對照表
        self.reference_step_data = {
            16: 0.40, 12: 0.35, 10: 0.32, 8: 0.28,
            6: 0.24, 5: 0.20, 4: 0.20, 3: 0.17,
            2: 0.14, 1.5: 0.12, 1: 0.10
        }
        
        # 主佈局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 標題和返回按鈕的佈局
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        # 返回按鈕
        back_btn = CustomButton(
            text='← 返回',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # 標題
        title = Label(
            text='球刀步距計算器',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint=(0.8, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # 輸入區域
        input_container = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.3)
        
        # 球刀直徑輸入行
        diameter_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.5)
        diameter_row.add_widget(Label(text='球刀直徑 (mm):', font_size='16sp', font_name='ChineseFont'))
        self.diameter_input = ValidatedTextInput(
            text='6', 
            multiline=False, 
            font_size='16sp',
            size_hint=(0.7, 1)
        )
        self.diameter_input.bind(text=self.update_reference_step)
        diameter_row.add_widget(self.diameter_input)
        input_container.add_widget(diameter_row)
        
        # 步距輸入行
        step_row = BoxLayout(orientation='vertical', spacing=5, size_hint_y=0.5)
        
        # 步距標籤和輸入框
        step_input_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.6)
        step_input_row.add_widget(Label(text='步距 (mm):', font_size='16sp', font_name='ChineseFont'))
        self.step_input = ValidatedTextInput(
            text='0.3', 
            multiline=False, 
            font_size='16sp',
            size_hint=(0.7, 1)
        )
        step_input_row.add_widget(self.step_input)
        step_row.add_widget(step_input_row)
        
        # 標準參考步距顯示
        self.reference_step_label = Label(
            text='標準參考步距: -- mm',
            font_size='16sp',
            bold=True,
            color=(1, 0, 0, 1),
            font_name='ChineseFont',
            size_hint_y=0.4,
            halign='center'
        )
        self.reference_step_label.bind(size=self.reference_step_label.setter('text_size'))
        step_row.add_widget(self.reference_step_label)
        
        input_container.add_widget(step_row)
        
        main_layout.add_widget(input_container)
        
        # 計算按鈕
        calc_btn = CustomButton(
            text='計算殘餘高度',
            size_hint_y=0.1,
            background_color=(0.27, 0.45, 0.77, 1),
            font_size='18sp',
            bold=True,
        )
        calc_btn.bind(on_press=lambda x: Clock.schedule_once(self.calculate, 0))
        main_layout.add_widget(calc_btn)
        
        # 結果顯示
        self.result_label = Label(
            text='殘餘高度: --',
            font_size='18sp',
            bold=True,
            size_hint_y=0.1,
            color=(0.27, 0.45, 0.77, 1),
            font_name='ChineseFont'
        )
        main_layout.add_widget(self.result_label)
        
        # 詳細結果
        self.detail_label = Label(
            text='詳細結果將顯示在這裡',
            font_size='14sp',
            size_hint_y=0.4,
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        self.detail_label.bind(size=self.detail_label.setter('text_size'))
        main_layout.add_widget(self.detail_label)
        
        # 初始化時顯示參考步距
        self.update_reference_step(None, self.diameter_input.text)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def get_reference_step(self, diameter):
        """根據直徑獲取參考步距"""
        try:
            diameter_val = float(diameter)
            if diameter_val in self.reference_step_data:
                return self.reference_step_data[diameter_val]
            
            standard_diameters = sorted(self.reference_step_data.keys())
            closest_diameter = min(standard_diameters, key=lambda x: abs(x - diameter_val))
            return self.reference_step_data[closest_diameter]
        except:
            return None
    
    def update_reference_step(self, instance, value):
        """更新標準參考步距顯示"""
        try:
            if not value:
                self.reference_step_label.text = '標準參考步距: -- mm'
                return
                
            ref_step = self.get_reference_step(value)
            if ref_step is not None:
                self.reference_step_label.text = f'標準參考步距: {ref_step} mm'
            else:
                self.reference_step_label.text = '標準參考步距: -- mm'
        except:
            self.reference_step_label.text = '標準參考步距: -- mm'
    
    def calculate(self, dt):
        try:
            # 獲取輸入值
            D_text = self.diameter_input.text.strip()
            P_text = self.step_input.text.strip()
            
            if not D_text or not P_text:
                self.result_label.text = "錯誤：請輸入數值"
                return
                
            D = float(D_text)
            P = float(P_text)
            
            # 輸入驗證
            if D <= 0:
                self.result_label.text = "錯誤：直徑必須大於0"
                self.detail_label.text = "請輸入大於0的刀具直徑"
                return
                
            if P <= 0:
                self.result_label.text = "錯誤：步距必須大於0"
                self.detail_label.text = "請輸入大於0的步距值"
                return
                
            if P >= D:
                self.result_label.text = "錯誤：步距必須小於直徑"
                self.detail_label.text = f"步距({P}mm)必須小於刀具直徑({D}mm)"
                return
            
            R = D / 2
            
            # 修正浮點精度問題
            if P/2 >= R:
                h = R  # 步距過大，殘餘高度等於半徑
                self.result_label.text = "警告：步距過大"
            else:
                # 使用 max(0, ...) 避免負數
                radicand = max(0, R**2 - (P/2)**2)
                h = R - math.sqrt(radicand)
            
            # 計算參考值
            P_ref = self.get_reference_step(D)
            if P_ref is not None and 0 < P_ref < D:
                radicand_ref = max(0, R**2 - (P_ref/2)**2)
                h_ref = R - math.sqrt(radicand_ref)
            else:
                h_ref = 0.0
                P_ref = 0.0
            
            # 顯示結果
            self.result_label.text = f"殘餘高度: {h*1000:.2f} μm"
            
            # 評估質量
            quality = "優良" if h*1000 < 10 else "良好" if h*1000 < 20 else "一般" if h*1000 < 30 else "較差"
            quality_color = (0, 0.7, 0, 1) if h*1000 < 10 else (0.2, 0.5, 0.2, 1) if h*1000 < 20 else (1, 0.6, 0, 1) if h*1000 < 30 else (1, 0, 0, 1)
            
            detail_text = f"""球刀直徑: {D} mm
球刀半徑: {R} mm
設定步距: {P} mm
殘餘高度: {h:.6f} mm ({h*1000:.2f} μm)
表面質量: {quality}

標準參考步距: {P_ref} mm
參考殘餘高度: {h_ref:.6f} mm ({h_ref*1000:.2f} μm)
差值: {abs(h - h_ref):.6f} mm ({abs(h - h_ref)*1000:.2f} μm)

建議：
• 殘餘高度 < 10μm：精加工
• 殘餘高度 10-20μm：半精加工
• 殘餘高度 20-30μm：粗加工
• 殘餘高度 > 30μm：表面粗糙，建議減小步距"""
            
            self.detail_label.text = detail_text
                
        except ValueError:
            self.result_label.text = "輸入錯誤"
            self.detail_label.text = "請輸入有效的數字（如：6.0, 0.3）"
        except Exception as e:
            self.result_label.text = "計算錯誤"
            self.detail_label.text = f"錯誤: {str(e)}"

class HelicalCalculator(Screen):
    """螺旋銑削計算器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 儲存當前銑削類型
        self.current_milling_type = "內徑螺旋銑"
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
        
        # 標題和返回按鈕的布局
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        
        # 返回按鈕
        back_btn = CustomButton(
            text='← 返回',
            size_hint=(0.25, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # 標題
        title = Label(
            text='螺旋銑削計算器',
            font_size='18sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint=(0.75, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # 創建滾動視圖
        scroll = ScrollView(size_hint=(1, 0.85), do_scroll_x=False, 
                           bar_width=dp(10), bar_color=(0.5, 0.5, 0.5, 0.5))
        content_layout = BoxLayout(orientation='vertical', spacing=5, 
                                  size_hint_y=None, padding=[5, 5, 5, 5])
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 銑削類型選擇
        type_layout = BoxLayout(orientation='horizontal', spacing=5, 
                               size_hint_y=None, height=dp(40))
        type_layout.add_widget(Label(text='銑削類型:', font_size='14sp', 
                                    font_name='ChineseFont', size_hint=(0.4, 1)))
        
        self.milling_type = ChineseSpinner(
            text='內徑螺旋銑',
            values=['內徑螺旋銑', '外徑螺旋銑', '爬坡銑'],
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            size_hint=(0.6, 1)
        )
        self.milling_type.bind(text=self.on_milling_type_changed)
        type_layout.add_widget(self.milling_type)
        content_layout.add_widget(type_layout)
        
        # 通用輸入區域
        input_layout = GridLayout(cols=2, spacing=5, 
                                 size_hint_y=None, height=dp(220))
        
        # 刀具直徑 Dc
        input_layout.add_widget(Label(text='刀具直徑 Dc (mm):', 
                                     font_size='14sp', font_name='ChineseFont'))
        self.tool_dia_input = ValidatedTextInput(text='10', multiline=False, 
                                       font_size='14sp')
        self.tool_dia_input.bind(text=self.update_min_hole_diameter)
        input_layout.add_widget(self.tool_dia_input)
        
        # 總切削深度 d
        input_layout.add_widget(Label(text='總切削深度 d (mm):', 
                                     font_size='14sp', font_name='ChineseFont'))
        self.depth_input = ValidatedTextInput(text='20', multiline=False, 
                                    font_size='14sp')
        input_layout.add_widget(self.depth_input)
        
        # 動態輸入區域1 - 根據銑削類型變化
        self.dynamic_label1 = Label(text='孔徑 Dm (mm):', 
                                   font_size='14sp', font_name='ChineseFont')
        input_layout.add_widget(self.dynamic_label1)
        
        self.dynamic_input1 = ValidatedTextInput(text='60', multiline=False, 
                                       font_size='14sp')
        input_layout.add_widget(self.dynamic_input1)
        
        # 動態輸入區域2 - 外徑螺旋銑專用
        self.dynamic_label2 = Label(text='切削寬度 W (mm):', 
                                   font_size='14sp', font_name='ChineseFont')
        self.dynamic_label2.opacity = 0  # 初始隱藏
        input_layout.add_widget(self.dynamic_label2)
        
        self.dynamic_input2 = ValidatedTextInput(text='10', multiline=False, 
                                       font_size='14sp')
        self.dynamic_input2.opacity = 0  # 初始隱藏
        input_layout.add_widget(self.dynamic_input2)
        
        content_layout.add_widget(input_layout)
        
        # 內徑螺旋銑專用：最小加工孔徑顯示
        self.min_hole_label = Label(
            text='最小加工孔徑建議: 12.0 mm',
            font_size='16sp',
            bold=True,
            color=(1, 0, 0, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        self.min_hole_label.opacity = 1  # 初始顯示
        self.min_hole_label.bind(size=self.min_hole_label.setter('text_size'))
        content_layout.add_widget(self.min_hole_label)
        
        # 參數說明標籤
        self.param_explain_label = Label(
            text='計算公式: φ = arctan(d/ΔR)\nΔR = (孔徑 - 刀具直徑)/2',
            font_size='12sp',
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle',
            font_name='ChineseFont'
        )
        self.param_explain_label.bind(size=self.param_explain_label.setter('text_size'))
        content_layout.add_widget(self.param_explain_label)
        
        # 外徑螺旋銑參數說明（初始隱藏）
        self.w_explain_label = Label(
            text='W:切削寬度，刀具每圈在徑向上的切削距離\n建議值: 刀具直徑的50%-80%',
            font_size='11sp',
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle',
            color=(0.5, 0.2, 0.8, 1),
            font_name='ChineseFont'
        )
        self.w_explain_label.opacity = 0  # 初始隱藏
        self.w_explain_label.bind(size=self.w_explain_label.setter('text_size'))
        content_layout.add_widget(self.w_explain_label)
        
        # 計算按鈕
        calc_btn = CustomButton(
            text='計算斜坡角度',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.61, 0.16, 0.69, 1),
            font_size='16sp',
            bold=True,
        )
        calc_btn.bind(on_press=lambda x: Clock.schedule_once(self.calculate, 0))
        content_layout.add_widget(calc_btn)
        
        # 結果顯示區域
        results_layout = BoxLayout(orientation='vertical', spacing=5, 
                                  size_hint_y=None, height=dp(250))
        
        # 斜坡角結果
        self.angle_result_label = Label(
            text='斜坡角度 φ = --°',
            font_size='24sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        self.angle_result_label.bind(size=self.angle_result_label.setter('text_size'))
        results_layout.add_widget(self.angle_result_label)
        
        # 安全評估
        self.safety_result_label = Label(
            text='安全評估: --',
            font_size='18sp',
            bold=True,
            color=(1, 0, 0, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        self.safety_result_label.bind(size=self.safety_result_label.setter('text_size'))
        results_layout.add_widget(self.safety_result_label)
        
        # 詳細參數結果
        self.detail_result_label = Label(
            text='',
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(80),
            halign='center'
        )
        self.detail_result_label.bind(size=self.detail_result_label.setter('text_size'))
        results_layout.add_widget(self.detail_result_label)
        
        # 建議標籤
        self.suggestion_label = Label(
            text='',
            font_size='12sp',
            color=(0.2, 0.5, 0.2, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        self.suggestion_label.bind(size=self.suggestion_label.setter('text_size'))
        results_layout.add_widget(self.suggestion_label)
        
        content_layout.add_widget(results_layout)
        
        # 詳細計算過程
        self.calc_process_label = Label(
            text='請輸入參數後點擊計算按鈕',
            font_size='12sp',
            size_hint_y=None,
            height=dp(120),
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        self.calc_process_label.bind(size=self.calc_process_label.setter('text_size'))
        content_layout.add_widget(self.calc_process_label)
        
        # 警告訊息
        self.warning_label = Label(
            text='',
            font_size='12sp',
            color=(1, 0.5, 0, 1),
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        self.warning_label.bind(size=self.warning_label.setter('text_size'))
        content_layout.add_widget(self.warning_label)
        
        # 應用建議
        self.advice_label = Label(
            text='內徑螺旋銑：用於加工孔，螺旋切削過程平穩，排屑效果好',
            font_size='11sp',
            halign='left',
            valign='top',
            font_name='ChineseFont',
            size_hint_y=None,
            height=dp(40)
        )
        self.advice_label.bind(size=self.advice_label.setter('text_size'))
        content_layout.add_widget(self.advice_label)
        
        # 設置滾動視圖內容
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # 計算按鈕
        calc_btn_bottom = CustomButton(
            text='重新計算',
            size_hint_y=0.07,
            background_color=(0.27, 0.45, 0.77, 1),
            font_size='14sp',
            bold=True,
        )
        calc_btn_bottom.bind(on_press=lambda x: Clock.schedule_once(self.calculate, 0))
        main_layout.add_widget(calc_btn_bottom)
        
        self.add_widget(main_layout)
        
        # 初始化介面
        self.on_milling_type_changed(None, '內徑螺旋銑')
        self.update_min_hole_diameter(None, self.tool_dia_input.text)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def update_min_hole_diameter(self, instance, value):
        """更新最小加工孔徑顯示"""
        try:
            if not value:
                return
                
            tool_dia = float(value) if value else 0
            if tool_dia <= 0:
                self.min_hole_label.text = '最小加工孔徑建議: -- mm'
                return
                
            min_hole_dia = self.calculate_min_hole_diameter(tool_dia)
            self.min_hole_label.text = f'最小加工孔徑建議: {min_hole_dia:.1f} mm'
        except:
            self.min_hole_label.text = '最小加工孔徑建議: -- mm'
    
    def on_milling_type_changed(self, instance, value):
        """當銑削類型改變時更新介面"""
        self.current_milling_type = value
        
        if value == '內徑螺旋銑':
            self.dynamic_label1.text = '孔徑 Dm (mm):'
            self.dynamic_label1.opacity = 1
            self.dynamic_input1.text = '60'
            self.dynamic_input1.opacity = 1
            self.dynamic_input1.disabled = False
            
            self.dynamic_label2.opacity = 0
            self.dynamic_input2.opacity = 0
            self.dynamic_input2.disabled = True
            
            self.min_hole_label.opacity = 1  # 顯示最小孔徑
            self.w_explain_label.opacity = 0  # 隱藏W說明
            
            self.param_explain_label.text = '計算公式: φ = arctan(d/ΔR)\nΔR = (孔徑 - 刀具直徑)/2'
            self.advice_label.text = '內徑螺旋銑：斜坡角度建議15°-45°，適合孔徑大於刀具直徑1.2倍的情況'
            
        elif value == '外徑螺旋銑':
            self.dynamic_label1.text = '凸台直徑 Dm (mm):'
            self.dynamic_label1.opacity = 1
            self.dynamic_input1.text = '60'
            self.dynamic_input1.opacity = 1
            self.dynamic_input1.disabled = False
            
            self.dynamic_label2.text = '切削寬度 W (mm):'
            self.dynamic_label2.opacity = 1
            self.dynamic_input2.text = '10'
            self.dynamic_input2.opacity = 1
            self.dynamic_input2.disabled = False
            
            self.min_hole_label.opacity = 0  # 隱藏最小孔徑
            self.w_explain_label.opacity = 1  # 顯示W說明
            
            self.param_explain_label.text = '計算公式: φ = arctan(d/W)\nW = 切削寬度（徑向切削量）'
            self.advice_label.text = '外徑螺旋銑：W建議為刀具直徑的50-80%，刀具從凸台外側開始螺旋'
            
        else:  # 爬坡銑
            self.dynamic_label1.text = '斜坡長度 L (mm):'
            self.dynamic_label1.opacity = 1
            self.dynamic_input1.text = '100'
            self.dynamic_input1.opacity = 1
            self.dynamic_input1.disabled = False
            
            self.dynamic_label2.opacity = 0
            self.dynamic_input2.opacity = 0
            self.dynamic_input2.disabled = True
            
            self.min_hole_label.opacity = 0  # 隱藏最小孔徑
            self.w_explain_label.opacity = 0  # 隱藏W說明
            
            self.param_explain_label.text = '計算公式: φ = arctan(d/L)\n常用角度5°-15°'
            self.advice_label.text = '爬坡銑：常用角度5°-15°，用於型腔切入或斜面加工'
        
        # 清除計算結果
        self.reset_results()
    
    def reset_results(self):
        """重置計算結果"""
        self.angle_result_label.text = '斜坡角度 φ = --°'
        self.safety_result_label.text = '安全評估: --'
        self.detail_result_label.text = ''
        self.suggestion_label.text = ''
        self.calc_process_label.text = '請輸入參數後點擊計算按鈕'
        self.warning_label.text = ''
    
    def calculate_min_hole_diameter(self, tool_dia):
        """計算最小加工孔徑"""
        # 經驗公式：最小孔徑 = 刀具直徑 × 1.2
        return tool_dia * 1.2
    
    def calculate(self, dt):
        """計算斜坡角度（異步執行）"""
        try:
            # 清空警告
            self.warning_label.text = ''
            
            # 獲取通用輸入參數
            tool_dia_text = self.tool_dia_input.text.strip()
            depth_text = self.depth_input.text.strip()
            
            if not tool_dia_text or not depth_text:
                self.warning_label.text = '錯誤：請輸入刀具直徑和切削深度'
                return
                
            tool_dia = float(tool_dia_text)
            depth = float(depth_text)
            milling_type = self.current_milling_type
            
            # 檢查輸入有效性
            if tool_dia <= 0:
                self.warning_label.text = '錯誤：刀具直徑必須大於0'
                return
                
            if depth <= 0:
                self.warning_label.text = '錯誤：切削深度必須大於0'
                return
            
            if milling_type == '內徑螺旋銑':
                hole_dia_text = self.dynamic_input1.text.strip()
                if not hole_dia_text:
                    self.warning_label.text = '錯誤：請輸入孔徑'
                    return
                    
                hole_dia = float(hole_dia_text)
                
                # 計算最小加工孔徑
                min_hole_dia = self.calculate_min_hole_diameter(tool_dia)
                
                # 檢查孔徑合理性
                if hole_dia <= tool_dia:
                    self.warning_label.text = f'錯誤：孔徑必須大於刀具直徑 ({tool_dia}mm)'
                    return
                
                # 檢查是否小於最小建議孔徑
                if hole_dia < min_hole_dia:
                    self.warning_label.text = f'警告：孔徑小於最小建議值 {min_hole_dia:.1f}mm'
                else:
                    self.warning_label.text = ''
                
                # 計算ΔR (半徑總變化量)
                ΔR = (hole_dia - tool_dia) / 2
                
                # 計算斜坡角度 φ = arctan(d/ΔR)
                if ΔR > 0:
                    φ_rad = math.atan(depth / ΔR)
                    φ_deg = math.degrees(φ_rad)
                else:
                    self.warning_label.text = '計算錯誤：ΔR必須大於0'
                    return
                
                # 計算過程
                calc_process = f"""內徑螺旋銑計算過程：
1. 刀具直徑 Dc = {tool_dia} mm
2. 孔徑 Dm = {hole_dia} mm
3. 半徑變化量 ΔR = (Dm - Dc)/2 = ({hole_dia} - {tool_dia})/2 = {ΔR:.2f} mm
4. 總切削深度 d = {depth} mm
5. 斜坡角度 φ = arctan(d/ΔR) = arctan({depth}/{ΔR:.2f}) = {φ_deg:.2f}°
6. 最小加工孔徑建議值 = Dc × 1.2 = {tool_dia} × 1.2 = {min_hole_dia:.1f} mm

加工建議：
- 刀具從孔中心開始螺旋運動
- 適合孔徑大於刀具直徑1.2倍的情況
- 常用角度範圍：15°-45°
- 當前孔徑與刀具直徑比值：{hole_dia/tool_dia:.2f}"""
                
                # 詳細結果顯示
                self.detail_result_label.text = f'ΔR: {ΔR:.2f}mm | 孔徑比: {hole_dia/tool_dia:.2f}'
                
            elif milling_type == '外徑螺旋銑':
                boss_dia_text = self.dynamic_input1.text.strip()
                width_text = self.dynamic_input2.text.strip()
                
                if not boss_dia_text or not width_text:
                    self.warning_label.text = '錯誤：請輸入凸台直徑和切削寬度'
                    return
                    
                boss_dia = float(boss_dia_text)
                width = float(width_text)
                
                # 檢查輸入合理性
                if width <= 0:
                    self.warning_label.text = '錯誤：切削寬度必須大於0'
                    return
                
                # 計算斜坡角度 φ = arctan(d/W)
                ΔR = width
                φ_rad = math.atan(depth / ΔR)
                φ_deg = math.degrees(φ_rad)
                
                # 切削寬度W的建議值範圍
                w_min = tool_dia * 0.5
                w_max = tool_dia * 0.8
                
                if width < w_min:
                    self.warning_label.text = f'警告：切削寬度小於建議最小值 {w_min:.1f}mm'
                elif width > w_max:
                    self.warning_label.text = f'警告：切削寬度大於建議最大值 {w_max:.1f}mm'
                else:
                    self.warning_label.text = ''
                
                # 計算過程
                calc_process = f"""外徑螺旋銑計算過程：
1. 刀具直徑 Dc = {tool_dia} mm
2. 凸台直徑 Dm = {boss_dia} mm
3. 切削寬度 W = {width} mm
4. 總切削深度 d = {depth} mm
5. 斜坡角度 φ = arctan(d/W) = arctan({depth}/{width}) = {φ_deg:.2f}°

重要說明：
• 斜坡角度φ只與深度d和切削寬度W有關，與刀具直徑無關
• 刀具直徑Dc會影響W的建議值範圍
• W建議範圍：刀具直徑的50%-80% ({w_min:.1f}mm - {w_max:.1f}mm)

加工建議：
- 刀具從凸台外側開始螺旋向內
- 切削寬度W建議為刀具直徑的50-80%
- 適合凸台外部輪廓加工"""
                
                # 詳細結果顯示
                self.detail_result_label.text = f'W: {width}mm | φ只與d/W有關'
                
            else:  # 爬坡銑
                length_text = self.dynamic_input1.text.strip()
                if not length_text:
                    self.warning_label.text = '錯誤：請輸入斜坡長度'
                    return
                    
                length = float(length_text)
                
                # 檢查長度合理性
                if length <= 0:
                    self.warning_label.text = '錯誤：斜坡長度必須大於0'
                    return
                
                # 計算斜坡角度 φ = arctan(d/L)
                φ_rad = math.atan(depth / length)
                φ_deg = math.degrees(φ_rad)
                
                # 計算實際斜坡長度
                actual_length = math.sqrt(length**2 + depth**2)
                
                # 計算過程
                calc_process = f"""爬坡銑計算過程：
1. 斜坡長度 L = {length} mm
2. 總切削深度 d = {depth} mm
3. 斜坡角度 φ = arctan(d/L) = arctan({depth}/{length}) = {φ_deg:.2f}°
4. 實際斜坡長度 = √(L² + d²) = √({length}² + {depth}²) = {actual_length:.2f} mm

加工建議：
- 刀具沿斜線切入材料
- 常用於型腔初始切入或窄槽加工
- 常用角度範圍：5°-15°"""
                
                # 詳細結果顯示
                self.detail_result_label.text = f'斜坡長度: {length}mm | 實際長度: {actual_length:.2f}mm'
            
            # 更新顯示結果
            self.angle_result_label.text = f'斜坡角度 φ = {φ_deg:.2f}°'
            
            # 安全評估
            safety_text, safety_color, suggestion = self.get_safety_assessment(milling_type, φ_deg)
            
            self.safety_result_label.text = f'安全評估: {safety_text}'
            self.safety_result_label.color = safety_color
            self.suggestion_label.text = suggestion
            
            # 詳細計算過程
            self.calc_process_label.text = calc_process
            
        except ValueError:
            self.calc_process_label.text = '錯誤：請輸入有效的數字'
            self.warning_label.text = '所有輸入必須為數字'
        except Exception as e:
            self.calc_process_label.text = f'計算錯誤：{str(e)}'
            self.warning_label.text = '請檢查輸入參數'
    
    def get_safety_assessment(self, milling_type, angle_deg):
        """根據銑削類型和角度獲取安全評估"""
        if milling_type == '內徑螺旋銑':
            if angle_deg < 5:
                return "角度過小", (0.5, 0.5, 1, 1), "建議：角度太小，加工效率低"
            elif angle_deg < 15:
                return "偏小", (0, 0.5, 1, 1), "建議：角度稍小，可提高效率"
            elif angle_deg < 30:
                return "安全", (0, 0.8, 0, 1), "建議：角度適中，加工穩定"
            elif angle_deg < 45:
                return "注意", (1, 0.5, 0, 1), "建議：角度稍大，注意刀具負荷"
            else:
                return "危險", (1, 0, 0, 1), "建議：角度過大，建議分層加工"
                
        elif milling_type == '外徑螺旋銑':
            if angle_deg < 5:
                return "角度過小", (0.5, 0.5, 1, 1), "建議：角度太小，加工效率低"
            elif angle_deg < 15:
                return "安全", (0, 0.8, 0, 1), "建議：角度適中，加工穩定"
            elif angle_deg < 30:
                return "注意", (1, 0.5, 0, 1), "建議：角度稍大，注意刀具側向力"
            elif angle_deg < 45:
                return "危險", (1, 0.5, 0, 1), "建議：角度過大，需分層加工"
            else:
                return "極危險", (1, 0, 0, 1), "建議：角度過大，不建議使用"
                
        else:  # 爬坡銑
            if angle_deg < 3:
                return "角度過小", (0.5, 0.5, 1, 1), "建議：角度太小，加工效率低"
            elif angle_deg < 8:
                return "安全", (0, 0.8, 0, 1), "建議：角度適中，加工穩定"
            elif angle_deg < 15:
                return "注意", (1, 0.5, 0, 1), "建議：角度稍大，注意刀具負荷"
            elif angle_deg < 20:
                return "危險", (1, 0.5, 0, 1), "建議：角度過大，建議減小深度"
            else:
                return "極危險", (1, 0, 0, 1), "建議：角度過大，不建議使用"

class CuttingConditionCalculator(Screen):
    """切削條件計算器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 材料參數表
        self.material_params = {
            "鋁合金": {"vc_range": (500, 1000), "fz_rough": (0.10, 0.30), "fz_finish": (0.05, 0.15)},
            "不鏽鋼": {"vc_range": (100, 200), "fz_rough": (0.05, 0.20), "fz_finish": (0.03, 0.10)},
            "模具鋼": {"vc_range": (80, 150), "fz_rough": (0.05, 0.15), "fz_finish": (0.03, 0.10)},
            "碳鋼": {"vc_range": (150, 300), "fz_rough": (0.10, 0.30), "fz_finish": (0.05, 0.15)},
            "銅合金": {"vc_range": (150, 250), "fz_rough": (0.10, 0.25), "fz_finish": (0.05, 0.15)},
            "鈦合金": {"vc_range": (50, 100), "fz_rough": (0.05, 0.15), "fz_finish": (0.03, 0.10)},
            "塑膠": {"vc_range": (200, 500), "fz_rough": (0.10, 0.30), "fz_finish": (0.05, 0.20)}
        }
        
        # 主佈局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 標題和返回按鈕的佈局
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        # 返回按鈕
        back_btn = CustomButton(
            text='← 返回',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # 標題
        title = Label(
            text='切削條件計算器',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint=(0.8, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # 創建滾動視圖
        scroll = ScrollView(size_hint=(1, 0.8), bar_width=dp(10), bar_color=(0.5, 0.5, 0.5, 0.5))
        content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 輸入區域
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=dp(320))
        
        # 材質下拉選單
        input_layout.add_widget(Label(text='材質:', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.material_spinner = ChineseSpinner(
            text='鋁合金',
            values=['鋁合金', '不鏽鋼', '模具鋼', '碳鋼', '銅合金', '鈦合金', '塑膠'],
            font_size='16sp',
            size_hint_y=None,
            height=dp(50)
        )
        input_layout.add_widget(self.material_spinner)
        
        # 刀具直徑輸入
        input_layout.add_widget(Label(text='刀具直徑 (mm):', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.tool_dia_input = ValidatedTextInput(text='10', multiline=False, font_size='16sp', size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.tool_dia_input)
        
        # 刀具齒數輸入
        input_layout.add_widget(Label(text='刀具齒數:', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.tooth_input = ValidatedTextInput(text='3', multiline=False, font_size='16sp', size_hint_y=None, height=dp(50), input_filter='int')
        input_layout.add_widget(self.tooth_input)
        
        # 加工類型下拉選單
        input_layout.add_widget(Label(text='加工類型:', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.machining_spinner = ChineseSpinner(
            text='粗加工',
            values=['粗加工', '精加工'],
            font_size='16sp',
            size_hint_y=None,
            height=dp(50)
        )
        input_layout.add_widget(self.machining_spinner)
        
        # VC條件下拉選單
        input_layout.add_widget(Label(text='VC條件:', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.vc_spinner = ChineseSpinner(
            text='中',
            values=['高', '中', '低'],
            font_size='16sp',
            size_hint_y=None,
            height=dp(50)
        )
        input_layout.add_widget(self.vc_spinner)
        
        # 切削速度條件下拉選單
        input_layout.add_widget(Label(text='切削速度條件:', font_size='16sp', size_hint_y=None, height=dp(50), font_name='ChineseFont'))
        self.feed_spinner = ChineseSpinner(
            text='中',
            values=['高', '中', '低'],
            font_size='16sp',
            size_hint_y=None,
            height=dp(50)
        )
        input_layout.add_widget(self.feed_spinner)
        
        content_layout.add_widget(input_layout)
        
        # 結果顯示區域
        self.vc_result = Label(
            text='切削速度 VC: --',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            font_name='ChineseFont'
        )
        content_layout.add_widget(self.vc_result)
        
        self.fz_result = Label(
            text='每齒進給 fz: --',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            font_name='ChineseFont'
        )
        content_layout.add_widget(self.fz_result)
        
        self.m_result = Label(
            text='主軸轉速 M: --',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(50),
            font_name='ChineseFont'
        )
        content_layout.add_widget(self.m_result)
        
        self.feed_result = Label(
            text='進給速度 F: --',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(50),
            font_name='ChineseFont'
        )
        content_layout.add_widget(self.feed_result)
        
        self.detail_result = Label(
            text='詳細計算過程將顯示在這裡',
            font_size='12sp',
            size_hint_y=None,
            height=dp(300),
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        self.detail_result.bind(size=self.detail_result.setter('text_size'))
        content_layout.add_widget(self.detail_result)
        
        # 設置滾動視圖內容
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # 計算按鈕
        calc_btn = CustomButton(
            text='計算切削條件',
            size_hint_y=0.1,
            background_color=(1, 0.6, 0, 1),
            font_size='18sp',
            bold=True,
        )
        calc_btn.bind(on_press=lambda x: Clock.schedule_once(self.calculate, 0))
        main_layout.add_widget(calc_btn)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def calculate(self, dt):
        try:
            # 獲取輸入值
            material = self.material_spinner.text
            tool_dia_text = self.tool_dia_input.text.strip()
            tooth_text = self.tooth_input.text.strip()
            
            if not tool_dia_text or not tooth_text:
                self.m_result.text = "錯誤: 請輸入刀具直徑和齒數"
                return
                
            tool_diameter = float(tool_dia_text)
            tooth_count = int(tooth_text)
            machining_type = self.machining_spinner.text
            vc_condition = self.vc_spinner.text
            feed_condition = self.feed_spinner.text
            
            # 輸入驗證
            if tool_diameter <= 0:
                self.m_result.text = "錯誤: 刀具直徑必須大於0"
                return
                
            if tooth_count <= 0:
                self.m_result.text = "錯誤: 刀具齒數必須大於0"
                return
            
            if material not in self.material_params:
                self.m_result.text = "錯誤: 未知材料"
                return
            
            params = self.material_params[material]
            vc_min, vc_max = params["vc_range"]
            
            # 根據VC條件選擇VC值
            if vc_condition == "高":
                vc = vc_max
            elif vc_condition == "中":
                vc = (vc_min + vc_max) / 2
            else:  # 低
                vc = vc_min
            
            # 根據加工類型選擇fz範圍
            if machining_type == "粗加工":
                fz_min, fz_max = params["fz_rough"]
            else:  # 精加工
                fz_min, fz_max = params["fz_finish"]
            
            # 根據切削速度條件選擇fz值
            if feed_condition == "高":
                fz = fz_max
            elif feed_condition == "中":
                fz = (fz_min + fz_max) / 2
            else:  # 低
                fz = fz_min
            
            # 計算主軸轉速 M = (VC * 1000) / (π * D)
            m = (vc * 1000) / (math.pi * tool_diameter)
            
            # 限制轉速範圍（安全考慮）
            m = max(100, min(20000, m))  # 限制在100-20000 RPM之間
            
            # 計算進給速度 F = M * N * fz
            f = m * tooth_count * fz
            
            # 限制進給速度（安全考慮）
            f = max(10, min(5000, f))  # 限制在10-5000 mm/min之間
            
            # 更新結果
            self.vc_result.text = f"切削速度 VC: {vc:.0f} m/min (範圍: {vc_min}-{vc_max} m/min)"
            self.fz_result.text = f"每齒進給 fz: {fz:.3f} mm/tooth (範圍: {fz_min}-{fz_max} mm/tooth)"
            self.m_result.text = f"主軸轉速 M: {m:.0f} RPM"
            self.feed_result.text = f"進給速度 F: {f:.0f} mm/min"
            
            # 顯示詳細計算過程
            detail_text = f"""計算過程:
1. 材料: {material}
2. 加工類型: {machining_type}
3. VC條件: {vc_condition} (VC = {vc:.0f} m/min)
4. 切削速度條件: {feed_condition} (fz = {fz:.3f} mm/tooth)
5. 刀具直徑: {tool_diameter} mm
6. 刀具齒數: {tooth_count}

計算公式:
主軸轉速 M = (VC × 1000) ÷ (π × D)
        = ({vc} × 1000) ÷ (3.1416 × {tool_diameter})
        = {vc*1000:.0f} ÷ {math.pi*tool_diameter:.1f}
        = {m:.0f} RPM

進給速度 F = M × N × fz
        = {m:.0f} × {tooth_count} × {fz}
        = {f:.0f} mm/min

安全限制:
• 主軸轉速限制: 100-20000 RPM
• 進給速度限制: 10-5000 mm/min

建議:
• 根據實際機台性能調整參數
• 首次加工建議進行試切削
• 密切注意刀具磨損情況"""
            
            self.detail_result.text = detail_text
            
        except ValueError:
            self.m_result.text = "錯誤: 請輸入有效的數字"
        except Exception as e:
            self.m_result.text = f"計算錯誤: {str(e)}"

class StockAllowanceCalculator(Screen):
    """切削預留量計算器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 預留量數據
        self.allowance_data = {
            "鋁合金": {
                "平面": {"rough": 0.5, "semi_finish": 0.3, "tool": "3刃鋁用面銑刀 (直徑>50mm)", "notes": "確保裝夾牢固，避免震刀；易粘刀，注意排屑"},
                "底面": {"rough": 0.4, "semi_finish": 0.25, "tool": "3刃鋁用平底刀", "notes": "注意刀具懸伸，防止過切；易粘刀，注意排屑"},
                "曲面": {"rough": 0.6, "semi_finish": 0.4, "tool": "2刃球刀 (R1-R6)", "notes": "使用小步距，注意殘留高度；易粘刀，注意排屑"},
                "側壁": {"rough": 0.4, "semi_finish": 0.25, "tool": "3刃鋁用平底刀", "notes": "注意刀具偏擺，檢查垂直度；易粘刀，注意排屑"},
                "型腔": {"rough": 0.5, "semi_finish": 0.3, "tool": "3刃鋁用平底刀", "notes": "分層加工，注意角部清角；易粘刀，注意排屑"},
                "孔加工": {"rough": 0.25, "semi_finish": 0.15, "tool": "中心鑽+螺旋銑刀", "notes": "中心鑽先定位，注意排屑；易粘刀，注意排屑"}
            },
            "不鏽鋼": {
                "平面": {"rough": 0.75, "semi_finish": 0.5, "tool": "4刃面銑刀 (塗層)", "notes": "確保裝夾牢固，避免震刀；加工硬化，小切深"},
                "底面": {"rough": 0.6, "semi_finish": 0.4, "tool": "4刃平底刀 (塗層)", "notes": "注意刀具懸伸，防止過切；加工硬化，小切深"},
                "曲面": {"rough": 1.0, "semi_finish": 0.8, "tool": "2刃球刀 (塗層)", "notes": "使用小步距，注意殘留高度；加工硬化，小切深"},
                "側壁": {"rough": 0.6, "semi_finish": 0.4, "tool": "4刃平底刀 (塗層)", "notes": "注意刀具偏擺，檢查垂直度；加工硬化，小切深"},
                "型腔": {"rough": 0.75, "semi_finish": 0.5, "tool": "4刃平底刀 (塗層)", "notes": "分層加工，注意角部清角；加工硬化，小切深"},
                "孔加工": {"rough": 0.4, "semi_finish": 0.25, "tool": "中心鑽+鑽頭+絞刀", "notes": "中心鑽先定位，注意排屑；加工硬化，小切深"}
            },
            "模具鋼": {
                "平面": {"rough": 0.6, "semi_finish": 0.4, "tool": "4刃塗層面銑刀", "notes": "確保裝夾牢固，避免震刀"},
                "底面": {"rough": 0.5, "semi_finish": 0.3, "tool": "4刃塗層平底刀", "notes": "注意刀具懸伸，防止過切"},
                "曲面": {"rough": 0.75, "semi_finish": 0.6, "tool": "2刃塗層球刀", "notes": "使用小步距，注意殘留高度"},
                "側壁": {"rough": 0.5, "semi_finish": 0.3, "tool": "4刃塗層平底刀", "notes": "注意刀具偏擺，檢查垂直度"},
                "型腔": {"rough": 0.6, "semi_finish": 0.4, "tool": "4刃塗層平底刀", "notes": "分層加工，注意角部清角"},
                "孔加工": {"rough": 0.3, "semi_finish": 0.2, "tool": "中心鑽+鑽頭+放電", "notes": "中心鑽先定位，注意排屑"}
            },
            "碳鋼": {
                "平面": {"rough": 0.5, "semi_finish": 0.35, "tool": "4刃塗層面銑刀", "notes": "確保裝夾牢固，避免震刀"},
                "底面": {"rough": 0.4, "semi_finish": 0.25, "tool": "4刃塗層平底刀", "notes": "注意刀具懸伸，防止過切"},
                "曲面": {"rough": 0.65, "semi_finish": 0.5, "tool": "2刃塗層球刀", "notes": "使用小步距，注意殘留高度"},
                "側壁": {"rough": 0.4, "semi_finish": 0.25, "tool": "4刃塗層平底刀", "notes": "注意刀具偏擺，檢查垂直度"},
                "型腔": {"rough": 0.5, "semi_finish": 0.35, "tool": "4刃塗層平底刀", "notes": "分層加工，注意角部清角"},
                "孔加工": {"rough": 0.25, "semi_finish": 0.18, "tool": "中心鑽+鑽頭", "notes": "中心鑽先定位，注意排屑"}
            },
            "銅合金": {
                "平面": {"rough": 0.4, "semi_finish": 0.25, "tool": "3刃銅用面銑刀", "notes": "確保裝夾牢固，避免震刀"},
                "底面": {"rough": 0.3, "semi_finish": 0.2, "tool": "3刃銅用平底刀", "notes": "注意刀具懸伸，防止過切"},
                "曲面": {"rough": 0.5, "semi_finish": 0.35, "tool": "2刃銅用球刀", "notes": "使用小步距，注意殘留高度"},
                "側壁": {"rough": 0.3, "semi_finish": 0.2, "tool": "3刃銅用平底刀", "notes": "注意刀具偏擺，檢查垂直度"},
                "型腔": {"rough": 0.4, "semi_finish": 0.25, "tool": "3刃銅用平底刀", "notes": "分層加工，注意角部清角"},
                "孔加工": {"rough": 0.2, "semi_finish": 0.12, "tool": "中心鑽+鑽頭", "notes": "中心鑽先定位，注意排屑"}
            },
            "鈦合金": {
                "平面": {"rough": 1.0, "semi_finish": 0.8, "tool": "3刃鈦用面銑刀", "notes": "確保裝夾牢固，避免震刀；散熱差，低轉速"},
                "底面": {"rough": 0.75, "semi_finish": 0.6, "tool": "3刃鈦用平底刀", "notes": "注意刀具懸伸，防止過切；散熱差，低轉速"},
                "曲面": {"rough": 1.25, "semi_finish": 1.0, "tool": "2刃鈦用球刀", "notes": "使用小步距，注意殘留高度；散熱差，低轉速"},
                "側壁": {"rough": 0.75, "semi_finish": 0.6, "tool": "3刃鈦用平底刀", "notes": "注意刀具偏擺，檢查垂直度；散熱差，低轉速"},
                "型腔": {"rough": 1.0, "semi_finish": 0.8, "tool": "3刃鈦用平底刀", "notes": "分層加工，注意角部清角；散熱差，低轉速"},
                "孔加工": {"rough": 0.5, "semi_finish": 0.3, "tool": "中心鑽+鈦用鑽頭", "notes": "中心鑽先定位，注意排屑；散熱差，低轉速"}
            },
            "塑膠": {
                "平面": {"rough": 0.25, "semi_finish": 0.15, "tool": "2刃塑膠用面銑刀", "notes": "確保裝夾牢固，避免震刀；易變形，空冷加工"},
                "底面": {"rough": 0.2, "semi_finish": 0.1, "tool": "2刃塑膠用平底刀", "notes": "注意刀具懸伸，防止過切；易變形，空冷加工"},
                "曲面": {"rough": 0.4, "semi_finish": 0.25, "tool": "2刃塑膠用球刀", "notes": "使用小步距，注意殘留高度；易變形，空冷加工"},
                "側壁": {"rough": 0.2, "semi_finish": 0.1, "tool": "2刃塑膠用平底刀", "notes": "注意刀具偏擺，檢查垂直度；易變形，空冷加工"},
                "型腔": {"rough": 0.25, "semi_finish": 0.15, "tool": "2刃塑膠用平底刀", "notes": "分層加工，注意角部清角；易變形，空冷加工"},
                "孔加工": {"rough": 0.15, "semi_finish": 0.08, "tool": "中心鑽+塑膠鑽頭", "notes": "中心鑽先定位，注意排屑；易變形，空冷加工"}
            }
        }
        
        # 主佈局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 標題和返回按鈕的佈局
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        # 返回按鈕
        back_btn = CustomButton(
            text='← 返回',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # 標題
        title = Label(
            text='切削預留量計算器',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1),
            font_name='ChineseFont',
            size_hint=(0.8, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # 輸入區域
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.2)
        
        input_layout.add_widget(Label(text='材質:', font_size='16sp', font_name='ChineseFont'))
        self.material_spinner = ChineseSpinner(
            text='鋁合金',
            values=['鋁合金', '不鏽鋼', '模具鋼', '碳鋼', '銅合金', '鈦合金', '塑膠'],
            font_size='16sp'
        )
        input_layout.add_widget(self.material_spinner)
        
        input_layout.add_widget(Label(text='加工類型:', font_size='16sp', font_name='ChineseFont'))
        self.machining_spinner = ChineseSpinner(
            text='平面',
            values=['平面', '底面', '曲面', '側壁', '型腔', '孔加工'],
            font_size='16sp'
        )
        input_layout.add_widget(self.machining_spinner)
        
        main_layout.add_widget(input_layout)
        
        # 查詢按鈕
        query_btn = CustomButton(
            text='查詢預留量',
            size_hint_y=0.1,
            background_color=(0.93, 0.41, 0.19, 1),
            font_size='18sp',
            bold=True,
        )
        query_btn.bind(on_press=lambda x: Clock.schedule_once(self.query, 0))
        main_layout.add_widget(query_btn)
        
        # 結果顯示
        self.rough_label = Label(
            text='單邊預留(粗加工): --',
            font_size='16sp',
            size_hint_y=0.1,
            font_name='ChineseFont'
        )
        main_layout.add_widget(self.rough_label)
        
        self.semi_finish_label = Label(
            text='半精加工: --',
            font_size='16sp',
            size_hint_y=0.1,
            font_name='ChineseFont'
        )
        main_layout.add_widget(self.semi_finish_label)
        
        self.tool_label = Label(
            text='參考刀具: --',
            font_size='16sp',
            size_hint_y=0.1,
            font_name='ChineseFont'
        )
        main_layout.add_widget(self.tool_label)
        
        self.detail_label = Label(
            text='詳細信息將顯示在這裡',
            font_size='14sp',
            size_hint_y=0.5,
            halign='left',
            valign='top',
            font_name='ChineseFont'
        )
        self.detail_label.bind(size=self.detail_label.setter('text_size'))
        main_layout.add_widget(self.detail_label)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def query(self, dt):
        material = self.material_spinner.text
        machining_type = self.machining_spinner.text
        
        if material in self.allowance_data and machining_type in self.allowance_data[material]:
            data = self.allowance_data[material][machining_type]
            
            self.rough_label.text = f"單邊預留(粗加工): {data['rough']} mm"
            self.semi_finish_label.text = f"半精加工: {data['semi_finish']} mm"
            self.tool_label.text = f"參考刀具: {data['tool']}"
            
            detail_text = f"""材質: {material}
加工類型: {machining_type}

加工參數建議:
• 單邊粗加工預留: {data['rough']} mm
• 半精加工預留: {data['semi_finish']} mm
• 總預留量建議: {data['rough'] + data['semi_finish'] + 0.1:.2f} mm

刀具推薦: {data['tool']}

注意事項: {data['notes']}

加工建議:
1. 粗加工: 去除大部分材料，保留{data['rough']}mm單邊餘量
2. 半精加工: 精確加工，保留{data['semi_finish']}mm單邊餘量
3. 精加工: 最終加工，達到圖紙尺寸要求

數據來源: CNC銑削加工預留量表
            
版本備註:
• v2.9: 增加輸入驗證和性能優化
• 更新日期: 2024年1月"""
            
            self.detail_label.text = detail_text
        else:
            self.rough_label.text = "單邊預留(粗加工): 無數據"
            self.semi_finish_label.text = "半精加工: 無數據"
            self.tool_label.text = "參考刀具: 無數據"
            self.detail_label.text = "錯誤: 找不到對應的預留量數據"

class CNCApp(App):
    """主應用程序"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def build(self):
        self.title = 'CNC加工工具包 v2.9 - 歐盛珠寶股份有限公司 ERREPI TAIWAN'
        
        # 創建屏幕管理器
        sm = ScreenManager()
        
        # 添加各個屏幕
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ToolCalculator(name='tool_calc'))
        sm.add_widget(BallMillCalculator(name='ballmill_calc'))
        sm.add_widget(HelicalCalculator(name='helical_calc'))
        sm.add_widget(CuttingConditionCalculator(name='cutting_calc'))
        sm.add_widget(StockAllowanceCalculator(name='stock_calc'))
        
        return sm
    
    def on_pause(self):
        """應用暫停時調用（Android）"""
        # 保存應用狀態
        return True
    
    def on_resume(self):
        """應用恢復時調用（Android）"""
        # 恢復應用狀態
        pass

if __name__ == '__main__':
    # 設置窗口背景色
    Window.clearcolor = (0.95, 0.95, 0.95, 1)
    
    # 運行應用
    CNCApp().run()
