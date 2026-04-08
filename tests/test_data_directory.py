"""Tests for DataDirectory utility."""
import os
import shutil
import tempfile

import pytest

from arceus.utils.data_directory import DataDirectory


@pytest.fixture
def tmp_root(tmp_path):
    return str(tmp_path)


def test_path_creates_directory(tmp_root):
    dd = DataDirectory(dID=1, comment='test', root=tmp_root)
    p = dd.path()
    assert os.path.isdir(p)


def test_path_format_with_comment(tmp_root):
    dd = DataDirectory(dID=5, comment='myrun', root=tmp_root)
    p = dd.path()
    assert 'D005_myrun' in p


def test_path_format_no_comment(tmp_root):
    dd = DataDirectory(dID=3, root=tmp_root)
    p = dd.path()
    assert 'D003' in p
    assert '_' not in os.path.basename(p.rstrip(os.sep))


def test_id_zero_padding(tmp_root):
    dd = DataDirectory(dID=7, root=tmp_root)
    assert dd.ID() == '007'


def test_file_organizer(tmp_root):
    # Create a fake dated subdirectory with CSV files named with Iset tokens
    date_dir = os.path.join(tmp_root, '20250101', 'D001')
    os.makedirs(date_dir)
    fnames = [
        'TimevsTemp_TsetC_30_Iset_1.00e-04.csv',
        'TimevsVolt_TsetC_30_Iset_2.00e-04.csv',
    ]
    for fname in fnames:
        open(os.path.join(date_dir, fname), 'w').close()

    dd = DataDirectory(directory=date_dir, key='Iset')
    dd.file_organizer()

    assert os.path.isdir(os.path.join(date_dir, 'Iset_1.00e-04.csv'))
    assert os.path.isdir(os.path.join(date_dir, 'Iset_2.00e-04.csv'))
