# encoding=utf-8

import os
import tempfile
import subprocess
import Tkinter as tk
import tkFileDialog as tkfd
import tkMessageBox as tkmsg
import ttk
from PIL import ImageTk

from config import config
import sequence
import avmerge
import video_slice


def start_merge(widgets):
    for w in ['avconv_path', 'mencoder_path', 'input_video_dir',
              'input_audio_file', 'output_path', 'sequence_file',
              'select_begin']:
        if not widgets[w].get():
            tkmsg.showerror(u'漏填参数', u'以上输入框中至少有一项内容没有填写')
            return widgets[w].focus_set()
    begin_sec_index = widgets['select_begin'].current()
    end_sec_index = widgets['select_end'].current()
    end_sec_name = widgets['select_end'].get()
    if begin_sec_index == -1 or (end_sec_name != '' and end_sec_index != 0 and
            end_sec_index <= begin_sec_index):
        tkmsg.showerror(
            u'节错误', u'开始节必须在结束节之前\n请检查选择的节名')
        return widgets['select_begin'].focus_set()
    config['avconv'] = widgets['avconv_path'].get()
    config['mencoder'] = widgets['mencoder_path'].get()
    avmerge.merge_partial(
        widgets['sequence_file'].get(), widgets['input_video_dir'].get(),
        widgets['input_audio_file'].get(), widgets['output_path'].get(),
        widgets['select_begin'].get(), end_sec_name)
    tkmsg.showinfo(u'搞定', u'已经做好了 \\(^o^)/')


def display_frame(topframe, widgets):
    config['avconv'] = widgets['avconv_path'].get()
    time_str = widgets['view_frame_time'].get()
    time = sequence.parse_time(time_str)
    if time is None:
        return tkmsg.showerror(u'错误的时间格式', u'错误的时间格式')
    videofile = widgets['view_frame_file'].get()
    imgf = video_slice.save_frame(videofile, time)
    if imgf is None:
        return tkmsg.showerror(u'图片生成时错误',
                               u'请确认时间没有超过视频播放时间')
    t = tk.Toplevel(topframe)
    t.wm_title(u'%s - %s' % (videofile, time_str))
    lbl = tk.Label(t, image=ImageTk.PhotoImage(file=imgf))
    lbl.pack(side='top', fill='both', expand=True)


class Entry(tk.Entry):
    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)

    def set_text(self, text):
        self.delete(0, tk.END)
        self.insert(0, text)


class MainFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        parent.title('Mad Magia')

        self._rownum = 0
        self._colnum = 0
        self._widgets = []
        self._widget_by_name = dict()

        self._init_widgets()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.pack(side='top', fill='x')

    def _init_widgets(self):
        self._widgets.append([
            self._mklabel(u'MAD 制作'),
        ])
        self._break()

        self._widgets.append([
            self._mklabel(u'AVConv 程序'),
            self._mkentry('avconv_path', os.path.realpath(config['avconv'])),
            self._mkbutton(u'手动选择 AVConv 应用程序',
                           self._ask_file_for('avconv_path')),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'MEncoder 程序'),
            self._mkentry('mencoder_path',
                          os.path.realpath(config['mencoder'])),
            self._mkbutton(u'手动选择 MEncoder 应用程序',
                           self._ask_file_for('mencoder_path')),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'输入视频文件目录'),
            self._mkentry('input_video_dir'),
            self._mkbutton(u'选择', self._ask_dir_for('input_video_dir')),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'输入音频文件'),
            self._mkentry('input_audio_file'),
            self._mkbutton(u'选择', self._ask_file_for('input_audio_file')),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'设置输出文件路径'),
            self._mkentry('output_path'),
            self._mkbutton(u'选择输出目录 (默认命名为 output.mp4)',
                           self._ask_dir_for('output_path', 'output.mp4')),
        ])
        self._break()

        def reset_sequence():
            try:
                seq_file = self._widget_by_name['sequence_file'].get()
                if not seq_file:
                    return tkmsg.showerror(u'请选择正确的序列文件')
                with open(seq_file, 'r') as seqf:
                    try:
                        secs = sequence.parse(seqf.readlines())[0][1:]
                    except sequence.ParseError, e:
                        return tkmsg.showerror(
                            u'序列文件格式错误',
                            u'发生在第 %d 行 (%s).\n详细信息: %s' % (
                                e.linenum, e.content, e.message))
                sec_names = [s.name for s in secs]

                select_begin = self._widget_by_name['select_begin']
                select_begin['values'] = [':begin'] + sec_names
                if select_begin.current() == -1:
                    select_begin.current(0)

                select_end = self._widget_by_name['select_end']
                select_end['values'] = [':end'] + sec_names
                if select_end.current() == -1:
                    select_end.current(0)
            except IOError:
                tkmsg.showerror(u'无法读取序列文件', u'无法读取序列文件')

        def on_sequence_file_selected():
            if self._ask_file_for('sequence_file')():
                reset_sequence()

        self._widgets.append([
            self._mklabel(u'序列文件'),
            self._mkentry('sequence_file'),
            self._mkbutton(u'选择', on_sequence_file_selected),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'开始节'),
            self._mkcombo('select_begin'),
            self._mkbutton(u'刷新序列文件', reset_sequence),
        ])
        self._break()
        self._widgets.append([
            self._mklabel(u'结束节'),
            self._mkcombo('select_end'),
            self._mkbutton(u'走你', lambda: start_merge(self._widget_by_name)),
        ])
        self._break()

        self._widgets.append([
            self._mklabel(u'查看视频帧'),
        ])
        self._break()

        self._widgets.append([
            self._mklabel(u'图片查看程序'),
            self._mkentry('display_path', os.path.realpath(config['display'])),
            self._mkbutton(u'手动选择图片查看程序',
                           self._ask_file_for('display_path')),
        ])
        self._break()

        self._widgets.append([
            self._mklabel(u'视频文件'),
            self._mkentry('view_frame_file'),
            self._mkbutton(u'选择视频', self._ask_file_for('view_frame_file')),
        ])
        self._break()

        self._widgets.append([
            self._mklabel(u'时刻'),
            self._mkentry('view_frame_time'),
            self._mkbutton(u'查看',
                           lambda: display_frame(self, self._widget_by_name)),
        ])
        self._break()

    def _break(self):
        self._rownum += 1
        self._colnum = 0

    def _mklabel(self, text):
        label = tk.Label(self, text=text, borderwidth=0, width=10)
        label.grid(row=self._rownum, column=self._colnum, sticky='nsew',
                   padx=1, pady=1)
        self._colnum += 1
        return label

    def _mkbutton(self, text, command):
        button = tk.Button(self, text=text, command=command)
        button.grid(row=self._rownum, column=self._colnum, sticky='nsew',
                    padx=1, pady=1)
        self._colnum += 1
        return button

    def _mkentry(self, name, default_text=''):
        entry = Entry(self)
        entry.set_text(default_text)
        entry.grid(row=self._rownum, column=self._colnum, sticky='nsew',
                   padx=1, pady=1)
        self._colnum += 1
        self._widget_by_name[name] = entry
        return entry

    def _mkcombo(self, name):
        cb = ttk.Combobox(self)
        cb.grid(row=self._rownum, column=self._colnum, sticky='nsew', padx=1,
                pady=1)
        self._colnum += 1
        self._widget_by_name[name] = cb
        return cb

    def _ask_file_for(self, widget_name):
        def ask_file():
            widget = self._widget_by_name[widget_name]
            fn = tkfd.askopenfilename(initialdir=os.path.dirname(widget.get()))
            if fn:
                widget.set_text(os.path.realpath(fn))
                widget.focus_set()
                return True
            return False
        return ask_file

    def _ask_dir_for(self, widget_name, append_name=''):
        def ask_file():
            widget = self._widget_by_name[widget_name]
            fn = tkfd.askdirectory(initialdir=os.path.dirname(widget.get()))
            if fn:
                widget.set_text(os.path.join(os.path.realpath(fn),
                                             append_name))
                widget.focus_set()
        return ask_file


def main():
    def confirm_exit():
        if tkmsg.askyesno(u'确认退出', u'确认要退出喵'):
            root.destroy()

    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', confirm_exit)
    MainFrame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
