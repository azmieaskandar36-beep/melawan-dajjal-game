from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle, Line, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.clock import Clock
import os
import json
import math
import urllib.parse
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VISUAL_DIR = os.path.join(PROJECT_DIR, "assets_visual")
VIDEO_DIR = os.path.join(PROJECT_DIR, "assets_video")
AUDIO_DIR = os.path.join(PROJECT_DIR, "assets_audio")

SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")

def load_game_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                return data.get("max_unlocked_level", 1)
        except:
            return 1
    return 1

def save_game_progress(level):
    try:
        data = {"max_unlocked_level": level}
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass


class CinematicProgressBar(FloatLayout):
    def __init__(self, **kwargs):
        super(CinematicProgressBar, self).__init__(**kwargs)
        self.max_val = 100
        self.current_val = 0
        
        with self.canvas:
            Color(0.1, 0.1, 0.1, 0.7)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            Color(0.85, 0.1, 0.1, 1)
            self.bar_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[6])
            Color(0.4, 0.4, 0.4, 0.8)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 6), width=1.2)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_value(self, value):
        self.current_val = max(0, min(value, self.max_val))
        self.update_canvas()

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 6)
        fill_width = self.width * (self.current_val / self.max_val)
        self.bar_rect.pos = self.pos
        self.bar_rect.size = (fill_width, self.height)


class RoundedButton(Button):
    def __init__(self, bg_image=None, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bg_image = bg_image
        
        with self.canvas.before:
            StencilPush()
            self.clip_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            StencilUse()
            if self.bg_image and os.path.exists(self.bg_image):
                self.img = Image(source=self.bg_image, allow_stretch=True, keep_ratio=False, pos=self.pos, size=self.size)
            else:
                self.img = None
            StencilUnUse()
            Color(0.3, 0.3, 0.3, 1)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 14), width=1.2)
            StencilPop()
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.clip_rect.pos = self.pos
        self.clip_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 14)
        if self.img:
            self.img.pos = self.pos
            self.img.size = self.size


