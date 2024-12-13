from setuptools import setup, find_packages

setup(
    name="Anime Genre Selector",
    version="1.0.0",
    description="Select your favorite genere to give the best 10 options usingAniList API.",
    author="Shane vibert",
    author_email="your_email@example.com",
    url="https://github.com/ShaneVibert/Anime_Scrapper",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pillow>=9.4.0",
    ],
    entry_points={
        "console_scripts": [
            "anime-finder=anime_finder.main:main",  # Creates a CLI command 'anime-finder' to run your app
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
