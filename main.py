from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from datetime import datetime, timedelta

Builder.load_string('''
<StopwatchScreen>:
    orientation: 'vertical'
    Label:
        text: "Selecione o tempo total de foco:"
    Label:
        text: "Horas"
    Spinner:
        id: hours_spinner
        text: '0'
        values: [str(i) for i in range(0, 13)]
        size_hint: (None, None)
        size: (100, 44)
        pos_hint: {'center_x': 0.5}
    Label:
        text: "Minutos"
    Spinner:
        id: minutes_spinner
        text: '0'
        values: [str(i) for i in range(0, 61)]
        size_hint: (None, None)
        size: (100, 44)
        pos_hint: {'center_x': 0.5}
    Button:
        text: "Set Time"
        on_press: root.set_time()
    Label:
        id: time_display
        text: "00:00:00"
        font_size: 48
    Label:
        id: countdown_label
        text: "Contagem regressiva: 00:00:00"
    Label:
        id: focus_periods_label
        text: "Períodos de foco: 0"
    Label:
        id: estimated_periods_label
        text: "Estimativa de períodos necessários: -"
    Label:
        id: total_dedication_label
        text: "Tempo total de dedicação: 00:00:00"
    Button:
        text: "Start"
        on_press: root.start()
        disabled: True
    Button:
        text: "Stop"
        on_press: root.stop()
        disabled: True
    Button:
        text: "Reset"
        on_press: root.reset()
        disabled: True
''')

class StopwatchScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_focus_time = timedelta(0)
        self.focus_time_remaining = timedelta(0)
        self.elapsed_time = timedelta(0)
        self.focus_periods = 0
        self.focus_times = []
        self.total_dedication_time = timedelta(0)
        self.running = False
        self.in_rest_period = False

    def set_time(self):
        try:
            hours = int(self.ids.hours_spinner.text)
            minutes = int(self.ids.minutes_spinner.text)
            total_seconds = (hours * 3600) + (minutes * 60)
            self.total_focus_time = timedelta(seconds=total_seconds)
            self.focus_time_remaining = self.total_focus_time
            self.ids.start.disabled = False
            self.ids.stop.disabled = False
            self.ids.reset.disabled = False
        except ValueError:
            self.ids.time_display.text = "Erro: selecione horas e minutos válidos"

    def update(self, dt):
        if self.running and not self.in_rest_period:
            current_time = datetime.now()
            self.elapsed_time = current_time - self.start_time
            self.ids.time_display.text = str(self.elapsed_time).split(".")[0]

    def start(self):
        if not self.running:
            self.start_time = datetime.now() - self.elapsed_time
            self.running = True
            Clock.schedule_interval(self.update, 0.05)

    def stop(self):
        if self.running:
            self.running = False
            self.in_rest_period = True
            self.rest_duration = self.elapsed_time / 4
            self.total_dedication_time += self.elapsed_time
            self.update_total_dedication_label()
            self.elapsed_time = timedelta(0)
            self.ids.time_display.text = "00:00:00"
            self.focus_periods += 1
            self.ids.focus_periods_label.text = f"Períodos de foco: {self.focus_periods}"
            self.focus_times.append(self.rest_duration * 4)
            self.recalculate_estimation()
            self.countdown(int(self.rest_duration.total_seconds()))

    def reset(self):
        self.running = False
        self.in_rest_period = False
        self.elapsed_time = timedelta(0)
        self.focus_time_remaining = self.total_focus_time
        self.total_dedication_time = timedelta(0)
        self.ids.time_display.text = "00:00:00"
        self.ids.countdown_label.text = "Contagem regressiva: 00:00:00"
        self.focus_periods = 0
        self.focus_times = []
        self.ids.focus_periods_label.text = "Períodos de foco: 0"
        self.ids.estimated_periods_label.text = "Estimativa de períodos necessários: -"
        self.ids.total_dedication_label.text = "Tempo total de dedicação: 00:00:00"

    def countdown(self, remaining_seconds):
        if remaining_seconds > 0:
            mins, secs = divmod(remaining_seconds, 60)
            self.ids.countdown_label.text = f"Contagem regressiva: {mins:02}:{secs:02}"
            Clock.schedule_once(lambda dt: self.countdown(remaining_seconds - 1), 1)
        else:
            self.in_rest_period = False
            self.focus_time_remaining -= timedelta(seconds=self.rest_duration.total_seconds() * 4)
            if self.focus_time_remaining > timedelta(0):
                self.start()
            else:
                self.reset()

    def recalculate_estimation(self):
        if len(self.focus_times) > 0:
            average_focus_time = sum(self.focus_times, timedelta()) / len(self.focus_times)
            estimated_periods = int(self.total_focus_time / average_focus_time)
            self.ids.estimated_periods_label.text = f"Estimativa de períodos necessários: {estimated_periods}"

    def update_total_dedication_label(self):
        total_dedication_str = str(self.total_dedication_time).split(".")[0]
        self.ids.total_dedication_label.text = f"Tempo total de dedicação: {total_dedication_str}"

class StopwatchApp(App):
    def build(self):
        return StopwatchScreen()

if __name__ == '__main__':
    StopwatchApp().run()
