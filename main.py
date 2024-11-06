from src.database import save_championship
from src.analysis import BaseAnalyzer, Visualizer

def main():
    championship_id = "your_id"
    muncher, db = save_championship(championship_id)

if __name__ == '__main__':
    main()