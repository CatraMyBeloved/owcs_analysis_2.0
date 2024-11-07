from src.database import save_championship
from src.analysis import Visualizer

def main():
    championship_id = "3976270f-6138-4289-81d9-998927cce41e"
    muncher, db = save_championship(championship_id)

if __name__ == '__main__':
    main()