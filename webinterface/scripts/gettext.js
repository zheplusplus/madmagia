window.mad = window.mad || {};
window.mad.gettext = function(t) {
    return {
        del_proj: '删除此项目',
        project_removed: '此项目已经被删除, 若需要恢复项目, 请新建一个项目, 然后将以下信息填入对应的输入框内',
        hint_ctrl_f_file: '你可以按下 Ctrl+F 用浏览器页面检索来寻找你想要的文件',
        select_current_dir: '选用当前目录',
        mkdir: '在当前位置创建一个目录',
        path_not_available: '此目录不存在, 请从上方路径中重新选择, 或单击左上角两条斜线来选择盘符',

        audio_path: '音频文件路径',
        video_path: '视频目录',
        output_path: '输出文件以及临时文件目录',
        select_file: '选择文件',
        select_dir: '选择目录',
        new_proj_name: '新建项目名',
        new_proj: '新建一个项目',
        save_projs: '保存所有项目信息',

        bad_audio: '无法读取音频文件的信息, 请确定文件存在, 并且是音频文件; 请返回项目面板重新选取',
        bad_video: '指定的视频文件不存在, 或损坏, 或非可操作的格式',
        bad_video_dir: '无法在指定的视频目录下找到视频文件, 或者视频文件命名不合规则; 请返回项目面板重新选取',
        empty_output_dir: '请返回项目面板为此项目指定一个输出目录',
        bad_output_dir: '无法在指定的输出目录下找到或新建项目文件, 请返回项目面板重新选取',

        section_enable_edit: '编辑分节',
        section_disable_edit: '预览分节',
        play_section_audio: '播放此分节内音频',
        play_section_as_first: '从此分节开始预览',
        play_section_as_last: '到此分节结束',
        play_section_cancel: '取消预览',
        new_section: '在此分节之后插入一个新分节',
        edit_section: '编辑此分节',
        del_section: '删除此分节',

        segment_panel_title: '片段规格设置',
        new_segment: '在此加入一个片段',
        del: '删',
        seg_filter_fillspan: '拉伸/压缩视频长度至',
        seg_filter_repeatframe: '单画面定格',
        seg_filter_hflip: '水平翻转',
        default_new_section_name_prefix: '新分节-',
        auto_created_section_name_prefix: '作为结束自动建立的分节-',

        edit_invalid_time: '不正确的时间格式',
        edit_invalid_num: '不正确的数值格式',
        bad_section_name: '不正确的分节名称',
        bad_section_name: '不正确的分节名称',
        section_time_out_of_range: '分节开始时间越界',

        slicing_segment: '正在准备片段',
        merging_segments: '正在合并片段 请耐心等待',
        segments_exported: '视频已输出到本机硬盘',

        about: '关于',

        '': ''
    }[t] || t;
};