class CapsuleButton(Button):
    def __init__(self, bg_color=(0.15, 0.15, 0.15, 0.65), border_color=(0.9, 0.9, 0.9, 0.9), radius=18, **kwargs):
        super(CapsuleButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.custom_bg_color = bg_color
        self.custom_border_color = border_color
        self.radius = radius
        
        with self.canvas.before:
            Color(*self.custom_bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            Color(*self.custom_border_color)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.5)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


# 1. Layar Loading Screen
class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        bg_path = os.path.join(VISUAL_DIR, "bg_loading.jpg")
        if os.path.exists(bg_path):
            self.bg = Image(source=bg_path, allow_stretch=True, keep_ratio=False, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            self.layout.add_widget(self.bg)

        self.custom_bar = CinematicProgressBar(size_hint=(0.75, 0.022), pos_hint={'center_x': 0.5, 'y': 0.22})
        self.layout.add_widget(self.custom_bar)

        self.percent_label = Label(text="MEMUAT 0%", font_size='14sp', bold=True, color=(0.9, 0.9, 0.9, 0.9), size_hint=(0.8, 0.05), pos_hint={'center_x': 0.5, 'y': 0.26})
        self.layout.add_widget(self.percent_label)

        self.quotes = [
            "\"Waspadalah terhadap fitnah terbesar di akhir zaman...\"",
            "\"Setiap pilihan yang kamu ambil menentukan arah keselamatan iman.\"",
            "\"Berpegang teguhlah pada prinsip tauhid, jangan mudah terbuai tipu daya.\""
        ]
        self.quote_index = 0
        self.quote_label = Label(text=self.quotes[0], font_size='13sp', italic=True, color=(0.85, 0.85, 0.85, 1), halign='center', valign='middle', size_hint=(0.85, 0.08), pos_hint={'center_x': 0.5, 'y': 0.12})
        self.quote_label.bind(size=self.quote_label.setter('text_size'))
        self.layout.add_widget(self.quote_label)

        with self.layout.canvas.after:
            Color(0, 0, 0, 0)
            self.fade_rect = RoundedRectangle(pos=(0,0), size=(1000, 1000))
        self.bind(size=self.update_fade_rect)
        self.add_widget(self.layout)

        self.load_progress = 0
        self.is_fading = False
        Clock.schedule_interval(self.update_loading, 0.04)
        Clock.schedule_interval(self.change_quote, 1.0)

    def update_fade_rect(self, *args):
        self.fade_rect.size = self.size

    def update_loading(self, dt):
        if not self.is_fading:
            if self.load_progress < 100:
                self.load_progress += 1
                self.custom_bar.set_value(self.load_progress)
                self.percent_label.text = f"MEMUAT {self.load_progress}%"
            else:
                self.is_fading = True
                self.fade_alpha = 0.0
                Clock.unschedule(self.change_quote)
                Clock.schedule_interval(self.do_fade_out, 0.02)
        
    def do_fade_out(self, dt):
        self.fade_alpha += 0.05
        if self.fade_alpha >= 1.0:
            self.fade_alpha = 1.0
            Clock.unschedule(self.do_fade_out)
            self.manager.current = 'menu_screen'
            self.layout.canvas.after.clear()
        
        self.layout.canvas.after.clear()
        with self.layout.canvas.after:
            Color(0, 0, 0, self.fade_alpha)
            self.fade_rect = RoundedRectangle(pos=(0,0), size=self.size)

    def change_quote(self, dt):
        self.quote_index = (self.quote_index + 1) % len(self.quotes)
        self.quote_label.text = self.quotes[self.quote_index]


# 2. Layar Menu Pilih Level
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.08, 0.08, 0.1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.header_layout = FloatLayout(size_hint=(0.0, 0.0), opacity=0, pos_hint={'center_x': 0.5, 'top': 0.94})
        with self.header_layout.canvas.before:
            Color(0.2, 0.2, 0.22, 1)
            self.cap_bg = RoundedRectangle(pos=self.header_layout.pos, size=self.header_layout.size, radius=[18])
            Color(0.85, 0.1, 0.1, 1)
            self.cap_border = Line(rounded_rectangle=(self.header_layout.x, self.header_layout.y, self.header_layout.width, self.header_layout.height, 18), width=1.5)
        
        def update_header_canvas(instance, value):
            self.cap_bg.pos = instance.pos
            self.cap_bg.size = instance.size
            self.cap_border.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, 18)
        self.header_layout.bind(pos=update_header_canvas, size=update_header_canvas)

        self.title_label = Label(text="SELESAIKAN LEVEL DI BAWAH INI", font_size='13sp', bold=True, color=(1, 1, 1, 1), size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}, halign='center', valign='middle')
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.header_layout.add_widget(self.title_label)
        self.layout.add_widget(self.header_layout)

        level_titles = {
            1: "Simpang Jalan Keyakinan",
            2: "Ujian Darah dan Ikatan",
            3: "Bayang-Bayang Kelaparan",
            4: "Fatwa Penyesatan",
            5: "Titik Nadir Iman"
        }

        self.grid_layout = GridLayout(cols=2, spacing=15, padding=[15, 10, 15, 20], size_hint=(0.95, 0.78), pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.cards = []
        
        for i in range(1, 6):
            card = BoxLayout(orientation='vertical', spacing=4, opacity=0)
            thumb_path = os.path.join(VISUAL_DIR, f"thumb_{i}.jpg")
            if not os.path.exists(thumb_path):
                thumb_path = None
                
            thumb_btn = RoundedButton(bg_image=thumb_path, size_hint=(1, 0.70))
            thumb_btn.level_num = i
            thumb_btn.bind(on_press=self.on_level_selected)
            card.add_widget(thumb_btn)
            
            lbl_status = Label(text="", font_size='11sp', bold=True, size_hint=(1, 0.10), halign='left', valign='middle')
            lbl_status.bind(size=lbl_status.setter('text_size'))
            card.add_widget(lbl_status)
            
            lbl_title = Label(text=level_titles.get(i, ""), font_size='12sp', bold=True, size_hint=(1, 0.20), halign='left', valign='top')
            lbl_title.bind(size=lbl_title.setter('text_size'))
            card.add_widget(lbl_title)
            
            card.lbl_status = lbl_status
            card.lbl_title = lbl_title
            card.thumb_btn = thumb_btn
            self.cards.append(card)
            self.grid_layout.add_widget(card)

        self.layout.add_widget(self.grid_layout)
        self.add_widget(self.layout)

    def on_enter(self):
        self.max_unlocked = load_game_progress()
        for i, card in enumerate(self.cards):
            lvl = i + 1
            is_unlocked = lvl <= self.max_unlocked
            card.thumb_btn.is_unlocked = is_unlocked
            if not card.thumb_btn.bg_image:
                card.thumb_btn.background_color = (0.7, 0.1, 0.1, 1) if is_unlocked else (0.3, 0.3, 0.3, 1)
            card.lbl_status.text = f"LEVEL {lvl}" if is_unlocked else f"LEVEL {lvl} (LOCKED)"
            card.lbl_status.color = (0.9, 0.2, 0.2, 1) if is_unlocked else (0.5, 0.5, 0.5, 1)
            card.lbl_title.color = (1, 1, 1, 1) if is_unlocked else (0.5, 0.5, 0.5, 1)

        self.anim_time = 0.0
        self.header_layout.size_hint = (0.0, 0.0)
        self.header_layout.opacity = 0
        for card in self.cards:
            card.opacity = 0
        Clock.schedule_interval(self.do_staggered_bounce, 0.02)

    def do_staggered_bounce(self, dt):
        self.anim_time += 0.03
        header_progress = min(1.0, self.anim_time / 0.4)
        if header_progress > 0:
            elastic_header = 1 + math.sin(header_progress * math.pi * 1.5) * (1 - header_progress) * 0.25
            if header_progress >= 1.0:
                elastic_header = 1.0
            self.header_layout.size_hint = (0.92 * elastic_header, 0.07 * elastic_header)
            self.header_layout.opacity = min(1.0, header_progress * 2)

        for i, card in enumerate(self.cards):
            delay = 0.2 + (i * 0.08)
            card_progress = max(0.0, min(1.0, (self.anim_time - delay) / 0.35))
            if card_progress > 0:
                card.opacity = min(1.0, card_progress * 2.5)

        if self.anim_time > 1.2:
            Clock.unschedule(self.do_staggered_bounce)

    def update_bg(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_level_selected(self, instance):
        if instance.is_unlocked:
            app = App.get_running_app()
            app.current_level = instance.level_num
            self.manager.transition = FadeTransition(duration=0.5)
            self.manager.current = 'cutscene_screen'
        else:
            print(f"Level {instance.level_num} masih terkunci!")


# 3. Layar Fase 3: Cutscene dengan Tombol Hotspot Transparan Penuh (Border 0.0)
class CutsceneScreen(Screen):
    def __init__(self, **kwargs):
        super(CutsceneScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_bg)

        self.video_player = None
        self.hotspots_layout = None
        self.game_over_panel = None
        self.timer_label = None
        self.target_pause_time = 0.0
        self.is_paused_for_choice = False
        
        with self.layout.canvas.after:
            self.fade_color = Color(0, 0, 0, 1)
            self.fade_overlay = RoundedRectangle(pos=(0,0), size=(2000, 2000))
        self.bind(size=self.update_fade_overlay)

        self.add_widget(self.layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_fade_overlay(self, *args):
        self.fade_overlay.size = self.size

    def on_enter(self):
        app = App.get_running_app()
        lvl = getattr(app, 'current_level', 1)
        
        pause_times = {
            1: 41.0,
            2: 69.0,
            3: 64.0,
            4: 78.0,
            5: 90.0
        }
        self.target_pause_time = pause_times.get(lvl, 30.0)
        self.is_paused_for_choice = False

        video_path = os.path.join(VIDEO_DIR, f"level_{lvl}.mp4")
        
        if self.video_player:
            self.layout.remove_widget(self.video_player)
            self.video_player = None
        if self.hotspots_layout:
            self.layout.remove_widget(self.hotspots_layout)
            self.hotspots_layout = None
        if self.game_over_panel:
            self.layout.remove_widget(self.game_over_panel)
            self.game_over_panel = None
        if self.timer_label:
            self.layout.remove_widget(self.timer_label)
            self.timer_label = None

        if os.path.exists(video_path):
            self.video_player = Video(
                source=video_path, 
                state='play', 
                options={'eos': 'pause'}, 
                size_hint=(1, 1), 
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.video_player.bind(position=self.check_pause_position)
            self.layout.add_widget(self.video_player)

        self.timer_label = Label(
            text="00:00 / 00:00",
            font_size='11sp',
            color=(0.9, 0.9, 0.9, 0.8),
            size_hint=(None, None),
            size=(100, 30),
            pos_hint={'x': 0.03, 'top': 0.96},
            halign='left',
            valign='middle'
        )
        self.timer_label.bind(size=self.timer_label.setter('text_size'))
        self.layout.add_widget(self.timer_label)

        self.current_fade_alpha = 1.0
        Clock.schedule_interval(self.do_fade_in, 0.03)

    def do_fade_in(self, dt):
        self.current_fade_alpha -= 0.05
        if self.current_fade_alpha <= 0.0:
            self.current_fade_alpha = 0.0
            Clock.unschedule(self.do_fade_in)
        self.fade_color.rgba = (0, 0, 0, self.current_fade_alpha)

    def check_pause_position(self, instance, pos):
        if instance.duration > 0:
            curr_m = int(pos // 60)
            curr_s = int(pos % 60)
            dur_m = int(instance.duration // 60)
            dur_s = int(instance.duration % 60)
            self.timer_label.text = f"{curr_m:02d}:{curr_s:02d} / {dur_m:02d}:{dur_s:02d}"

        if not self.is_paused_for_choice and pos >= self.target_pause_time:
            self.trigger_pause_state()

    def trigger_pause_state(self):
        if self.is_paused_for_choice:
            return
        self.is_paused_for_choice = True
        
        if self.video_player:
            self.video_player.state = 'pause'

        app = App.get_running_app()
        lvl = getattr(app, 'current_level', 1)
        self.show_transparent_hotspots(lvl)

    def show_transparent_hotspots(self, current_lvl):
        if self.hotspots_layout:
            return

        self.hotspots_layout = FloatLayout(size_hint=(1, 1))

        if current_lvl in [1, 5]:
            top_is_success = True
            bottom_is_success = False
        else:
            top_is_success = False
            bottom_is_success = True

        level_coords = {
            1: {'size': (0.50, 0.055), 'top_pos': {'center_x': 0.5, 'center_y': 0.624}, 'bottom_pos': {'center_x': 0.5, 'center_y': 0.550}},
            2: {'size': (0.50, 0.055), 'top_pos': {'center_x': 0.5, 'center_y': 0.705}, 'bottom_pos': {'center_x': 0.5, 'center_y': 0.629}},
            3: {'size': (0.50, 0.055), 'top_pos': {'center_x': 0.5, 'center_y': 0.729}, 'bottom_pos': {'center_x': 0.5, 'center_y': 0.654}},
            4: {'size': (0.55, 0.055), 'top_pos': {'center_x': 0.5, 'center_y': 0.729}, 'bottom_pos': {'center_x': 0.5, 'center_y': 0.654}},
            5: {'size': (0.43, 0.055), 'top_pos': {'center_x': 0.5, 'center_y': 0.729}, 'bottom_pos': {'center_x': 0.5, 'center_y': 0.654}}
        }

        cfg = level_coords.get(current_lvl, level_coords[1])

        btn_top = CapsuleButton(
            text="", bg_color=(0, 0, 0, 0.0), border_color=(0, 0, 0, 0.0), radius=18,
            size_hint=cfg['size'], pos_hint=cfg['top_pos']
        )
        btn_top.bind(on_press=lambda x: self.resolve_choice(current_lvl, top_is_success))
        
        btn_bottom = CapsuleButton(
            text="", bg_color=(0, 0, 0, 0.0), border_color=(0, 0, 0, 0.0), radius=18,
            size_hint=cfg['size'], pos_hint=cfg['bottom_pos']
        )
        btn_bottom.bind(on_press=lambda x: self.resolve_choice(current_lvl, bottom_is_success))

        self.hotspots_layout.add_widget(btn_bottom)
        self.hotspots_layout.add_widget(btn_top)
        self.layout.add_widget(self.hotspots_layout)

    def play_sound(self, is_correct):
        sfx_name = "sound_correct.wav" if is_correct else "sound_wrong.wav"
        sfx_path = os.path.join(AUDIO_DIR, sfx_name)
        if os.path.exists(sfx_path):
            sound = SoundLoader.load(sfx_path)
            if sound:
                sound.play()

    def resolve_choice(self, current_lvl, is_success):
        if self.hotspots_layout:
            self.layout.remove_widget(self.hotspots_layout)
            self.hotspots_layout = None
        if self.timer_label:
            self.layout.remove_widget(self.timer_label)
            self.timer_label = None

        if is_success:
            self.play_sound(True)
            if current_lvl == 5:
                self.manager.transition = FadeTransition(duration=0.6)
                self.manager.current = 'victory_photo_screen'
            else:
                next_lvl = current_lvl + 1
                max_unlocked = load_game_progress()
                if next_lvl > max_unlocked and next_lvl <= 5:
                    save_game_progress(next_lvl)
                
                app = App.get_running_app()
                app.current_level = next_lvl
                
                self.current_fade_alpha = 0.0
                Clock.schedule_interval(self.do_fade_out_to_next_video, 0.03)
        else:
            self.play_sound(False)
            self.show_game_over_panel(current_lvl)

    def show_game_over_panel(self, current_lvl):
        if self.game_over_panel:
            return

        self.game_over_panel = FloatLayout(size_hint=(0.85, 0.38), pos_hint={'center_x': 0.5, 'center_y': 0.46})
        box = BoxLayout(orientation='vertical', spacing=10, padding=[12, 12, 12, 12], size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        lbl_title = Label(text="PERINGATAN: IMAN TERPEDAYA!", font_size='11.5sp', bold=True, color=(0.9, 0.2, 0.2, 1), size_hint=(1, 0.25), halign='center', valign='middle')
        lbl_title.bind(size=lbl_title.setter('text_size'))
        box.add_widget(lbl_title)

        lbl_warning = Label(text="Jawaban Anda salah.", font_size='11sp', italic=True, color=(0.95, 0.95, 0.95, 1), size_hint=(1, 0.35), halign='center', valign='middle')
        lbl_warning.bind(size=lbl_warning.setter('text_size'))
        box.add_widget(lbl_warning)

        btn_layout = BoxLayout(orientation='horizontal', spacing=6, size_hint=(1, 0.3), pos_hint={'center_x': 0.5})

        btn_replay = CapsuleButton(text="REPLAY", bg_color=(0.2, 0.5, 0.8, 1), border_color=(0.3, 0.6, 0.9, 1), radius=14, size_hint=(1, 1))
        btn_replay.font_size = '8.5sp'; btn_replay.bold = True; btn_replay.color = (1, 1, 1, 1); btn_replay.halign = 'center'; btn_replay.valign = 'middle'
        btn_replay.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        btn_replay.bind(on_press=lambda x: self.action_replay_video())
        btn_layout.add_widget(btn_replay)

        btn_choose = CapsuleButton(text="PILIH LAGI", bg_color=(0.2, 0.7, 0.3, 1), border_color=(0.3, 0.8, 0.4, 1), radius=14, size_hint=(1, 1))
        btn_choose.font_size = '8.5sp'; btn_choose.bold = True; btn_choose.color = (1, 1, 1, 1); btn_choose.halign = 'center'; btn_choose.valign = 'middle'
        btn_choose.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        btn_choose.bind(on_press=lambda x: self.action_choose_again())
        btn_layout.add_widget(btn_choose)

        btn_menu = CapsuleButton(text="MENU", bg_color=(0.5, 0.5, 0.5, 1), border_color=(0.6, 0.6, 0.6, 1), radius=14, size_hint=(1, 1))
        btn_menu.font_size = '8.5sp'; btn_menu.bold = True; btn_menu.color = (1, 1, 1, 1); btn_menu.halign = 'center'; btn_menu.valign = 'middle'
        btn_menu.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        btn_menu.bind(on_press=lambda x: self.action_back_to_menu())
        btn_layout.add_widget(btn_menu)

        box.add_widget(btn_layout)
        self.game_over_panel.add_widget(box)
        self.layout.add_widget(self.game_over_panel)

    def action_replay_video(self):
        if self.game_over_panel:
            self.layout.remove_widget(self.game_over_panel)
            self.game_over_panel = None
        if self.video_player:
            self.video_player.position = 0
            self.video_player.state = 'play'
        self.is_paused_for_choice = False

    def action_choose_again(self):
        if self.game_over_panel:
            self.layout.remove_widget(self.game_over_panel)
            self.game_over_panel = None
        app = App.get_running_app()
        lvl = getattr(app, 'current_level', 1)
        self.show_transparent_hotspots(lvl)

    def action_back_to_menu(self):
        self.manager.transition = SlideTransition(duration=0.4)
        self.manager.current = 'menu_screen'

    def do_fade_out_to_next_video(self, dt):
        self.current_fade_alpha += 0.05
        if self.current_fade_alpha >= 1.0:
            self.current_fade_alpha = 1.0
            Clock.unschedule(self.do_fade_out_to_next_video)
            self.on_enter()
        self.fade_color.rgba = (0, 0, 0, self.current_fade_alpha)


# ==========================================
# 4. FASE EMPAT: LAYAR APRESIASI (FOTO victory_photo.jpg & AUDIO BGM LOOPING)
# ==========================================
class VictoryPhotoScreen(Screen):
    def __init__(self, **kwargs):
        super(VictoryPhotoScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.05, 0.05, 0.08, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda inst, val: setattr(self.bg, 'size', val))

        self.sound = None

        photo_path = os.path.join(VISUAL_DIR, "victory_photo.jpg")
        
        self.img_victory = Image(
            source=photo_path if os.path.exists(photo_path) else "",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.layout.add_widget(self.img_victory)

        self.btn_next = CapsuleButton(
            text="LEWATI APRESIASI & LANJUT KE ULASAN", 
            bg_color=(0.85, 0.1, 0.1, 1), 
            border_color=(1, 0.3, 0.3, 1), 
            radius=16,
            size_hint=(None, None),
            size=(280, 40),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        self.btn_next.font_size = '9.5sp'
        self.btn_next.bold = True
        self.btn_next.color = (1, 1, 1, 1)
        self.btn_next.halign = 'center'
        self.btn_next.valign = 'middle'
        self.btn_next.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self.btn_next.bind(on_press=self.on_next_pressed)
        
        self.layout.add_widget(self.btn_next)
        self.add_widget(self.layout)

    def on_enter(self):
        audio_path = os.path.join(AUDIO_DIR, "bgm_appreciation.mp3")
        if os.path.exists(audio_path):
            self.sound = SoundLoader.load(audio_path)
            if self.sound:
                self.sound.loop = True
                self.sound.play()

    def on_leave(self):
        if self.sound:
            self.sound.stop()

    def on_next_pressed(self, instance):
        if self.sound:
            self.sound.stop()
        self.manager.transition = FadeTransition(duration=0.5)
        self.manager.current = 'appreciation_screen'


# ==========================================
# 5. FASE LIMA: ULASAN & RATING & KIRIM KE WHATSAPP
# ==========================================
class AppreciationScreen(Screen):
    def __init__(self, **kwargs):
        super(AppreciationScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.05, 0.05, 0.08, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda inst, val: setattr(self.bg, 'size', val))

        self.bgm = None
        self.current_rating = 5
        self.build_form_ui()
        self.add_widget(self.layout)

    def on_enter(self):
        bgm_path = os.path.join(AUDIO_DIR, "bgm_apreciation.wav")
        if os.path.exists(bgm_path):
            self.bgm = SoundLoader.load(bgm_path)
            if self.bgm:
                self.bgm.loop = True
                self.bgm.play()

    def on_leave(self):
        if self.bgm:
            self.bgm.stop()

    def build_form_ui(self):
        self.layout.clear_widgets()
        
        box = BoxLayout(orientation='vertical', spacing=8, padding=12, size_hint=(0.92, 0.92), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        title = Label(text="BERIKAN PENILAIAN ANDA", font_size='13sp', bold=True, color=(1, 0.8, 0.2, 1), size_hint=(1, 0.08), halign='center', valign='middle')
        title.bind(size=title.setter('text_size'))
        box.add_widget(title)

        star_layout = GridLayout(cols=5, spacing=8, size_hint=(1, 0.12))
        self.star_buttons = []
        for i in range(1, 6):
            btn = CapsuleButton(
                text=f"★\n{i}", 
                bg_color=(0.2, 0.2, 0.25, 1), 
                border_color=(0.4, 0.4, 0.4, 0.5), 
                radius=14,
                size_hint=(1, 1)
            )
            btn.font_size = '10sp'; btn.bold = True; btn.color = (1, 1, 1, 1); btn.halign = 'center'; btn.valign = 'middle'
            btn.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            btn.rating_val = i
            btn.bind(on_press=self.select_rating)
            self.star_buttons.append(btn)
            star_layout.add_widget(btn)
        self.update_star_visuals()
        box.add_widget(star_layout)

        form_box = BoxLayout(orientation='vertical', spacing=4, size_hint=(1, 0.54))

        lbl_review = Label(text="Tuliskan ulasan Anda di sini...", font_size='9.5sp', color=(0.8, 0.8, 0.8, 1), size_hint=(1, 0.12), halign='left')
        lbl_review.bind(size=lbl_review.setter('text_size'))
        form_box.add_widget(lbl_review)

        self.input_review = TextInput(text="", font_size='10.5sp', multiline=True, size_hint=(1, 0.42))
        form_box.add_widget(self.input_review)

        lbl_name = Label(text="Tulis nama Anda di sini agar bisa kami update:", font_size='9.5sp', color=(0.8, 0.8, 0.8, 1), size_hint=(1, 0.12), halign='left')
        lbl_name.bind(size=lbl_name.setter('text_size'))
        form_box.add_widget(lbl_name)

        self.input_name = TextInput(text="", font_size='10.5sp', multiline=False, size_hint=(1, 0.26))
        form_box.add_widget(self.input_name)

        box.add_widget(form_box)

        btn_submit = CapsuleButton(
            text="KIRIM PESAN", 
            bg_color=(0.85, 0.1, 0.1, 1), 
            border_color=(1, 0.3, 0.3, 1), 
            radius=16,
            size_hint=(None, None),
            size=(120, 32),
            pos_hint={'center_x': 0.5}
        )
        btn_submit.font_size = '9.5sp'; btn_submit.bold = True; btn_submit.color = (1, 1, 1, 1); btn_submit.halign = 'center'; btn_submit.valign = 'middle'
        btn_submit.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        btn_submit.bind(on_press=self.submit_review)
        box.add_widget(btn_submit)

        self.layout.add_widget(box)

    def select_rating(self, instance):
        self.current_rating = instance.rating_val
        self.update_star_visuals()

    def update_star_visuals(self):
        for btn in self.star_buttons:
            if btn.rating_val <= self.current_rating:
                btn.custom_bg_color = (0.9, 0.7, 0.1, 1)
            else:
                btn.custom_bg_color = (0.2, 0.2, 0.25, 1)
            btn.canvas.before.clear()
            with btn.canvas.before:
                Color(*btn.custom_bg_color)
                btn.bg_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[btn.radius])
                Color(0.4, 0.4, 0.4, 0.5)
                btn.border_line = Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, btn.radius), width=1.2)

    def submit_review(self, instance):
        review = self.input_review.text.strip()
        name = self.input_name.text.strip()
        
        if not name:
            name = "Anonim"
        if not review:
            review = "Tanpa ulasan tertulis."

        # Nomor WhatsApp kamu
        my_whatsapp_number = "6287866742281"
        
        message_body = (
            f"*ULASAN GAME MELAWAN DAJJAL*\n\n"
            f"⭐ *Rating:* {self.current_rating} / 5 Bintang\n"
            f"👤 *Nama:* {name}\n"
            f"💬 *Pesan:* \"{review}\""
        )

        encoded_message = urllib.parse.quote(message_body)
        whatsapp_url = f"https://wa.me/{my_whatsapp_number}?text={encoded_message}"

        try:
            webbrowser.open(whatsapp_url)
        except Exception as e:
            print(f"Gagal membuka WhatsApp: {e}")

        # Setelah dari WhatsApp dan kembali ke game, lanjut ke layar Terima Kasih
        self.build_thankyou_ui(self.current_rating)

    def build_thankyou_ui(self, rating):
        self.layout.clear_widgets()

        box = BoxLayout(
            orientation='vertical', 
            spacing=5,            
            padding=[12, 18, 12, 15], 
            size_hint=(0.92, 0.90), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        title = Label(
            text="TERIMA KASIH ATAS ULASANMU!", 
            font_size='20sp', 
            bold=True, 
            color=(1, 0.8, 0.2, 1), 
            size_hint=(1, 0.08), 
            halign='center', 
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        box.add_widget(title)

        messages = {
            1: "Wah, terima kasih banyak sudah mampir dan memberikan ratingnya. Mohon maaf banget ya kalau game 'Melawan Dajjal' ini masih banyak kurangnya atau bikin kamu kurang nyaman. Masukan sejujurnya dari kamu bakal jadi catatan penting buat kami untuk perbaikin dan rombak banyak hal supaya ke depannya jadi jauh lebih baik lagi. Terima kasih ya!",
            2: "Terima kasih banyak atas waktunya untuk mencoba game ini dan memberikan ulasannya. Kami ngerti banget kalau masih ada bagian yang terasa kurang pas atau bikin bosan. Tenang saja, kritik dan saran dari kamu sudah kami catat kok untuk bahan evaluasi update berikutnya. Tetap semangat ya!",
            3: "Makasih banyak ya sudah meluangkan waktu main 'Melawan Dajjal' dan ngasih rating bintang 3! Senang tahu kalau ada bagian yang cukup menghibur buat kamu. Ke depannya, kami bakal terus nambahin fitur-fitur seru dan poles visualnya biar pengalaman main kamu jadi makin asyik lagi. Ditunggu update selanjutnya ya!",
            4: "Wah, terima kasih banyak atas bintang 4-nya! Senang banget denger kamu menikmati alur cerita dan tantangan di game ini. Apresiasi dan ulasan positif dari kamu bener-bener bikin tim pengembang jadi makin semangat. Jangan lupa mainkan terus dan nantikan update level atau fitur menarik lainnya ya!",
            5: "Wah, luar biasa! Terima kasih banyak atas bintang 5-nya! Senang banget denger kamu suka banget sama game dan konsep sinematiknya. Review dan dukungan semangat dari kamu ini berharga banget buat kami untuk terus berkarya. Tetap jaga iman, sehat selalu, dan sampai jumpa di karya-karya seru berikutnya ya!"
        }
        
        msg_text = messages.get(rating, messages[5])
        
        lbl_msg = Label(
            text=msg_text, 
            font_size='15.5sp', 
            color=(0.9, 0.9, 0.9, 1), 
            size_hint=(1, 0.38),  
            halign='center', 
            valign='middle'
        )
        lbl_msg.bind(size=lbl_msg.setter('text_size'))
        box.add_widget(lbl_msg)

        credits_text = (
            "[b]KREDIT PENGEMBANG[/b]\n"
            "• Tim: Masih kerja sendirian soalnya belum punya karyawan\n"
            "• Pembuat & Sutradara: Abdurrahman Syahir\n"
            "• Pengembangan & Sinematik: Melawan Dajjal Studio"
        )
        
        lbl_credits = Label(
            text=credits_text, 
            markup=True, 
            font_size='15sp', 
            color=(0.8, 0.8, 0.8, 1), 
            size_hint=(1, 0.30),  
            halign='center', 
            valign='middle'
        )
        lbl_credits.bind(size=lbl_credits.setter('text_size'))
        box.add_widget(lbl_credits)

        btn_home = CapsuleButton(
            text="KEMBALI KE MENU", 
            bg_color=(0.85, 0.1, 0.1, 1), 
            border_color=(1, 0.3, 0.3, 1), 
            radius=16,
            size_hint=(None, None),
            size=(130, 32),
            pos_hint={'center_x': 0.5}
        )
        btn_home.font_size = '9.5sp'
        btn_home.bold = True
        btn_home.color = (1, 1, 1, 1)
        btn_home.halign = 'center'
        btn_home.valign = 'middle'
        btn_home.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        btn_home.bind(on_press=self.back_to_menu)
        
        btn_wrapper = FloatLayout(size_hint=(1, 0.14))
        btn_home.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        btn_wrapper.add_widget(btn_home)
        
        box.add_widget(btn_wrapper)
        self.layout.add_widget(box)

    def back_to_menu(self, instance):
        if self.bgm:
            self.bgm.stop()
        self.manager.transition = SlideTransition(direction='right', duration=0.5)
        self.manager.current = 'menu_screen'


# 6. Aplikasi Utama
class MelawanDajjalApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.size = (360, 640)
        
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(MenuScreen(name='menu_screen'))
        sm.add_widget(CutsceneScreen(name='cutscene_screen'))
        sm.add_widget(VictoryPhotoScreen(name='victory_photo_screen'))
        sm.add_widget(AppreciationScreen(name='appreciation_screen'))
        
        return sm

if __name__ == '__main__':
    MelawanDajjalApp().run()