# DataDirectory — date-stamped save-path helper
import datetime
import glob
import os
import shutil

DEFAULT_ROOT = 'C:\\Lab_Data\\Data'


class DataDirectory:

    def __init__(self, dID=None, comment='', root=DEFAULT_ROOT, **kwargs):
        self.dID = dID
        self.comment = comment
        self.root = root
        self.__dict__.update(kwargs)

    def date(self):
        return datetime.datetime.now().strftime("%Y%m%d")

    def ID(self):
        return "{:03d}".format(int(self.dID))

    def path(self):
        folder = 'D{}_{}'.format(self.ID(), self.comment) if self.comment else 'D{}'.format(self.ID())
        p = os.path.join(self.root, self.date(), folder) + os.sep
        if not os.path.exists(p):
            os.makedirs(p)
        return p

    def get_csvs(self):
        return glob.glob(os.path.join(self.directory, "*.csv"))

    def get_setpoint(self, f):
        split_str = f.split('_')
        try:
            index = split_str.index(self.key)
        except ValueError:
            print(f"'{self.key}' not found in filename: {split_str}")
            raise
        return split_str[index + 1]

    def file_organizer(self):
        for f in self.get_csvs():
            sp = self.get_setpoint(f)
            dest_dir = os.path.join(self.directory, 'Iset_{}'.format(sp))
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(f))
            try:
                shutil.copy(f, dest)
            except FileNotFoundError:
                print(f"Source not found: {f}")
            except Exception as e:
                print(f"Error copying {f}: {e}")

    def sub_dirs(self):
        return [d for d in os.listdir(self.directory) if os.path.isdir(os.path.join(self.directory, d))]


if __name__ == "__main__":
    dd = DataDirectory(directory='C:\\Lab_Data\\Data\\20250723\\D000', key='Iset')
    dd.file_organizer()
