# coding: utf-8

import datetime
import os
from django import forms
from django.utils import timezone, six


class DailyFileManager(object):

    def __init__(self):
        self.open_files = {}
        self.current_date = timezone.now().date()

    def is_open(self, file_name):
        if timezone.now().date() != self.current_date:
            # Archive file
            old_current_date = self.current_date
            archive_file_name = '%s.%s' % (file_name, old_current_date)

            opened_file = self.open_files.get(file_name, None)
            if opened_file:
                opened_file.close()
            if os.path.exists(archive_file_name):
                with open(archive_file_name, 'a') as fp:
                    temp = open(file_name, 'r')
                    fp.write(temp.read())
                    temp.close()
            else:
                os.rename(file_name, archive_file_name)

            self.current_date = timezone.now().date()
            for key in self.open_files:
                self.open_files[key].close()
                self.open_files[key] = open('%s' % key, 'a')

        if file_name in self.open_files:
            return True

    def open(self, file_name):
        self.open_files[file_name] = open('%s' % file_name, 'a')

    def write(self, file_name, data):
        self.open_files[file_name].write(data)
        self.open_files[file_name].flush()


daily_file_manager = DailyFileManager()


class DailyLogForm(forms.Form):
    name = forms.CharField()
    created = forms.CharField()
    level = forms.CharField()
    process = forms.CharField()
    thread = forms.CharField()
    filename = forms.CharField()
    line_no = forms.CharField()
    module = forms.CharField()
    func_name = forms.CharField()
    msg = forms.CharField()
    log_path = forms.CharField()

    def write_file(self):
        created = self.cleaned_data['created']

        level = self.cleaned_data["level"]
        process = self.cleaned_data['process']
        thread = self.cleaned_data['thread']

        filename = self.cleaned_data['filename']
        line_no = self.cleaned_data["line_no"]
        module = self.cleaned_data['module']

        func_name = self.cleaned_data["func_name"]
        msg = self.cleaned_data['msg']

        log_path = self.cleaned_data["log_path"]
        time = datetime.datetime.fromtimestamp(float(created)).strftime('%Y-%m-%d %H:%M:%S')

        data = "%s | %s | %s : %s | %s: %s | %s. %s | %s \n" % (
            time, level, process, thread, filename, line_no, module, func_name, msg
        )

        if not daily_file_manager.is_open(log_path):
            daily_file_manager.open(log_path)

        if six.PY2:
            data = data.encode('UTF-8')

        daily_file_manager.write(log_path, data)