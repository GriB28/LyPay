from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
from datetime import datetime
from psutil import cpu_percent as CPU, virtual_memory as RAM, process_iter

from os import getcwd, listdir


EXE_path = getcwd() + '\\data\\executor'

data_source = ColumnDataSource(data={
    'CPU_t': [],
    'RAM_t': [],
    'CPU_b': [],
    'RAM_b': [],
    'EXE': [],
    't': []
})

graph1 = figure(
    x_axis_type='datetime',
    y_axis_type='linear',
    width=1800, height=900,
    tooltips=[('CPU_t', '@CPU_t'), ('RAM_t', '@RAM_t')],
    title='Heartbeat: total'
)
graph2 = figure(
    x_axis_type='datetime',
    y_axis_type='linear',
    width=1800, height=900,
    tooltips=[('CPU_b', '@CPU_b'), ('RAM_b', '@RAM_b')],
    title='Heartbeat: build'
)
graph3 = figure(
    x_axis_type='datetime',
    y_axis_type='linear',
    width=1800, height=900,
    tooltips=[('EXE', '@EXE')],
    title='Heartbeat: exe tasks'
)

graph1.line(
    x='t',
    y='CPU_t',
    line_color='blue',
    line_width=3.0,
    source=data_source,
    legend_label="CPU total"
)
graph1.line(
    x='t',
    y='RAM_t',
    line_color='red',
    line_width=3.0,
    source=data_source,
    legend_label="RAM total"
)
graph2.line(
    x='t',
    y='CPU_b',
    line_color='blue',
    line_width=3.0,
    source=data_source,
    legend_label="CPU build"
)
graph2.line(
    x='t',
    y='RAM_b',
    line_color='red',
    line_width=3.0,
    source=data_source,
    legend_label="RAM build"
)
graph3.line(
    x='t',
    y='EXE',
    line_color='green',
    line_width=3.0,
    source=data_source,
    legend_label="EXE tasks"
)

graph1.xaxis.formatter = DatetimeTickFormatter(
    seconds='%H:%M:%S',
    minutes='%H:%M:%S',
    hours='%H:%M:%S',
    days='%H:%M:%S'
)
graph2.xaxis.formatter = DatetimeTickFormatter(
    seconds='%H:%M:%S',
    minutes='%H:%M:%S',
    hours='%H:%M:%S',
    days='%H:%M:%S'
)
graph3.xaxis.formatter = DatetimeTickFormatter(
    seconds='%H:%M:%S',
    minutes='%H:%M:%S',
    hours='%H:%M:%S',
    days='%H:%M:%S'
)


def stream():
    r_total = RAM()
    c_total = CPU()
    python_processes = list()
    for running_process in process_iter():
        if running_process.name() == "python.exe":
            python_processes.append(running_process)
    if len(python_processes) == 0:
        print("[LPAA] machine call fail\nПроцесс python.exe не найден!")

    new_data = {
        'CPU_t': [c_total],
        'RAM_t': [round(r_total.percent, 2)],
        'CPU_b': [sum(list(map(lambda p: p.cpu_percent(), python_processes))) / len(python_processes)],
        'RAM_b': [round(sum(list(map(lambda p: p.memory_percent(), python_processes))) / len(python_processes), 2)],
        'EXE': [len(list(f for f in listdir(EXE_path) if f.find('.log') == -1))],
        't': [datetime.now()]
    }

    data_source.stream(new_data, None)


curdoc().add_periodic_callback(stream, 300)
curdoc().add_root(graph1)
curdoc().add_root(graph2)
curdoc().add_root(graph3)
