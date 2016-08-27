from distutils.core import setup

setup(
    name='pixelsorter',
    packages=['pixelsorter'],
    version='1.2',
    description='A powerful and extensible library for pixel-sorting.',
    author='Raphael Kargon',
    author_email='raphael.kargon@gmail.com',
    url='https://github.com/rkargon/pixelsorter',
    download_url='https://github.com/rkargon/pixelsorter/tarball/1.1',
    keywords=['pixelsorting', 'glitch art', 'pixel', 'sorting'],
    classifiers=[],
    install_requires=["Pillow"],
    scripts=['pixelsort']
)
