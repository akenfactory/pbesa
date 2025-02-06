pip uninstall pbesa -y;
rm -rf dist;
python setup.py bdist_wheel;
pip install dist/pbesa-4.0.0-py3-none-any.whl;